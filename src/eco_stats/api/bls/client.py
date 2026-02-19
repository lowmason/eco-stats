'''
Client for the Bureau of Labor Statistics (BLS).

All data methods return :class:`polars.DataFrame` objects with typed
columns.  Where applicable a ``date`` column is derived from the BLS
``year`` and ``period`` fields.

Four layers of access:

1. **JSON API** — ``get_series()`` and convenience methods hit the
   BLS Public Data API (v1 without key, v2 with key).
2. **Discovery** — ``list_programs()``, ``get_mapping()``,
   ``search_series()`` expose the LABSTAT metadata.
3. **Flat files** — ``get_bulk_data()`` downloads complete
   tab-delimited datasets with no rate limits.
4. **QCEW slices** — ``get_qcew_industry()``, ``get_qcew_area()``,
   ``get_qcew_size()`` use the CEW open-data CSV API.
'''

from datetime import date
from typing import Any, Dict, List, Optional

import polars as pl
import requests

from eco_stats.api.bls.flat_files import BLSFlatFileClient
from eco_stats.api.bls.qcew import QCEWClient
from eco_stats.api.bls.programs import (
    BLSProgram,
    get_program,
    list_programs,
)
from eco_stats.api.bls.series_id import build_series_id, parse_series_id

# Programs whose survey reference period is the pay period including
# the 12th of the month.  Dates for these programs use day=12;
# all others default to day=1.
_REFERENCE_DAY_12_PROGRAMS = frozenset({'CE', 'EN'})


def _reference_day(program_prefix: str) -> int:
    '''Return the reference day-of-month for a BLS program prefix.'''
    return 12 if program_prefix.upper() in _REFERENCE_DAY_12_PROGRAMS else 1


def _period_to_month(period: str) -> Optional[int]:
    '''
    Convert a BLS period code to a month number.

    Monthly periods ``M01``–``M12`` map to months 1–12.
    ``M13`` (annual average) returns ``None``.  Quarterly
    ``Q01``–``Q04`` map to the first month of the quarter.
    Semi-annual ``S01``–``S02`` map to months 1 and 7.
    Annual ``A01`` maps to month 1.

    Args:
        period: BLS period string (e.g., ``'M01'``, ``'Q03'``).

    Returns:
        Month number (1–12) or ``None`` if not mappable.
    '''
    if not period or len(period) < 2:
        return None
    code = period[0].upper()
    try:
        num = int(period[1:])
    except (ValueError, TypeError):
        return None

    if code == 'M' and 1 <= num <= 12:
        return num
    if code == 'Q' and 1 <= num <= 4:
        return (num - 1) * 3 + 1
    if code == 'S' and 1 <= num <= 2:
        return (num - 1) * 6 + 1
    if code == 'A':
        return 1
    return None


class BLSClient:
    '''
    Unified client for BLS data access.

    All data methods return :class:`polars.DataFrame` objects with
    typed columns.  Time-series results include a ``date`` column
    derived from the BLS ``year`` and ``period`` fields.

    Args:
        api_key: BLS API registration key (optional but recommended).
            Register at https://data.bls.gov/registrationEngine/
        cache_dir: Local directory for cached flat files.
    '''

    BASE_URL_V2 = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
    BASE_URL_V1 = 'https://api.bls.gov/publicAPI/v1/timeseries/data/'

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: str = '.cache/bls',
    ) -> None:
        self.api_key = api_key
        self.session = requests.Session()
        self.base_url = self.BASE_URL_V2 if api_key else self.BASE_URL_V1
        self._flat = BLSFlatFileClient(cache_dir=cache_dir)
        self._qcew = QCEWClient(cache_dir=f'{cache_dir}/qcew')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_api_response(raw: Dict[str, Any]) -> pl.DataFrame:
        '''
        Parse a BLS JSON API response into a Polars DataFrame.

        Extracts rows from ``Results.series[*].data[*]``, adds a
        ``series_id`` column, constructs a ``date`` from year/period,
        and casts ``value`` to Float64.

        Args:
            raw: The full JSON dict returned by the BLS API.

        Returns:
            A :class:`polars.DataFrame` with columns ``series_id``,
            ``date``, ``year``, ``period``, ``period_name``, ``value``.

        Raises:
            ValueError: If the API response indicates failure.
        '''
        schema = {
            'series_id': pl.Utf8,
            'date': pl.Date,
            'year': pl.Int64,
            'period': pl.Utf8,
            'period_name': pl.Utf8,
            'value': pl.Float64,
        }

        status = raw.get('status', '')
        if status != 'REQUEST_SUCCEEDED':
            message = raw.get('message', [])
            raise ValueError(f'BLS API request failed (status={status!r}): {message}')

        rows: List[Dict[str, Any]] = []
        for series in raw.get('Results', {}).get('series', []):
            sid = series.get('seriesID', '')
            day = _reference_day(sid[:2]) if len(sid) >= 2 else 1
            for obs in series.get('data', []):
                year_str = obs.get('year', '')
                period = obs.get('period', '')

                try:
                    year_int = int(year_str)
                except (ValueError, TypeError):
                    year_int = None

                month = _period_to_month(period)
                obs_date = (
                    date(year_int, month, day)
                    if year_int is not None and month is not None
                    else None
                )

                try:
                    value = float(obs.get('value', ''))
                except (ValueError, TypeError):
                    value = None

                rows.append(
                    {
                        'series_id': sid,
                        'date': obs_date,
                        'year': year_int,
                        'period': period,
                        'period_name': obs.get('periodName', ''),
                        'value': value,
                    }
                )

        return pl.DataFrame(rows, schema=schema).sort('date')

    @staticmethod
    def _add_date_column(df: pl.DataFrame, day: int = 1) -> pl.DataFrame:
        '''
        Derive a ``date`` column from ``year`` and ``period`` columns.

        Uses native Polars expressions so the operation is vectorised
        and efficient on large flat-file datasets.

        Args:
            df: DataFrame with ``year`` (Int64) and ``period`` (Utf8)
                columns.
            day: Day-of-month to use in the constructed date.
                CES and QCEW use 12 (the survey reference date);
                most other programs use 1.

        Returns:
            The input DataFrame with an added ``date`` column of type
            :class:`polars.Date`.
        '''
        period_code = pl.col('period').str.slice(0, 1)
        period_num = pl.col('period').str.slice(1).cast(pl.Int64, strict=False)

        month = (
            pl.when((period_code == 'M') & period_num.is_between(1, 12))
            .then(period_num)
            .when((period_code == 'Q') & period_num.is_between(1, 4))
            .then((period_num - 1) * 3 + 1)
            .when((period_code == 'S') & period_num.is_between(1, 2))
            .then((period_num - 1) * 6 + 1)
            .when(period_code == 'A')
            .then(1)
            .otherwise(None)
        )

        return df.with_columns(pl.date(pl.col('year'), month, day).alias('date'))

    # ------------------------------------------------------------------
    # JSON API access
    # ------------------------------------------------------------------

    def get_series(
        self,
        series_ids: List[str],
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
        catalog: bool = False,
        calculations: bool = False,
        annual_average: bool = False,
        aspects: bool = False,
    ) -> pl.DataFrame:
        '''
        Get time series data via the BLS Public Data API.

        Args:
            series_ids: List of BLS series IDs
                (e.g., ``['LNS14000000']`` for unemployment rate).
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).
            catalog: Include catalog metadata.
            calculations: Include net/percent change calculations.
            annual_average: Include annual averages.
            aspects: Include aspects (if available).

        Returns:
            :class:`polars.DataFrame` with columns ``series_id``,
            ``date``, ``year``, ``period``, ``period_name``, ``value``.
        '''
        payload: Dict[str, Any] = {'seriesid': series_ids}

        if self.api_key:
            payload['registrationkey'] = self.api_key

        if start_year:
            payload['startyear'] = start_year
        if end_year:
            payload['endyear'] = end_year
        if catalog:
            payload['catalog'] = catalog
        if calculations:
            payload['calculations'] = calculations
        if annual_average:
            payload['annualaverage'] = annual_average
        if aspects:
            payload['aspects'] = aspects

        headers = {'Content-Type': 'application/json'}
        response = self.session.post(
            self.base_url,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return self._parse_api_response(response.json())

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def get_unemployment_rate(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
    ) -> pl.DataFrame:
        '''
        Get the U.S. unemployment rate (seasonally adjusted).

        Uses series ``LNS14000000`` from the Labor Force Statistics
        (LN) program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            :class:`polars.DataFrame` with columns ``series_id``,
            ``date``, ``year``, ``period``, ``period_name``, ``value``.
        '''
        return self.get_series(
            series_ids=['LNS14000000'],
            start_year=start_year,
            end_year=end_year,
        )

    def get_cpi_all_items(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
    ) -> pl.DataFrame:
        '''
        Get CPI for All Urban Consumers (CPI-U), All Items.

        Uses series ``CUUR0000SA0`` from the Consumer Price Index (CU)
        program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            :class:`polars.DataFrame` with columns ``series_id``,
            ``date``, ``year``, ``period``, ``period_name``, ``value``.
        '''
        return self.get_series(
            series_ids=['CUUR0000SA0'],
            start_year=start_year,
            end_year=end_year,
        )

    def get_employment(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
    ) -> pl.DataFrame:
        '''
        Get total nonfarm employment (seasonally adjusted).

        Uses series ``CES0000000001`` from the Current Employment
        Statistics (CE) program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            :class:`polars.DataFrame` with columns ``series_id``,
            ``date``, ``year``, ``period``, ``period_name``, ``value``.
        '''
        return self.get_series(
            series_ids=['CES0000000001'],
            start_year=start_year,
            end_year=end_year,
        )

    def get_average_hourly_earnings(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
    ) -> pl.DataFrame:
        '''
        Get average hourly earnings of all employees (seasonally adjusted).

        Uses series ``CES0500000003`` from the Current Employment
        Statistics (CE) program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            :class:`polars.DataFrame` with columns ``series_id``,
            ``date``, ``year``, ``period``, ``period_name``, ``value``.
        '''
        return self.get_series(
            series_ids=['CES0500000003'],
            start_year=start_year,
            end_year=end_year,
        )

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_programs(self) -> Dict[str, str]:
        '''
        List all registered BLS programs.

        Returns:
            Dictionary of ``{prefix: program_name}``.

        Example::

            >>> client.list_programs()
            {'AP': 'Average Price Data',
             'BD': 'Business Employment Dynamics',
             'CE': 'Current Employment Statistics (National)',
             ...}
        '''
        return list_programs()

    def get_program_info(self, prefix: str) -> BLSProgram:
        '''
        Get detailed metadata for a BLS program.

        Args:
            prefix: Two-letter program code (e.g., ``"CE"``).

        Returns:
            :class:`BLSProgram` with fields, mapping files, etc.
        '''
        return get_program(prefix)

    def get_mapping(
        self,
        program: str,
        mapping_name: str,
    ) -> pl.DataFrame:
        '''
        Download a mapping/lookup table for a program.

        For example, ``get_mapping("CU", "area")`` returns a DataFrame
        of all CPI area codes and their names.

        Args:
            program: Two-letter program prefix.
            mapping_name: Mapping file name (e.g., ``"area"``,
                ``"industry"``, ``"item"``).

        Returns:
            :class:`polars.DataFrame` with one row per entry.
        '''
        rows = self._flat.get_mapping(program, mapping_name)
        if not rows:
            return pl.DataFrame()
        return pl.DataFrame(rows)

    def search_series(
        self,
        program: str,
        **filters: str,
    ) -> pl.DataFrame:
        '''
        Search the master series list for a program.

        Filters are applied as exact matches on column values.

        Args:
            program: Two-letter program prefix.
            **filters: Column name -> value pairs for filtering.

        Returns:
            :class:`polars.DataFrame` of matching series metadata.

        Example::

            >>> client.search_series('CE', seasonal='S',
            ...                      data_type_code='01')
        '''
        rows = self._flat.get_series_list(program, **filters)
        if not rows:
            return pl.DataFrame()
        return pl.DataFrame(rows)

    # ------------------------------------------------------------------
    # Series ID helpers
    # ------------------------------------------------------------------

    def parse_series_id(self, series_id: str) -> Dict[str, str]:
        '''
        Decompose a series ID into its named component fields.

        Args:
            series_id: Full BLS series ID string.

        Returns:
            Dictionary mapping field names to extracted values.

        Example::

            >>> client.parse_series_id('CUUR0000SA0')
            {'program': 'CU', 'prefix': 'CU', 'seasonal': 'U',
             'periodicity': 'R', 'area': '0000', 'item': 'SA0'}
        '''
        return parse_series_id(series_id)

    def build_series_id(self, program: str, **components: str) -> str:
        '''
        Construct a series ID from named components.

        Components not provided are zero-filled to the correct width.

        Args:
            program: Two-letter program prefix.
            **components: Field values keyed by name.

        Returns:
            Assembled series ID string.

        Example::

            >>> client.build_series_id(
            ...     'CU', seasonal='U', periodicity='R',
            ...     area='0000', item='SA0')
            'CUUR0000SA0'
        '''
        return build_series_id(program, **components)

    # ------------------------------------------------------------------
    # QCEW (Quarterly Census of Employment and Wages) — CSV slices
    # ------------------------------------------------------------------

    def get_qcew_industry(
        self,
        industry_code: str = '10',
        start_year: int = 2016,
        end_year: int = 2026,
        quarters: Optional[List[int]] = None,
    ) -> pl.DataFrame:
        '''
        Fetch QCEW data sliced by industry across a year range.

        Uses the CEW open-data CSV API at ``data.bls.gov``.

        Args:
            industry_code: NAICS or supersector code.  ``'10'`` for
                total, all industries.  Hyphenated NAICS codes use
                underscores (e.g., ``'31_33'`` for manufacturing).
            start_year: First year to fetch (inclusive).
            end_year: Last year to fetch (inclusive).
            quarters: Quarters to include (default ``[1, 2, 3, 4]``).

        Returns:
            :class:`polars.DataFrame` with the QCEW quarterly CSV
            columns.
        '''
        return self._qcew.get_industry(industry_code, start_year, end_year, quarters)

    def get_qcew_area(
        self,
        area_code: str = 'US000',
        start_year: int = 2016,
        end_year: int = 2026,
        quarters: Optional[List[int]] = None,
    ) -> pl.DataFrame:
        '''
        Fetch QCEW data sliced by area across a year range.

        Uses the CEW open-data CSV API at ``data.bls.gov``.

        Args:
            area_code: FIPS-style area code.  ``'US000'`` for national
                totals; state codes like ``'26000'`` (Michigan).
            start_year: First year to fetch (inclusive).
            end_year: Last year to fetch (inclusive).
            quarters: Quarters to include (default ``[1, 2, 3, 4]``).

        Returns:
            :class:`polars.DataFrame` with the QCEW quarterly CSV
            columns.
        '''
        return self._qcew.get_area(area_code, start_year, end_year, quarters)

    def get_qcew_size(
        self,
        size_code: str = '1',
        start_year: int = 2016,
        end_year: int = 2026,
    ) -> pl.DataFrame:
        '''
        Fetch QCEW data sliced by establishment-size class.

        Size data is only published for Q1 of each year and excludes
        size code 0 (all sizes).

        Args:
            size_code: Size class code (``'1'``–``'9'``).
            start_year: First year to fetch (inclusive).
            end_year: Last year to fetch (inclusive).

        Returns:
            :class:`polars.DataFrame` with the QCEW quarterly CSV
            columns.
        '''
        return self._qcew.get_size(size_code, start_year, end_year)

    # ------------------------------------------------------------------
    # Flat file / bulk data access
    # ------------------------------------------------------------------

    def get_bulk_data(
        self,
        program: str,
        file_suffix: str = '0.Current',
    ) -> pl.DataFrame:
        '''
        Download a complete data file from BLS flat files.

        For the QCEW program (``'EN'``), this automatically uses the
        CEW open-data CSV API instead of the LABSTAT flat files (which
        are frequently blocked).  Use :meth:`get_qcew_industry`,
        :meth:`get_qcew_area`, or :meth:`get_qcew_size` for more
        control over QCEW queries.

        Args:
            program: Two-letter program prefix (e.g., ``"CE"``).
            file_suffix: Portion after ``xx.data.`` in the filename.
                Common suffixes include ``"0.Current"`` and
                ``"0.AllCESSeries"`` (for CE).  Ignored when
                *program* is ``"EN"``.

        Returns:
            :class:`polars.DataFrame`.  For most programs this has
            columns ``series_id``, ``date``, ``year``, ``period``,
            ``value``, ``footnote_codes``.  For ``EN`` (QCEW) the
            native CSV columns are returned instead (``area_fips``,
            ``own_code``, ``industry_code``, ``year``, ``qtr``,
            employment levels, wages, etc.).
        '''
        if program.upper() == 'EN':
            return self.get_qcew_industry()

        rows = self._flat.get_data(program, file_suffix)
        if not rows:
            return pl.DataFrame()

        df = pl.DataFrame(rows)

        # Flat files return all strings — cast numeric columns.
        if 'year' in df.columns:
            df = df.with_columns(pl.col('year').cast(pl.Int64, strict=False))
        if 'value' in df.columns:
            df = df.with_columns(pl.col('value').cast(pl.Float64, strict=False))

        # Derive date from year + period.
        if 'year' in df.columns and 'period' in df.columns:
            df = self._add_date_column(df, day=_reference_day(program))

            # Reorder so date is near the front.
            col_order = ['series_id', 'date', 'year', 'period', 'value']
            extra = [c for c in df.columns if c not in col_order]
            df = df.select([c for c in col_order if c in df.columns] + extra)
            df = df.sort('series_id', 'date')

        return df

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        '''Close HTTP sessions.'''
        self.session.close()
        self._flat.close()
        self._qcew.close()

    def __enter__(self) -> 'BLSClient':
        '''Context manager entry.'''
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> None:
        '''Context manager exit.'''
        self.close()

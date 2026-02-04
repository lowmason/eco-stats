'''
Refactored client for the Bureau of Labor Statistics (BLS).

Combines the existing BLS Public Data API access with:

* **Program registry** — structured metadata for every BLS survey.
* **Series ID builder/parser** — construct and decompose series IDs
  from named components instead of opaque strings.
* **Flat file access** — download complete LABSTAT datasets from
  ``download.bls.gov`` with no rate limits.

Backward compatible: the original ``get_series()``, convenience
methods, and context-manager protocol are preserved unchanged.
'''

import requests
from typing import Any, Dict, List, Optional

from eco_stats.api.bls.programs import (
    BLSProgram,
    get_program,
    list_programs,
)
from eco_stats.api.bls.series_id import build_series_id, parse_series_id
from eco_stats.api.bls.flat_files import BLSFlatFileClient


class BLSClient:
    '''
    Unified client for BLS data access.

    Provides three layers of access:

    1. **JSON API** — ``get_series()`` and convenience methods hit the
       BLS Public Data API (v1 without key, v2 with key).  Rate-limited
       but returns JSON directly.
    2. **Discovery** — ``list_programs()``, ``get_mapping()``,
       ``search_series()`` expose the LABSTAT metadata so users can
       explore what's available.
    3. **Flat files** — ``get_bulk_data()`` downloads complete
       tab-delimited datasets with no rate limits.

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

    # ------------------------------------------------------------------
    # JSON API access (existing interface, preserved)
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
    ) -> Dict[str, Any]:
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
            Dictionary containing the requested time series data.
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
        return response.json()

    # ------------------------------------------------------------------
    # Convenience methods (existing interface, preserved)
    # ------------------------------------------------------------------

    def get_unemployment_rate(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
    ) -> Dict[str, Any]:
        '''
        Get the U.S. unemployment rate (seasonally adjusted).

        Uses series ``LNS14000000`` from the Labor Force Statistics
        (LN) program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            Dictionary containing unemployment rate data.
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
    ) -> Dict[str, Any]:
        '''
        Get CPI for All Urban Consumers (CPI-U), All Items.

        Uses series ``CUUR0000SA0`` from the Consumer Price Index (CU)
        program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            Dictionary containing CPI data.
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
    ) -> Dict[str, Any]:
        '''
        Get total nonfarm employment (seasonally adjusted).

        Uses series ``CES0000000001`` from the Current Employment
        Statistics (CE) program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            Dictionary containing employment data.
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
    ) -> Dict[str, Any]:
        '''
        Get average hourly earnings of all employees (seasonally adjusted).

        Uses series ``CES0500000003`` from the Current Employment
        Statistics (CE) program.

        Args:
            start_year: Start year (format: ``'YYYY'``).
            end_year: End year (format: ``'YYYY'``).

        Returns:
            Dictionary containing earnings data.
        '''
        return self.get_series(
            series_ids=['CES0500000003'],
            start_year=start_year,
            end_year=end_year,
        )

    # ------------------------------------------------------------------
    # Discovery (new)
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
    ) -> List[Dict[str, str]]:
        '''
        Download a mapping/lookup table for a program.

        For example, ``get_mapping("CU", "area")`` returns a list of
        all CPI area codes and their names.

        Args:
            program: Two-letter program prefix.
            mapping_name: Mapping file name (e.g., ``"area"``,
                ``"industry"``, ``"item"``).

        Returns:
            List of dicts, one per row.
        '''
        return self._flat.get_mapping(program, mapping_name)

    def search_series(
        self,
        program: str,
        **filters: str,
    ) -> List[Dict[str, str]]:
        '''
        Search the master series list for a program.

        Filters are applied as exact matches on column values.

        Args:
            program: Two-letter program prefix.
            **filters: Column name → value pairs for filtering.

        Returns:
            List of matching series metadata dicts.

        Example::

            >>> client.search_series("CE", seasonal="S",
            ...                      data_type_code="01")
        '''
        return self._flat.get_series_list(program, **filters)

    # ------------------------------------------------------------------
    # Series ID helpers (new)
    # ------------------------------------------------------------------

    def parse_series_id(self, series_id: str) -> Dict[str, str]:
        '''
        Decompose a series ID into its named component fields.

        Args:
            series_id: Full BLS series ID string.

        Returns:
            Dictionary mapping field names to extracted values.

        Example::

            >>> client.parse_series_id("CUUR0000SA0")
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
            ...     "CU", seasonal="U", periodicity="R",
            ...     area="0000", item="SA0")
            'CUUR0000SA0'
        '''
        return build_series_id(program, **components)

    # ------------------------------------------------------------------
    # Flat file / bulk data access (new)
    # ------------------------------------------------------------------

    def get_bulk_data(
        self,
        program: str,
        file_suffix: str = '0.Current',
    ) -> List[Dict[str, str]]:
        '''
        Download a complete data file from BLS flat files.

        These files contain full historical data with no API rate
        limits.  Files are cached locally.

        Args:
            program: Two-letter program prefix (e.g., ``"CE"``).
            file_suffix: Portion after ``xx.data.`` in the filename.
                Common suffixes include ``"0.Current"`` and
                ``"0.AllCESSeries"`` (for CE).

        Returns:
            List of observation dicts with keys ``series_id``,
            ``year``, ``period``, ``value``, ``footnote_codes``.
        '''
        return self._flat.get_data(program, file_suffix)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        '''Close HTTP sessions.'''
        self.session.close()
        self._flat.close()

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

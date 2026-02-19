'''
QCEW (Quarterly Census of Employment and Wages) CSV data-slice client.

Uses the open-data CSV API at ``data.bls.gov/cew/data/api/`` rather
than the LABSTAT flat files at ``download.bls.gov``, which are
frequently blocked by Akamai.

Three slice types are available:

* **industry** — all areas for one industry code in a given quarter
* **area** — all industries for one area (FIPS) code in a given quarter
* **size** — all records for one establishment-size class (Q1 only)

API reference:
    https://www.bls.gov/cew/additional-resources/open-data/csv-data-slices.htm
'''

import os
import time
from io import StringIO
from typing import Any, List, Optional

import httpx
import polars as pl

_VALID_SLICE_TYPES = frozenset({'industry', 'area', 'size'})

# Columns that look numeric but are really codes — force Utf8.
_TEXT_COLUMNS = {
    'area_fips': pl.Utf8,
    'own_code': pl.Utf8,
    'industry_code': pl.Utf8,
    'agglvl_code': pl.Utf8,
    'size_code': pl.Utf8,
    'year': pl.Int32,
    'qtr': pl.Utf8,
    'disclosure_code': pl.Utf8,
    'lq_disclosure_code': pl.Utf8,
    'oty_disclosure_code': pl.Utf8,
}


class QCEWClient:
    '''
    Download and cache QCEW CSV data slices from ``data.bls.gov``.

    Args:
        cache_dir: Local directory for cached CSV files.
            Defaults to ``".cache/qcew"``.
        cache_ttl: Cache time-to-live in seconds.  Cached files
            older than this are re-downloaded.
            Defaults to 86 400 (24 hours).
    '''

    BASE_URL = 'https://data.bls.gov/cew/data/api'

    def __init__(
        self,
        cache_dir: str = '.cache/qcew',
        cache_ttl: int = 86_400,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.client = httpx.Client(
            timeout=60.0,
            follow_redirects=True,
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_slice(
        self,
        year: int,
        qtr: int,
        slice_type: str = 'industry',
        slice_code: str = '10',
    ) -> pl.DataFrame:
        '''
        Fetch a single QCEW CSV data slice.

        Args:
            year: Four-digit year.
            qtr: Quarter (1–4).
            slice_type: One of ``'industry'``, ``'area'``, ``'size'``.
            slice_code: Code for the slice.  Examples:
                ``'10'`` (all industries), ``'US000'`` (national area),
                ``'3'`` (size class 3).  Hyphenated NAICS codes use
                underscores (e.g., ``'31_33'`` for manufacturing).

        Returns:
            :class:`polars.DataFrame` with the QCEW quarterly CSV
            columns, or an empty DataFrame if the slice is not yet
            published (404).
        '''
        if slice_type not in _VALID_SLICE_TYPES:
            raise ValueError(
                f'Invalid slice_type {slice_type!r}. '
                f'Must be one of {sorted(_VALID_SLICE_TYPES)}'
            )
        url = f'{self.BASE_URL}/{year}/{qtr}/{slice_type}/{slice_code}.csv'
        cache_key = f'{slice_type}_{slice_code}_{year}_Q{qtr}'
        text = self._fetch(url, cache_key)
        if text is None:
            return pl.DataFrame()
        return pl.read_csv(
            StringIO(text),
            schema_overrides=_TEXT_COLUMNS,
            infer_schema_length=10_000,
        )

    def get_industry(
        self,
        industry_code: str = '10',
        start_year: int = 2016,
        end_year: int = 2026,
        quarters: Optional[List[int]] = None,
    ) -> pl.DataFrame:
        '''
        Fetch QCEW data sliced by industry across a year range.

        Args:
            industry_code: NAICS or supersector code.  Use ``'10'``
                for total, all industries.  Hyphenated codes use
                underscores (e.g., ``'31_33'``).
            start_year: First year to fetch (inclusive).
            end_year: Last year to fetch (inclusive).
            quarters: Quarters to include (default all four).

        Returns:
            :class:`polars.DataFrame` with all matching quarters
            concatenated vertically.
        '''
        return self._fetch_range('industry', industry_code, start_year, end_year, quarters)

    def get_area(
        self,
        area_code: str = 'US000',
        start_year: int = 2016,
        end_year: int = 2026,
        quarters: Optional[List[int]] = None,
    ) -> pl.DataFrame:
        '''
        Fetch QCEW data sliced by area across a year range.

        Args:
            area_code: FIPS-style area code.  ``'US000'`` for national
                totals; ``'26000'`` for Michigan, etc.
            start_year: First year to fetch (inclusive).
            end_year: Last year to fetch (inclusive).
            quarters: Quarters to include (default all four).

        Returns:
            :class:`polars.DataFrame` with all matching quarters
            concatenated vertically.
        '''
        return self._fetch_range('area', area_code, start_year, end_year, quarters)

    def get_size(
        self,
        size_code: str = '1',
        start_year: int = 2016,
        end_year: int = 2026,
    ) -> pl.DataFrame:
        '''
        Fetch QCEW data sliced by establishment-size class.

        Size data is only published for Q1 of each year and does not
        include size code 0 (all sizes).

        Args:
            size_code: Size class code (``'1'``–``'9'``).
            start_year: First year to fetch (inclusive).
            end_year: Last year to fetch (inclusive).

        Returns:
            :class:`polars.DataFrame` with all matching years
            concatenated vertically.
        '''
        return self._fetch_range('size', size_code, start_year, end_year, [1])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_range(
        self,
        slice_type: str,
        slice_code: str,
        start_year: int,
        end_year: int,
        quarters: Optional[List[int]] = None,
    ) -> pl.DataFrame:
        '''Fetch slices across a year/quarter range and concatenate.'''
        if quarters is None:
            quarters = [1, 2, 3, 4]

        parts: list[pl.DataFrame] = []
        for year in range(start_year, end_year + 1):
            for qtr in quarters:
                df = self.get_slice(year, qtr, slice_type, slice_code)
                if df.height > 0:
                    parts.append(df)

        if not parts:
            return pl.DataFrame()

        return pl.concat(parts, how='vertical_relaxed')

    def _fetch(self, url: str, cache_key: str) -> Optional[str]:
        '''Download a CSV (or load from cache).  Returns None on 404.'''
        cache_path = os.path.join(
            self.cache_dir,
            f'{cache_key}.csv'.replace('/', '_').replace('\\', '_'),
        )

        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as fh:
                return fh.read()

        response = self.client.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()

        text = response.text
        os.makedirs(self.cache_dir, exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as fh:
            fh.write(text)

        return text

    def _is_cache_valid(self, path: str) -> bool:
        '''Check whether a cached file exists and is within TTL.'''
        if not os.path.exists(path):
            return False
        age = time.time() - os.path.getmtime(path)
        return age < self.cache_ttl

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        '''Close the HTTP client.'''
        self.client.close()

    def __enter__(self) -> 'QCEWClient':
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> None:
        self.close()

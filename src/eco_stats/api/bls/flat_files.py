'''
BLS LABSTAT flat file downloader and parser.

The Bureau of Labor Statistics publishes complete datasets as
tab-delimited text files at ``https://download.bls.gov/pub/time.series/``.
Each program (two-letter prefix) has its own subdirectory containing:

* ``xx.series``  — master list of every series with metadata
* ``xx.data.*``  — observation data (series_id, year, period, value)
* ``xx.area``, ``xx.industry``, ``xx.item``, etc. — mapping/lookup files

This module provides utilities for downloading, caching, and parsing
those files.
'''

import csv
import io
import os
import time
from typing import Any, Dict, List

import requests

from eco_stats.api.bls.programs import get_program

# BLS blocks default Python user agents.  Use a descriptive UA that
# identifies us as a legitimate library rather than a scraper.
_USER_AGENT = (
    'eco-stats/0.1.0 '
    '(Python; +https://github.com/lowmason/eco-stats) '
    'requests/{req_version}'
).format(req_version=requests.__version__)


class BLSFlatFileClient:
    '''
    Download and parse BLS LABSTAT flat files.

    Downloaded files are cached locally so that repeated access does
    not re-download from BLS.

    Args:
        cache_dir: Local directory for cached flat files.
            Defaults to ``".cache/bls"``.
        cache_ttl: Cache time-to-live in seconds.  Cached files
            older than this are re-downloaded.
            Defaults to 86 400 (24 hours).
    '''

    BASE_URL = 'https://download.bls.gov/pub/time.series'

    def __init__(
        self,
        cache_dir: str = '.cache/bls',
        cache_ttl: int = 86_400,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.session = requests.Session()
        self.session.headers['User-Agent'] = _USER_AGENT

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_mapping(
        self,
        prefix: str,
        mapping_name: str,
    ) -> List[Dict[str, str]]:
        '''
        Download and parse a mapping/lookup file.

        For example, ``get_mapping("CU", "area")`` downloads and parses
        ``download.bls.gov/pub/time.series/cu/cu.area``.

        Args:
            prefix: Two-letter program code (e.g., ``"CU"``).
            mapping_name: Mapping file name without the prefix dot
                (e.g., ``"area"``, ``"industry"``, ``"item"``).

        Returns:
            List of dicts, one per row, keyed by column header.
        '''
        get_program(prefix)  # validate prefix exists
        filename = f'{prefix.lower()}.{mapping_name}'
        url = f'{self.BASE_URL}/{prefix.lower()}/{filename}'
        return self._download_and_parse(url, filename)

    def get_series_list(
        self,
        prefix: str,
        **filters: str,
    ) -> List[Dict[str, str]]:
        '''
        Download and parse the master series file, optionally filtering.

        Args:
            prefix: Two-letter program code.
            **filters: Column name → value pairs used to filter rows.
                Only rows where *all* filters match are returned.

        Returns:
            List of dicts, one per matching series.
        '''
        rows = self.get_mapping(prefix, 'series')
        if not filters:
            return rows
        return [
            row
            for row in rows
            if all(row.get(k, '').strip() == v for k, v in filters.items())
        ]

    def get_data(
        self,
        prefix: str,
        file_suffix: str = '0.Current',
    ) -> List[Dict[str, str]]:
        '''
        Download and parse a data file.

        BLS data files are named like ``ce.data.0.AllCESSeries`` or
        ``cu.data.0.Current``.

        Args:
            prefix: Two-letter program code.
            file_suffix: The portion of the filename after ``xx.data.``
                (e.g., ``"0.Current"``, ``"0.AllCESSeries"``).

        Returns:
            List of dicts with keys like ``series_id``, ``year``,
            ``period``, ``value``, ``footnote_codes``.
        '''
        filename = f'{prefix.lower()}.data.{file_suffix}'
        url = f'{self.BASE_URL}/{prefix.lower()}/{filename}'
        return self._download_and_parse(url, filename)

    # ------------------------------------------------------------------
    # Caching helpers
    # ------------------------------------------------------------------

    def _cache_path(self, filename: str) -> str:
        '''Return the local cache file path for a given filename.'''
        safe_name = filename.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, safe_name)

    def _is_cache_valid(self, path: str) -> bool:
        '''Check whether a cached file exists and is within TTL.'''
        if not os.path.exists(path):
            return False
        age = time.time() - os.path.getmtime(path)
        return age < self.cache_ttl

    # ------------------------------------------------------------------
    # Download and parse
    # ------------------------------------------------------------------

    def _download_and_parse(
        self,
        url: str,
        filename: str,
    ) -> List[Dict[str, str]]:
        '''
        Download a file (or load from cache), then parse as
        tab-delimited text.

        Returns:
            List of dicts keyed by the header row.
        '''
        cache_path = self._cache_path(filename)

        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
        else:
            text = self._download(url)
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as fh:
                fh.write(text)

        return self._parse_tsv(text)

    def _download(self, url: str) -> str:
        '''
        Download a URL and return its text content.

        Raises:
            requests.HTTPError: On non-2xx responses.
        '''
        response = self.session.get(url, timeout=60)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _parse_tsv(text: str) -> List[Dict[str, str]]:
        '''
        Parse tab-separated text with a header row into a list of dicts.

        BLS flat files use tab delimiters and often have trailing
        whitespace in fields, which we strip.
        '''
        reader = csv.DictReader(io.StringIO(text), delimiter='\t')
        rows: List[Dict[str, str]] = []
        for row in reader:
            cleaned = {
                k.strip(): v.strip() if v else ''
                for k, v in row.items()
                if k is not None
            }
            rows.append(cleaned)
        return rows

    def close(self) -> None:
        '''Close the HTTP session.'''
        self.session.close()

    def __enter__(self) -> 'BLSFlatFileClient':
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> None:
        self.close()

'''
BLS (Bureau of Labor Statistics) client package.

This package provides structured access to BLS data through the
JSON API and the LABSTAT flat file archive.
'''

from eco_stats.api.bls.client import BLSClient
from eco_stats.api.bls.programs import (
    BLSProgram,
    SeriesField,
    PROGRAMS,
    get_program,
    list_programs,
)
from eco_stats.api.bls.series_id import build_series_id, parse_series_id
from eco_stats.api.bls.flat_files import BLSFlatFileClient

__all__ = [
    'BLSClient',
    'BLSFlatFileClient',
    'BLSProgram',
    'SeriesField',
    'PROGRAMS',
    'build_series_id',
    'get_program',
    'list_programs',
    'parse_series_id',
]

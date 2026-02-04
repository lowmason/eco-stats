"""
eco-stats: A Python library for pulling statistical series from BEA, BLS, Census, and FRED APIs.
"""

__version__ = "0.1.0"

from eco_stats.api.bea_client import BEAClient
from eco_stats.api.bls_client import BLSClient
from eco_stats.api.census_client import CensusClient
from eco_stats.api.fred_client import FREDClient
from eco_stats.__main__ import EcoStats

__all__ = [
    "BEAClient",
    "BLSClient",
    "CensusClient",
    "FREDClient",
    "EcoStats",
]

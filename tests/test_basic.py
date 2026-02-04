'''
Basic tests for eco-stats package structure.
'''

import pytest


def test_package_imports():
    '''Test that all main modules can be imported.'''
    from eco_stats import BEAClient, BLSClient, CensusClient, FREDClient

    assert BEAClient is not None
    assert BLSClient is not None
    assert CensusClient is not None
    assert FREDClient is not None


def test_eco_stats_main_import():
    '''Test that the main EcoStats class can be imported.'''
    from eco_stats import EcoStats

    assert EcoStats is not None


def test_utility_imports():
    '''Test that utility functions can be imported.'''
    from eco_stats.utils import (
        validate_date,
        format_date,
        parse_response,
        convert_to_dataframe,
    )

    assert validate_date is not None
    assert format_date is not None
    assert parse_response is not None
    assert convert_to_dataframe is not None


def test_date_validation():
    '''Test the date validation utility.'''
    from eco_stats.utils import validate_date

    assert validate_date('2024-01-01') is True
    assert validate_date('2024-13-01') is False
    assert validate_date('invalid') is False


def test_percent_change_calculation():
    '''Test percent change calculation.'''
    from eco_stats.utils import calculate_percent_change

    values = [100, 105, 110]
    pct_change = calculate_percent_change(values)

    assert pct_change[0] is None  # First value has no previous value
    assert pct_change[1] == 5.0  # (105-100)/100 * 100 = 5%
    assert abs(pct_change[2] - 4.761904761904762) < 0.0001  # (110-105)/105 * 100


def test_moving_average_calculation():
    '''Test moving average calculation.'''
    from eco_stats.utils import calculate_moving_average

    values = [100, 102, 104, 106, 108]
    moving_avg = calculate_moving_average(values, window=3)

    assert moving_avg[0] is None
    assert moving_avg[1] is None
    assert moving_avg[2] == 102.0  # (100+102+104)/3
    assert moving_avg[3] == 104.0  # (102+104+106)/3


def test_bls_client_initialization():
    '''Test BLS client can be initialized.'''
    from eco_stats import BLSClient

    # Should work without API key
    client = BLSClient()
    assert client is not None

    # Should work with API key
    client_with_key = BLSClient(api_key='test_key')
    assert client_with_key is not None
    assert client_with_key.api_key == 'test_key'


def test_bea_client_initialization():
    '''Test BEA client requires API key.'''
    from eco_stats import BEAClient

    client = BEAClient(api_key='test_key')
    assert client is not None
    assert client.api_key == 'test_key'


def test_census_client_initialization():
    '''Test Census client requires API key.'''
    from eco_stats import CensusClient

    client = CensusClient(api_key='test_key')
    assert client is not None
    assert client.api_key == 'test_key'


def test_fred_client_initialization():
    '''Test FRED client requires API key.'''
    from eco_stats import FREDClient

    client = FREDClient(api_key='test_key')
    assert client is not None
    assert client.api_key == 'test_key'


def test_eco_stats_initialization():
    '''Test EcoStats unified interface initialization.'''
    from eco_stats import EcoStats

    eco = EcoStats(
        bea_api_key='bea_key',
        bls_api_key='bls_key',
        census_api_key='census_key',
        fred_api_key='fred_key',
    )

    assert eco is not None
    assert eco.bea is not None
    assert eco.bls is not None
    assert eco.census is not None
    assert eco.fred is not None


def test_eco_stats_missing_keys():
    '''Test EcoStats handles missing API keys.'''
    from eco_stats import EcoStats

    eco = EcoStats()

    # BLS should work without key
    assert eco.bls is not None

    # Others should raise errors
    with pytest.raises(ValueError):
        _ = eco.bea

    with pytest.raises(ValueError):
        _ = eco.census

    with pytest.raises(ValueError):
        _ = eco.fred

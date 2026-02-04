"""
Utility functions for eco-stats.

This module provides helper functions for date validation, data formatting,
response parsing, and other common operations.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import hashlib
import os


def validate_date(date_string: str, date_format: str = '%Y-%m-%d') -> bool:
    """
    Validate if a string is a valid date.
    
    Args:
        date_string: Date string to validate
        date_format: Expected date format (default: '%Y-%m-%d')
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_string, date_format)
        return True
    except (ValueError, TypeError):
        return False


def format_date(
    date_obj: datetime,
    date_format: str = '%Y-%m-%d'
) -> str:
    """
    Format a datetime object to a string.
    
    Args:
        date_obj: Datetime object to format
        date_format: Output date format (default: '%Y-%m-%d')
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime(date_format)


def parse_response(response_data: Dict[str, Any], data_key: Optional[str] = None) -> Any:
    """
    Parse API response and extract data.
    
    Args:
        response_data: Raw API response dictionary
        data_key: Optional key to extract specific data from response
        
    Returns:
        Parsed data from response
    """
    if data_key and data_key in response_data:
        return response_data[data_key]
    return response_data


def convert_to_dataframe(data: List[Dict[str, Any]]) -> Any:
    """
    Convert list of dictionaries to a pandas DataFrame.
    
    Args:
        data: List of dictionaries containing data
        
    Returns:
        Pandas DataFrame if pandas is installed, otherwise returns original data
    """
    try:
        import pandas as pd
        return pd.DataFrame(data)
    except ImportError:
        # If pandas is not installed, return the raw data
        return data


def extract_series_data(
    response: Dict[str, Any],
    api_type: str = 'fred'
) -> List[Dict[str, Any]]:
    """
    Extract time series data from API responses.
    
    Args:
        response: API response dictionary
        api_type: Type of API ('fred', 'bls', 'bea', 'census')
        
    Returns:
        List of dictionaries with standardized format
    """
    data = []
    
    if api_type == 'fred':
        if 'observations' in response:
            for obs in response['observations']:
                data.append({
                    'date': obs.get('date'),
                    'value': obs.get('value'),
                    'realtime_start': obs.get('realtime_start'),
                    'realtime_end': obs.get('realtime_end')
                })
    
    elif api_type == 'bls':
        if 'Results' in response and 'series' in response['Results']:
            for series in response['Results']['series']:
                series_id = series.get('seriesID')
                for obs in series.get('data', []):
                    data.append({
                        'series_id': series_id,
                        'year': obs.get('year'),
                        'period': obs.get('period'),
                        'value': obs.get('value'),
                        'period_name': obs.get('periodName')
                    })
    
    elif api_type == 'bea':
        if 'BEAAPI' in response and 'Results' in response['BEAAPI']:
            results = response['BEAAPI']['Results']
            if 'Data' in results:
                for item in results['Data']:
                    data.append(item)
    
    elif api_type == 'census':
        # Census data is typically returned as a list of lists
        if isinstance(response, list) and len(response) > 0:
            headers = response[0]
            for row in response[1:]:
                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                data.append(row_dict)
    
    return data


def cache_response(
    response_data: Dict[str, Any],
    cache_dir: str = '.cache',
    cache_key: Optional[str] = None
) -> str:
    """
    Cache API response to disk.
    
    Args:
        response_data: Response data to cache
        cache_dir: Directory to store cache files
        cache_key: Optional key for the cache file (auto-generated if None)
        
    Returns:
        Path to the cached file
    """
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Generate cache key if not provided
    if cache_key is None:
        data_str = json.dumps(response_data, sort_keys=True)
        cache_key = hashlib.md5(data_str.encode()).hexdigest()
    
    # Save to cache
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    with open(cache_path, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    return cache_path


def load_cached_response(
    cache_key: str,
    cache_dir: str = '.cache'
) -> Optional[Dict[str, Any]]:
    """
    Load cached API response from disk.
    
    Args:
        cache_key: Key for the cache file
        cache_dir: Directory where cache files are stored
        
    Returns:
        Cached response data if found, None otherwise
    """
    cache_path = os.path.join(cache_dir, f"{cache_key}.json")
    
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    
    return None


def calculate_percent_change(
    values: List[float],
    periods: int = 1
) -> List[Optional[float]]:
    """
    Calculate percent change for a series of values.
    
    Args:
        values: List of numeric values
        periods: Number of periods to look back for comparison (default: 1)
        
    Returns:
        List of percent changes (None for first 'periods' values)
    """
    result = [None] * periods
    
    for i in range(periods, len(values)):
        if values[i - periods] != 0 and values[i - periods] is not None:
            pct_change = ((values[i] - values[i - periods]) / values[i - periods]) * 100
            result.append(pct_change)
        else:
            result.append(None)
    
    return result


def calculate_moving_average(
    values: List[float],
    window: int = 3
) -> List[Optional[float]]:
    """
    Calculate moving average for a series of values.
    
    Args:
        values: List of numeric values
        window: Window size for moving average
        
    Returns:
        List of moving averages (None for first 'window-1' values)
    """
    result = [None] * (window - 1)
    
    for i in range(window - 1, len(values)):
        window_values = values[i - window + 1:i + 1]
        if all(v is not None for v in window_values):
            avg = sum(window_values) / window
            result.append(avg)
        else:
            result.append(None)
    
    return result


def filter_by_date_range(
    data: List[Dict[str, Any]],
    start_date: str,
    end_date: str,
    date_field: str = 'date'
) -> List[Dict[str, Any]]:
    """
    Filter data by date range.
    
    Args:
        data: List of dictionaries containing date field
        start_date: Start date (format: 'YYYY-MM-DD')
        end_date: End date (format: 'YYYY-MM-DD')
        date_field: Name of the date field in dictionaries
        
    Returns:
        Filtered list of dictionaries
    """
    filtered = []
    
    for item in data:
        if date_field in item:
            item_date = item[date_field]
            if start_date <= item_date <= end_date:
                filtered.append(item)
    
    return filtered

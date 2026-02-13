'''
Example: Using utility functions.

This example demonstrates how to use the utility functions provided
by eco-stats for data processing and manipulation.
'''

import os
from datetime import datetime
from dotenv import load_dotenv
from eco_stats import FREDClient

# Load environment variables from .env file
load_dotenv()
from eco_stats.utils import (
    validate_date,
    format_date,
    extract_series_data,
    convert_to_dataframe,
    calculate_percent_change,
    calculate_moving_average,
    cache_response,
    load_cached_response
)


def main():
    print('=' * 60)
    print('Utility Functions Example')
    print('=' * 60)
    
    # Example 1: Date validation and formatting
    print('\n1. Date validation and formatting...')
    test_date = '2024-01-01'
    is_valid = validate_date(test_date)
    print(f"   Is '{test_date}' a valid date? {is_valid}")
    
    now = datetime.now()
    formatted = format_date(now, '%Y-%m-%d')
    print(f'   Current date formatted: {formatted}')
    
    # Example 2: Extract series data
    print('\n2. Extracting series data from API response...')
    api_key = os.getenv('FRED_API_KEY')
    
    if api_key:
        with FREDClient(api_key=api_key) as fred:
            try:
                gdp_response = fred.get_gdp(
                    observation_start='2023-01-01',
                    observation_end='2024-01-01'
                )
                
                # Extract series data
                data = extract_series_data(gdp_response, api_type='fred')
                print(f'   Extracted {len(data)} observations')
                if len(data) > 0:
                    print(f'   First observation: {data[0]}')
                
                # Example 3: Convert to DataFrame (if polars available)
                print('\n3. Converting to DataFrame...')
                try:
                    df = convert_to_dataframe(data)
                    print(f'   DataFrame shape: {df.shape}')
                    print(f'   DataFrame columns: {list(df.columns)}')
                except ImportError:
                    print('   Polars not installed, returning raw data')
                
                # Example 4: Cache response
                print('\n4. Caching API response...')
                cache_path = cache_response(gdp_response, cache_key='gdp_example')
                print(f'   Cached to: {cache_path}')
                
                # Example 5: Load cached response
                print('\n5. Loading cached response...')
                cached_data = load_cached_response('gdp_example')
                if cached_data:
                    print(f'   Successfully loaded cached data')
                    print(f'   Keys in cached data: {list(cached_data.keys())}')
                
            except Exception as e:
                print(f'   Error: {e}')
    else:
        print('   FRED_API_KEY not set, skipping API examples')
    
    # Example 6: Calculate percent change
    print('\n6. Calculating percent change...')
    values = [100, 105, 110, 108, 112, 115]
    pct_change = calculate_percent_change(values, periods=1)
    print(f'   Original values: {values}')
    print(f'   Percent change: {pct_change}')
    
    # Example 7: Calculate moving average
    print('\n7. Calculating moving average...')
    values = [100, 102, 105, 103, 107, 110, 108, 112]
    moving_avg = calculate_moving_average(values, window=3)
    print(f'   Original values: {values}')
    print(f'   3-period moving average: {moving_avg}')
    
    # Example 8: Year-over-year percent change
    print('\n8. Calculating year-over-year percent change...')
    quarterly_values = [100, 102, 105, 107, 108, 110, 113, 115]  # 2 years of quarterly data
    yoy_change = calculate_percent_change(quarterly_values, periods=4)
    print(f'   Quarterly values: {quarterly_values}')
    print(f'   Year-over-year change: {yoy_change}')
    
    print('\n' + '=' * 60)
    print('Utility functions example completed successfully!')
    print('=' * 60)


if __name__ == '__main__':
    main()

'''
Example: Using the FRED API client.

This example demonstrates how to fetch economic time series data
from the Federal Reserve Economic Data (FRED) system.
'''

import os
from dotenv import load_dotenv
from eco_stats import FREDClient

# Load environment variables from .env file
load_dotenv()


def main():
    # Get API key from environment
    api_key = os.getenv('FRED_API_KEY')
    
    if not api_key:
        print('Error: FRED_API_KEY environment variable not set.')
        print('Register for a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html')
        return
    
    # Create FRED client
    with FREDClient(api_key=api_key) as fred:
        print('=' * 60)
        print('FRED API Example')
        print('=' * 60)
        
        # Example 1: Get GDP data
        print('\n1. Getting GDP data...')
        try:
            gdp = fred.get_gdp(
                observation_start='2020-01-01',
                observation_end='2024-01-01'
            )
            print(f'   Status: Success')
            if 'observations' in gdp:
                obs_count = len(gdp['observations'])
                print(f'   Observations returned: {obs_count}')
                if obs_count > 0:
                    latest = gdp['observations'][-1]
                    print(f"   Latest: {latest['date']} = {latest['value']}")
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 2: Get unemployment rate
        print('\n2. Getting unemployment rate...')
        try:
            unemployment = fred.get_unemployment_rate(
                observation_start='2020-01-01',
                observation_end='2024-01-01'
            )
            print(f'   Status: Success')
            if 'observations' in unemployment:
                obs_count = len(unemployment['observations'])
                print(f'   Observations returned: {obs_count}')
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 3: Get federal funds rate
        print('\n3. Getting Federal Funds Rate...')
        try:
            fed_funds = fred.get_federal_funds_rate(
                observation_start='2020-01-01',
                observation_end='2024-01-01'
            )
            print(f'   Status: Success')
            if 'observations' in fed_funds:
                obs_count = len(fed_funds['observations'])
                print(f'   Observations returned: {obs_count}')
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 4: Get inflation rate
        print('\n4. Getting inflation rate (CPI year-over-year % change)...')
        try:
            inflation = fred.get_inflation_rate(
                observation_start='2020-01-01',
                observation_end='2024-01-01'
            )
            print(f'   Status: Success')
            if 'observations' in inflation:
                obs_count = len(inflation['observations'])
                print(f'   Observations returned: {obs_count}')
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 5: Search for series
        print("\n5. Searching for 'housing' related series...")
        try:
            search_results = fred.search_series(
                search_text='housing',
                limit=5
            )
            print(f'   Status: Success')
            if 'seriess' in search_results:
                series_count = len(search_results['seriess'])
                print(f'   Series found: {series_count}')
                if series_count > 0:
                    print(f"   First result: {search_results['seriess'][0]['title']}")
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 6: Get series info
        print('\n6. Getting series information for GDP...')
        try:
            series_info = fred.get_series('GDP')
            print(f'   Status: Success')
            if 'seriess' in series_info and len(series_info['seriess']) > 0:
                info = series_info['seriess'][0]
                print(f"   Title: {info.get('title')}")
                print(f"   Frequency: {info.get('frequency')}")
                print(f"   Units: {info.get('units')}")
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 7: Get custom series
        print('\n7. Getting 10-Year Treasury Rate...')
        try:
            treasury = fred.get_series_observations(
                series_id='DGS10',
                observation_start='2023-01-01',
                observation_end='2024-01-01'
            )
            print(f'   Status: Success')
            if 'observations' in treasury:
                obs_count = len(treasury['observations'])
                print(f'   Observations returned: {obs_count}')
        except Exception as e:
            print(f'   Error: {e}')
        
        print('\n' + '=' * 60)
        print('FRED API example completed successfully!')
        print('=' * 60)


if __name__ == '__main__':
    main()

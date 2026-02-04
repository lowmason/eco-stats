"""
Example: Using the BLS API client.

This example demonstrates how to fetch employment, unemployment, and
price data from the Bureau of Labor Statistics.
"""

import os
from eco_stats import BLSClient


def main():
    # Get API key from environment (optional for BLS, but recommended)
    api_key = os.getenv('BLS_API_KEY')
    
    if not api_key:
        print("Note: BLS_API_KEY not set. Using public API with limited access.")
        print("Register for a free API key at: https://data.bls.gov/registrationEngine/")
    
    # Create BLS client
    with BLSClient(api_key=api_key) as bls:
        print("=" * 60)
        print("BLS API Example")
        print("=" * 60)
        
        # Example 1: Get unemployment rate
        print("\n1. Getting unemployment rate...")
        try:
            unemployment = bls.get_unemployment_rate(
                start_year='2022',
                end_year='2024'
            )
            print(f"   Status: Success")
            if 'status' in unemployment:
                print(f"   API Status: {unemployment['status']}")
            if 'Results' in unemployment and 'series' in unemployment['Results']:
                series_count = len(unemployment['Results']['series'])
                print(f"   Series returned: {series_count}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Example 2: Get CPI data
        print("\n2. Getting Consumer Price Index (CPI) data...")
        try:
            cpi = bls.get_cpi_all_items(
                start_year='2022',
                end_year='2024'
            )
            print(f"   Status: Success")
            if 'status' in cpi:
                print(f"   API Status: {cpi['status']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Example 3: Get employment data
        print("\n3. Getting total nonfarm employment...")
        try:
            employment = bls.get_employment(
                start_year='2022',
                end_year='2024'
            )
            print(f"   Status: Success")
            if 'status' in employment:
                print(f"   API Status: {employment['status']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Example 4: Get multiple series
        print("\n4. Getting multiple series (unemployment + employment)...")
        try:
            multi_series = bls.get_series(
                series_ids=['LNS14000000', 'CES0000000001'],
                start_year='2023',
                end_year='2024'
            )
            print(f"   Status: Success")
            if 'status' in multi_series:
                print(f"   API Status: {multi_series['status']}")
            if 'Results' in multi_series and 'series' in multi_series['Results']:
                series_count = len(multi_series['Results']['series'])
                print(f"   Series returned: {series_count}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "=" * 60)
        print("BLS API example completed successfully!")
        print("=" * 60)


if __name__ == '__main__':
    main()

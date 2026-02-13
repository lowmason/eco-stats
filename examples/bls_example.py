'''
Example: Using the BLS API client.

This example demonstrates how to fetch employment, unemployment, and
price data from the Bureau of Labor Statistics as Polars DataFrames.
'''

import os

import polars as pl
from dotenv import load_dotenv

from eco_stats import BLSClient

# Load environment variables from .env file
load_dotenv()


def main():
    # Get API key from environment (optional for BLS, but recommended)
    api_key = os.getenv('BLS_API_KEY')

    if not api_key:
        print('Note: BLS_API_KEY not set. Using public API with limited access.')
        print(
            'Register for a free API key at: https://data.bls.gov/registrationEngine/'
        )

    # Create BLS client
    with BLSClient(api_key=api_key) as bls:
        print('=' * 60)
        print('BLS API Example')
        print('=' * 60)

        # Example 1: Get unemployment rate
        print('\n1. Unemployment rate (2020–2025)')
        unemployment = bls.get_unemployment_rate(
            start_year='2020',
            end_year='2025',
        )
        print(unemployment)

        # Example 2: Get CPI data
        print('\n2. CPI-U All Items (2020–2025)')
        cpi = bls.get_cpi_all_items(
            start_year='2020',
            end_year='2025',
        )
        print(cpi)

        # Example 3: Get total nonfarm employment
        print('\n3. Total nonfarm employment (2023–2025)')
        employment = bls.get_employment(
            start_year='2023',
            end_year='2025',
        )
        print(employment)

        # Example 4: Fetch multiple series at once
        print('\n4. Multiple series in one call')
        multi = bls.get_series(
            series_ids=['LNS14000000', 'CES0000000001'],
            start_year='2024',
            end_year='2025',
        )
        print(multi)

        # Example 5: DataFrame operations — filter and compute
        print('\n5. Year-over-year CPI change (Polars expressions)')
        yoy = (
            cpi.sort('date')
            .with_columns(pl.col('value').pct_change(12).mul(100).alias('yoy_pct'))
            .drop_nulls('yoy_pct')
        )
        print(yoy.select('date', 'value', 'yoy_pct'))


if __name__ == '__main__':
    main()

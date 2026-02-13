'''
Example: Using the unified EcoStats interface.

This example demonstrates how to use the unified interface to access
all API clients through a single EcoStats object.
'''

import os
from dotenv import load_dotenv
from eco_stats import EcoStats

# Load environment variables from .env file
load_dotenv()


def main():
    # Get API keys from environment
    bea_key = os.getenv('BEA_API_KEY')
    bls_key = os.getenv('BLS_API_KEY')
    census_key = os.getenv('CENSUS_API_KEY')
    fred_key = os.getenv('FRED_API_KEY')
    
    print('=' * 60)
    print('Unified EcoStats Interface Example')
    print('=' * 60)
    
    # Create unified EcoStats instance
    with EcoStats(
        bea_api_key=bea_key,
        bls_api_key=bls_key,
        census_api_key=census_key,
        fred_api_key=fred_key
    ) as eco:
        
        print('\nAvailable clients:')
        print(f"  - BEA: {'✓' if bea_key else '✗'}")
        print(f"  - BLS: {'✓' if bls_key else '✗ (using public API)'}")
        print(f"  - Census: {'✓' if census_key else '✗'}")
        print(f"  - FRED: {'✓' if fred_key else '✗'}")
        
        # FRED examples
        if fred_key:
            print('\n' + '-' * 60)
            print('FRED API (Federal Reserve Economic Data)')
            print('-' * 60)
            
            try:
                print('\n1. Getting GDP...')
                gdp = eco.fred.get_gdp(observation_start='2023-01-01')
                if 'observations' in gdp:
                    print(f"   ✓ Retrieved {len(gdp['observations'])} observations")
            except Exception as e:
                print(f'   ✗ Error: {e}')
            
            try:
                print('\n2. Getting unemployment rate...')
                unemployment = eco.fred.get_unemployment_rate(observation_start='2023-01-01')
                if 'observations' in unemployment:
                    print(f"   ✓ Retrieved {len(unemployment['observations'])} observations")
            except Exception as e:
                print(f'   ✗ Error: {e}')
        
        # BLS examples
        print('\n' + '-' * 60)
        print('BLS API (Bureau of Labor Statistics)')
        print('-' * 60)
        
        try:
            print('\n1. Getting unemployment rate...')
            unemployment = eco.bls.get_unemployment_rate(start_year='2023', end_year='2024')
            if 'status' in unemployment:
                print(f"   ✓ API Status: {unemployment['status']}")
        except Exception as e:
            print(f'   ✗ Error: {e}')
        
        try:
            print('\n2. Getting CPI data...')
            cpi = eco.bls.get_cpi_all_items(start_year='2023', end_year='2024')
            if 'status' in cpi:
                print(f"   ✓ API Status: {cpi['status']}")
        except Exception as e:
            print(f'   ✗ Error: {e}')
        
        # BEA examples
        if bea_key:
            print('\n' + '-' * 60)
            print('BEA API (Bureau of Economic Analysis)')
            print('-' * 60)
            
            try:
                print('\n1. Getting GDP data...')
                gdp = eco.bea.get_nipa_data(table_name='T10101', frequency='Q', year='2023')
                if 'BEAAPI' in gdp:
                    print(f'   ✓ Retrieved BEA data')
            except Exception as e:
                print(f'   ✗ Error: {e}')
        
        # Census examples
        if census_key:
            print('\n' + '-' * 60)
            print('Census Bureau API')
            print('-' * 60)
            
            try:
                print('\n1. Getting population by state...')
                population = eco.census.get_population(geo_level='state:*', year='2021')
                print(f'   ✓ Retrieved data for {len(population) - 1} states')
            except Exception as e:
                print(f'   ✗ Error: {e}')
        
        print('\n' + '=' * 60)
        print('Unified interface example completed!')
        print('=' * 60)
        
        # Note: Context manager will automatically close all clients


if __name__ == '__main__':
    main()

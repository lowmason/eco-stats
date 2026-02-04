'''
Example: Using the BEA API client.

This example demonstrates how to fetch GDP and regional economic data
from the Bureau of Economic Analysis.
'''

import os
from eco_stats import BEAClient


def main():
    # Get API key from environment
    api_key = os.getenv('BEA_API_KEY')
    
    if not api_key:
        print('Error: BEA_API_KEY environment variable not set.')
        print('Register for a free API key at: https://apps.bea.gov/api/signup/')
        return
    
    # Create BEA client
    with BEAClient(api_key=api_key) as bea:
        print('=' * 60)
        print('BEA API Example')
        print('=' * 60)
        
        # Example 1: Get NIPA data (GDP)
        print('\n1. Getting GDP data (NIPA Table T10101)...')
        try:
            gdp_data = bea.get_nipa_data(
                table_name='T10101',
                frequency='Q',  # Quarterly
                year='2023'
            )
            print(f'   Status: Success')
            if 'BEAAPI' in gdp_data:
                print(f"   Response keys: {list(gdp_data['BEAAPI'].keys())}")
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 2: Get parameter list for NIPA dataset
        print('\n2. Getting parameter list for NIPA dataset...')
        try:
            params = bea.get_parameter_list('NIPA')
            print(f'   Status: Success')
            if 'BEAAPI' in params:
                print(f"   Response keys: {list(params['BEAAPI'].keys())}")
        except Exception as e:
            print(f'   Error: {e}')
        
        # Example 3: Get regional data
        print('\n3. Getting regional personal income data...')
        try:
            regional_data = bea.get_regional_data(
                table_name='CAINC1',
                line_code='1',
                geo_fips='STATE',
                year='LAST5'
            )
            print(f'   Status: Success')
            if 'BEAAPI' in regional_data:
                print(f"   Response keys: {list(regional_data['BEAAPI'].keys())}")
        except Exception as e:
            print(f'   Error: {e}')
        
        print('\n' + '=' * 60)
        print('BEA API example completed successfully!')
        print('=' * 60)


if __name__ == '__main__':
    main()

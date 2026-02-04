"""
Example: Using the Census Bureau API client.

This example demonstrates how to fetch demographic and economic data
from the U.S. Census Bureau.
"""

import os
from eco_stats import CensusClient


def main():
    # Get API key from environment
    api_key = os.getenv('CENSUS_API_KEY')
    
    if not api_key:
        print("Error: CENSUS_API_KEY environment variable not set.")
        print("Register for a free API key at: https://api.census.gov/data/key_signup.html")
        return
    
    # Create Census client
    with CensusClient(api_key=api_key) as census:
        print("=" * 60)
        print("Census Bureau API Example")
        print("=" * 60)
        
        # Example 1: Get population by state
        print("\n1. Getting population by state (2021)...")
        try:
            population = census.get_population(
                geo_level='state:*',
                year='2021'
            )
            print(f"   Status: Success")
            print(f"   Records returned: {len(population) - 1}")  # -1 for header
            if len(population) > 1:
                print(f"   Sample (first state): {population[1]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Example 2: Get median income by state
        print("\n2. Getting median household income by state (2021)...")
        try:
            income = census.get_median_income(
                geo_level='state:*',
                year='2021'
            )
            print(f"   Status: Success")
            print(f"   Records returned: {len(income) - 1}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Example 3: Get ACS data for specific state (California)
        print("\n3. Getting ACS data for California counties...")
        try:
            ca_data = census.get_acs_data(
                variables=['NAME', 'B01001_001E', 'B19013_001E'],
                geo_level='county:*',
                geo_filter={'state': '06'},  # California FIPS code
                year='2021'
            )
            print(f"   Status: Success")
            print(f"   Records returned: {len(ca_data) - 1}")
            if len(ca_data) > 1:
                print(f"   Headers: {ca_data[0]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Example 4: Get custom data
        print("\n4. Getting custom ACS data for all states...")
        try:
            custom_data = census.get_data(
                dataset='acs/acs5',
                variables=['NAME', 'B01001_001E', 'B01002_001E'],  # Pop + Median Age
                geo_level='state:*',
                year='2021'
            )
            print(f"   Status: Success")
            print(f"   Records returned: {len(custom_data) - 1}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "=" * 60)
        print("Census Bureau API example completed successfully!")
        print("=" * 60)


if __name__ == '__main__':
    main()

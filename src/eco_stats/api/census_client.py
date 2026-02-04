'''
Client for interacting with the U.S. Census Bureau API.

The Census API provides access to demographic, economic, and geographic data.
More info: https://www.census.gov/data/developers.html
'''

import requests
from typing import Dict, List, Optional, Any


class CensusClient:
    '''
    Client for accessing U.S. Census Bureau data.

    The Census API provides access to demographic data, economic data,
    American Community Survey (ACS), and many other datasets.
    '''

    BASE_URL = 'https://api.census.gov/data'

    def __init__(self, api_key: str):
        '''
        Initialize the Census client.

        Args:
            api_key: Your Census API key. Register at https://api.census.gov/data/key_signup.html
        '''
        self.api_key = api_key
        self.session = requests.Session()

    def get_data(
        self,
        dataset: str,
        variables: List[str],
        geo_level: str,
        geo_filter: Optional[Dict[str, str]] = None,
        year: Optional[str] = None,
        **kwargs,
    ) -> List[List[str]]:
        '''
        Get data from the Census API.

        Args:
            dataset: Dataset path (e.g., 'acs/acs5', 'dec/sf1', 'timeseries/poverty/saipe')
            variables: List of variable codes to retrieve
            geo_level: Geographic level (e.g., 'us:*', 'state:*', 'county:*')
            geo_filter: Optional geographic filters (e.g., {'state': '06'})
            year: Year for the dataset (if applicable)
            **kwargs: Additional query parameters

        Returns:
            List of lists containing the data (first row is headers)
        '''
        # Build the URL
        if year:
            url = f'{self.BASE_URL}/{year}/{dataset}'
        else:
            url = f'{self.BASE_URL}/{dataset}'

        # Build parameters
        params = {'get': ','.join(variables), 'for': geo_level, 'key': self.api_key}

        # Add geographic filters
        if geo_filter:
            for key, value in geo_filter.items():
                params[f'in'] = f'{key}:{value}'

        # Add additional parameters
        params.update(kwargs)

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_acs_data(
        self,
        variables: List[str],
        geo_level: str,
        year: str = '2021',
        survey: str = 'acs5',
        geo_filter: Optional[Dict[str, str]] = None,
    ) -> List[List[str]]:
        '''
        Get American Community Survey (ACS) data.

        Args:
            variables: List of ACS variable codes (e.g., ['B01001_001E'] for total population)
            geo_level: Geographic level (e.g., 'state:*', 'county:*')
            year: Year for the data (e.g., '2021')
            survey: Survey type ('acs1' for 1-year, 'acs5' for 5-year)
            geo_filter: Optional geographic filters

        Returns:
            List of lists containing the ACS data
        '''
        return self.get_data(
            dataset=f'acs/{survey}',
            variables=variables,
            geo_level=geo_level,
            geo_filter=geo_filter,
            year=year,
        )

    def get_population(
        self,
        geo_level: str = 'us:*',
        year: str = '2021',
        geo_filter: Optional[Dict[str, str]] = None,
    ) -> List[List[str]]:
        '''
        Get population data from ACS.

        Args:
            geo_level: Geographic level (e.g., 'state:*', 'county:*')
            year: Year for the data
            geo_filter: Optional geographic filters

        Returns:
            List of lists containing population data
        '''
        return self.get_acs_data(
            variables=['NAME', 'B01001_001E'],  # Total population
            geo_level=geo_level,
            year=year,
            geo_filter=geo_filter,
        )

    def get_median_income(
        self,
        geo_level: str = 'us:*',
        year: str = '2021',
        geo_filter: Optional[Dict[str, str]] = None,
    ) -> List[List[str]]:
        '''
        Get median household income from ACS.

        Args:
            geo_level: Geographic level (e.g., 'state:*', 'county:*')
            year: Year for the data
            geo_filter: Optional geographic filters

        Returns:
            List of lists containing median income data
        '''
        return self.get_acs_data(
            variables=['NAME', 'B19013_001E'],  # Median household income
            geo_level=geo_level,
            year=year,
            geo_filter=geo_filter,
        )

    def get_poverty_rate(
        self,
        geo_level: str = 'us:*',
        year: str = '2021',
        geo_filter: Optional[Dict[str, str]] = None,
    ) -> List[List[str]]:
        '''
        Get poverty rate from SAIPE (Small Area Income and Poverty Estimates).

        Args:
            geo_level: Geographic level (e.g., 'state:*', 'county:*')
            year: Year for the data
            geo_filter: Optional geographic filters

        Returns:
            List of lists containing poverty rate data
        '''
        return self.get_data(
            dataset='timeseries/poverty/saipe',
            variables=['NAME', 'SAEPOVRTALL_PT'],  # All ages poverty rate
            geo_level=geo_level,
            year=year,
            geo_filter=geo_filter,
        )

    def get_economic_indicators(
        self, variables: List[str], geo_level: str = 'us:*', year: Optional[str] = None
    ) -> List[List[str]]:
        '''
        Get economic indicators from the Economic Census or other economic datasets.

        Args:
            variables: List of variable codes
            geo_level: Geographic level
            year: Year for the data (if applicable)

        Returns:
            List of lists containing economic indicator data
        '''
        return self.get_data(
            dataset='cbp',  # County Business Patterns
            variables=variables,
            geo_level=geo_level,
            year=year,
        )

    def close(self):
        '''Close the session.'''
        self.session.close()

    def __enter__(self):
        '''Context manager entry.'''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Context manager exit.'''
        self.close()

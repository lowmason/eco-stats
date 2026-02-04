'''
Client for interacting with the Bureau of Economic Analysis (BEA) API.

The BEA API provides access to official U.S. macroeconomic statistics.
More info: https://apps.bea.gov/api/
'''

import requests
from typing import Dict, List, Optional, Any
import json


class BEAClient:
    '''
    Client for accessing BEA (Bureau of Economic Analysis) data.

    The BEA API provides access to official U.S. macroeconomic statistics
    including National Income and Product Accounts (NIPA), Regional Economic
    Accounts, and more.
    '''

    BASE_URL = 'https://apps.bea.gov/api/data'

    def __init__(self, api_key: str):
        '''
        Initialize the BEA client.

        Args:
            api_key: Your BEA API key. Register at https://apps.bea.gov/api/signup/
        '''
        self.api_key = api_key
        self.session = requests.Session()

    def get_parameter_list(self, dataset_name: str) -> Dict[str, Any]:
        '''
        Get the list of parameters for a specific dataset.

        Args:
            dataset_name: Name of the dataset (e.g., 'NIPA', 'NIUnderlyingDetail', 'FixedAssets')

        Returns:
            Dictionary containing parameter information
        '''
        params = {
            'UserID': self.api_key,
            'method': 'GetParameterList',
            'datasetname': dataset_name,
            'ResultFormat': 'JSON',
        }

        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

    def get_data(
        self,
        dataset_name: str,
        table_name: Optional[str] = None,
        frequency: Optional[str] = None,
        year: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        '''
        Get data from the BEA API.

        Args:
            dataset_name: Name of the dataset (e.g., 'NIPA', 'NIUnderlyingDetail')
            table_name: Table name or number
            frequency: Data frequency ('A' for annual, 'Q' for quarterly, 'M' for monthly)
            year: Year or range (e.g., '2020', 'X' for all years)
            **kwargs: Additional parameters specific to the dataset

        Returns:
            Dictionary containing the requested data
        '''
        params = {
            'UserID': self.api_key,
            'method': 'GetData',
            'datasetname': dataset_name,
            'ResultFormat': 'JSON',
        }

        if table_name:
            params['TableName'] = table_name
        if frequency:
            params['Frequency'] = frequency
        if year:
            params['Year'] = year

        # Add any additional parameters
        params.update(kwargs)

        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

    def get_nipa_data(
        self, table_name: str, frequency: str = 'A', year: str = 'X'
    ) -> Dict[str, Any]:
        '''
        Get National Income and Product Accounts (NIPA) data.

        Args:
            table_name: NIPA table name (e.g., 'T10101' for Gross Domestic Product)
            frequency: 'A' (annual), 'Q' (quarterly), or 'M' (monthly)
            year: Year or 'X' for all years

        Returns:
            Dictionary containing NIPA data
        '''
        return self.get_data(
            dataset_name='NIPA', table_name=table_name, frequency=frequency, year=year
        )

    def get_regional_data(
        self, table_name: str, line_code: str, geo_fips: str, year: str = 'LAST5'
    ) -> Dict[str, Any]:
        '''
        Get Regional Economic Accounts data.

        Args:
            table_name: Table name (e.g., 'CAINC1' for Personal Income Summary)
            line_code: Line code for specific data series
            geo_fips: Geographic FIPS code
            year: Year range (e.g., 'LAST5' for last 5 years)

        Returns:
            Dictionary containing regional data
        '''
        return self.get_data(
            dataset_name='Regional',
            TableName=table_name,
            LineCode=line_code,
            GeoFips=geo_fips,
            Year=year,
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

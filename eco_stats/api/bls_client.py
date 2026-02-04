"""
Client for interacting with the Bureau of Labor Statistics (BLS) API.

The BLS API provides access to employment, unemployment, prices, and other labor statistics.
More info: https://www.bls.gov/developers/
"""

import requests
from typing import Dict, List, Optional, Any
import json


class BLSClient:
    """
    Client for accessing BLS (Bureau of Labor Statistics) data.
    
    The BLS API provides access to employment, unemployment, Consumer Price Index (CPI),
    Producer Price Index (PPI), and many other labor-related statistics.
    """
    
    BASE_URL_V2 = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    BASE_URL_V1 = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the BLS client.
        
        Args:
            api_key: Your BLS API key (optional, but recommended for higher limits).
                    Register at https://data.bls.gov/registrationEngine/
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.base_url = self.BASE_URL_V2 if api_key else self.BASE_URL_V1
    
    def get_series(
        self,
        series_ids: List[str],
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
        catalog: bool = False,
        calculations: bool = False,
        annual_average: bool = False,
        aspects: bool = False
    ) -> Dict[str, Any]:
        """
        Get time series data for specified series IDs.
        
        Args:
            series_ids: List of BLS series IDs (e.g., ['LNS14000000'] for unemployment rate)
            start_year: Start year for data (format: 'YYYY')
            end_year: End year for data (format: 'YYYY')
            catalog: Include catalog metadata
            calculations: Include calculations (net changes, percent changes)
            annual_average: Include annual averages
            aspects: Include aspects (if available)
            
        Returns:
            Dictionary containing the requested time series data
        """
        payload = {
            'seriesid': series_ids
        }
        
        if self.api_key:
            payload['registrationkey'] = self.api_key
        
        if start_year:
            payload['startyear'] = start_year
        if end_year:
            payload['endyear'] = end_year
        if catalog:
            payload['catalog'] = catalog
        if calculations:
            payload['calculations'] = calculations
        if annual_average:
            payload['annualaverage'] = annual_average
        if aspects:
            payload['aspects'] = aspects
        
        headers = {'Content-Type': 'application/json'}
        response = self.session.post(
            self.base_url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_unemployment_rate(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the U.S. unemployment rate (seasonally adjusted).
        
        Args:
            start_year: Start year (format: 'YYYY')
            end_year: End year (format: 'YYYY')
            
        Returns:
            Dictionary containing unemployment rate data
        """
        return self.get_series(
            series_ids=['LNS14000000'],
            start_year=start_year,
            end_year=end_year
        )
    
    def get_cpi_all_items(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the Consumer Price Index for All Urban Consumers (CPI-U), All Items.
        
        Args:
            start_year: Start year (format: 'YYYY')
            end_year: End year (format: 'YYYY')
            
        Returns:
            Dictionary containing CPI data
        """
        return self.get_series(
            series_ids=['CUUR0000SA0'],
            start_year=start_year,
            end_year=end_year
        )
    
    def get_employment(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get total nonfarm employment (seasonally adjusted).
        
        Args:
            start_year: Start year (format: 'YYYY')
            end_year: End year (format: 'YYYY')
            
        Returns:
            Dictionary containing employment data
        """
        return self.get_series(
            series_ids=['CES0000000001'],
            start_year=start_year,
            end_year=end_year
        )
    
    def get_average_hourly_earnings(
        self,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get average hourly earnings of all employees (seasonally adjusted).
        
        Args:
            start_year: Start year (format: 'YYYY')
            end_year: End year (format: 'YYYY')
            
        Returns:
            Dictionary containing earnings data
        """
        return self.get_series(
            series_ids=['CES0500000003'],
            start_year=start_year,
            end_year=end_year
        )
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

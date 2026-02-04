"""
Main application module for eco-stats.

This module provides a unified interface to all API clients and utility functions.
"""

from typing import Optional
from eco_stats.api.bea_client import BEAClient
from eco_stats.api.bls_client import BLSClient
from eco_stats.api.census_client import CensusClient
from eco_stats.api.fred_client import FREDClient


class EcoStats:
    """
    Main application class for eco-stats.
    
    Provides a unified interface to access data from BEA, BLS, Census, and FRED APIs.
    """
    
    def __init__(
        self,
        bea_api_key: Optional[str] = None,
        bls_api_key: Optional[str] = None,
        census_api_key: Optional[str] = None,
        fred_api_key: Optional[str] = None
    ):
        """
        Initialize the EcoStats application.
        
        Args:
            bea_api_key: BEA API key
            bls_api_key: BLS API key (optional, but recommended)
            census_api_key: Census API key
            fred_api_key: FRED API key
        """
        self.bea_client = BEAClient(bea_api_key) if bea_api_key else None
        self.bls_client = BLSClient(bls_api_key) if bls_api_key else BLSClient()
        self.census_client = CensusClient(census_api_key) if census_api_key else None
        self.fred_client = FREDClient(fred_api_key) if fred_api_key else None
    
    @property
    def bea(self) -> Optional[BEAClient]:
        """Get BEA client."""
        if self.bea_client is None:
            raise ValueError("BEA API key not provided. Initialize EcoStats with bea_api_key.")
        return self.bea_client
    
    @property
    def bls(self) -> BLSClient:
        """Get BLS client."""
        return self.bls_client
    
    @property
    def census(self) -> Optional[CensusClient]:
        """Get Census client."""
        if self.census_client is None:
            raise ValueError("Census API key not provided. Initialize EcoStats with census_api_key.")
        return self.census_client
    
    @property
    def fred(self) -> Optional[FREDClient]:
        """Get FRED client."""
        if self.fred_client is None:
            raise ValueError("FRED API key not provided. Initialize EcoStats with fred_api_key.")
        return self.fred_client
    
    def close(self):
        """Close all client sessions."""
        if self.bea_client:
            self.bea_client.close()
        if self.bls_client:
            self.bls_client.close()
        if self.census_client:
            self.census_client.close()
        if self.fred_client:
            self.fred_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Main entry point for the application."""
    import os
    
    # Get API keys from environment variables
    bea_key = os.getenv('BEA_API_KEY')
    bls_key = os.getenv('BLS_API_KEY')
    census_key = os.getenv('CENSUS_API_KEY')
    fred_key = os.getenv('FRED_API_KEY')
    
    # Create EcoStats instance
    eco = EcoStats(
        bea_api_key=bea_key,
        bls_api_key=bls_key,
        census_api_key=census_key,
        fred_api_key=fred_key
    )
    
    print("EcoStats application initialized.")
    print("\nAvailable clients:")
    print(f"  - BEA: {'✓' if bea_key else '✗'}")
    print(f"  - BLS: {'✓' if bls_key else '✗ (limited access)'}")
    print(f"  - Census: {'✓' if census_key else '✗'}")
    print(f"  - FRED: {'✓' if fred_key else '✗'}")
    
    eco.close()


if __name__ == '__main__':
    main()

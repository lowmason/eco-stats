"""
Client for interacting with the Federal Reserve Economic Data (FRED) API.

The FRED API provides access to thousands of economic time series from the Federal Reserve Bank of St. Louis.
More info: https://fred.stlouisfed.org/docs/api/
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class FREDClient:
    """
    Client for accessing FRED (Federal Reserve Economic Data).

    The FRED API provides access to over 800,000 economic time series
    from the Federal Reserve Bank of St. Louis.
    """

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(self, api_key: str):
        """
        Initialize the FRED client.

        Args:
            api_key: Your FRED API key. Register at https://fred.stlouisfed.org/docs/api/api_key.html
        """
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the FRED API.

        Args:
            endpoint: API endpoint (e.g., 'series/observations')
            params: Query parameters

        Returns:
            Dictionary containing the API response
        """
        if params is None:
            params = {}

        params["api_key"] = self.api_key
        params["file_type"] = "json"

        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_series(self, series_id: str) -> Dict[str, Any]:
        """
        Get information about a specific series.

        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'DGS10')

        Returns:
            Dictionary containing series information
        """
        return self._make_request("series", {"series_id": series_id})

    def get_series_observations(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
        units: str = "lin",
        frequency: Optional[str] = None,
        aggregation_method: str = "avg",
        output_type: int = 1,
        vintage_dates: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """
        Get observations (data values) for a specific series.

        Args:
            series_id: FRED series ID
            observation_start: Start date (format: 'YYYY-MM-DD')
            observation_end: End date (format: 'YYYY-MM-DD')
            units: Units for data (e.g., 'lin' for levels, 'chg' for change, 'pch' for percent change)
            frequency: Data frequency (e.g., 'd', 'w', 'm', 'q', 'sa', 'a')
            aggregation_method: Method for aggregating data ('avg', 'sum', 'eop')
            output_type: Output type (1=observations by real-time period, 2-4=other formats)
            vintage_dates: Vintage dates for real-time data
            limit: Maximum number of results
            offset: Offset for pagination
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing series observations
        """
        params = {
            "series_id": series_id,
            "units": units,
            "aggregation_method": aggregation_method,
            "output_type": output_type,
            "sort_order": sort_order,
        }

        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if frequency:
            params["frequency"] = frequency
        if vintage_dates:
            params["vintage_dates"] = vintage_dates
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        return self._make_request("series/observations", params)

    def search_series(
        self,
        search_text: str,
        search_type: str = "full_text",
        limit: int = 1000,
        offset: int = 0,
        order_by: str = "search_rank",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Search for series.

        Args:
            search_text: Text to search for
            search_type: Type of search ('full_text' or 'series_id')
            limit: Maximum number of results
            offset: Offset for pagination
            order_by: Order results by ('search_rank', 'series_id', 'title', etc.)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing search results
        """
        params = {
            "search_text": search_text,
            "search_type": search_type,
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        return self._make_request("series/search", params)

    def get_categories(self, category_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get categories or a specific category.

        Args:
            category_id: Category ID (if None, returns root category)

        Returns:
            Dictionary containing category information
        """
        params = {}
        if category_id:
            params["category_id"] = category_id

        return self._make_request("category", params)

    def get_category_series(
        self, category_id: int, limit: int = 1000, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get series in a category.

        Args:
            category_id: Category ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Dictionary containing series in the category
        """
        params = {"category_id": category_id, "limit": limit, "offset": offset}

        return self._make_request("category/series", params)

    def get_gdp(
        self,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get Gross Domestic Product data.

        Args:
            observation_start: Start date (format: 'YYYY-MM-DD')
            observation_end: End date (format: 'YYYY-MM-DD')

        Returns:
            Dictionary containing GDP data
        """
        return self.get_series_observations(
            series_id="GDP",
            observation_start=observation_start,
            observation_end=observation_end,
        )

    def get_unemployment_rate(
        self,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get unemployment rate data.

        Args:
            observation_start: Start date (format: 'YYYY-MM-DD')
            observation_end: End date (format: 'YYYY-MM-DD')

        Returns:
            Dictionary containing unemployment rate data
        """
        return self.get_series_observations(
            series_id="UNRATE",
            observation_start=observation_start,
            observation_end=observation_end,
        )

    def get_federal_funds_rate(
        self,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get Federal Funds Effective Rate.

        Args:
            observation_start: Start date (format: 'YYYY-MM-DD')
            observation_end: End date (format: 'YYYY-MM-DD')

        Returns:
            Dictionary containing federal funds rate data
        """
        return self.get_series_observations(
            series_id="DFF",
            observation_start=observation_start,
            observation_end=observation_end,
        )

    def get_inflation_rate(
        self,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get CPI-based inflation rate (year-over-year percent change).

        Args:
            observation_start: Start date (format: 'YYYY-MM-DD')
            observation_end: End date (format: 'YYYY-MM-DD')

        Returns:
            Dictionary containing inflation rate data
        """
        return self.get_series_observations(
            series_id="CPIAUCSL",
            observation_start=observation_start,
            observation_end=observation_end,
            units="pc1",  # Percent change from year ago
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

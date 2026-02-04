"""
Example API client module demonstrating usage of config loaded with python-dotenv.
"""
from config import config


class APIClient:
    """Base API client that uses configuration from environment variables."""
    
    def __init__(self, api_name):
        """
        Initialize API client with configuration.
        
        Args:
            api_name: Name of the API ('weather', 'carbon', or 'eco_data')
        """
        self.api_name = api_name
        self.api_config = config.get_api_config(api_name)
        self.endpoint = self.api_config['endpoint']
        self.api_key = self.api_config['api_key']
        self.timeout = self.api_config['timeout']
        self.max_retries = self.api_config['max_retries']
    
    def get_headers(self):
        """Get headers for API requests including authentication."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
    
    def __repr__(self):
        return f"APIClient(api_name='{self.api_name}', endpoint='{self.endpoint}')"


class WeatherAPIClient(APIClient):
    """Client for weather API."""
    
    def __init__(self):
        super().__init__('weather')
    
    def get_weather(self, location):
        """
        Example method to get weather data.
        
        Args:
            location: Location for weather data
        
        Returns:
            str: Example response (actual implementation would make HTTP request)
        """
        return f"Getting weather for {location} from {self.endpoint}"


class CarbonAPIClient(APIClient):
    """Client for carbon intensity API."""
    
    def __init__(self):
        super().__init__('carbon')
    
    def get_carbon_intensity(self, region):
        """
        Example method to get carbon intensity data.
        
        Args:
            region: Region for carbon intensity data
        
        Returns:
            str: Example response (actual implementation would make HTTP request)
        """
        return f"Getting carbon intensity for {region} from {self.endpoint}"


class EcoDataAPIClient(APIClient):
    """Client for eco data API."""
    
    def __init__(self):
        super().__init__('eco_data')
    
    def get_eco_stats(self, metric):
        """
        Example method to get eco statistics.
        
        Args:
            metric: The metric to retrieve
        
        Returns:
            str: Example response (actual implementation would make HTTP request)
        """
        return f"Getting eco stats for {metric} from {self.endpoint}"


# Example usage
if __name__ == '__main__':
    # Validate configuration before using
    try:
        config.validate()
        print("✓ Configuration validated successfully")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("Please copy .env.example to .env and fill in your API keys")
        exit(1)
    
    # Create API clients
    weather_client = WeatherAPIClient()
    carbon_client = CarbonAPIClient()
    eco_client = EcoDataAPIClient()
    
    # Display configuration (without exposing keys)
    print(f"\nWeather API Client: {weather_client}")
    print(f"Carbon API Client: {carbon_client}")
    print(f"Eco Data API Client: {eco_client}")
    
    # Example usage
    print("\n--- Example API Calls ---")
    print(weather_client.get_weather("London"))
    print(carbon_client.get_carbon_intensity("UK"))
    print(eco_client.get_eco_stats("air_quality"))

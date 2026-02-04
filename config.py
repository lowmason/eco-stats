"""
Configuration module for eco-stats.
Loads API endpoints and keys from environment variables using python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration class to manage API endpoints and keys."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # API Endpoints
        self.WEATHER_API_ENDPOINT = os.getenv('WEATHER_API_ENDPOINT', 'https://api.openweathermap.org/data/2.5')
        self.CARBON_API_ENDPOINT = os.getenv('CARBON_API_ENDPOINT', 'https://api.carbonintensity.org.uk')
        self.ECO_DATA_API_ENDPOINT = os.getenv('ECO_DATA_API_ENDPOINT', 'https://api.example.com/eco')
        
        # API Keys
        self.WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
        self.CARBON_API_KEY = os.getenv('CARBON_API_KEY')
        self.ECO_DATA_API_KEY = os.getenv('ECO_DATA_API_KEY')
        
        # Optional configuration with error handling
        try:
            self.API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
        except ValueError:
            raise ValueError("API_TIMEOUT must be a valid integer")
        
        try:
            self.API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', '3'))
        except ValueError:
            raise ValueError("API_MAX_RETRIES must be a valid integer")
    
    def validate(self):
        """
        Validate that required configuration values are set.
        Raises ValueError if any required values are missing.
        """
        required_keys = [
            ('WEATHER_API_KEY', self.WEATHER_API_KEY),
            ('CARBON_API_KEY', self.CARBON_API_KEY),
            ('ECO_DATA_API_KEY', self.ECO_DATA_API_KEY),
        ]
        
        missing_keys = [key for key, value in required_keys if not value]
        
        if missing_keys:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_keys)}. "
                f"Please check your .env file."
            )
    
    def get_api_config(self, api_name):
        """
        Get API configuration for a specific API.
        
        Args:
            api_name: Name of the API ('weather', 'carbon', or 'eco_data')
        
        Returns:
            dict: Configuration dictionary with endpoint and key
        """
        api_configs = {
            'weather': {
                'endpoint': self.WEATHER_API_ENDPOINT,
                'api_key': self.WEATHER_API_KEY,
                'timeout': self.API_TIMEOUT,
                'max_retries': self.API_MAX_RETRIES,
            },
            'carbon': {
                'endpoint': self.CARBON_API_ENDPOINT,
                'api_key': self.CARBON_API_KEY,
                'timeout': self.API_TIMEOUT,
                'max_retries': self.API_MAX_RETRIES,
            },
            'eco_data': {
                'endpoint': self.ECO_DATA_API_ENDPOINT,
                'api_key': self.ECO_DATA_API_KEY,
                'timeout': self.API_TIMEOUT,
                'max_retries': self.API_MAX_RETRIES,
            },
        }
        
        if api_name not in api_configs:
            raise ValueError(f"Unknown API name: {api_name}")
        
        return api_configs[api_name]


# Create a singleton instance for easy import
config = Config()

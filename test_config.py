"""
Tests for configuration module.
"""
import os
import unittest
from unittest.mock import patch
from config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    @patch.dict(os.environ, {
        'WEATHER_API_KEY': 'test_weather_key',
        'CARBON_API_KEY': 'test_carbon_key',
        'ECO_DATA_API_KEY': 'test_eco_key',
        'API_TIMEOUT': '60',
        'API_MAX_RETRIES': '5'
    })
    def test_config_loads_from_env(self):
        """Test that configuration loads from environment variables."""
        config = Config()
        self.assertEqual(config.WEATHER_API_KEY, 'test_weather_key')
        self.assertEqual(config.CARBON_API_KEY, 'test_carbon_key')
        self.assertEqual(config.ECO_DATA_API_KEY, 'test_eco_key')
        self.assertEqual(config.API_TIMEOUT, 60)
        self.assertEqual(config.API_MAX_RETRIES, 5)
    
    @patch.dict(os.environ, {
        'WEATHER_API_KEY': 'test_key',
        'CARBON_API_KEY': 'test_key',
        'ECO_DATA_API_KEY': 'test_key'
    })
    def test_validate_success(self):
        """Test validation succeeds when all required keys are present."""
        config = Config()
        # Should not raise an exception
        config.validate()
    
    @patch.dict(os.environ, {
        'WEATHER_API_KEY': 'test_key',
        'CARBON_API_KEY': ''  # Missing key
    }, clear=True)
    def test_validate_failure(self):
        """Test validation fails when required keys are missing."""
        config = Config()
        with self.assertRaises(ValueError) as context:
            config.validate()
        self.assertIn('Missing required environment variables', str(context.exception))
    
    @patch.dict(os.environ, {
        'WEATHER_API_ENDPOINT': 'https://test.example.com',
        'WEATHER_API_KEY': 'test_key',
        'CARBON_API_KEY': 'test_key',
        'ECO_DATA_API_KEY': 'test_key'
    })
    def test_get_api_config(self):
        """Test getting API-specific configuration."""
        config = Config()
        weather_config = config.get_api_config('weather')
        
        self.assertEqual(weather_config['endpoint'], 'https://test.example.com')
        self.assertEqual(weather_config['api_key'], 'test_key')
        self.assertIn('timeout', weather_config)
        self.assertIn('max_retries', weather_config)
    
    @patch.dict(os.environ, {
        'WEATHER_API_KEY': 'test_key',
        'CARBON_API_KEY': 'test_key',
        'ECO_DATA_API_KEY': 'test_key'
    })
    def test_get_api_config_invalid_name(self):
        """Test that invalid API name raises ValueError."""
        config = Config()
        with self.assertRaises(ValueError) as context:
            config.get_api_config('invalid_api')
        self.assertIn('Unknown API name', str(context.exception))
    
    def test_default_values(self):
        """Test that default values are used when env vars are not set."""
        config = Config()
        self.assertEqual(config.API_TIMEOUT, 30)
        self.assertEqual(config.API_MAX_RETRIES, 3)
        self.assertIsNotNone(config.WEATHER_API_ENDPOINT)
        self.assertIsNotNone(config.CARBON_API_ENDPOINT)
        self.assertIsNotNone(config.ECO_DATA_API_ENDPOINT)


if __name__ == '__main__':
    unittest.main()

# eco-stats

A Python application for collecting and analyzing environmental statistics from various APIs.

## Features

- **Environment-based Configuration**: Uses `python-dotenv` to securely load API endpoints and keys from environment variables
- **Multiple API Support**: Configurable clients for weather, carbon intensity, and eco data APIs
- **Easy Configuration Management**: Simple configuration class with validation

## Setup

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lowmason/eco-stats.git
cd eco-stats
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your actual API keys and endpoints:
```env
# API Configuration
WEATHER_API_ENDPOINT=https://api.openweathermap.org/data/2.5
WEATHER_API_KEY=your_actual_weather_api_key

CARBON_API_ENDPOINT=https://api.carbonintensity.org.uk
CARBON_API_KEY=your_actual_carbon_api_key

ECO_DATA_API_ENDPOINT=https://api.example.com/eco
ECO_DATA_API_KEY=your_actual_eco_data_api_key
```

## Usage

### Using the Configuration Module

```python
from config import config

# Access configuration values
print(config.WEATHER_API_ENDPOINT)
print(config.WEATHER_API_KEY)

# Validate all required keys are present
try:
    config.validate()
    print("Configuration is valid!")
except ValueError as e:
    print(f"Configuration error: {e}")

# Get API-specific configuration
weather_config = config.get_api_config('weather')
print(weather_config)
```

### Using API Clients

```python
from api_client import WeatherAPIClient, CarbonAPIClient, EcoDataAPIClient

# Create API clients (automatically loads config from environment)
weather_client = WeatherAPIClient()
carbon_client = CarbonAPIClient()
eco_client = EcoDataAPIClient()

# Use the clients
weather_client.get_weather("London")
carbon_client.get_carbon_intensity("UK")
eco_client.get_eco_stats("air_quality")
```

### Running the Example

```bash
python api_client.py
```

## Configuration

### Environment Variables

The following environment variables can be configured in your `.env` file:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `WEATHER_API_ENDPOINT` | Weather API base URL | No | `https://api.openweathermap.org/data/2.5` |
| `WEATHER_API_KEY` | Weather API authentication key | Yes | - |
| `CARBON_API_ENDPOINT` | Carbon Intensity API base URL | No | `https://api.carbonintensity.org.uk` |
| `CARBON_API_KEY` | Carbon Intensity API authentication key | Yes | - |
| `ECO_DATA_API_ENDPOINT` | Eco Data API base URL | No | `https://api.example.com/eco` |
| `ECO_DATA_API_KEY` | Eco Data API authentication key | Yes | - |
| `API_TIMEOUT` | Request timeout in seconds | No | `30` |
| `API_MAX_RETRIES` | Maximum number of retry attempts | No | `3` |

## Security

- **Never commit your `.env` file** to version control (it's already in `.gitignore`)
- Store sensitive API keys only in the `.env` file
- Use `.env.example` as a template for required variables (without actual values)
- Rotate API keys regularly and update your `.env` file accordingly

## Project Structure

```
eco-stats/
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules (includes .env)
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── config.py             # Configuration loader using python-dotenv
└── api_client.py         # Example API client implementations
```

## License

MIT License - see LICENSE file for details
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
A Python library for pulling statistical series from multiple U.S. government economic data APIs, including BEA, BLS, Census, and FRED.

## Features

- **Bureau of Economic Analysis (BEA)**: Access to GDP, national income, and regional economic data
- **Bureau of Labor Statistics (BLS)**: Employment, unemployment, CPI, and wage data
- **U.S. Census Bureau**: Demographic data, American Community Survey, and economic indicators
- **Federal Reserve Economic Data (FRED)**: 800,000+ economic time series from the Federal Reserve Bank of St. Louis
- **Utility Functions**: Helper functions for date validation, data parsing, caching, and more

## Installation

### From source

```bash
git clone https://github.com/lowmason/eco-stats.git
cd eco-stats
pip install -e .
```

### With pandas support (optional)

```bash
pip install -e .[pandas]
```

## API Keys

To use this library, you'll need API keys from the respective services:

- **BEA**: Register at https://apps.bea.gov/api/signup/
- **BLS**: Register at https://data.bls.gov/registrationEngine/ (optional, but recommended for higher limits)
- **Census**: Register at https://api.census.gov/data/key_signup.html
- **FRED**: Register at https://fred.stlouisfed.org/docs/api/api_key.html

Set your API keys as environment variables:

```bash
export BEA_API_KEY="your_bea_api_key"
export BLS_API_KEY="your_bls_api_key"
export CENSUS_API_KEY="your_census_api_key"
export FRED_API_KEY="your_fred_api_key"
```

## Quick Start

### Using Individual Clients

```python
from eco_stats import BEAClient, BLSClient, CensusClient, FREDClient

# BEA Example
bea = BEAClient(api_key="your_bea_api_key")
gdp_data = bea.get_nipa_data(table_name='T10101', frequency='Q', year='X')
print(gdp_data)

# BLS Example
bls = BLSClient(api_key="your_bls_api_key")
unemployment = bls.get_unemployment_rate(start_year='2020', end_year='2024')
print(unemployment)

# Census Example
census = CensusClient(api_key="your_census_api_key")
population = census.get_population(geo_level='state:*', year='2021')
print(population)

# FRED Example
fred = FREDClient(api_key="your_fred_api_key")
gdp = fred.get_gdp(observation_start='2020-01-01', observation_end='2024-01-01')
print(gdp)
```

### Using the Unified Interface

```python
from eco_stats import EcoStats

# Initialize with all API keys
eco = EcoStats(
    bea_api_key="your_bea_api_key",
    bls_api_key="your_bls_api_key",
    census_api_key="your_census_api_key",
    fred_api_key="your_fred_api_key"
)

# Access any client
gdp_data = eco.fred.get_gdp()
unemployment = eco.bls.get_unemployment_rate()

eco.close()
```

### Using Context Managers

```python
from eco_stats import FREDClient

with FREDClient(api_key="your_fred_api_key") as fred:
    gdp = fred.get_gdp()
    unemployment = fred.get_unemployment_rate()
    # Session automatically closed
```

## API Client Examples

### BEA (Bureau of Economic Analysis)

```python
from eco_stats import BEAClient

bea = BEAClient(api_key="your_bea_api_key")

# Get GDP data
gdp = bea.get_nipa_data(table_name='T10101', frequency='Q', year='X')

# Get regional data
regional = bea.get_regional_data(
    table_name='CAINC1',
    line_code='1',
    geo_fips='STATE',
    year='LAST5'
)

bea.close()
```

### BLS (Bureau of Labor Statistics)

```python
from eco_stats import BLSClient

bls = BLSClient(api_key="your_bls_api_key")

# Get unemployment rate
unemployment = bls.get_unemployment_rate(start_year='2020', end_year='2024')

# Get CPI data
cpi = bls.get_cpi_all_items(start_year='2020', end_year='2024')

# Get custom series
custom = bls.get_series(
    series_ids=['LNS14000000', 'CES0000000001'],
    start_year='2020',
    end_year='2024'
)

bls.close()
```

### Census Bureau

```python
from eco_stats import CensusClient

census = CensusClient(api_key="your_census_api_key")

# Get population by state
population = census.get_population(geo_level='state:*', year='2021')

# Get median income
income = census.get_median_income(geo_level='state:*', year='2021')

# Get custom ACS data
acs_data = census.get_acs_data(
    variables=['B01001_001E', 'B19013_001E'],
    geo_level='county:*',
    geo_filter={'state': '06'},  # California
    year='2021'
)

census.close()
```

### FRED (Federal Reserve Economic Data)

```python
from eco_stats import FREDClient

fred = FREDClient(api_key="your_fred_api_key")

# Get GDP
gdp = fred.get_gdp(observation_start='2020-01-01')

# Get unemployment rate
unemployment = fred.get_unemployment_rate(observation_start='2020-01-01')

# Get federal funds rate
fed_funds = fred.get_federal_funds_rate(observation_start='2020-01-01')

# Get inflation rate
inflation = fred.get_inflation_rate(observation_start='2020-01-01')

# Search for series
search_results = fred.search_series(search_text='unemployment')

# Get custom series observations
custom = fred.get_series_observations(
    series_id='DGS10',  # 10-Year Treasury Constant Maturity Rate
    observation_start='2020-01-01',
    units='lin'
)

fred.close()
```

## Utility Functions

```python
from eco_stats.utils import (
    validate_date,
    format_date,
    extract_series_data,
    convert_to_dataframe,
    calculate_percent_change,
    calculate_moving_average,
    cache_response,
    load_cached_response
)

# Validate date
is_valid = validate_date('2024-01-01')  # Returns True

# Extract series data
fred_response = fred.get_gdp()
data = extract_series_data(fred_response, api_type='fred')

# Convert to DataFrame (requires pandas)
df = convert_to_dataframe(data)

# Calculate percent change
values = [100, 105, 110, 108]
pct_change = calculate_percent_change(values)

# Calculate moving average
moving_avg = calculate_moving_average(values, window=3)

# Cache response
cache_path = cache_response(fred_response, cache_key='gdp_2024')

# Load cached response
cached_data = load_cached_response('gdp_2024')
```

## Command Line Interface

Run the application from the command line:

```bash
eco-stats
```

Or using Python:

```bash
python -m eco_stats
```

## Examples

See the `examples/` directory for complete working examples.

## Development

### Running Tests

```bash
pip install -e .[dev]
pytest
```

### Code Style

```bash
black eco_stats/
flake8 eco_stats/
```

## License

MIT License - see LICENSE file for details
MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Bureau of Economic Analysis
- Bureau of Labor Statistics
- U.S. Census Bureau
- Federal Reserve Bank of St. Louis

## Resources

- [BEA API Documentation](https://apps.bea.gov/api/)
- [BLS API Documentation](https://www.bls.gov/developers/)
- [Census API Documentation](https://www.census.gov/data/developers.html)
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)

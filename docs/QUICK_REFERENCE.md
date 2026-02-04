# Quick Reference Guide

## Installation

```bash
pip install -e .
```

## Environment Setup

Copy `.env.template` to `.env` and add your API keys:

```bash
cp .env.template .env
# Edit .env with your API keys
```

## Quick Usage Examples

### BEA (Bureau of Economic Analysis)

```python
from eco_stats import BEAClient

bea = BEAClient(api_key="your_api_key")
gdp = bea.get_nipa_data(table_name='T10101', frequency='Q', year='2023')
bea.close()
```

### BLS (Bureau of Labor Statistics)

```python
from eco_stats import BLSClient

bls = BLSClient(api_key="your_api_key")  # API key optional
unemployment = bls.get_unemployment_rate(start_year='2020', end_year='2024')
bls.close()
```

### Census Bureau

```python
from eco_stats import CensusClient

census = CensusClient(api_key="your_api_key")
population = census.get_population(geo_level='state:*', year='2021')
census.close()
```

### FRED (Federal Reserve Economic Data)

```python
from eco_stats import FREDClient

fred = FREDClient(api_key="your_api_key")
gdp = fred.get_gdp(observation_start='2020-01-01')
fred.close()
```

### Unified Interface

```python
from eco_stats import EcoStats

with EcoStats(fred_api_key="your_key", bls_api_key="your_key") as eco:
    gdp = eco.fred.get_gdp()
    unemployment = eco.bls.get_unemployment_rate()
```

## Utility Functions

```python
from eco_stats.utils import (
    validate_date,
    calculate_percent_change,
    calculate_moving_average,
    convert_to_dataframe
)

# Validate date
is_valid = validate_date('2024-01-01')

# Calculate percent change
values = [100, 105, 110]
pct_change = calculate_percent_change(values)

# Calculate moving average
moving_avg = calculate_moving_average(values, window=3)
```

## Running Tests

```bash
pip install -e .[dev]
pytest tests/
```

## Running Examples

```bash
# Set your API keys as environment variables first
export FRED_API_KEY="your_key"
export BLS_API_KEY="your_key"

# Run an example
python examples/fred_example.py
python examples/bls_example.py
```

## CLI Usage

```bash
eco-stats
```

## Common Series IDs

### BLS Series IDs
- `LNS14000000` - Unemployment Rate
- `CUUR0000SA0` - Consumer Price Index (CPI-U)
- `CES0000000001` - Total Nonfarm Employment
- `CES0500000003` - Average Hourly Earnings

### FRED Series IDs
- `GDP` - Gross Domestic Product
- `UNRATE` - Unemployment Rate
- `DFF` - Federal Funds Effective Rate
- `CPIAUCSL` - Consumer Price Index
- `DGS10` - 10-Year Treasury Constant Maturity Rate

### BEA Tables
- `T10101` - Gross Domestic Product
- `CAINC1` - Personal Income Summary (Regional)

### Census Variables
- `B01001_001E` - Total Population
- `B19013_001E` - Median Household Income
- `B01002_001E` - Median Age

## API Documentation Links

- [BEA API Docs](https://apps.bea.gov/api/)
- [BLS API Docs](https://www.bls.gov/developers/)
- [Census API Docs](https://www.census.gov/data/developers.html)
- [FRED API Docs](https://fred.stlouisfed.org/docs/api/)

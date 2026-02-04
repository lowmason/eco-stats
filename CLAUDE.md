# CLAUDE.md

## Project Overview

eco-stats is a Python library for pulling statistical series from U.S. government economic data APIs: BEA, BLS, Census Bureau, and FRED.

## Tech Stack

- Python 3.8+
- `requests` for HTTP, `python-dotenv` for env config
- Optional: `polars` for dataframe support (preferred over pandas)
- Dev tools: `pytest`, `ruff`

## Project Structure

```
src/
  eco_stats/            # Main package
    __init__.py         # Exports: BEAClient, BLSClient, CensusClient, FREDClient, EcoStats
    __main__.py         # EcoStats unified class + CLI entry point
    api/                # Individual API clients (bea, bls, census, fred)
    utils/helpers.py    # Date validation, data parsing, caching, calculations
tests/                  # pytest test suite
examples/               # Example scripts for each API + unified usage
```

## Common Commands

```bash
# Install
pip install -e .            # Base install
pip install -e .[dev]       # With dev tools (pytest, ruff)
pip install -e .[polars]    # With polars support (preferred)

# Test
pytest tests/
pytest tests/test_basic.py -v
pytest --cov=eco_stats tests/

# Lint & Check
ruff check src/             # Lint code
ruff format --check src/    # Check formatting (without modifying)

# Format (manual only, not on commit)
ruff format src/            # Format code

# Run CLI
python -m eco_stats
```

## Environment Setup

API keys are loaded from `.env` via `python-dotenv`. Copy `.env.template` and fill in keys:
- `BEA_API_KEY`, `BLS_API_KEY`, `CENSUS_API_KEY`, `FRED_API_KEY`

Never commit `.env` files — they are in `.gitignore`.

## Code Conventions

- PEP 8 with `ruff` formatting
- **Single quotes for strings** — always use `'single'` instead of `"double"` quotes for string literals
- Type hints throughout (`Optional[str]`, etc.)
- Docstrings on all public classes and functions (triple single quotes: `'''docstring'''`)
- snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- Each API client uses `requests.Session()` with context manager support (`__enter__`/`__exit__`)
- Private methods prefixed with `_` (e.g., `_make_request`)
- Code is linted/formatted manually, not automatically on commit
- **Polars over pandas** — when adding dataframe support, use polars (faster, more memory-efficient)

## Architecture Notes

- Each API has its own client class in `src/eco_stats/api/`
- `EcoStats` in `__main__.py` wraps all clients into a unified interface with lazy property accessors
- Utility functions in `src/eco_stats/utils/helpers.py` handle cross-cutting concerns (date validation, caching, percent change calculations)
- BLS client works without an API key (limited access); all others require keys

"""
Client for the U.S. Census Bureau API.

Provides access to demographic, economic, and geographic data from
dozens of Census surveys and programs.  Results are returned as Polars
DataFrames by default.

API docs:
    https://www.census.gov/data/developers.html
Available APIs:
    https://www.census.gov/data/developers/data-sets.html
"""

from typing import Any, Dict, List, Optional, Union

import requests

try:
    import polars as pl

    _HAS_POLARS = True
except ImportError:
    _HAS_POLARS = False


# ---------------------------------------------------------------------------
# Dataset catalog
# ---------------------------------------------------------------------------

DATASET_CATALOG: Dict[str, Dict[str, Any]] = {
    # American Community Survey ------------------------------------------------
    'acs1': {
        'path': 'acs/acs1',
        'timeseries': False,
        'name': 'American Community Survey 1-Year Estimates',
        'description': (
            'Social, economic, demographic, and housing data '
            'for areas with 65,000+ population.'
        ),
        'years': '2005-2024',
        'default_year': '2023',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/acs-1year.html'),
    },
    'acs5': {
        'path': 'acs/acs5',
        'timeseries': False,
        'name': 'American Community Survey 5-Year Estimates',
        'description': (
            'Social, economic, demographic, and housing data '
            'available down to the block-group level.'
        ),
        'years': '2009-2024',
        'default_year': '2023',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/acs-5year.html'),
    },
    # Decennial Census ---------------------------------------------------------
    'dec/pl': {
        'path': 'dec/pl',
        'timeseries': False,
        'name': 'Decennial Census Redistricting Data',
        'description': (
            'Population and housing by sex, age, race, and '
            'Hispanic origin at all geographic levels.'
        ),
        'years': '2000, 2010, 2020',
        'default_year': '2020',
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/decennial-census.html'
        ),
    },
    # Economic Census ----------------------------------------------------------
    'ecnbasic': {
        'path': 'ecnbasic',
        'timeseries': False,
        'name': 'Economic Census \u2013 Economy-Wide Key Statistics',
        'description': (
            'Establishments, sales, payroll, and employees by industry '
            'and geography from the five-year Economic Census.'
        ),
        'years': '2002, 2007, 2012, 2017, 2022',
        'default_year': '2022',
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/economic-census.html'
        ),
    },
    'ecnsize': {
        'path': 'ecnsize',
        'timeseries': False,
        'name': 'Economic Census \u2013 Establishment & Firm Size',
        'description': (
            'Establishment and firm size statistics from the Economic Census.'
        ),
        'years': '2012, 2017, 2022',
        'default_year': '2022',
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/economic-census.html'
        ),
    },
    'ecncomp': {
        'path': 'ecncomp',
        'timeseries': False,
        'name': 'Economic Census \u2013 Comparative Statistics',
        'description': (
            'Comparative statistics on 2017 NAICS basis for 2022 and 2017.'
        ),
        'years': '2022',
        'default_year': '2022',
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/economic-census.html'
        ),
    },
    # Business Dynamics Statistics ----------------------------------------------
    'bds': {
        'path': 'timeseries/bds',
        'timeseries': True,
        'year_param': 'YEAR',
        'name': 'Business Dynamics Statistics',
        'description': (
            'Annual job creation/destruction, establishment '
            'births/deaths, and firm startups/shutdowns (1978\u20132023).'
        ),
        'years': '1978-2023',
        'default_year': None,
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/business-dynamics.html'
        ),
    },
    # Annual Business Survey ---------------------------------------------------
    'abscs': {
        'path': 'abscs',
        'timeseries': False,
        'name': 'Annual Business Survey \u2013 Company Summary',
        'description': (
            'Employer firm counts, revenue, employment, and payroll '
            'by sector, sex, ethnicity, race, and veteran status.'
        ),
        'years': '2017-2023',
        'default_year': '2023',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/abs.html'),
    },
    'abscb': {
        'path': 'abscb',
        'timeseries': False,
        'name': 'Annual Business Survey \u2013 Characteristics of Businesses',
        'description': (
            'Detailed business characteristics for employer firms '
            'by sector, demographics, and size.'
        ),
        'years': '2017-2023',
        'default_year': '2023',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/abs.html'),
    },
    'abscbo': {
        'path': 'abscbo',
        'timeseries': False,
        'name': ('Annual Business Survey \u2013 Characteristics of Business Owners'),
        'description': (
            'Owner-level data by sector, sex, ethnicity, race, '
            'veteran status, and owner characteristics.'
        ),
        'years': '2017-2023',
        'default_year': '2023',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/abs.html'),
    },
    'absmcb': {
        'path': 'absmcb',
        'timeseries': False,
        'name': ('Annual Business Survey \u2013 Module Business Characteristics'),
        'description': (
            'Technology use, financing, and pandemic impacts for employer firms.'
        ),
        'years': '2021-2023',
        'default_year': '2023',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/abs.html'),
    },
    # Quarterly Workforce Indicators -------------------------------------------
    'qwi/sa': {
        'path': 'timeseries/qwi/sa',
        'timeseries': True,
        'year_param': 'year',
        'name': 'Quarterly Workforce Indicators \u2013 Sex by Age',
        'description': (
            'Employment, wages, hires, separations, and job flows '
            'by worker sex and age group.'
        ),
        'years': '1990-present',
        'default_year': None,
        'docs_url': ('https://www.census.gov/data/developers/data-sets/qwi.html'),
    },
    'qwi/se': {
        'path': 'timeseries/qwi/se',
        'timeseries': True,
        'year_param': 'year',
        'name': 'Quarterly Workforce Indicators \u2013 Sex by Education',
        'description': (
            'Employment flow indicators by worker sex and educational attainment.'
        ),
        'years': '1990-present',
        'default_year': None,
        'docs_url': ('https://www.census.gov/data/developers/data-sets/qwi.html'),
    },
    'qwi/rh': {
        'path': 'timeseries/qwi/rh',
        'timeseries': True,
        'year_param': 'year',
        'name': ('Quarterly Workforce Indicators \u2013 Race by Ethnicity'),
        'description': ('Employment flow indicators by worker race and ethnicity.'),
        'years': '1990-present',
        'default_year': None,
        'docs_url': ('https://www.census.gov/data/developers/data-sets/qwi.html'),
    },
    # Public Sector Statistics -------------------------------------------------
    'govs': {
        'path': 'timeseries/govs',
        'timeseries': True,
        'year_param': 'YEAR',
        'name': 'Annual Public Sector Statistics',
        'description': (
            'State and local government finances, employment, '
            'payroll, pensions, and tax collections (1942\u2013present).'
        ),
        'years': '1942-present',
        'default_year': None,
        'docs_url': (
            'https://www.census.gov/data/developers/'
            'data-sets/annual-public-sector-stats.html'
        ),
    },
    # County Business Patterns -------------------------------------------------
    'cbp': {
        'path': 'cbp',
        'timeseries': False,
        'name': 'County Business Patterns',
        'description': (
            'Establishments, employment, and payroll by industry '
            'at county, state, and national levels.'
        ),
        'years': '1986-2022',
        'default_year': '2022',
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/cbp-nonemp.html'
        ),
    },
    # Poverty / SAIPE ----------------------------------------------------------
    'saipe': {
        'path': 'timeseries/poverty/saipe',
        'timeseries': True,
        'year_param': 'time',
        'name': 'Small Area Income and Poverty Estimates',
        'description': (
            'Income and poverty estimates for school districts, counties, and states.'
        ),
        'years': '1989-present',
        'default_year': None,
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/Poverty-Statistics.html'
        ),
    },
    # Geography Information ----------------------------------------------------
    'geoinfo': {
        'path': 'geoinfo',
        'timeseries': False,
        'name': 'Geography Information',
        'description': (
            'Spatial attributes (lat/lon, land/water area) for all '
            'Census-disseminated geographies.'
        ),
        'years': '2020-2024',
        'default_year': '2024',
        'docs_url': ('https://www.census.gov/data/developers/data-sets/geo-info.html'),
    },
    # Population Estimates -----------------------------------------------------
    'pep': {
        'path': 'pep/population',
        'timeseries': False,
        'name': 'Population Estimates Program',
        'description': (
            'Intercensal population estimates from births, deaths, and migration.'
        ),
        'years': '2015-2024',
        'default_year': '2024',
        'docs_url': (
            'https://www.census.gov/data/developers/data-sets/popest-popproj.html'
        ),
    },
}

# Columns that should remain as strings during numeric auto-casting.
_IDENTIFIER_COLUMNS = frozenset(
    {
        # Geographic FIPS codes
        'state',
        'county',
        'tract',
        'block group',
        'block',
        'place',
        'zip code tabulation area',
        'congressional district',
        'metropolitan statistical area/micropolitan statistical area',
        'combined statistical area',
        'workforce investment area',
        'school district (elementary)',
        'school district (secondary)',
        'school district (unified)',
        'region',
        'division',
        'geo_id',
        'geoid',
        'fips',
        'ucgid',
        'sumlevel',
        'sumlev',
        # Industry / classification codes
        'naics',
        'naics2017',
        'naics2022',
        'sic',
        'ind_level',
        'indlevel',
        # BDS / ABS categorical codes
        'fage',
        'eage',
        'empszfi',
        'empszfii',
        'empszes',
        'empszesi',
        'ownercode',
        'seasonadj',
        'periodicity',
        # QWI worker characteristics
        'sex',
        'agegrp',
        'education',
        'race',
        'ethnicity',
        'metro',
        'geocomp',
        'firmsize',
        'firmage',
        # Public sector identifiers
        'svy_comp',
        'govtype',
        'geotype',
        'agg_desc',
        # Misc
        'us',
        'time',
    }
)


class CensusClient:
    """
    Client for accessing U.S. Census Bureau data.

    Provides methods for querying dozens of Census datasets and returns
    results as Polars DataFrames (with an optional raw list-of-lists
    fallback).

    Usage::

        from eco_stats import CensusClient

        with CensusClient(api_key='your_key') as census:
            # List available datasets
            census.list_datasets()

            # Explore variables in a dataset
            census.get_variables('acs5', year='2023')

            # Pull ACS population by state
            census.get_population(geo_for='state:*')

            # Pull BDS job-creation data
            census.get_bds(
                indicators=['JOB_CREATION', 'JOB_DESTRUCTION'],
                geo_for='us:1',
                year='2023',
            )
    """

    BASE_URL = 'https://api.census.gov/data'
    GEOCODER_URL = 'https://geocoding.geo.census.gov/geocoder'

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Census client.

        Args:
            api_key: Census API key.  Register free at
                https://api.census.gov/data/key_signup.html
                Required for most endpoints (geocoding is an exception).
        """
        self.api_key = api_key
        self.session = requests.Session()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_url(self, dataset: str, year: Optional[str] = None) -> str:
        """Build the full API URL for *dataset*, consulting the catalog."""
        info = DATASET_CATALOG.get(dataset)
        if info:
            if info['timeseries']:
                return f'{self.BASE_URL}/{info["path"]}'
            use_year = year or info.get('default_year')
            if not use_year:
                raise ValueError(
                    f'Year is required for dataset {dataset!r} '
                    f'and no default is configured.'
                )
            return f'{self.BASE_URL}/{use_year}/{info["path"]}'
        # Fallback: treat *dataset* as a literal path segment.
        if dataset.startswith('timeseries/'):
            return f'{self.BASE_URL}/{dataset}'
        if year:
            return f'{self.BASE_URL}/{year}/{dataset}'
        return f'{self.BASE_URL}/{dataset}'

    def _request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute a GET request and return parsed JSON."""
        params = dict(params or {})
        if self.api_key:
            params['key'] = self.api_key
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'error' in data:
            raise ValueError(f'Census API error: {data["error"]}')
        return data

    @staticmethod
    def _require_polars() -> None:
        """Raise if polars is not installed."""
        if not _HAS_POLARS:
            raise ImportError(
                'polars is required for DataFrame output. '
                'Install with:  pip install eco-stats[polars]'
            )

    def _to_dataframe(self, data: List[List[str]]) -> 'pl.DataFrame':
        """Convert a Census list-of-lists response to a Polars DataFrame."""
        self._require_polars()
        if not isinstance(data, list) or len(data) < 2:
            return pl.DataFrame()
        headers = data[0]
        rows = data[1:]
        # Deduplicate column names
        seen: Dict[str, int] = {}
        unique: List[str] = []
        for h in headers:
            low = h.lower()
            if low in seen:
                seen[low] += 1
                unique.append(f'{low}_{seen[low]}')
            else:
                seen[low] = 0
                unique.append(low)
        # Build column-oriented dict (all Utf8 initially)
        col_data = {
            unique[i]: [row[i] if i < len(row) else None for row in rows]
            for i in range(len(unique))
        }
        df = pl.DataFrame(col_data)
        return self._cast_numeric_columns(df)

    @staticmethod
    def _is_identifier_column(name: str) -> bool:
        """Return True if *name* should remain a string."""
        low = name.lower()
        if low in _IDENTIFIER_COLUMNS:
            return True
        if low.endswith('_f') or low.endswith('_label'):
            return True
        if 'name' in low:
            return True
        return False

    @staticmethod
    def _cast_numeric_columns(df: 'pl.DataFrame') -> 'pl.DataFrame':
        """Auto-cast string columns that are entirely numeric to Float64."""
        cast_exprs = []
        for col_name in df.columns:
            if CensusClient._is_identifier_column(col_name):
                continue
            series = df.get_column(col_name)
            # Skip if already numeric
            if series.dtype.is_numeric():
                continue
            non_null = series.drop_nulls()
            if non_null.len() == 0:
                continue
            trial = non_null.cast(pl.Float64, strict=False)
            if trial.null_count() == 0:
                cast_exprs.append(pl.col(col_name).cast(pl.Float64))
        if cast_exprs:
            df = df.with_columns(cast_exprs)
        return df

    # ------------------------------------------------------------------
    # Core query
    # ------------------------------------------------------------------

    def get_data(
        self,
        dataset: str,
        variables: Union[str, List[str]],
        geo_for: str,
        geo_in: Optional[str] = None,
        year: Optional[str] = None,
        raw: bool = False,
        **predicates: Any,
    ) -> Union['pl.DataFrame', List[List[str]]]:
        """
        Query any Census dataset.

        Args:
            dataset: Dataset key from the catalog (e.g. ``'acs5'``,
                ``'bds'``) **or** a raw API path segment
                (e.g. ``'acs/acs5'``).
            variables: Variable codes to retrieve.  Pass a list
                (``['NAME', 'B01001_001E']``) or a comma-separated
                string (``'NAME,B01001_001E'``).
            geo_for: Geography selector for the ``for`` clause
                (e.g. ``'state:*'``, ``'county:001'``, ``'us:1'``).
            geo_in: Optional containing-geography for the ``in``
                clause (e.g. ``'state:06'``).
            year: Data year.  For year-based datasets it appears in
                the URL path; for timeseries datasets it is sent as
                a query predicate.
            raw: If ``True``, return the raw list-of-lists instead
                of a DataFrame.
            **predicates: Additional query predicates passed straight
                to the API (e.g. ``NAICS='54'``, ``YEAR='2023'``).

        Returns:
            ``polars.DataFrame`` (default) or ``list[list[str]]`` when
            *raw* is ``True``.
        """
        info = DATASET_CATALOG.get(dataset)
        if info and info['timeseries']:
            url = f'{self.BASE_URL}/{info["path"]}'
            if year is not None and info.get('year_param'):
                predicates.setdefault(info['year_param'], year)
        else:
            url = self._build_url(dataset, year)

        get_str = variables if isinstance(variables, str) else ','.join(variables)
        params: Dict[str, Any] = {
            'get': get_str,
            'for': geo_for,
        }
        if geo_in is not None:
            params['in'] = geo_in
        params.update(predicates)

        data = self._request(url, params)
        if raw:
            return data
        return self._to_dataframe(data)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_datasets(self) -> 'pl.DataFrame':
        """
        Return the built-in dataset catalog as a DataFrame.

        Columns: ``key``, ``name``, ``description``, ``timeseries``,
        ``years``, ``default_year``, ``docs_url``.
        """
        self._require_polars()
        rows = [
            {
                'key': key,
                'name': info['name'],
                'description': info['description'],
                'timeseries': info['timeseries'],
                'years': info['years'],
                'default_year': info.get('default_year', ''),
                'docs_url': info.get('docs_url', ''),
            }
            for key, info in DATASET_CATALOG.items()
        ]
        return pl.DataFrame(rows)

    def get_variables(
        self,
        dataset: str,
        year: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        List the variables available for a dataset.

        Args:
            dataset: Catalog key (e.g. ``'acs5'``) or raw path.
            year: Year (required for year-based datasets without a
                default).

        Returns:
            DataFrame with ``name``, ``label``, ``concept``,
            ``predicate_type``, ``group``.
        """
        self._require_polars()
        url = self._build_url(dataset, year)
        data = self._request(f'{url}/variables.json', {})
        variables = data.get('variables', {})
        rows = []
        for var_name, meta in variables.items():
            if var_name in ('for', 'in', 'key', 'ucgid'):
                continue
            rows.append(
                {
                    'name': var_name,
                    'label': meta.get('label', ''),
                    'concept': meta.get('concept', ''),
                    'predicate_type': meta.get('predicateType', ''),
                    'group': meta.get('group', ''),
                }
            )
        return pl.DataFrame(rows).sort('name')

    def get_geographies(
        self,
        dataset: str,
        year: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        List the geographies supported by a dataset.

        Args:
            dataset: Catalog key or raw path.
            year: Year (if required).

        Returns:
            DataFrame with ``name``, ``level``, ``requires``,
            ``wildcard``.
        """
        self._require_polars()
        url = self._build_url(dataset, year)
        data = self._request(f'{url}/geography.json', {})
        fips_list = data.get('fips', [])
        rows = []
        for geo in fips_list:
            rows.append(
                {
                    'name': geo.get('name', ''),
                    'level': geo.get('geoLevelDisplay', ''),
                    'requires': ', '.join(geo.get('requires', [])),
                    'wildcard': ', '.join(geo.get('wildcard', [])),
                }
            )
        return pl.DataFrame(rows)

    # ------------------------------------------------------------------
    # American Community Survey
    # ------------------------------------------------------------------

    def get_acs(
        self,
        variables: List[str],
        geo_for: str = 'state:*',
        geo_in: Optional[str] = None,
        year: str = '2023',
        survey: str = 'acs5',
    ) -> 'pl.DataFrame':
        """
        Get American Community Survey data.

        Args:
            variables: ACS variable codes
                (e.g. ``['NAME', 'B01001_001E']``).
            geo_for: Geography (``'state:*'``, ``'county:*'``, etc.).
            geo_in: Containing geography (e.g. ``'state:06'``).
            year: Data year (default ``'2023'``).
            survey: ``'acs1'`` (1-year) or ``'acs5'`` (5-year).
        """
        return self.get_data(
            dataset=survey,
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
        )

    def get_population(
        self,
        geo_for: str = 'state:*',
        geo_in: Optional[str] = None,
        year: str = '2023',
        survey: str = 'acs5',
    ) -> 'pl.DataFrame':
        """
        Convenience: total population from ACS (``B01001_001E``).
        """
        return self.get_acs(
            variables=['NAME', 'B01001_001E'],
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
            survey=survey,
        )

    def get_median_income(
        self,
        geo_for: str = 'state:*',
        geo_in: Optional[str] = None,
        year: str = '2023',
        survey: str = 'acs5',
    ) -> 'pl.DataFrame':
        """
        Convenience: median household income from ACS
        (``B19013_001E``).
        """
        return self.get_acs(
            variables=['NAME', 'B19013_001E'],
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
            survey=survey,
        )

    # ------------------------------------------------------------------
    # Economic Census
    # ------------------------------------------------------------------

    def get_economic_census(
        self,
        variables: List[str],
        geo_for: str = 'us:*',
        geo_in: Optional[str] = None,
        year: str = '2022',
        table: str = 'ecnbasic',
        naics: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        Get Economic Census data.

        Args:
            variables: Variable codes (e.g.
                ``['NAICS2022_LABEL', 'EMP', 'PAYANN', 'RCPTOT']``).
            geo_for: Geography (``'us:*'``, ``'state:*'``, etc.).
            geo_in: Containing geography.
            year: Census year (every five years:
                ``'2002'``\u2013``'2022'``).
            table: Sub-table: ``'ecnbasic'``, ``'ecnsize'``,
                ``'ecncomp'``, ``'ecnmatfuel'``, ``'ecnnapcsind'``,
                ``'ecnnapcsprd'``, etc.
            naics: NAICS code filter (e.g. ``'54'``).  The predicate
                name is auto-set to ``NAICS{year}`` to match the
                Economic Census vintage.

        See https://www.census.gov/data/developers/data-sets/economic-census.html
        """
        predicates: Dict[str, str] = {}
        if naics is not None:
            predicates[f'NAICS{year}'] = naics
        return self.get_data(
            dataset=table,
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
            **predicates,
        )

    # ------------------------------------------------------------------
    # Business Dynamics Statistics
    # ------------------------------------------------------------------

    def get_bds(
        self,
        indicators: List[str],
        geo_for: str = 'us:1',
        geo_in: Optional[str] = None,
        year: Optional[Union[str, List[str]]] = None,
        naics: Optional[str] = None,
        firm_size: Optional[str] = None,
        initial_firm_size: Optional[str] = None,
        estab_size: Optional[str] = None,
        initial_estab_size: Optional[str] = None,
        firm_age: Optional[str] = None,
        estab_age: Optional[str] = None,
        metro: Optional[str] = None,
        geocomp: Optional[str] = None,
        ind_level: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        Get Business Dynamics Statistics.

        Args:
            indicators: BDS indicators (e.g.
                ``['JOB_CREATION', 'JOB_DESTRUCTION', 'FIRM',
                'ESTAB']``).
            geo_for: Geography (``'us:1'``, ``'state:*'``,
                ``'county:*'``).
            geo_in: Containing geography.
            year: Year(s) (``'2023'``, ``['2020','2021','2022']``,
                or ``'*'`` for all).
            naics: NAICS sector / subsector / industry-group code.
            firm_size: Firm employment-size code (``EMPSZFI``).
            initial_firm_size: Initial firm-size code (``EMPSZFII``).
            estab_size: Establishment-size code (``EMPSZES``).
            initial_estab_size: Initial estab-size (``EMPSZESI``).
            firm_age: Firm-age code (``FAGE``).
            estab_age: Establishment-age code (``EAGE``).
            metro: Metro / non-metro code (``'M'`` or ``'N'``).
                Use with *geocomp*.
            geocomp: Geography-component code.  Use with *metro*.
            ind_level: Industry level (``'2'`` sector, ``'3'``
                subsector, ``'4'`` industry group).

        See https://www.census.gov/data/developers/data-sets/business-dynamics.html
        """
        predicates: Dict[str, Any] = {}
        _optionals = {
            'YEAR': year,
            'NAICS': naics,
            'EMPSZFI': firm_size,
            'EMPSZFII': initial_firm_size,
            'EMPSZES': estab_size,
            'EMPSZESI': initial_estab_size,
            'FAGE': firm_age,
            'EAGE': estab_age,
            'METRO': metro,
            'GEOCOMP': geocomp,
            'INDLEVEL': ind_level,
        }
        for key, val in _optionals.items():
            if val is not None:
                predicates[key] = val
        return self.get_data(
            dataset='bds',
            variables=indicators,
            geo_for=geo_for,
            geo_in=geo_in,
            **predicates,
        )

    # ------------------------------------------------------------------
    # Annual Business Survey
    # ------------------------------------------------------------------

    def get_abs(
        self,
        variables: List[str],
        geo_for: str = 'us:*',
        geo_in: Optional[str] = None,
        year: str = '2023',
        table: str = 'abscs',
        sex: Optional[str] = None,
        ethnicity: Optional[str] = None,
        race: Optional[str] = None,
        veteran: Optional[str] = None,
        naics: Optional[str] = None,
        empszfi: Optional[str] = None,
        qdesc: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        Get Annual Business Survey data.

        Args:
            variables: Variable codes (see ``get_variables()``).
            geo_for: Geography.
            geo_in: Containing geography.
            year: Reference year (default ``'2023'``).
            table: ``'abscs'`` (Company Summary),
                ``'abscb'`` (Characteristics of Businesses),
                ``'abscbo'`` (Characteristics of Business Owners),
                ``'absmcb'`` (Module Business Characteristics).
            sex: Sex filter code.
            ethnicity: Ethnicity-group code (``ETH_GROUP``).
            race: Race-group code (``RACE_GROUP``).
            veteran: Veteran-group code (``VET_GROUP``).
            naics: NAICS code filter.
            empszfi: Employment-size-of-firm code.
            qdesc: Question-description filter label (for
                ``abscb`` / ``abscbo`` / ``absmcb``).

        Note:
            For ``abscbo`` (Business Owners), the demographic
            predicates use ``OWNER_SEX``, ``OWNER_ETH``,
            ``OWNER_RACE``, ``OWNER_VET`` instead of the standard
            names.  Pass those directly via ``get_data()``
            or as ``**predicates``.

        See https://www.census.gov/data/developers/data-sets/abs.html
        """
        predicates: Dict[str, str] = {}
        _optionals = {
            'SEX': sex,
            'ETH_GROUP': ethnicity,
            'RACE_GROUP': race,
            'VET_GROUP': veteran,
            'NAICS2022': naics,
            'EMPSZFI': empszfi,
            'QDESC_LABEL': qdesc,
        }
        for key, val in _optionals.items():
            if val is not None:
                predicates[key] = val
        return self.get_data(
            dataset=table,
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
            **predicates,
        )

    # ------------------------------------------------------------------
    # Quarterly Workforce Indicators
    # ------------------------------------------------------------------

    def get_qwi(
        self,
        indicators: List[str],
        geo_for: str = 'state:*',
        geo_in: Optional[str] = None,
        endpoint: str = 'sa',
        year: Optional[Union[str, List[str]]] = None,
        quarter: Optional[Union[str, List[str]]] = None,
        time: Optional[str] = None,
        industry: Optional[Union[str, List[str]]] = None,
        ind_level: Optional[str] = None,
        sex: Optional[Union[str, List[str]]] = None,
        agegrp: Optional[Union[str, List[str]]] = None,
        education: Optional[Union[str, List[str]]] = None,
        race: Optional[Union[str, List[str]]] = None,
        ethnicity: Optional[Union[str, List[str]]] = None,
        firmsize: Optional[str] = None,
        firmage: Optional[str] = None,
        ownercode: Optional[str] = None,
        seasonadj: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        Get Quarterly Workforce Indicators.

        Args:
            indicators: QWI indicator names \u2014 **case-sensitive**
                (e.g. ``['Emp', 'EarnS', 'HirA', 'Sep']``).
            geo_for: Geography (``'state:24'``, ``'county:*'``).
            geo_in: Containing geography (e.g. ``'state:24'``).
            endpoint: ``'sa'`` (Sex/Age), ``'se'`` (Sex/Education),
                or ``'rh'`` (Race/Ethnicity).
            year: Year(s).
            quarter: Quarter(s) (``'1'``\u2013``'4'``).
            time: Combined year-quarter (``'2023-Q1'`` or
                ``'from 2020-Q1 to 2023-Q4'``).
            industry: NAICS code(s).
            ind_level: Industry level (``'S'`` sector,
                ``'3'``\u2013``'6'`` digit).
            sex: Sex code(s).
            agegrp: Age-group code(s) (``sa`` endpoint).
            education: Education code(s) (``se`` endpoint).
            race: Race code(s) (``rh`` endpoint).
            ethnicity: Ethnicity code(s) (``rh`` endpoint).
            firmsize: Firm-size code.
            firmage: Firm-age code.
            ownercode: Ownership code (e.g. ``'A05'`` all private).
            seasonadj: Seasonal adjustment (``'U'`` unadjusted).

        See https://www.census.gov/data/developers/data-sets/qwi.html
        """
        dataset = f'qwi/{endpoint}'
        predicates: Dict[str, Any] = {}
        _optionals: Dict[str, Any] = {
            'year': year,
            'quarter': quarter,
            'time': time,
            'industry': industry,
            'ind_level': ind_level,
            'sex': sex,
            'agegrp': agegrp,
            'education': education,
            'race': race,
            'ethnicity': ethnicity,
            'firmsize': firmsize,
            'firmage': firmage,
            'ownercode': ownercode,
            'seasonadj': seasonadj,
        }
        for key, val in _optionals.items():
            if val is not None:
                predicates[key] = val
        return self.get_data(
            dataset=dataset,
            variables=indicators,
            geo_for=geo_for,
            geo_in=geo_in,
            **predicates,
        )

    # ------------------------------------------------------------------
    # Public Sector Statistics
    # ------------------------------------------------------------------

    def get_public_sector(
        self,
        variables: List[str],
        geo_for: str = 'us',
        geo_in: Optional[str] = None,
        year: Optional[Union[str, List[str]]] = None,
        survey_component: Optional[str] = None,
        gov_type: Optional[str] = None,
        agg_desc: Optional[Union[str, List[str]]] = None,
    ) -> 'pl.DataFrame':
        """
        Get Annual Public Sector Statistics.

        Args:
            variables: Variable codes (e.g.
                ``['SVY_COMP_LABEL', 'AGG_DESC_LABEL',
                'AMOUNT_FORMATTED']``).
            geo_for: Geography (``'us'``, ``'state:24'``,
                ``'state:*'``).
            geo_in: Containing geography.
            year: Year(s).
            survey_component: ``SVY_COMP`` code \u2014
                ``'01'`` Employment & Payroll,
                ``'02'`` State & Local Finances,
                ``'03'`` State Tax Collections,
                ``'04'`` Public Pensions,
                ``'05'`` State Govt. Finances,
                ``'06'`` School System Finances,
                ``'07'`` Government Organization.
            gov_type: ``GOVTYPE`` code (e.g. ``'001'`` State+Local,
                ``'002'`` State, ``'003'`` Local).
            agg_desc: ``AGG_DESC`` code(s) for specific measures.

        See https://www.census.gov/data/developers/data-sets/annual-public-sector-stats.html
        """
        predicates: Dict[str, Any] = {}
        _optionals: Dict[str, Any] = {
            'YEAR': year,
            'SVY_COMP': survey_component,
            'GOVTYPE': gov_type,
            'AGG_DESC': agg_desc,
        }
        for key, val in _optionals.items():
            if val is not None:
                predicates[key] = val
        return self.get_data(
            dataset='govs',
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            **predicates,
        )

    # ------------------------------------------------------------------
    # County Business Patterns
    # ------------------------------------------------------------------

    def get_cbp(
        self,
        variables: List[str],
        geo_for: str = 'us:*',
        geo_in: Optional[str] = None,
        year: str = '2022',
        naics: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        Get County Business Patterns data.

        Args:
            variables: Variables (e.g.
                ``['NAME', 'ESTAB', 'EMP', 'PAYANN']``).
            geo_for: Geography.
            geo_in: Containing geography.
            year: Data year (default ``'2022'``).
            naics: NAICS code filter (``NAICS2017`` predicate).
                Use ``get_variables('cbp')`` to confirm the
                predicate name for your chosen year.
        """
        predicates: Dict[str, str] = {}
        if naics is not None:
            predicates['NAICS2017'] = naics
        return self.get_data(
            dataset='cbp',
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
            **predicates,
        )

    # ------------------------------------------------------------------
    # Poverty / SAIPE
    # ------------------------------------------------------------------

    def get_poverty(
        self,
        variables: Optional[List[str]] = None,
        geo_for: str = 'state:*',
        geo_in: Optional[str] = None,
        year: Optional[str] = None,
    ) -> 'pl.DataFrame':
        """
        Get Small Area Income and Poverty Estimates (SAIPE).

        Args:
            variables: Variable codes.  Defaults to name and the
                all-ages poverty rate (``SAEPOVRTALL_PT``).
            geo_for: Geography.
            geo_in: Containing geography.
            year: Time period (e.g. ``'2022'``).
        """
        if variables is None:
            variables = ['NAME', 'SAEPOVRTALL_PT']
        return self.get_data(
            dataset='saipe',
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
        )

    # ------------------------------------------------------------------
    # Geography Information
    # ------------------------------------------------------------------

    def get_geo_info(
        self,
        variables: Optional[List[str]] = None,
        geo_for: str = 'state:*',
        geo_in: Optional[str] = None,
        year: str = '2024',
    ) -> 'pl.DataFrame':
        """
        Get Geography Information (spatial attributes).

        Args:
            variables: Variable codes.  Defaults to ``['NAME']``.
            geo_for: Geography.
            geo_in: Containing geography.
            year: Data year (default ``'2024'``).

        See https://www.census.gov/data/developers/data-sets/geo-info.html
        """
        if variables is None:
            variables = ['NAME']
        return self.get_data(
            dataset='geoinfo',
            variables=variables,
            geo_for=geo_for,
            geo_in=geo_in,
            year=year,
        )

    # ------------------------------------------------------------------
    # Geocoding
    # ------------------------------------------------------------------

    def geocode(
        self,
        address: Optional[str] = None,
        *,
        street: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        return_type: str = 'geographies',
        benchmark: str = 'Public_AR_Current',
        vintage: str = 'Current_Current',
    ) -> 'pl.DataFrame':
        """
        Geocode a single address (no API key required).

        Provide **either** a one-line *address* **or** structured
        fields (*street*, *city*, *state*, *zip_code*).

        Args:
            address: Full one-line address string.
            street: Street address.
            city: City name.
            state: State abbreviation.
            zip_code: ZIP code.
            return_type: ``'locations'`` for coordinates only or
                ``'geographies'`` (default) to include Census
                geography codes.
            benchmark: Geocoder benchmark dataset.
            vintage: Geocoder vintage (used with ``'geographies'``).

        Returns:
            DataFrame with one row per address match containing
            ``matched_address``, ``longitude``, ``latitude``, and
            (optionally) Census geography columns.

        See https://www.census.gov/data/developers/data-sets/Geocoding-services.html
        """
        self._require_polars()
        if address:
            url = f'{self.GEOCODER_URL}/{return_type}/onelineaddress'
            params: Dict[str, str] = {
                'address': address,
                'benchmark': benchmark,
                'format': 'json',
            }
        elif street:
            url = f'{self.GEOCODER_URL}/{return_type}/address'
            params = {
                'street': street,
                'benchmark': benchmark,
                'format': 'json',
            }
            if city:
                params['city'] = city
            if state:
                params['state'] = state
            if zip_code:
                params['zip'] = zip_code
        else:
            raise ValueError(
                'Provide either address or street '
                '(with optional city, state, zip_code).'
            )

        if return_type == 'geographies':
            params['vintage'] = vintage

        response = self.session.get(url, params=params)
        response.raise_for_status()
        result = response.json().get('result', {})
        matches = result.get('addressMatches', [])

        rows: List[Dict[str, Any]] = []
        for match in matches:
            row: Dict[str, Any] = {
                'matched_address': match.get('matchedAddress', ''),
                'longitude': match.get('coordinates', {}).get('x'),
                'latitude': match.get('coordinates', {}).get('y'),
                'tiger_line_id': match.get('tigerLine', {}).get('tigerLineId', ''),
                'side': match.get('tigerLine', {}).get('side', ''),
            }
            # Flatten geography layers when present
            for geo_type, geo_list in match.get('geographies', {}).items():
                if geo_list:
                    geo = geo_list[0]
                    prefix = geo_type.lower().replace(' ', '_').rstrip('s')
                    for k, v in geo.items():
                        col = f'{prefix}_{k.lower()}'
                        row[col] = str(v) if v is not None else None
            rows.append(row)

        if not rows:
            return pl.DataFrame(
                schema={
                    'matched_address': pl.Utf8,
                    'longitude': pl.Float64,
                    'latitude': pl.Float64,
                }
            )
        return self._cast_numeric_columns(pl.DataFrame(rows))

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> 'CensusClient':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

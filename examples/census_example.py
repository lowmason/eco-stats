"""
Example: Using the Census Bureau API client.

Demonstrates the expanded CensusClient with Polars DataFrames,
dataset discovery, and convenience methods for ACS, Economic Census,
BDS, ABS, QWI, Public Sector, CBP, SAIPE, Geography Info, and
Geocoding.
"""

import os

from dotenv import load_dotenv

from eco_stats import CensusClient

load_dotenv()


def main():
    api_key = os.getenv('CENSUS_API_KEY')
    if not api_key:
        print('Error: CENSUS_API_KEY not set.')
        print('Register at: https://api.census.gov/data/key_signup.html')
        return

    with CensusClient(api_key=api_key) as census:
        print('=' * 60)
        print('Census Bureau API — Expanded Client Examples')
        print('=' * 60)

        # -- Discovery -------------------------------------------------
        print('\n--- Dataset Catalog ---')
        datasets = census.list_datasets()
        print(datasets)

        print('\n--- ACS 5-Year Variables (first 10) ---')
        try:
            variables = census.get_variables('acs5', year='2023')
            print(variables.head(10))
        except Exception as e:
            print(f'  Error: {e}')

        print('\n--- ACS 5-Year Geographies ---')
        try:
            geos = census.get_geographies('acs5', year='2023')
            print(geos)
        except Exception as e:
            print(f'  Error: {e}')

        # -- ACS -------------------------------------------------------
        print('\n--- Population by State (ACS 5-Year, 2023) ---')
        try:
            pop = census.get_population(geo_for='state:*')
            print(pop.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        print('\n--- Median Income by State (ACS 5-Year, 2023) ---')
        try:
            income = census.get_median_income(geo_for='state:*')
            print(income.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        print('\n--- Custom ACS: Pop + Median Age, CA Counties ---')
        try:
            ca = census.get_acs(
                variables=['NAME', 'B01001_001E', 'B01002_001E'],
                geo_for='county:*',
                geo_in='state:06',
                year='2023',
            )
            print(ca.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- Economic Census -------------------------------------------
        print('\n--- Economic Census: Prof Services (NAICS 54) ---')
        try:
            ecn = census.get_economic_census(
                variables=['NAICS2022_LABEL', 'EMP', 'PAYANN', 'GEO_ID'],
                geo_for='us:*',
                naics='54',
            )
            print(ecn)
        except Exception as e:
            print(f'  Error: {e}')

        # -- Business Dynamics Statistics ------------------------------
        print('\n--- BDS: National Job Creation, 2020-2023 ---')
        try:
            bds = census.get_bds(
                indicators=['JOB_CREATION', 'JOB_DESTRUCTION', 'FIRM'],
                geo_for='us:1',
                year=['2020', '2021', '2022', '2023'],
            )
            print(bds)
        except Exception as e:
            print(f'  Error: {e}')

        # -- Annual Business Survey ------------------------------------
        print('\n--- ABS Company Summary: National, 2023 ---')
        try:
            abs_data = census.get_abs(
                variables=[
                    'GEO_ID',
                    'NAICS2022_LABEL',
                    'FIRMPDEMP',
                    'RCPPDEMP',
                    'EMP',
                ],
                geo_for='us:*',
            )
            print(abs_data.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- QWI -------------------------------------------------------
        print('\n--- QWI: Employment by State, 2023-Q1 ---')
        try:
            qwi = census.get_qwi(
                indicators=['Emp', 'EarnS'],
                geo_for='state:*',
                year='2023',
                quarter='1',
            )
            print(qwi.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- Public Sector ---------------------------------------------
        print('\n--- Public Sector: US Tax Collections, 2022 ---')
        try:
            govs = census.get_public_sector(
                variables=[
                    'SVY_COMP_LABEL',
                    'AGG_DESC_LABEL',
                    'AMOUNT_FORMATTED',
                ],
                geo_for='us',
                year='2022',
                survey_component='03',
            )
            print(govs.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- CBP -------------------------------------------------------
        print('\n--- CBP: Establishments by State, 2022 ---')
        try:
            cbp = census.get_cbp(
                variables=['NAME', 'ESTAB', 'EMP', 'PAYANN'],
                geo_for='state:*',
            )
            print(cbp.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- Poverty / SAIPE ------------------------------------------
        print('\n--- SAIPE: Poverty Rate by State ---')
        try:
            pov = census.get_poverty(
                geo_for='state:*',
                year='2022',
            )
            print(pov.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- Geography Info --------------------------------------------
        print('\n--- Geography Info: States, 2024 ---')
        try:
            geo = census.get_geo_info(
                variables=['NAME', 'INTPTLAT', 'INTPTLON'],
                geo_for='state:*',
            )
            print(geo.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        # -- Geocoding (no key required) -------------------------------
        print('\n--- Geocode: 1600 Pennsylvania Ave NW, DC ---')
        try:
            result = census.geocode(
                address='1600 Pennsylvania Ave NW, Washington, DC 20500'
            )
            print(result)
        except Exception as e:
            print(f'  Error: {e}')

        # -- Generic get_data ------------------------------------------
        print('\n--- Generic: Decennial 2020 Pop by State ---')
        try:
            dec = census.get_data(
                dataset='dec/pl',
                variables=['NAME', 'P1_001N'],
                geo_for='state:*',
                year='2020',
            )
            print(dec.head(5))
        except Exception as e:
            print(f'  Error: {e}')

        print('\n' + '=' * 60)
        print('Census Bureau API examples complete.')
        print('=' * 60)


if __name__ == '__main__':
    main()

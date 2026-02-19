'''
CLI entry point for scraping BLS release schedules.
'''

from pathlib import Path

import polars as pl

from eco_stats.vintage.bls_schedule import scrape_range


def main() -> None:
    '''Scrape BLS schedule pages and write output files.'''
    print('Scraping BLS release schedules (2016-2026)...\n')

    df = scrape_range(start_year=2016, end_year=2026, delay=1.0)

    print(f'\nTotal rows: {df.height}')
    print('\nBy source:')
    print(df.group_by('source').len().sort('source'))

    print('\n-- CES National (Employment Situation) --')
    with pl.Config(tbl_rows=30):
        print(df.filter(pl.col('source') == 'ces_national').select('reference_period', 'release_date'))

    print('\n-- CES State --')
    with pl.Config(tbl_rows=30):
        print(df.filter(pl.col('source') == 'ces_state').select('reference_period', 'release_date'))

    print('\n-- QCEW (County Employment and Wages) --')
    with pl.Config(tbl_rows=30):
        print(df.filter(pl.col('source') == 'qcew').select('reference_period', 'release_date'))

    out = Path('/mnt/user-data/outputs')
    out.mkdir(parents=True, exist_ok=True)

    parquet_path = out / 'bls_release_dates_scraped.parquet'
    df.write_parquet(parquet_path)
    print(f'\nSaved: {parquet_path} ({df.height} rows)')

    csv_path = out / 'bls_release_dates_scraped.csv'
    df.write_csv(csv_path)
    print(f'Saved: {csv_path}')


if __name__ == '__main__':
    main()

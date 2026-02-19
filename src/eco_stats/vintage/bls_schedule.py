'''
Scrape BLS yearly release schedules for CES National, CES State, and QCEW.

Source pages: https://www.bls.gov/schedule/YYYY/home.htm (2016-2026)
'''

import re
import time
from datetime import date
from typing import Any

import httpx
import polars as pl
from bs4 import BeautifulSoup


BASE_URL = 'https://www.bls.gov/schedule/{year}/home.htm'

# BLS schedule name -> our program label.
# Keys are lowercased for matching; order matters (longest match first).
PROGRAM_MAP: dict[str, str] = {
    'employment situation': 'ces_national',
    'regional and state employment and unemployment (monthly)': 'ces_state',
    'regional and state employment and unemployment': 'ces_state',
    'state employment and unemployment (monthly)': 'ces_state',
    'state employment and unemployment': 'ces_state',
    'county employment and wages': 'qcew',
}


def _build_http2_client() -> httpx.Client:
    '''Build an HTTP/2 client with browser-like headers for BLS schedule pages.'''
    return httpx.Client(
        http2=True,
        follow_redirects=True,
        timeout=60.0,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
    )


def scrape_year(year: int, session: httpx.Client | None = None) -> list[dict[str, Any]]:
    '''
    Scrape a single yearly schedule page and return matching rows.

    The page at https://www.bls.gov/schedule/YYYY/home.htm contains
    12 monthly tables, each with columns: Date | Time | Release.

    The Release cell contains the program name (in <b> or <strong>)
    followed by "for <reference_period>".

    Returns a list of dicts with keys:
      source, reference_period, ref_date, release_date, schedule_year, bls_program_name
    '''
    created_client = session is None
    if session is None:
        session = _build_http2_client()

    url = BASE_URL.format(year=year)
    try:
        resp = session.get(url)
        resp.raise_for_status()
    finally:
        if created_client:
            session.close()

    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = []

    for table in soup.find_all('table'):
        for tr in table.find_all('tr'):
            cells = tr.find_all('td')
            if len(cells) < 3:
                continue

            date_text = cells[0].get_text(strip=True)
            release_cell = cells[2]

            # Extract the program name from bold/strong tags.
            bold = release_cell.find(['b', 'strong'])
            if bold is None:
                continue

            program_name = bold.get_text(strip=True)
            program_key = _match_program(program_name)
            if program_key is None:
                continue

            # Extract reference period from the full cell text.
            # Use separator=' ' to preserve spacing between elements
            # (e.g., <b>Name</b> for Period -> "Name for Period").
            full_text = release_cell.get_text(separator=' ', strip=True)
            ref_period = _extract_reference_period(full_text, program_name)
            ref_date = _parse_reference_period_date(ref_period, source=program_key)

            # Parse the release date.
            release_date = _parse_schedule_date(date_text)
            if release_date is None:
                continue

            rows.append(
                {
                    'source': program_key,
                    'reference_period': ref_period,
                    'ref_date': ref_date,
                    'release_date': release_date,
                    'schedule_year': year,
                    'bls_program_name': program_name,
                }
            )

    return rows


def scrape_range(
    start_year: int = 2016,
    end_year: int = 2026,
    delay: float = 1.0,
) -> pl.DataFrame:
    '''
    Scrape all yearly schedule pages from start_year to end_year.

    Args:
        start_year: First year to scrape (inclusive).
        end_year: Last year to scrape (inclusive).
        delay: Seconds to wait between requests (be polite to BLS).

    Returns:
        Polars DataFrame with columns:
          source, reference_period, ref_date, release_date, schedule_year, bls_program_name
    '''
    all_rows: list[dict[str, Any]] = []
    with _build_http2_client() as session:
        for year in range(start_year, end_year + 1):
            print(f'  Scraping {year}...', end=' ', flush=True)
            try:
                rows = scrape_year(year, session=session)
                all_rows.extend(rows)
                counts = {}
                for row in rows:
                    counts[row['source']] = counts.get(row['source'], 0) + 1
                print(
                    f'ces_national={counts.get("ces_national", 0)}, '
                    f'ces_state={counts.get("ces_state", 0)}, '
                    f'qcew={counts.get("qcew", 0)}'
                )
            except httpx.HTTPError as exc:
                print(f'FAILED: {exc}')

            if year < end_year:
                time.sleep(delay)

    if not all_rows:
        return pl.DataFrame(
            schema={
                'source': pl.Utf8,
                'reference_period': pl.Utf8,
                'ref_date': pl.Date,
                'release_date': pl.Date,
                'schedule_year': pl.Int64,
                'bls_program_name': pl.Utf8,
            }
        )

    return (
        pl.DataFrame(all_rows)
        .sort('source', 'release_date')
        .unique(subset=['source', 'release_date'], keep='first')
    )


def _match_program(name: str) -> str | None:
    '''
    Match a BLS program name to our label.

    Returns the program key if matched, None otherwise.
    '''
    normalized = name.lower().strip()
    for pattern, key in PROGRAM_MAP.items():
        if normalized == pattern or normalized.startswith(pattern):
            return key
    return None


def _extract_reference_period(full_text: str, program_name: str) -> str:
    '''
    Extract the reference period from the release cell text.

    The cell text is typically:
      "Employment Situation for December 2023"
      "County Employment and Wages for 3rd Quarter 2016"

    We extract everything after "for " that follows the program name.
    '''
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    idx = full_text.find(program_name)
    if idx == -1:
        return ''

    after_name = full_text[idx + len(program_name) :]

    match = re.match(r'\s+for\s+(.+)', after_name, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return after_name.strip()


def _parse_reference_period_date(reference_period: str, source: str | None = None) -> date | None:
    '''
    Parse a schedule reference period into a date with day fixed to 12.

    Supported formats include:
      - "December 2023"
      - "3rd Quarter 2016"
      - "Q3 2016"

    Quarter handling:
      - For qcew, quarter maps to quarter-end month (Q1->Mar, Q2->Jun, Q3->Sep, Q4->Dec)
      - For other sources, quarter maps to first month of quarter
    '''
    normalized = re.sub(r'\s+', ' ', reference_period).strip()
    if not normalized:
        return None

    month_year = re.fullmatch(r'([A-Za-z]+)\s+(\d{4})', normalized)
    if month_year:
        month = _MONTH_MAP.get(month_year.group(1).lower())
        if month is None:
            return None
        return date(int(month_year.group(2)), month, 12)

    quarter_year = re.fullmatch(
        r'([1-4])(?:st|nd|rd|th)?\s+quarter\s+(\d{4})',
        normalized,
        flags=re.IGNORECASE,
    )
    if quarter_year:
        quarter = int(quarter_year.group(1))
        year = int(quarter_year.group(2))
        if source == 'qcew':
            month = quarter * 3
        else:
            month = (quarter - 1) * 3 + 1
        return date(year, month, 12)

    quarter_word = re.fullmatch(
        r'(first|second|third|fourth)\s+quarter\s+(\d{4})',
        normalized,
        flags=re.IGNORECASE,
    )
    if quarter_word:
        quarter = _QUARTER_WORD_MAP[quarter_word.group(1).lower()]
        year = int(quarter_word.group(2))
        if source == 'qcew':
            month = quarter * 3
        else:
            month = (quarter - 1) * 3 + 1
        return date(year, month, 12)

    quarter_short = re.fullmatch(r'Q([1-4])\s+(\d{4})', normalized, flags=re.IGNORECASE)
    if quarter_short:
        quarter = int(quarter_short.group(1))
        year = int(quarter_short.group(2))
        if source == 'qcew':
            month = quarter * 3
        else:
            month = (quarter - 1) * 3 + 1
        return date(year, month, 12)

    return None


_MONTH_MAP = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}

_QUARTER_WORD_MAP = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
}

_DATE_RE = re.compile(
    r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s+'
    r'([a-z]+)\s+(\d{1,2}),?\s+(\d{4})',
    re.IGNORECASE,
)


def _parse_schedule_date(text: str) -> date | None:
    '''
    Parse a BLS schedule date like "Friday, January 05, 2024".
    '''
    match = _DATE_RE.search(text)
    if not match:
        return None

    month_str = match.group(1).lower()
    day = int(match.group(2))
    year = int(match.group(3))

    month = _MONTH_MAP.get(month_str)
    if month is None:
        return None

    try:
        return date(year, month, day)
    except ValueError:
        return None

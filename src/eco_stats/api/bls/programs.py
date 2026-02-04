"""
BLS LABSTAT program registry.

Each BLS program (survey) is identified by a two-letter prefix and has a
well-defined series ID format documented at:
  https://www.bls.gov/help/hlpforma.htm
  https://download.bls.gov/pub/time.series/overview.txt

This module encodes those formats as structured data so that series IDs
can be built, parsed, and validated programmatically.
"""

from typing import Dict, List, Optional


class SeriesField:
    """
    A single positional field within a BLS series ID.

    Positions are 1-indexed to match the official BLS documentation
    (e.g., ``xx.txt`` files and the Series ID Formats page).

    Args:
        name: Machine-readable field name (e.g., ``"seasonal"``).
        start: Start position, 1-indexed inclusive.
        end: End position, 1-indexed inclusive.
        description: Human-readable description of the field.
    """

    def __init__(
        self,
        name: str,
        start: int,
        end: int,
        description: str = "",
    ) -> None:
        self.name = name
        self.start = start
        self.end = end
        self.description = description

    @property
    def length(self) -> int:
        """Number of characters this field occupies."""
        return self.end - self.start + 1

    def extract(self, series_id: str) -> str:
        """Extract this field's value from a full series ID string."""
        return series_id[self.start - 1 : self.end]  # noqa: E203

    def __repr__(self) -> str:
        return (
            f"SeriesField({self.name!r}, {self.start}, {self.end}, "
            f"{self.description!r})"
        )


class BLSProgram:
    """
    Metadata for a single BLS LABSTAT program (survey).

    Attributes:
        prefix: Two-letter program identifier (e.g., ``"CE"``).
        name: Full program name.
        description: Brief description of the survey.
        fields: Ordered list of :class:`SeriesField` definitions that
            make up the series ID format for this program.
        mapping_files: Names of available mapping/lookup files
            (e.g., ``["area", "industry", "datatype"]``).  These
            correspond to flat files at
            ``download.bls.gov/pub/time.series/{prefix}/{prefix}.{name}``.
    """

    def __init__(
        self,
        prefix: str,
        name: str,
        description: str,
        fields: List[SeriesField],
        mapping_files: Optional[List[str]] = None,
    ) -> None:
        self.prefix = prefix.upper()
        self.name = name
        self.description = description
        self.fields = fields
        self.mapping_files = mapping_files or []

    @property
    def series_id_length(self) -> int:
        """Expected total length of a series ID for this program."""
        if not self.fields:
            return 0
        return max(f.end for f in self.fields)

    def field_names(self) -> List[str]:
        """Return the ordered list of field names."""
        return [f.name for f in self.fields]

    def get_field(self, name: str) -> Optional[SeriesField]:
        """Look up a field by name, or return ``None``."""
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def __repr__(self) -> str:
        return f"BLSProgram({self.prefix!r}, {self.name!r})"


# ---------------------------------------------------------------------------
# Program registry
#
# Sources:
#   - https://www.bls.gov/help/hlpforma.htm
#   - Individual xx.txt files at download.bls.gov/pub/time.series/xx/
# ---------------------------------------------------------------------------

PROGRAMS: Dict[str, BLSProgram] = {}


def _register(program: BLSProgram) -> BLSProgram:
    """Add a program to the global registry and return it."""
    PROGRAMS[program.prefix] = program
    return program


# ── CE: Current Employment Statistics (National) ──────────────────────────
_register(
    BLSProgram(
        prefix="CE",
        name="Current Employment Statistics (National)",
        description=(
            "Monthly estimates of employment, hours, and earnings from "
            "the payroll survey (NAICS basis)."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (CE)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("supersector", 4, 5, "Supersector code"),
            SeriesField("industry", 6, 11, "Industry code"),
            SeriesField("data_type", 12, 13, "Data type code"),
        ],
        mapping_files=[
            "datatype",
            "industry",
            "seasonal",
            "series",
            "supersector",
        ],
    )
)

# ── CU: Consumer Price Index – All Urban Consumers (CPI-U) ───────────────
_register(
    BLSProgram(
        prefix="CU",
        name="Consumer Price Index - All Urban Consumers",
        description=(
            "Monthly data on changes in the prices paid by urban "
            "consumers for a representative basket of goods and services."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (CU)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("periodicity", 4, 4, "Periodicity code"),
            SeriesField("area", 5, 8, "Area code"),
            SeriesField("item", 9, 16, "Item code"),
        ],
        mapping_files=[
            "area",
            "base",
            "item",
            "periodicity",
            "seasonal",
            "series",
        ],
    )
)

# ── CW: Consumer Price Index – Urban Wage Earners (CPI-W) ────────────────
_register(
    BLSProgram(
        prefix="CW",
        name="Consumer Price Index - Urban Wage Earners and Clerical Workers",
        description=("Monthly CPI data for urban wage earners and clerical workers."),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (CW)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("periodicity", 4, 4, "Periodicity code"),
            SeriesField("area", 5, 8, "Area code"),
            SeriesField("item", 9, 16, "Item code"),
        ],
        mapping_files=[
            "area",
            "base",
            "item",
            "periodicity",
            "seasonal",
            "series",
        ],
    )
)

# ── LN: Labor Force Statistics (CPS) ─────────────────────────────────────
_register(
    BLSProgram(
        prefix="LN",
        name="Labor Force Statistics",
        description=(
            "Monthly labor force, employment, and unemployment estimates "
            "from the Current Population Survey (CPS)."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (LN)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("series_code", 4, 11, "Series classification code"),
        ],
        mapping_files=[
            "ages",
            "born",
            "class",
            "duration",
            "education",
            "ethnic",
            "indy",
            "lfst",
            "occupation",
            "origins",
            "pcts",
            "race",
            "seasonal",
            "series",
            "sexs",
        ],
    )
)

# ── LA: Local Area Unemployment Statistics ────────────────────────────────
_register(
    BLSProgram(
        prefix="LA",
        name="Local Area Unemployment Statistics",
        description=(
            "Monthly and annual labor force, employment, unemployment, "
            "and unemployment rate for states, MSAs, counties, and cities."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (LA)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("area_type", 4, 4, "Area type code"),
            SeriesField("state_fips", 5, 6, "State FIPS code"),
            SeriesField("area", 7, 11, "Area code"),
            SeriesField("measure", 12, 13, "Measure code"),
        ],
        mapping_files=[
            "area",
            "area_type",
            "measure",
            "seasonal",
            "series",
            "state_region_division",
        ],
    )
)

# ── SM: State and Metro Area Employment, Hours, and Earnings (NAICS) ─────
_register(
    BLSProgram(
        prefix="SM",
        name="State and Area Employment, Hours, and Earnings",
        description=(
            "Monthly estimates of employment, hours, and earnings for "
            "states and metropolitan areas (NAICS basis)."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (SM)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("state", 4, 5, "State code"),
            SeriesField("area", 6, 10, "Area code"),
            SeriesField("supersector_industry", 11, 18, "Supersector/industry code"),
            SeriesField("data_type", 19, 20, "Data type code"),
        ],
        mapping_files=[
            "area",
            "datatype",
            "industry",
            "seasonal",
            "series",
            "state",
            "supersector",
        ],
    )
)

# ── JT: Job Openings and Labor Turnover Survey (JOLTS) ───────────────────
_register(
    BLSProgram(
        prefix="JT",
        name="Job Openings and Labor Turnover Survey",
        description=(
            "Monthly data on job openings, hires, and separations "
            "by industry and region."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (JT)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("industry", 4, 9, "Industry code"),
            SeriesField("state", 10, 11, "State code"),
            SeriesField("area", 12, 16, "Area code"),
            SeriesField("sizeclass", 17, 18, "Size class code"),
            SeriesField("dataelement", 19, 20, "Data element code"),
            SeriesField("ratelevel", 21, 21, "Rate or level code"),
        ],
        mapping_files=[
            "area",
            "dataelement",
            "industry",
            "ratelevel",
            "seasonal",
            "series",
            "sizeclass",
            "state",
        ],
    )
)

# ── AP: Average Price Data ────────────────────────────────────────────────
_register(
    BLSProgram(
        prefix="AP",
        name="Average Price Data",
        description=(
            "Monthly average retail prices for selected food, energy, "
            "and other items."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (AP)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("area", 4, 7, "Area code"),
            SeriesField("item", 8, 13, "Item code"),
        ],
        mapping_files=[
            "area",
            "item",
            "seasonal",
            "series",
        ],
    )
)

# ── WP: Producer Price Index (Commodities) ────────────────────────────────
_register(
    BLSProgram(
        prefix="WP",
        name="Producer Price Index - Commodities",
        description=(
            "Monthly producer price changes for commodities, "
            "organized by SIC and commodity groupings."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (WP)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("group", 4, 5, "Group code"),
            SeriesField("item", 6, 14, "Item code"),
        ],
        mapping_files=[
            "group",
            "item",
            "seasonal",
            "series",
        ],
    )
)

# ── PC: Producer Price Index (Industry Data) ──────────────────────────────
_register(
    BLSProgram(
        prefix="PC",
        name="Producer Price Index - Industry Data",
        description=("Monthly producer price index data by NAICS industry."),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (PC)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("industry", 4, 9, "Industry code"),
            SeriesField("product", 10, 21, "Product code"),
        ],
        mapping_files=[
            "industry",
            "product",
            "seasonal",
            "series",
        ],
    )
)

# ── CI: Employment Cost Index ─────────────────────────────────────────────
_register(
    BLSProgram(
        prefix="CI",
        name="Employment Cost Index",
        description=(
            "Quarterly changes in employer costs for employee "
            "compensation (wages, salaries, and benefits)."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (CI)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("ownership", 4, 4, "Ownership code"),
            SeriesField("compensation", 5, 6, "Compensation component code"),
            SeriesField("industry", 7, 10, "Industry code"),
            SeriesField("occupation", 11, 13, "Occupation code"),
            SeriesField("subcell", 14, 16, "Subcell code"),
            SeriesField("periodicity", 17, 17, "Periodicity code"),
        ],
        mapping_files=[
            "compensation",
            "industry",
            "occupation",
            "ownership",
            "periodicity",
            "seasonal",
            "series",
            "subcell",
        ],
    )
)

# ── BD: Business Employment Dynamics ──────────────────────────────────────
_register(
    BLSProgram(
        prefix="BD",
        name="Business Employment Dynamics",
        description=(
            "Quarterly data on gross job gains and losses, "
            "establishment births and deaths."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (BD)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("state_fips", 4, 5, "State FIPS code"),
            SeriesField("msa", 6, 10, "MSA code"),
            SeriesField("industry", 11, 16, "Industry code"),
            SeriesField("data_element", 17, 18, "Data element code"),
            SeriesField("sizeclass", 19, 19, "Size class code"),
            SeriesField("data_class", 20, 20, "Data class code"),
            SeriesField("ratelevel", 21, 21, "Rate or level code"),
            SeriesField("periodicity", 22, 22, "Periodicity code"),
        ],
        mapping_files=[
            "dataelement",
            "industry",
            "msa",
            "ratelevel",
            "seasonal",
            "series",
            "sizeclass",
            "state",
        ],
    )
)

# ── EN: Quarterly Census of Employment and Wages (QCEW) ──────────────────
_register(
    BLSProgram(
        prefix="EN",
        name="Quarterly Census of Employment and Wages",
        description=(
            "Quarterly employment and wages data covering nearly all "
            "employers, derived from unemployment insurance records."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (EN)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("area", 4, 8, "Area code"),
            SeriesField("data_type", 9, 9, "Data type code"),
            SeriesField("size", 10, 10, "Size code"),
            SeriesField("ownership", 11, 11, "Ownership code"),
            SeriesField("industry", 12, 17, "Industry code"),
        ],
        mapping_files=[
            "area",
            "datatype",
            "industry",
            "ownership",
            "seasonal",
            "series",
            "size",
        ],
    )
)

# ── IP: Industry Productivity ─────────────────────────────────────────────
_register(
    BLSProgram(
        prefix="IP",
        name="Industry Productivity",
        description=(
            "Annual and quarterly output, hours, and productivity "
            "measures for major U.S. industries."
        ),
        fields=[
            SeriesField("prefix", 1, 2, "Survey prefix (IP)"),
            SeriesField("seasonal", 3, 3, "Seasonal adjustment code"),
            SeriesField("sector", 4, 5, "Sector code"),
            SeriesField("industry", 6, 11, "Industry code"),
            SeriesField("measure", 12, 13, "Measure code"),
            SeriesField("duration", 14, 14, "Duration code"),
        ],
        mapping_files=[
            "duration",
            "industry",
            "measure",
            "seasonal",
            "sector",
            "series",
        ],
    )
)


def get_program(prefix: str) -> BLSProgram:
    """
    Look up a BLS program by its two-letter prefix.

    Args:
        prefix: Two-letter program code (case-insensitive).

    Returns:
        The :class:`BLSProgram` for the given prefix.

    Raises:
        KeyError: If the prefix is not in the registry.
    """
    key = prefix.upper()
    if key not in PROGRAMS:
        available = ", ".join(sorted(PROGRAMS.keys()))
        raise KeyError(
            f"Unknown BLS program prefix {key!r}. " f"Available programs: {available}"
        )
    return PROGRAMS[key]


def list_programs() -> Dict[str, str]:
    """
    Return a mapping of all registered program prefixes to their names.

    Returns:
        Dictionary of ``{prefix: program_name}``.
    """
    return {p.prefix: p.name for p in PROGRAMS.values()}

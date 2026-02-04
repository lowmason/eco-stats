"""
Tests for the refactored BLS client package.

Covers:
  - Program registry (programs.py)
  - Series ID builder/parser (series_id.py)
  - Flat file parser (flat_files.py, parsing only — no network)
  - BLSClient initialization and backward compatibility
"""

import pytest


# ======================================================================
# Program registry
# ======================================================================


class TestProgramRegistry:
    """Tests for eco_stats.api.bls.programs."""

    def test_programs_dict_is_populated(self):
        from eco_stats.api.bls.programs import PROGRAMS

        assert len(PROGRAMS) > 0
        assert "CE" in PROGRAMS
        assert "CU" in PROGRAMS
        assert "LN" in PROGRAMS

    def test_list_programs_returns_all(self):
        from eco_stats.api.bls.programs import list_programs, PROGRAMS

        result = list_programs()
        assert isinstance(result, dict)
        assert len(result) == len(PROGRAMS)
        assert result["CE"] == "Current Employment Statistics (National)"

    def test_get_program_valid(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("CE")
        assert prog.prefix == "CE"
        assert prog.name == "Current Employment Statistics (National)"
        assert len(prog.fields) > 0

    def test_get_program_case_insensitive(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("ce")
        assert prog.prefix == "CE"

    def test_get_program_unknown_raises(self):
        from eco_stats.api.bls.programs import get_program

        with pytest.raises(KeyError, match="Unknown BLS program prefix"):
            get_program("ZZ")

    def test_program_field_names(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("CE")
        names = prog.field_names()
        assert "prefix" in names
        assert "seasonal" in names
        assert "data_type" in names

    def test_program_series_id_length(self):
        from eco_stats.api.bls.programs import get_program

        ce = get_program("CE")
        assert ce.series_id_length == 13  # CE series IDs are 13 chars

        cu = get_program("CU")
        assert cu.series_id_length == 16  # CU series IDs are up to 16

    def test_program_get_field(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("CE")
        field = prog.get_field("seasonal")
        assert field is not None
        assert field.start == 3
        assert field.end == 3
        assert field.length == 1

    def test_program_get_field_missing(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("CE")
        assert prog.get_field("nonexistent") is None

    def test_program_mapping_files(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("CU")
        assert "area" in prog.mapping_files
        assert "item" in prog.mapping_files
        assert "series" in prog.mapping_files

    def test_all_programs_have_prefix_field(self):
        from eco_stats.api.bls.programs import PROGRAMS

        for prefix, prog in PROGRAMS.items():
            assert (
                prog.get_field("prefix") is not None
            ), f"Program {prefix} missing 'prefix' field"

    def test_all_programs_have_seasonal_field(self):
        from eco_stats.api.bls.programs import PROGRAMS

        for prefix, prog in PROGRAMS.items():
            assert (
                prog.get_field("seasonal") is not None
            ), f"Program {prefix} missing 'seasonal' field"

    def test_series_field_extract(self):
        from eco_stats.api.bls.programs import SeriesField

        field = SeriesField("area", 5, 8, "Area code")
        assert field.extract("CUUR0000SA0XXXX") == "0000"

    def test_series_field_repr(self):
        from eco_stats.api.bls.programs import SeriesField

        field = SeriesField("area", 5, 8, "Area code")
        assert "area" in repr(field)

    def test_program_repr(self):
        from eco_stats.api.bls.programs import get_program

        prog = get_program("CE")
        assert "CE" in repr(prog)


# ======================================================================
# Series ID builder / parser
# ======================================================================


class TestSeriesId:
    """Tests for eco_stats.api.bls.series_id."""

    def test_parse_cpi_series(self):
        from eco_stats.api.bls.series_id import parse_series_id

        result = parse_series_id("CUUR0000SA0     ")
        assert result["program"] == "CU"
        assert result["prefix"] == "CU"
        assert result["seasonal"] == "U"
        assert result["periodicity"] == "R"
        assert result["area"] == "0000"

    def test_parse_ces_series(self):
        from eco_stats.api.bls.series_id import parse_series_id

        result = parse_series_id("CES0000000001")
        assert result["program"] == "CE"
        assert result["seasonal"] == "S"
        assert result["supersector"] == "00"
        assert result["industry"] == "000000"
        assert result["data_type"] == "01"

    def test_parse_ces_earnings_series(self):
        from eco_stats.api.bls.series_id import parse_series_id

        result = parse_series_id("CES0500000003")
        assert result["program"] == "CE"
        assert result["seasonal"] == "S"
        assert result["supersector"] == "05"
        assert result["data_type"] == "03"

    def test_parse_ln_series(self):
        from eco_stats.api.bls.series_id import parse_series_id

        result = parse_series_id("LNS14000000")
        assert result["program"] == "LN"
        assert result["seasonal"] == "S"
        assert result["series_code"] == "14000000"

    def test_parse_jolts_series(self):
        from eco_stats.api.bls.series_id import parse_series_id

        result = parse_series_id("JTU000000000000000HIL")
        assert result["program"] == "JT"
        assert result["seasonal"] == "U"
        assert result["industry"] == "000000"
        assert result["dataelement"] == "HI"
        assert result["ratelevel"] == "L"

    def test_parse_unknown_prefix_raises(self):
        from eco_stats.api.bls.series_id import parse_series_id

        with pytest.raises(KeyError):
            parse_series_id("ZZ12345")

    def test_parse_too_short_raises(self):
        from eco_stats.api.bls.series_id import parse_series_id

        with pytest.raises(ValueError, match="at least 2 characters"):
            parse_series_id("C")

    def test_parse_short_for_program_raises(self):
        from eco_stats.api.bls.series_id import parse_series_id

        with pytest.raises(ValueError, match="too short"):
            parse_series_id("CE12")  # CE needs 13 chars

    def test_build_cpi_series(self):
        from eco_stats.api.bls.series_id import build_series_id

        result = build_series_id(
            "CU",
            seasonal="U",
            periodicity="R",
            area="0000",
            item="SA0",
        )
        # Should produce CUUR0000SA000000 (padded to 16)
        assert result[:11] == "CUUR0000SA0"
        assert result.startswith("CU")

    def test_build_ces_series(self):
        from eco_stats.api.bls.series_id import build_series_id

        result = build_series_id(
            "CE",
            seasonal="S",
            supersector="00",
            industry="000000",
            data_type="01",
        )
        assert result == "CES0000000001"

    def test_build_defaults_to_zeros(self):
        from eco_stats.api.bls.series_id import build_series_id

        result = build_series_id("CE", seasonal="S")
        assert result.startswith("CES")
        assert len(result) == 13

    def test_roundtrip_ces(self):
        from eco_stats.api.bls.series_id import (
            build_series_id,
            parse_series_id,
        )

        original = "CES0000000001"
        parsed = parse_series_id(original)
        # Remove 'program' key (not a build input) and 'prefix' (auto-set)
        components = {k: v for k, v in parsed.items() if k not in ("program", "prefix")}
        rebuilt = build_series_id("CE", **components)
        assert rebuilt == original

    def test_roundtrip_ln(self):
        from eco_stats.api.bls.series_id import (
            build_series_id,
            parse_series_id,
        )

        original = "LNS14000000"
        parsed = parse_series_id(original)
        components = {k: v for k, v in parsed.items() if k not in ("program", "prefix")}
        rebuilt = build_series_id("LN", **components)
        assert rebuilt == original


# ======================================================================
# Flat file parser (unit tests — no network)
# ======================================================================


class TestFlatFileParser:
    """Test the TSV parsing logic without hitting BLS servers."""

    def test_parse_tsv_basic(self):
        from eco_stats.api.bls.flat_files import BLSFlatFileClient

        text = (
            "series_id\tyear\tperiod\tvalue\n"
            "CES0000000001\t2024\tM01\t157533\n"
            "CES0000000001\t2024\tM02\t157829\n"
        )
        rows = BLSFlatFileClient._parse_tsv(text)
        assert len(rows) == 2
        assert rows[0]["series_id"] == "CES0000000001"
        assert rows[0]["year"] == "2024"
        assert rows[0]["period"] == "M01"
        assert rows[0]["value"] == "157533"

    def test_parse_tsv_strips_whitespace(self):
        from eco_stats.api.bls.flat_files import BLSFlatFileClient

        text = "code \t name  \n" " 01 \t Alabama \n" " 02 \t Alaska  \n"
        rows = BLSFlatFileClient._parse_tsv(text)
        assert len(rows) == 2
        assert rows[0]["code"] == "01"
        assert rows[0]["name"] == "Alabama"
        assert rows[1]["code"] == "02"

    def test_parse_tsv_empty(self):
        from eco_stats.api.bls.flat_files import BLSFlatFileClient

        text = "col_a\tcol_b\n"
        rows = BLSFlatFileClient._parse_tsv(text)
        assert rows == []

    def test_parse_tsv_mapping_file(self):
        from eco_stats.api.bls.flat_files import BLSFlatFileClient

        text = (
            "area_code\tarea_name\n"
            "0000\tU.S. city average\n"
            "0100\tNortheast urban\n"
            "0200\tMidwest urban\n"
        )
        rows = BLSFlatFileClient._parse_tsv(text)
        assert len(rows) == 3
        assert rows[0]["area_code"] == "0000"
        assert rows[0]["area_name"] == "U.S. city average"

    def test_flat_file_client_context_manager(self):
        from eco_stats.api.bls.flat_files import BLSFlatFileClient

        with BLSFlatFileClient() as client:
            assert client is not None


# ======================================================================
# BLSClient integration
# ======================================================================


class TestBLSClientIntegration:
    """Test the refactored BLSClient."""

    def test_initialization_no_key(self):
        from eco_stats.api.bls import BLSClient

        client = BLSClient()
        assert client.api_key is None
        assert "v1" in client.base_url
        client.close()

    def test_initialization_with_key(self):
        from eco_stats.api.bls import BLSClient

        client = BLSClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert "v2" in client.base_url
        client.close()

    def test_context_manager(self):
        from eco_stats.api.bls import BLSClient

        with BLSClient() as client:
            assert client is not None

    def test_list_programs(self):
        from eco_stats.api.bls import BLSClient

        with BLSClient() as client:
            programs = client.list_programs()
            assert isinstance(programs, dict)
            assert "CE" in programs
            assert "CU" in programs

    def test_get_program_info(self):
        from eco_stats.api.bls import BLSClient

        with BLSClient() as client:
            info = client.get_program_info("CE")
            assert info.prefix == "CE"
            assert len(info.fields) > 0

    def test_parse_series_id_via_client(self):
        from eco_stats.api.bls import BLSClient

        with BLSClient() as client:
            result = client.parse_series_id("CES0000000001")
            assert result["program"] == "CE"
            assert result["data_type"] == "01"

    def test_build_series_id_via_client(self):
        from eco_stats.api.bls import BLSClient

        with BLSClient() as client:
            result = client.build_series_id(
                "CE",
                seasonal="S",
                supersector="00",
                industry="000000",
                data_type="01",
            )
            assert result == "CES0000000001"


# ======================================================================
# Backward compatibility
# ======================================================================


class TestBackwardCompatibility:
    """Ensure old import paths still work."""

    def test_import_from_bls_client_module(self):
        from eco_stats.api.bls_client import BLSClient

        client = BLSClient()
        assert client is not None
        client.close()

    def test_import_from_api_package(self):
        from eco_stats.api import BLSClient

        client = BLSClient()
        assert client is not None
        client.close()

    def test_import_from_eco_stats_top_level(self):
        from eco_stats import BLSClient

        client = BLSClient()
        assert client is not None
        client.close()

    def test_old_api_still_present(self):
        """All original methods must still exist."""
        from eco_stats import BLSClient

        client = BLSClient(api_key="test_key")
        assert hasattr(client, "get_series")
        assert hasattr(client, "get_unemployment_rate")
        assert hasattr(client, "get_cpi_all_items")
        assert hasattr(client, "get_employment")
        assert hasattr(client, "get_average_hourly_earnings")
        assert hasattr(client, "close")
        assert hasattr(client, "__enter__")
        assert hasattr(client, "__exit__")
        client.close()

    def test_new_methods_present(self):
        """New methods added by refactoring must exist."""
        from eco_stats import BLSClient

        client = BLSClient()
        assert hasattr(client, "list_programs")
        assert hasattr(client, "get_program_info")
        assert hasattr(client, "get_mapping")
        assert hasattr(client, "search_series")
        assert hasattr(client, "parse_series_id")
        assert hasattr(client, "build_series_id")
        assert hasattr(client, "get_bulk_data")
        client.close()

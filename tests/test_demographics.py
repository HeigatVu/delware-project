"""Tests for demographics module."""

from pathlib import Path
from delware_speech.demographics import (
    map_education_to_years,
    map_sex,
    load_delaware_demographics,
)


def test_map_education_to_years():
    assert map_education_to_years(0) == 0.0
    assert map_education_to_years(1) == 6.0
    assert map_education_to_years(2) == 9.0
    assert map_education_to_years(3) == 12.0
    assert map_education_to_years(4) == 13.0
    assert map_education_to_years(5) == 14.0
    assert map_education_to_years(6) == 14.0
    assert map_education_to_years(7) == 16.0
    assert map_education_to_years(8) == 18.0
    assert map_education_to_years(9) == 20.0
    assert map_education_to_years(10) == 21.0
    assert map_education_to_years(None) is None
    assert map_education_to_years("invalid") is None


def test_map_sex():
    assert map_sex(1) == "female"
    assert map_sex("1") == "female"
    assert map_sex("female") == "female"
    assert map_sex(2) == "male"
    assert map_sex("2") == "male"
    assert map_sex("male") == "male"


def test_load_delaware_demographics():
    excel_path = Path("/shared-data/dementiabank/Delaware/demo-test-fixed.xlsx")
    if excel_path.exists():
        df = load_delaware_demographics(excel_path)
        assert len(df) > 50
        assert "ID" in df.columns
        assert "Age" in df.columns
        assert "Sex" in df.columns
        assert "Education_Years" in df.columns
        assert "MoCA" in df.columns
        assert "Diagnosis" in df.columns

        # Check that 01-2 exists
        row_01_2 = df[df["ID"] == "01-2"]
        assert len(row_01_2) == 1
        assert row_01_2.iloc[0]["Age"] > 60

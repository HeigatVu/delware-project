"""Demographics harmonization and processing for the Delaware DementiaBank corpus.

Implements education level code to years mapping and MoCA score extraction
per Nyongesa et al. (2025).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd


EDUCATION_CODE_TO_YEARS: Dict[int, float] = {
    0: 0.0,    # No schooling completed
    1: 6.0,    # Elementary school through 8th grade
    2: 9.0,    # Some high school (no diploma)
    3: 12.0,   # High school graduate (diploma or GED)
    4: 13.0,   # Some college credit (no degree)
    5: 14.0,   # Trade/technical/vocational training
    6: 14.0,   # Associates degree
    7: 16.0,   # Bachelor's degree
    8: 18.0,   # Master's degree
    9: 20.0,   # Professional degree (JD, MD, etc.)
    10: 21.0,  # Doctorate degree (PhD, EdD, etc.)
}

CLASSIFICATION_CODE_TO_NAME: Dict[int, str] = {
    1: "Control",
    2: "MCI",
    3: "PossibleAD",
    4: "Other",
}


def map_education_to_years(code: Union[int, float, str, None]) -> Optional[float]:
    """Map categorical education level code (0-10) to approximate years of education."""
    if pd.isna(code):
        return None
    try:
        val = int(float(code))
        return EDUCATION_CODE_TO_YEARS.get(val, None)
    except (ValueError, TypeError):
        return None


def map_sex(code_or_str: Union[int, float, str, None]) -> str:
    """Standardize sex representation (1=Female, 2=Male)."""
    if pd.isna(code_or_str):
        return "unknown"
    val = str(code_or_str).strip().lower()
    if val in ("1", "1.0", "f", "female"):
        return "female"
    if val in ("2", "2.0", "m", "male"):
        return "male"
    return val


def parse_numeric(val: Union[int, float, str, None]) -> Optional[float]:
    """Parse numeric score or return None if DNC/missing."""
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def load_delaware_demographics(excel_path: Union[str, Path]) -> pd.DataFrame:
    """Load and harmonize demographics from demo-test-fixed.xlsx.

    Reads 'Control' and 'MCI' sheets, harmonizes column names, applies education
    years mapping, and extracts MoCA cognitive scores.
    """
    path = Path(excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Demographics file not found: {path}")

    sheets_to_read = ["Control", "MCI"]
    dfs = []

    for sheet in sheets_to_read:
        sheet_df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
        sheet_df["Source_Sheet"] = sheet
        dfs.append(sheet_df)

    combined = pd.concat(dfs, ignore_index=True)

    # Normalize ID column
    combined["ID"] = combined["ID"].astype(str).str.strip()

    # Extract clean columns
    clean_records = []
    for _, row in combined.iterrows():
        pid = row["ID"]
        record_id = str(row.get("RECORD ID", "")).strip()

        # Age
        age = parse_numeric(row.get("AGE AT TESTING"))

        # Sex
        sex = map_sex(row.get("SEX"))

        # Education
        edu_code = row.get("EDUCATION LEVEL CODE")
        edu_years = map_education_to_years(edu_code)

        # MoCA score
        moca_score = parse_numeric(row.get("MOCA (v 7.1) SCORE *Total score = 30*"))
        if moca_score is None:
            # Fall back to blind score if regular not available
            blind_score = parse_numeric(row.get("MoCA Blind RAW SCORE *Total score = 22* "))
            if blind_score is not None:
                # Convert 22-scale to approximate 30-scale if needed, or record as is
                moca_score = (blind_score / 22.0) * 30.0

        # Classification
        classification_raw = row.get("CLASSIFICATION")
        if pd.notna(classification_raw):
            try:
                cls_int = int(float(classification_raw))
                diag = CLASSIFICATION_CODE_TO_NAME.get(cls_int, row["Source_Sheet"])
            except (ValueError, TypeError):
                diag = str(classification_raw).strip()
        else:
            diag = row["Source_Sheet"]

        # Visit number
        visit_num = parse_numeric(row.get("Visit Number", row.get("Visit Number ")))

        clean_records.append({
            "ID": pid,
            "Record_ID": record_id,
            "Visit_Number": visit_num,
            "Age": age,
            "Sex": sex,
            "Education_Code": edu_code,
            "Education_Years": edu_years,
            "MoCA": moca_score,
            "Diagnosis": diag,
            "Source_Sheet": row["Source_Sheet"],
        })

    result_df = pd.DataFrame(clean_records)
    # Deduplicate by ID if multiple occurrences exist, taking first complete record
    result_df = result_df.drop_duplicates(subset=["ID"], keep="first").reset_index(drop=True)
    return result_df

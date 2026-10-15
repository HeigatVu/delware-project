# `demographics` — demographics harmonizer

Source: `src/delware_speech/demographics.py` (147 lines).
Replicates the demographics half of `reference_repo/speech/02_demographics_summary_processing.py`.
Unit tests: `tests/test_demographics.py`.

## What it does

Reads the Delaware demographics workbook (`demo-test-fixed.xlsx`, sheets `Control` and
`MCI`) and produces one tidy row per participant with harmonized age, sex, education in
years, MoCA score, and diagnosis — the covariates and grouping labels every later stage
needs.

## Constants

### `EDUCATION_CODE_TO_YEARS`

The paper's categorical-code → years-of-schooling table:

| Code | Years | Meaning |
|------|-------|---------|
| 0 | 0.0 | No schooling completed |
| 1 | 6.0 | Elementary through 8th grade |
| 2 | 9.0 | Some high school, no diploma |
| 3 | 12.0 | High school graduate / GED |
| 4 | 13.0 | Some college credit, no degree |
| 5 | 14.0 | Trade/technical/vocational training |
| 6 | 14.0 | Associate's degree |
| 7 | 16.0 | Bachelor's degree |
| 8 | 18.0 | Master's degree |
| 9 | 20.0 | Professional degree (JD, MD, …) |
| 10 | 21.0 | Doctorate (PhD, EdD, …) |

### `CLASSIFICATION_CODE_TO_NAME`

`1 → Control`, `2 → MCI`, `3 → PossibleAD`, `4 → Other`.

## Functions

### `map_education_to_years(code) -> Optional[float]`

Accepts int/float/str/None; `None`/NaN → `None`; unknown codes → `None`.

### `map_sex(code_or_str) -> str`

`"1"`, `"1.0"`, `"f"`, `"female"` → `"female"`; `"2"`, `"2.0"`, `"m"`, `"male"` →
`"male"`; NaN → `"unknown"`; anything else passes through lowercased.

### `parse_numeric(val) -> Optional[float]`

Float-or-None coercion used for every numeric workbook cell (age, MoCA, visit number).

### `load_delaware_demographics(excel_path) -> pd.DataFrame`

Entry point. Behavior, in order:

1. Reads sheets `Control` and `MCI` (openpyxl engine); raises `FileNotFoundError` if the
   workbook is missing.
2. Tags each row with `Source_Sheet` and strips whitespace from `ID`.
3. Per row builds: `ID`, `Record_ID` (from `RECORD ID`), `Visit_Number`, `Age`
   (`AGE AT TESTING`), `Sex`, `Education_Code` + `Education_Years`, `MoCA`, `Diagnosis`,
   `Source_Sheet`.
4. MoCA fallback: when the regular 30-point column (`MOCA (v 7.1) SCORE…`) is missing,
   the blind 22-point raw score is rescaled to the 30-point scale (`blind / 22 * 30`).
5. Diagnosis: numeric `CLASSIFICATION` codes map through
   `CLASSIFICATION_CODE_TO_NAME`; non-numeric values pass through stripped; missing
   values fall back to the sheet name.
6. Deduplicates by `ID` keeping the first record.

Output columns: `ID, Record_ID, Visit_Number, Age, Sex, Education_Code,
Education_Years, MoCA, Diagnosis, Source_Sheet`.

## Notes for reviewers

- This module is the only consumer of the workbook's raw column names; if the workbook
  layout changes, only the `row.get(...)` calls here need updating.
- Education years is what `perform_ancova` uses as a covariate — the code→years table is
  a paper design decision, not a generic conversion.

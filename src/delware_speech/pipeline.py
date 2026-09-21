"""Pipeline orchestration module for processing DementiaBank Delaware transcripts.

Coordinates reading CHAT files, demographics harmonization, linguistic feature
extraction, and participant-level aggregation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from tqdm import tqdm

from delware_speech.chat_reader import (
    CANONICAL_PICTURE_TASKS,
    parse_cha_file,
)
from delware_speech.demographics import load_delaware_demographics
from delware_speech.features import extract_linguistic_features

logger = logging.getLogger(__name__)


def map_to_canonical_task(task_name: str) -> Optional[str]:
    """Map raw CHAT task tag to canonical picture task name."""
    norm = task_name.strip().lower()
    for canonical, aliases in CANONICAL_PICTURE_TASKS.items():
        if norm in aliases:
            return canonical
    return None


def process_single_cha(
    cha_path: Union[str, Path],
    demographics_df: Optional[pd.DataFrame] = None,
) -> List[Dict[str, Union[str, float, int, None]]]:
    """Process a single .cha file and extract linguistic features for all picture tasks."""
    parsed = parse_cha_file(cha_path)
    file_id = parsed.file_id

    # Lookup demographic info
    demo_info: Dict[str, Union[str, float, int, None]] = {
        "Record_ID": file_id.split("-")[0] if "-" in file_id else file_id,
        "Visit_Number": None,
        "Age": parsed.participant_header.age,
        "Sex": parsed.participant_header.sex,
        "Education_Code": None,
        "Education_Years": None,
        "MoCA": parsed.participant_header.mmse_moca,
        "Diagnosis": parsed.participant_header.diagnosis or "Control",
    }

    if demographics_df is not None and not demographics_df.empty:
        matched = demographics_df[demographics_df["ID"] == file_id]
        if not matched.empty:
            row = matched.iloc[0]
            if pd.notna(row.get("Record_ID")):
                demo_info["Record_ID"] = str(row["Record_ID"])
            if pd.notna(row.get("Visit_Number")):
                demo_info["Visit_Number"] = row["Visit_Number"]
            if pd.notna(row.get("Age")):
                demo_info["Age"] = float(row["Age"])
            if pd.notna(row.get("Sex")):
                demo_info["Sex"] = str(row["Sex"])
            if pd.notna(row.get("Education_Code")):
                demo_info["Education_Code"] = row["Education_Code"]
            if pd.notna(row.get("Education_Years")):
                demo_info["Education_Years"] = float(row["Education_Years"])
            if pd.notna(row.get("MoCA")):
                demo_info["MoCA"] = float(row["MoCA"])
            if pd.notna(row.get("Diagnosis")):
                demo_info["Diagnosis"] = str(row["Diagnosis"])

    records: List[Dict[str, Union[str, float, int, None]]] = []
    # Collect utterances for canonical picture tasks
    for task_name, utterances in parsed.tasks.items():
        canonical = map_to_canonical_task(task_name)
        if canonical is None:
            continue

        text = " ".join(utterances).strip()
        if not text:
            continue

        feats = extract_linguistic_features(text)
        record: Dict[str, Union[str, float, int, None]] = {
            "ID": file_id,
            "Record_ID": demo_info["Record_ID"],
            "Visit_Number": demo_info["Visit_Number"],
            "Task_Raw": task_name,
            "Task": canonical,
            "Age": demo_info["Age"],
            "Sex": demo_info["Sex"],
            "Education_Code": demo_info["Education_Code"],
            "Education_Years": demo_info["Education_Years"],
            "Diagnosis": demo_info["Diagnosis"],
            "MoCA": demo_info["MoCA"],
            "Participant_Text": text,
        }
        record.update(feats)
        records.append(record)

    return records


def process_dataset(
    corpus_root: Union[str, Path],
    demographics_excel: Optional[Union[str, Path]] = None,
    show_progress: bool = True,
) -> pd.DataFrame:
    """Process all transcripts in the Delaware corpus root directory.

    Args:
        corpus_root: Root path containing transcript/ directory or .cha files.
        demographics_excel: Path to demo-test-fixed.xlsx.
        show_progress: Whether to show tqdm progress bar.
    """
    root = Path(corpus_root)
    transcript_dir = root / "transcript" if (root / "transcript").exists() else root

    cha_files = sorted(list(transcript_dir.rglob("*.cha")))
    if not cha_files:
        logger.warning(f"No .cha files found under {corpus_root}")
        return pd.DataFrame()

    demo_df = None
    if demographics_excel:
        demo_path = Path(demographics_excel)
        if demo_path.exists():
            demo_df = load_delaware_demographics(demo_path)

    all_records = []
    iterator = tqdm(cha_files, desc="Processing CHAT files") if show_progress else cha_files
    for cha_file in iterator:
        try:
            records = process_single_cha(cha_file, demo_df)
            all_records.extend(records)
        except Exception as err:
            logger.error(f"Error processing {cha_file}: {err}")

    df = pd.DataFrame(all_records)
    return df


def select_unique_participants(
    df_all: pd.DataFrame,
    priority: Tuple[str, ...] = ("Cookie", "Cat", "Rockwell"),
) -> pd.DataFrame:
    """Select one representative picture task per participant.

    Prioritizes tasks per Nyongesa et al. (2025):
    Priority: Cookie Theft > Cat Rescue > Rockwell.
    Uses Record_ID (or ID base) to identify distinct participants.
    """
    if df_all.empty:
        return df_all

    df = df_all.copy()
    task_priority = {t: i for i, t in enumerate(priority)}
    df["_priority"] = df["Task"].map(lambda x: task_priority.get(x, 999))

    # Participant identifier: use Record_ID if available, else ID base
    if "Record_ID" in df.columns and df["Record_ID"].notna().any():
        group_key = "Record_ID"
    else:
        df["_pid"] = df["ID"].astype(str).apply(lambda x: x.split("-")[0] if "-" in x else x)
        group_key = "_pid"

    # Sort so top priority and earliest visit come first
    sort_cols = [group_key, "_priority"]
    if "Visit_Number" in df.columns:
        sort_cols.append("Visit_Number")

    df_sorted = df.sort_values(by=sort_cols, ascending=True)
    df_unique = df_sorted.drop_duplicates(subset=[group_key], keep="first")

    # Clean up temporary helper columns
    drop_cols = [c for c in ["_priority", "_pid"] if c in df_unique.columns]
    df_unique = df_unique.drop(columns=drop_cols).reset_index(drop=True)
    return df_unique

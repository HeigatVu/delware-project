"""Tests for pipeline module."""

import pandas as pd
from delware_speech.pipeline import (
    map_to_canonical_task,
    process_single_cha,
    select_unique_participants,
)

SAMPLE_CHA = """@UTF8
@PID:\t11312/a-00088341-0
@Begin
@Languages:\teng
@Participants:\tINV Investigator, PAR Participant
@ID:\teng|Delaware|PAR|87;00.|female|Control||Participant|||
@G:\tCookie
*PAR:\tthe boy is taking a cookie from the jar .
@G:\tCat
*PAR:\tthe cat is stuck in a tree .
@G:\tRockwell
*PAR:\tthe family is driving in a car .
@End
"""


def test_map_to_canonical_task():
    assert map_to_canonical_task("Cookie") == "Cookie"
    assert map_to_canonical_task("cookie") == "Cookie"
    assert map_to_canonical_task("Cat") == "Cat"
    assert map_to_canonical_task("Rockwell") == "Rockwell"
    assert map_to_canonical_task("Sandwich") is None


def test_process_single_cha(tmp_path):
    cha_path = tmp_path / "01-2.cha"
    cha_path.write_text(SAMPLE_CHA, encoding="utf-8")

    demo_df = pd.DataFrame([{
        "ID": "01-2",
        "Record_ID": "01",
        "Visit_Number": 2,
        "Age": 87.0,
        "Sex": "female",
        "Education_Code": 3,
        "Education_Years": 12.0,
        "MoCA": 28.0,
        "Diagnosis": "Control",
    }])

    records = process_single_cha(cha_path, demo_df)
    assert len(records) == 3
    tasks = {r["Task"] for r in records}
    assert tasks == {"Cookie", "Cat", "Rockwell"}

    cookie_rec = [r for r in records if r["Task"] == "Cookie"][0]
    assert cookie_rec["ID"] == "01-2"
    assert cookie_rec["Education_Years"] == 12.0
    assert cookie_rec["MoCA"] == 28.0
    assert cookie_rec["word_count"] > 0
    assert "syntactic_complexity" in cookie_rec


def test_select_unique_participants():
    df = pd.DataFrame([
        {"ID": "01-1", "Record_ID": "01", "Task": "Rockwell", "Visit_Number": 1},
        {"ID": "01-2", "Record_ID": "01", "Task": "Cookie", "Visit_Number": 2},
        {"ID": "01-3", "Record_ID": "01", "Task": "Cat", "Visit_Number": 3},
        {"ID": "02-1", "Record_ID": "02", "Task": "Cat", "Visit_Number": 1},
        {"ID": "02-2", "Record_ID": "02", "Task": "Rockwell", "Visit_Number": 2},
    ])

    unique_df = select_unique_participants(df)
    assert len(unique_df) == 2

    p1 = unique_df[unique_df["Record_ID"] == "01"].iloc[0]
    # Priority Cookie > Cat > Rockwell, so Cookie must be selected
    assert p1["Task"] == "Cookie"

    p2 = unique_df[unique_df["Record_ID"] == "02"].iloc[0]
    # Priority Cat > Rockwell, so Cat must be selected
    assert p2["Task"] == "Cat"

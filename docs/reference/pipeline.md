# `pipeline` — dataset processing and orchestration

Source: `src/delware_speech/pipeline.py` (182 lines).
Replicates `reference_repo/speech/03_process_text_files.py`.
Unit tests: `tests/test_pipeline.py`.

## What it does

Coordinates `chat_reader`, `demographics`, and `features` to convert a corpus directory
into two analysis datasets: **all task records** (one row per participant × picture
task) and **unique participants** (one row per person, per the paper's task-priority
rule).

## Functions

### `map_to_canonical_task(task_name: str) -> Optional[str]`

Lowercases a raw `@G:` tag and looks it up in `CANONICAL_PICTURE_TASKS`; returns the
canonical name (`Cookie`/`Cat`/`Rockwell`) or `None` for tags that are not picture
tasks (so free conversation and introductions are excluded from extraction).

### `process_single_cha(cha_path, demographics_df=None) -> List[Dict]`

One transcript → zero or more records (one per canonical picture task with non-empty
text). Each record carries:

- Identity: `ID` (file stem), `Record_ID` (workbook value, else the ID prefix before
  `-`), `Visit_Number`, `Task_Raw`, `Task`.
- Demographics: `Age`, `Sex`, `Education_Code`, `Education_Years`, `Diagnosis`, `MoCA`
  — workbook values when the participant's `ID` matches a demographics row, otherwise
  the transcript `@ID:` header values (`Diagnosis` defaults to `"Control"`).
- `Participant_Text` — the exact joined utterances the features were computed from,
  kept so any number can be traced back to its source text.
- All feature keys from `extract_linguistic_features`.

### `process_dataset(corpus_root, demographics_excel=None, show_progress=True) -> pd.DataFrame`

Batch entry point:

1. Resolves the transcript directory: `corpus_root/transcript` if it exists, else the
   root itself; recursively globs `*.cha` (sorted).
2. Loads demographics via `load_delaware_demographics` when a workbook path is given
   and exists (a missing workbook is skipped silently, not fatal).
3. Processes each file with `process_single_cha`; exceptions are logged with the file
   path and the file is skipped — one broken transcript never kills the batch.
4. Returns all records as a DataFrame (empty DataFrame with a logged warning when no
   `.cha` files were found).

### `select_unique_participants(df_all, priority=("Cookie", "Cat", "Rockwell")) -> pd.DataFrame`

Implements the paper's unique-participant dataset:

1. Maps each task to its priority rank (Cookie = 0, Cat = 1, Rockwell = 2, other = 999).
2. Groups by `Record_ID` when available, else by the `ID` prefix before `-`.
3. Sorts by group key, priority, then `Visit_Number`, and keeps the first row per group
   — i.e. a participant's Cookie Theft record beats their Cat Rescue record, and the
   earliest visit wins within a task.
4. Drops the helper columns and resets the index.

## Notes for reviewers

- The all/unique pair written by `main.py` (`output/processed-data/processed_features_all.csv`,
  `output/processed-data/processed_features_unique.csv`) comes directly from these two functions; the
  statistics stages in the paper run on the unique dataset, the task radar on the all
  dataset.
- Demographics matching is by exact `ID` equality between the file stem and the
  workbook `ID` column — not by `Record_ID` — which is why workbook rows keep the
  participant ID format of the transcripts.

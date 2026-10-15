# `chat_reader` — CHAT transcript parser

Source: `src/delware_speech/chat_reader.py` (170 lines).
Replicates the transcript-reading half of `reference_repo/speech/01_convert_cha_to_txt.py`.
Unit tests: `tests/test_chat_reader.py`.

## What it does

Reads a DementiaBank CHAT (`.cha`) file and returns the participant's cleaned speech,
organized by picture-description task, plus the participant metadata on the `@ID:` line.
Investigator utterances (`*INV:`) are ignored; only `*PAR:` lines are kept.

## Data classes

### `ParticipantHeader`

| Field | Type | Meaning |
|-------|------|---------|
| `pid` | `str` | Participant ID (from `@ID:` code field, else the file stem) |
| `corpus` | `str` | Corpus name from the `@ID:` line |
| `age` | `Optional[float]` | Age in years (parsed from CHAT `YY;MM` format) |
| `sex` | `str` | Lowercased sex from the header |
| `diagnosis` | `str` | Group field from the `@ID:` line |
| `mmse_moca` | `Optional[float]` | Cognitive score if present in the education/score field |
| `raw_header` | `str` | The raw `@ID:` line, kept for auditing |

### `ParsedTranscript`

| Field | Type | Meaning |
|-------|------|---------|
| `file_id` | `str` | File stem, used as the participant ID downstream |
| `file_path` | `str` | Source path |
| `participant_header` | `ParticipantHeader` | Metadata above |
| `tasks` | `Dict[str, List[str]]` | Task name → cleaned participant utterances |

Methods:

- `get_task_text(task_name) -> str` — utterances of one task joined with spaces.
- `get_all_picture_tasks() -> Dict[str, str]` — combined text for every canonical
  picture task present in the transcript.

## Constants

### `CANONICAL_PICTURE_TASKS`

Maps the three canonical task names to the CHAT `@G:` labels found in the Delaware
corpus:

| Canonical | Aliases accepted |
|-----------|------------------|
| `Cookie` | `cookie`, `cookies`, `cookie_theft`, `cookie_incomplete` |
| `Cat` | `cat`, `cat_rescue` |
| `Rockwell` | `rockwell`, `coming_and_going`, `coming and going`, `rackwell`, `rockwell_intro` |

The misspelling `rackwell` is real corpus data, preserved deliberately.

## Functions

### `clean_chat_utterance(text: str) -> str`

Removes CHAT annotation layers while keeping spoken words and natural disfluencies
(*uh*, *um* — disfluency rate is a study feature, so they are **not** noise here).
Stripped: alignment timestamps (`22301_28488`), bracketed codes (`[//]`, `[/]`,
`[+ exc]`, `[=! laughs]`, `[*]`), phonological/fragment codes (`&~…`, `&+…`),
postcode markup (`@q`, `@s`), linked symbols (`+…`, `+/.`, `+/?)`), pause symbols
(`#`), and the remaining special characters `_ % * < >`. Whitespace is collapsed.
Filled-pause codes `&-uh` / `&-um` keep their word (the `&-` marker is dropped). Known issue:
`(.)` pause markers, `xxx` tokens and parenthesised completions like `(be)cause` are not removed.

### `parse_age(age_str: str) -> Optional[float]`

`"87;00."` → `87.0`, `"72;05"` → `72.0 + 5/12`. Returns `None` on empty/unparseable
input.

### `parse_participant_header(cha_content: str, fallback_id: str) -> ParticipantHeader`

Scans lines for the participant `@ID:` entry (containing `|PAR|` or ending
`|Participant|||`), splits the pipe-delimited fields
(`lang | corpus | code | age | sex | group | SES | role | education | test`), and fills
the header fields that are present. `fallback_id` becomes `pid` when the code field is
empty or `PAR`.

### `parse_cha_file(file_path: str | Path) -> ParsedTranscript`

Entry point. Reads the file (UTF-8, errors replaced), unfolds continuation lines (lines
starting with a tab or three spaces are appended to the previous line), then walks the
lines: a `@G:` tag switches the current task (default `"Default"`); a `*PAR:` line is
cleaned by `clean_chat_utterance` and appended to the current task. Empty utterances are
dropped.

## Notes for reviewers

- The parser never raises on malformed lines; the worst case is a task with fewer
  utterances than a human would count.
- `mmse_moca` is read from header position 8 (the education/score column), which is
  where some Delaware files carry it; the demographics workbook overrides it downstream
  when a row exists for the participant.

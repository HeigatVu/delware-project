"""CHAT (.cha) file parser for DementiaBank TalkBank transcripts.

Extracts participant utterances (*PAR:) for specific picture description tasks
(e.g., Cookie Theft, Cat Rescue, Coming & Going / Rockwell) while removing
investigator speech (*INV:) and CHAT transcription annotation codes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ParticipantHeader:
    """Metadata extracted from @ID: line for the participant."""

    pid: str
    corpus: str = ""
    age: Optional[float] = None
    sex: str = ""
    diagnosis: str = ""
    mmse_moca: Optional[float] = None
    raw_header: str = ""


@dataclass
class ParsedTranscript:
    """Structured transcript data extracted from a .cha file."""

    file_id: str
    file_path: str
    participant_header: ParticipantHeader
    tasks: Dict[str, List[str]] = field(default_factory=dict)

    def get_task_text(self, task_name: str) -> str:
        """Return combined participant utterances for a specific task."""
        utterances = self.tasks.get(task_name, [])
        return " ".join(utterances).strip()

    def get_all_picture_tasks(self) -> Dict[str, str]:
        """Return combined text for standardized picture description tasks."""
        out = {}
        for canonical, aliases in CANONICAL_PICTURE_TASKS.items():
            combined = []
            for name, utts in self.tasks.items():
                if name.lower() in aliases:
                    combined.extend(utts)
            if combined:
                out[canonical] = " ".join(combined).strip()
        return out


CANONICAL_PICTURE_TASKS = {
    "Cookie": {"cookie", "cookies", "cookie_theft", "cookie_incomplete"},
    "Cat": {"cat", "cat_rescue"},
    "Rockwell": {"rockwell", "coming_and_going", "coming and going", "rackwell", "rockwell_intro"},
}


def clean_chat_utterance(text: str) -> str:
    """Clean CHAT annotations and retain spoken participant words.

    Removes timestamps, phonetic codes, retracing/repetition markers,
    nonverbal cues, and punctuation markup while retaining words and natural
    disfluencies (uh, um, etc.).
    """
    # Remove timestamps like 22301_28488
    text = re.sub(r"\d+_\d+", "", text)

    # Remove CHAT bracket annotations like [//], [/], [+ exc], [=! laughs], [* ...]
    text = re.sub(r"\[.*?\]", "", text)

    # Remove phonological / fragment codes like &~something, &*PAR:okay, &+something
    text = re.sub(r"&\S+", "", text)

    # Remove CHAT meta quotes like okay@q, word@s
    text = re.sub(r"@\w+", "", text)

    # Remove special CHAT symbols like +..., +/., +/?, +,, ++, # (pauses), _
    text = re.sub(r"\+[.?!,]+", "", text)
    text = re.sub(r"[#_%*<>]", " ", text)

    # Remove orphan punctuation or noise
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_age(age_str: str) -> Optional[float]:
    """Parse age string like '87;00.' or '72;05' to float years."""
    if not age_str:
        return None
    match = re.match(r"(\d+)(?:;(\d+))?", age_str.strip())
    if not match:
        return None
    years = float(match.group(1))
    months = float(match.group(2)) if match.group(2) else 0.0
    return years + (months / 12.0)


def parse_participant_header(cha_content: str, fallback_id: str) -> ParticipantHeader:
    """Extract participant metadata from @ID: line."""
    header = ParticipantHeader(pid=fallback_id)
    for line in cha_content.splitlines():
        if line.startswith("@ID:") and ("|PAR|" in line or line.endswith("|Participant|||")):
            header.raw_header = line
            parts = [p.strip() for p in line[len("@ID:"):].strip().split("|")]
            # Format: lang|corpus|code|age|sex|group|ses|role|education|test|
            if len(parts) > 1 and parts[1]:
                header.corpus = parts[1]
            if len(parts) > 2 and parts[2] and parts[2] != "PAR":
                header.pid = parts[2]
            if len(parts) > 3 and parts[3]:
                header.age = parse_age(parts[3])
            if len(parts) > 4 and parts[4]:
                header.sex = parts[4].lower()
            if len(parts) > 5 and parts[5]:
                header.diagnosis = parts[5]
            if len(parts) > 8 and parts[8]:
                try:
                    header.mmse_moca = float(parts[8])
                except ValueError:
                    pass
            break
    return header


def parse_cha_file(file_path: str | Path) -> ParsedTranscript:
    """Parse a single .cha file into structured participant speech by task."""
    path = Path(file_path)
    file_id = path.stem

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    participant_header = parse_participant_header(content, file_id)

    # Split lines and unfold continuation lines (lines starting with tab or spaces)
    raw_lines = content.splitlines()
    unfolded_lines: List[str] = []
    for line in raw_lines:
        if line.startswith(("\t", "   ")) and unfolded_lines:
            unfolded_lines[-1] += " " + line.strip()
        else:
            unfolded_lines.append(line)

    tasks: Dict[str, List[str]] = {}
    current_task = "Default"

    for line in unfolded_lines:
        line_str = line.strip()
        if line_str.startswith("@G:"):
            task_name = line_str[len("@G:"):].strip()
            current_task = task_name
            if current_task not in tasks:
                tasks[current_task] = []
        elif line_str.startswith("*PAR:"):
            speech = line_str[len("*PAR:"):].strip()
            cleaned = clean_chat_utterance(speech)
            if cleaned:
                tasks.setdefault(current_task, []).append(cleaned)

    return ParsedTranscript(
        file_id=file_id,
        file_path=str(path),
        participant_header=participant_header,
        tasks=tasks,
    )

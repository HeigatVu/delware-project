"""Validate the code-tour files: schema, coverage, and anchor integrity.

The Code Tour VS Code extension (``vsls-contrib.codetour``) opens JSON tour files
from the repo-root ``.tours`` directory. These tests keep every step's file/line
anchor honest, so a tour cannot silently drift when the annotated code moves.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOURS_DIR = REPO_ROOT / ".tours"

# Every file the tours must walk a reader through: the CLI entry point and all
# eight pipeline modules.
EXPECTED_COVERAGE = {
    "main.py",
    "src/delware_speech/chat_reader.py",
    "src/delware_speech/clustering.py",
    "src/delware_speech/demographics.py",
    "src/delware_speech/features.py",
    "src/delware_speech/importance.py",
    "src/delware_speech/pipeline.py",
    "src/delware_speech/statistical_analysis.py",
    "src/delware_speech/visualization.py",
}


def load_tours():
    """Return (filename, parsed tour) pairs for every .tour file, sorted by name."""
    tours = []
    for path in sorted(TOURS_DIR.glob("*.tour")):
        with open(path, "r", encoding="utf-8") as fh:
            tours.append((path.name, json.load(fh)))
    return tours


def test_tours_directory_has_tour_files():
    tours = load_tours()
    assert len(tours) >= 6, f"expected tour files in .tours/, found {len(tours)}"


def test_tour_schema():
    for name, tour in load_tours():
        assert isinstance(tour.get("title"), str) and tour["title"].strip(), f"{name}: missing title"
        steps = tour.get("steps")
        assert isinstance(steps, list) and steps, f"{name}: missing steps"
        for i, step in enumerate(steps):
            where = f"{name} step {i} ({step.get('title', '?')})"
            assert isinstance(step.get("description"), str) and step["description"].strip(), (
                f"{where}: missing description"
            )
            assert isinstance(step.get("file"), str) and step["file"], f"{where}: missing file"
            assert isinstance(step.get("line"), int) and step["line"] >= 1, f"{where}: bad line"
            assert step.get("title"), f"{where}: missing step title"


def test_step_anchors_resolve():
    for name, tour in load_tours():
        for i, step in enumerate(tour["steps"]):
            where = f"{name} step {i} ({step.get('title', '?')})"
            target = REPO_ROOT / step["file"]
            assert target.is_file(), f"{where}: {step['file']} does not exist"
            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            assert step["line"] <= len(lines), (
                f"{where}: line {step['line']} beyond end of {step['file']} ({len(lines)} lines)"
            )
            assert lines[step["line"] - 1].strip(), (
                f"{where}: line {step['line']} of {step['file']} is blank"
            )


def test_tours_cover_entry_point_and_all_modules():
    covered = set()
    for _, tour in load_tours():
        covered.update(step["file"] for step in tour["steps"])
    missing = EXPECTED_COVERAGE - covered
    assert not missing, f"tours do not cover: {sorted(missing)}"


def test_one_primary_tour_and_next_tour_chain_visits_all():
    tours = load_tours()
    by_title = {tour["title"]: (name, tour) for name, tour in tours}
    primaries = [name for name, tour in tours if tour.get("isPrimary")]
    assert len(primaries) == 1, f"exactly one tour must be isPrimary, found: {primaries}"

    visited, current = [], tours[0][1]["title"]
    assert tours[0][0] == primaries[0], "the primary tour should be the first file"
    while current is not None:
        assert current in by_title, f"nextTour points at unknown tour: {current!r}"
        name, tour = by_title[current]
        assert name not in visited, f"nextTour chain revisits {name}"
        visited.append(name)
        current = tour.get("nextTour")
    unchained = [name for name, _ in tours if name not in visited]
    assert not unchained, f"tours unreachable from the primary tour: {unchained}"

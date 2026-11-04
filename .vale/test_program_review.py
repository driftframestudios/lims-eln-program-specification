"""Exercise independent Program rule selection with the real advisory engine."""

from pathlib import Path
from shutil import copytree

import pytest

from qualify import qualify
from qualify_program import OVERLAP, ROOT


@pytest.mark.parametrize(
    ("retired", "expected"),
    [
        ("CountToConclusion", [(1, "ProgramReview.ContextualWording", "suggestion")]),
        ("ContextualWording", [(1, "ProgramReview.CountToConclusion", "suggestion")]),
    ],
    ids=["wording-only", "count-only"],
)
def test_retiring_one_suggestion_keeps_the_other(
    tmp_path: Path, retired: str, expected: list[tuple[int, str, str]]
) -> None:
    profile = ROOT / ".vale" / "program.ini"
    copytree(profile.parent / "styles", tmp_path / "styles")
    settings = profile.read_text(encoding="utf-8")
    enabled = f"ProgramReview.{retired} = YES"
    assert settings.count(enabled) == 1
    config = tmp_path / "program.ini"
    config.write_text(
        settings.replace(enabled, f"ProgramReview.{retired} = NO"), encoding="utf-8"
    )
    qualify(config, {"retained-cue.md": (OVERLAP, expected)})

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import pages_projection
from scripts import validate_program


ROOT = Path(__file__).resolve().parents[1]


class CollaborationWorkbenchTests(unittest.TestCase):
    def copy_workbench(self, destination: Path) -> Path:
        for orientation_path in ("AGENTS.md", "README.md"):
            shutil.copy2(ROOT / orientation_path, destination / orientation_path)
        for slug in validate_program.COLLABORATION_SKILL_CONTRACTS:
            relative_path = Path(".agents") / "skills" / slug / "SKILL.md"
            target = destination / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative_path, target)
        return destination

    def test_complete_workbench_is_exact_and_publishable(self) -> None:
        summary = validate_program.validate_collaboration_workbench(
            ROOT, pages_projection.discover_public_skills(ROOT)
        )
        self.assertEqual(
            {
                "published_skills": 3,
                "public_possible_skills": 3,
                "public_ready_skills": 3,
            },
            summary,
        )

    def test_upstream_lineage_mutation_is_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_workbench(Path(temporary))
            skill_path = (
                source
                / ".agents"
                / "skills"
                / "repository-reentry"
                / "SKILL.md"
            )
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace(
                    "c60bb1bac3a993c78d94b1d05aaa7a97761b99275fc9acdc8285acba6f688f02",
                    "0" * 64,
                ),
                encoding="utf-8",
            )
            public_skills = pages_projection.discover_public_skills(source)
            with self.assertRaisesRegex(ValueError, "metadata or lineage differs"):
                validate_program.validate_collaboration_workbench(
                    source, public_skills
                )

    def test_yaml_comment_or_control_cannot_supply_a_description(self) -> None:
        invalid_descriptions = (
            "description: # one two three four five six seven eight",
            "description: \tA portable description with eight ordinary words after it",
            "description: A portable\tdescription with eight ordinary words after it",
        )
        for invalid_description in invalid_descriptions:
            with self.subTest(value=invalid_description):
                with tempfile.TemporaryDirectory() as temporary:
                    source = self.copy_workbench(Path(temporary))
                    skill_path = (
                        source
                        / ".agents"
                        / "skills"
                        / "contextual-jargon-scan"
                        / "SKILL.md"
                    )
                    source_text = skill_path.read_text(encoding="utf-8")
                    description = next(
                        line
                        for line in source_text.splitlines()
                        if line.startswith("description:")
                    )
                    skill_path.write_text(
                        source_text.replace(description, invalid_description, 1),
                        encoding="utf-8",
                    )
                    with self.assertRaises(pages_projection.ProjectionError):
                        pages_projection.discover_public_skills(source)


if __name__ == "__main__":
    unittest.main()

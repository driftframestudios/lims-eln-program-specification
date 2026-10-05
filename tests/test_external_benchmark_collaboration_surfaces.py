from __future__ import annotations

from pathlib import Path
import re
import unittest

from scripts import pages_projection


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_DIRECTORY = ROOT / ".agents" / "runbooks"
SKILL_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "external-benchmark-reception"
    / "SKILL.md"
)
RUNBOOKS = (
    "external-benchmark-intake.v0.1.md",
    "administrative-context-contract-evolution.v0.1.md",
    "constellation-contract-release-handoff.v0.1.md",
)
PRIVATE_LOCATOR_PATTERNS = (
    "notion.so/",
    "notion.site/",
    "app.notion.com/",
    "/users/",
    "/private/",
)


def scalar_front_matter(source: str) -> dict[str, str]:
    """Read the runbook's deliberately scalar metadata profile."""

    lines = source.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("front matter opening is absent")
    try:
        closing = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("front matter closing is absent") from error
    values: dict[str, str] = {}
    for line in lines[1:closing]:
        key, separator, value = line.partition(":")
        if not separator or not key or not value.strip():
            raise ValueError(f"front matter line is not a scalar pair: {line!r}")
        values[key] = value.strip()
    return values


class ExternalBenchmarkCollaborationSurfaceTests(unittest.TestCase):
    def test_skill_has_portable_metadata_and_stays_out_of_ready_catalog(self) -> None:
        source = SKILL_PATH.read_text(encoding="utf-8")
        relative_path = SKILL_PATH.relative_to(ROOT).as_posix()
        front_matter = pages_projection.parse_skill_front_matter(
            source, relative_path
        )
        self.assertIsNotNone(front_matter)
        assert front_matter is not None
        self.assertEqual("external-benchmark-reception", front_matter["name"])
        self.assertEqual(
            {
                "source_band": "public_possible",
                "skill_version": "0.1.0",
                "adaptation_relation": "repository_local_original",
            },
            pages_projection.skill_package_metadata(front_matter, relative_path),
        )
        self.assertNotIn(
            "external-benchmark-reception",
            {skill.slug for skill in pages_projection.discover_public_skills(ROOT)},
        )

    def test_index_leads_to_each_declared_runbook(self) -> None:
        index = (RUNBOOK_DIRECTORY / "README.md").read_text(encoding="utf-8")
        for filename in RUNBOOKS:
            with self.subTest(filename=filename):
                self.assertIn(f"]({filename})", index)
                self.assertTrue((RUNBOOK_DIRECTORY / filename).is_file())

    def test_runbooks_share_metadata_and_phase_contract(self) -> None:
        shared_metadata = {
            "version": "0.1.0",
            "audience": "human_and_ai_collaborators",
            "source_band": "public_possible",
            "task_type": "operational_collaboration",
        }
        expected_status = {
            "external-benchmark-intake.v0.1.md": "working",
            "administrative-context-contract-evolution.v0.1.md": "exercised",
            "constellation-contract-release-handoff.v0.1.md": "exercised",
        }
        required_phase_markers = (
            "**Owner:**",
            "**Action mode:**",
            "**Checkpoint:**",
            "**Recovery:**",
            "**Stop condition:**",
        )
        for filename in RUNBOOKS:
            with self.subTest(filename=filename):
                source = (RUNBOOK_DIRECTORY / filename).read_text(encoding="utf-8")
                metadata = scalar_front_matter(source)
                self.assertTrue(metadata.get("title"))
                self.assertEqual(expected_status[filename], metadata.get("status"))
                for key, value in shared_metadata.items():
                    self.assertEqual(value, metadata.get(key))
                phases = re.split(r"(?m)^### Phase \d+[^\n]*$", source)[1:]
                self.assertGreaterEqual(len(phases), 6)
                for phase in phases:
                    for marker in required_phase_markers:
                        self.assertIn(marker, phase)

    def test_public_possible_sources_exclude_private_locators(self) -> None:
        sources = [SKILL_PATH, RUNBOOK_DIRECTORY / "README.md"]
        sources.extend(RUNBOOK_DIRECTORY / filename for filename in RUNBOOKS)
        for source_path in sources:
            with self.subTest(source_path=source_path.name):
                source = source_path.read_text(encoding="utf-8").lower()
                for pattern in PRIVATE_LOCATOR_PATTERNS:
                    self.assertNotIn(pattern, source)

    def test_source_identity_supports_non_git_benchmarks(self) -> None:
        skill = SKILL_PATH.read_text(encoding="utf-8")
        intake = (
            RUNBOOK_DIRECTORY / "external-benchmark-intake.v0.1.md"
        ).read_text(encoding="utf-8")
        for source_kind in (
            "Repository or software release",
            "Dataset or distributed artifact",
            "Paper",
            "Standard or vocabulary",
            "API or hosted interface",
        ):
            with self.subTest(source_kind=source_kind):
                self.assertIn(source_kind, skill)
        self.assertIn("A paper has no Git release", skill)
        self.assertIn("not applicable rather than unresolved", skill)
        self.assertIn("standard/vocabulary, or API/interface", intake)

    def test_environment_route_has_owned_entry_and_return_paths(self) -> None:
        guide = ROOT / "docs" / "RESEARCHER_ENVIRONMENTS.md"
        source = guide.read_text(encoding="utf-8")
        for relative in (
            "../constellation.lock.json",
            "../release/repository-role.json",
            "../release/contract-package-coordinate.json",
            "../.agents/runbooks/README.md",
            "../.agents/runbooks/constellation-contract-release-handoff.v0.1.md",
            "../.agents/skills/uv-backed-python-execution/SKILL.md",
            "../README.md",
        ):
            with self.subTest(relative=relative):
                self.assertIn(f"]({relative})", source)
                self.assertTrue((guide.parent / relative).is_file())
        for path, target in (
            (ROOT / "README.md", "docs/RESEARCHER_ENVIRONMENTS.md"),
            (RUNBOOK_DIRECTORY / "README.md", "../../docs/RESEARCHER_ENVIRONMENTS.md"),
            (RUNBOOK_DIRECTORY / "constellation-contract-release-handoff.v0.1.md", "../../docs/RESEARCHER_ENVIRONMENTS.md"),
        ):
            with self.subTest(path=path.name):
                self.assertIn(f"]({target})", path.read_text(encoding="utf-8"))
        for pattern in PRIVATE_LOCATOR_PATTERNS:
            self.assertNotIn(pattern, source.lower())

    def test_dataset_metadata_route_is_artifact_class_aware(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for artifact_class in (
            "Canonical state",
            "Synthetic fixtures",
            "Validation corpora",
            "Evidence registries and receipts",
            "Generated manifests and projections",
        ):
            with self.subTest(artifact_class=artifact_class):
                self.assertIn(artifact_class, readme)
        self.assertIn("MLCommons Croissant 1.1", readme)
        self.assertIn("package-local dataset card", readme)
        self.assertIn("lims-eln-simulated-final-state/issues/38", readme)
        self.assertIn("lims-eln-comparative-evidence/issues/41", readme)

    def test_contract_evolution_exercise_keeps_adapter_and_claims_distinct(
        self,
    ) -> None:
        source = (
            RUNBOOK_DIRECTORY
            / "administrative-context-contract-evolution.v0.1.md"
        ).read_text(encoding="utf-8")
        for statement in (
            "**Action mode:** `implementation_authorized`",
            "Program-owned synthetic fixture",
            "source-neutral\nadministrative adapter contract",
            "connected extract-through-emit stages",
            "precedence-resolved rule conflict",
            "reviewed\nrevision",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, source)


if __name__ == "__main__":
    unittest.main()

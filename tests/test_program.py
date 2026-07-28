from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_program", ROOT / "scripts" / "validate_program.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SECRET_SPEC = importlib.util.spec_from_file_location(
    "scan_secret_shapes", ROOT / "scripts" / "scan_secret_shapes.py"
)
assert SECRET_SPEC and SECRET_SPEC.loader
SECRET_SHAPES = importlib.util.module_from_spec(SECRET_SPEC)
sys.modules["scan_secret_shapes"] = SECRET_SHAPES
SECRET_SPEC.loader.exec_module(SECRET_SHAPES)


class ProgramValidationTests(unittest.TestCase):
    def test_complete_program_validates(self) -> None:
        summary = MODULE.validate()
        self.assertEqual(summary["proof_classes"], 4)
        self.assertEqual(summary["repositories"], 5)
        self.assertEqual(summary["requirements"], 8)
        self.assertEqual(summary["scenarios"], 13)
        self.assertEqual(summary["open_receipts"], 9)

    def test_program_and_governance_release_coordinates_are_explicit(self) -> None:
        versioned_paths = (
            "constellation.json",
            "machine-node.json",
            "specifications/capabilities.json",
            "specifications/invariants.json",
            "examples/scenarios.json",
            "receipts/open-receipts.json",
            "acceptance/roles.json",
            "acceptance/proof-classes.json",
        )
        for relative_path in versioned_paths:
            document = json.loads((ROOT / relative_path).read_text())
            self.assertEqual(MODULE.PROGRAM_RELEASE, document["version"])

        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        self.assertEqual(MODULE.PROGRAM_RELEASE, lock["constellation_version"])
        self.assertEqual("spec-v0.2.0", lock["specification"]["release"])
        self.assertEqual("governance-v1.0.0", lock["governance"]["release"])
        self.assertEqual("1.0.0", lock["comparison"]["receipt_schema"])
        for role in ("specification", "governance"):
            status = lock[role]["coordinate_status"]
            self.assertIn(status, {"pending_release_commit", "pinned"})
            if status == "pending_release_commit":
                self.assertEqual(MODULE.PENDING_COMMIT, lock[role]["commit"])
                self.assertEqual(MODULE.PENDING_TREE_DIGEST, lock[role]["digest"])
            else:
                self.assertNotEqual(MODULE.PENDING_COMMIT, lock[role]["commit"])
                self.assertNotEqual(
                    MODULE.PENDING_TREE_DIGEST,
                    lock[role]["digest"],
                )

        status = (ROOT / "STATUS.yaml").read_text()
        self.assertIn("version: 0.2.0", status)
        self.assertIn("planned_release: spec-v0.2.0", status)
        self.assertIn("governance_contract: governance-v1.0.0", status)
        self.assertIn('version = "0.2.0"', (ROOT / "pyproject.toml").read_text())

    def test_every_open_receipt_has_accountable_roles(self) -> None:
        data = json.loads((ROOT / "receipts" / "open-receipts.json").read_text())
        self.assertTrue(all(receipt["accountable_roles"] for receipt in data["receipts"]))

    def test_forecast_precedes_observation(self) -> None:
        data = json.loads(
            (ROOT / "forecasts" / "forecast-2026-Q3-r1.json").read_text()
        )
        self.assertTrue(data["released_before_observation"])
        self.assertTrue(all(item["status"] == "unexamined" for item in data["predictions"]))

    def test_simulation_authority_remains_advisory(self) -> None:
        data = json.loads(
            (ROOT / "forecasts" / "forecast-2026-Q3-r1.json").read_text()
        )
        self.assertEqual(data["simulation_authority"], "advisory_only")

    def test_aws_configuration_and_secret_lifecycle_is_traceable(self) -> None:
        capabilities = json.loads(
            (ROOT / "specifications" / "capabilities.json").read_text()
        )["requirements"]
        invariants = json.loads(
            (ROOT / "specifications" / "invariants.json").read_text()
        )["rules"]
        scenarios = json.loads((ROOT / "examples" / "scenarios.json").read_text())[
            "scenarios"
        ]
        receipts = json.loads(
            (ROOT / "receipts" / "open-receipts.json").read_text()
        )["receipts"]
        self.assertTrue(
            any(item["id"] == "SPEC-SECR-001" for item in capabilities)
        )
        secret_rule = next(item for item in invariants if item["id"] == "RULE-SECR-001")
        self.assertIn("Parameter Store", secret_rule["statement"])
        self.assertIn("Secrets Manager", secret_rule["statement"])
        self.assertTrue(any(item["id"] == "SCN-SECR-001" for item in scenarios))
        self.assertTrue(any(item["id"] == "RCP-SECR-001" for item in receipts))

    def test_non_finite_json_tokens_are_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(MODULE.NonFiniteNumberError):
                MODULE.reject_non_finite(token)
        with self.assertRaises(MODULE.NonFiniteNumberError):
            MODULE.parse_finite_float("1e10000")

    def test_secret_shape_findings_redact_values(self) -> None:
        shaped_value = "gh" + "p_" + ("A" * 24)
        findings = SECRET_SHAPES.scan_text(
            Path("fixture.env"),
            f'GITHUB_TOKEN="{shaped_value}"\n',
        )
        self.assertTrue(findings)
        rendered = "\n".join(str(finding) for finding in findings)
        self.assertNotIn(shaped_value, rendered)
        self.assertIn("redacted", rendered)

    def test_runtime_secret_references_are_accepted(self) -> None:
        self.assertEqual(
            [],
            SECRET_SHAPES.scan_text(
                Path("fixture.env"),
                'API_KEY="${API_KEY}"\n'
                'PASSWORD="secretsmanager://lims/vendor/password"\n',
            ),
        )

    def test_repository_secret_shape_scan_passes(self) -> None:
        self.assertEqual([], SECRET_SHAPES.scan_repository(ROOT))


if __name__ == "__main__":
    unittest.main()

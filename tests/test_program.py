from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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
        self.assertEqual(summary["requirements"], 9)
        self.assertEqual(summary["scenarios"], 16)
        self.assertEqual(summary["open_receipts"], 9)
        self.assertEqual(summary["promotion_receipts"], 1)
        self.assertEqual(summary["operations"], 3)
        self.assertEqual(summary["probes"], 10)
        self.assertEqual(summary["simulated_closures"], 4)
        self.assertEqual(summary["governance_closure_families"], 4)
        self.assertEqual(summary["receipt_vocabulary_mappings"], 7)

    def test_program_and_governance_release_coordinates_are_explicit(self) -> None:
        versioned_paths = (
            "constellation.json",
            "specifications/capabilities.json",
            "specifications/invariants.json",
            "specifications/bounded-caller.json",
            "examples/scenarios.json",
            "receipts/open-receipts.json",
            "probes/catalog.json",
            "simulations/future-reality-closure-v0.3.json",
            "forecasts/forecast-2026-Q3-r2.json",
            "acceptance/roles.json",
            "acceptance/proof-classes.json",
        )
        for relative_path in versioned_paths:
            document = json.loads((ROOT / relative_path).read_text())
            self.assertEqual(MODULE.PROGRAM_RELEASE, document["version"])

        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        self.assertEqual(MODULE.PROGRAM_RELEASE, lock["constellation_version"])
        self.assertEqual("spec-v0.3.0", lock["specification"]["release"])
        self.assertEqual("governance-v2.0.0", lock["governance"]["release"])
        self.assertEqual("2.0.0", lock["governance"]["schema_version"])
        self.assertEqual(
            "Control Plane Profile 0.3.0",
            lock["governance"]["profile"],
        )
        self.assertEqual("2.0.0", lock["comparison"]["receipt_schema"])
        for role in MODULE.RELEASE_PATTERNS:
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
        self.assertIn("version: 0.3.0", status)
        self.assertIn("planned_release: spec-v0.3.0", status)
        self.assertIn("governance_contract: governance-v2.0.0", status)
        self.assertIn("governance_schema: 2.0.0", status)
        self.assertIn("receipt_schema: 2.0.0", status)
        self.assertIn('version = "0.3.0"', (ROOT / "pyproject.toml").read_text())

    def test_every_open_receipt_has_accountable_roles(self) -> None:
        data = json.loads((ROOT / "receipts" / "open-receipts.json").read_text())
        self.assertTrue(all(receipt["accountable_roles"] for receipt in data["receipts"]))

    def test_simulated_receipt_closure_preserves_observed_successor(self) -> None:
        receipts = json.loads(
            (ROOT / "receipts" / "open-receipts.json").read_text()
        )["receipts"]
        for receipt in receipts:
            self.assertEqual("open", receipt["status"])
            self.assertEqual("simulated", receipt["simulation"]["evidence_mode"])
            self.assertEqual(
                "closed_in_future_reality",
                receipt["simulation"]["status"],
            )
            self.assertEqual(
                {"evidence_mode": "observed", "status": "open"},
                receipt["future_observed_closure"],
            )

        future = json.loads(
            (
                ROOT
                / "simulations"
                / "future-reality-closure-v0.3.json"
            ).read_text()
        )
        self.assertEqual("simulated", future["evidence_mode"])
        self.assertEqual("advisory_design_only", future["authority"])
        self.assertEqual("advisory_design", future["design_status"])
        self.assertEqual(
            "FUTURE-REALITY-DESIGN-LIMS-2028-001",
            future["design_future_reality_id"],
        )
        self.assertEqual(
            MODULE.CANONICAL_CLOSURE_DIGEST,
            future["canonical_execution_successor"]["digest"],
        )
        self.assertEqual(4, len(future["closures"]))
        self.assertTrue(
            all(
                item["future_observed_closure"]["status"] == "open"
                for item in future["closures"]
            )
        )

    def test_program_carries_exact_canonical_simulation_closure(self) -> None:
        projection = json.loads(
            (
                ROOT
                / "simulations"
                / "simulated-receipt-closure.v2.json"
            ).read_text()
        )
        self.assertEqual("simulated", projection["evidence_mode"])
        self.assertEqual(
            "closed_in_simulation",
            projection["closure_status"],
        )
        self.assertEqual(
            "separate_unasserted_state",
            projection["environment_observed_closure"],
        )
        self.assertEqual("none", projection["production_authorization_effect"])
        self.assertEqual(
            "CLOSURE-SIM-SUBSTANTIVE-2028-V1",
            projection["closure_id"],
        )
        self.assertEqual(
            "FUTURE-REALITY-LIMS-2028-001",
            projection["future_reality"]["future_reality_id"],
        )
        self.assertEqual(
            {
                "configured_vendor_environments",
                "representative_migration_restore_rehearsals",
                "production_security_observability",
                "accountable_scientific_quality_regulatory_acceptance",
            },
            {item["family"] for item in projection["receipt_closures"]},
        )
        self.assertEqual(
            MODULE.CANONICAL_CLOSURE_DIGEST,
            MODULE.canonical_json_digest(projection),
        )
        canonical_source_path = (
            ROOT.parent
            / "lims-eln-simulated-final-state"
            / "build"
            / "simulation"
            / "simulated-receipt-closure.json"
        )
        if canonical_source_path.exists():
            self.assertEqual(
                json.loads(canonical_source_path.read_text()),
                projection,
            )

    def test_receipt_vocabulary_maps_each_layer_explicitly(self) -> None:
        vocabulary = json.loads(
            (
                ROOT
                / "specifications"
                / "receipt-vocabulary-map.v1.json"
            ).read_text()
        )
        self.assertEqual("RECEIPT-VOCABULARY-MAP-001", vocabulary["contract_id"])
        self.assertEqual("1.0.0", vocabulary["version"])
        self.assertEqual(7, len(vocabulary["family_mappings"]))
        self.assertEqual(
            {
                ("closed_in_future_reality", "closed_in_simulation"),
                ("open", "separate_unasserted_state"),
            },
            {
                (item["source_status"], item["target_status"])
                for item in vocabulary["status_mappings"]
            },
        )
        engineering = next(
            item
            for item in vocabulary["family_mappings"]
            if item["individual_receipt_family"] == "engineering_verification"
        )
        self.assertEqual(
            "explicit_family_required",
            engineering["grouped_canonical_family"],
        )

    def test_bounded_caller_covers_three_effect_classes(self) -> None:
        contract = json.loads(
            (ROOT / "specifications" / "bounded-caller.json").read_text()
        )
        operations = contract["operations"]
        self.assertEqual(
            {
                "read",
                "narrow_idempotent_write",
                "approval_gated_broad_write",
            },
            {item["effect_class"] for item in operations},
        )
        self.assertTrue(
            all(
                item["input_schema"]["additional_properties"] is False
                for item in operations
            )
        )
        broad = next(
            item
            for item in operations
            if item["effect_class"] == "approval_gated_broad_write"
        )
        self.assertIn("canonical_request_digest", broad["approval_binding"])
        self.assertNotIn("ai_bounded_caller", broad["allowed_callers"])

    def test_practitioner_probes_are_levelled_and_traceable(self) -> None:
        catalog = json.loads((ROOT / "probes" / "catalog.json").read_text())
        self.assertEqual(10, len(catalog["probes"]))
        for probe in catalog["probes"]:
            self.assertEqual([1, 2, 3, 4, 5], [
                item["level"] for item in probe["levels"]
            ])
            self.assertIn(
                probe["veracity"]["status"],
                catalog["veracity_vocabulary"],
            )
            self.assertTrue(probe["evidence_links"]["scenario_ids"])

    def test_machine_node_and_coordination_horizon_are_non_authorizing(self) -> None:
        machine_node = json.loads((ROOT / "machine-node.json").read_text())
        horizon = json.loads(
            (ROOT / "coordination-horizon.json").read_text()
        )
        first_receipt = json.loads((ROOT / "first-receipt.json").read_text())
        self.assertEqual(
            "orientation_only",
            machine_node["authority"]["mode"],
        )
        self.assertEqual("0.3.0", machine_node["control_plane_profile"])
        self.assertEqual("2.0.0", machine_node["schema_release"])
        self.assertEqual("settling", machine_node["lifecycle_state"])
        self.assertEqual(
            "spec-v0.2.0",
            machine_node["seed_lineage"]["release"],
        )
        self.assertEqual(
            MODULE.PENDING_COMMIT,
            machine_node["current_provenance"]["commit"],
        )
        self.assertEqual(
            first_receipt["first_receipt_id"],
            machine_node["first_receipt_contract_id"],
        )
        self.assertEqual(
            horizon["horizon_id"],
            machine_node["coordination_horizon_id"],
        )
        self.assertEqual(
            "orientation_only",
            first_receipt["authority_posture"]["mode"],
        )
        self.assertIn(
            MODULE.PROMOTION_RECEIPT_ID,
            machine_node["open_receipts"],
        )
        self.assertEqual(
            set(machine_node["open_receipts"]),
            set(first_receipt["open_receipts"]),
        )
        current_items = [
            item
            for item in horizon["work_items"]
            if item["item_id"] in horizon["current_item_ids"]
        ]
        self.assertTrue(
            any(
                item["state"] == "settling"
                and "promotion" in item["horizon_label"].lower()
                for item in current_items
            )
        )
        self.assertEqual(
            {
                "HORIZON-CONTRACTS",
                "HORIZON-VERTICAL-SLICE",
                "HORIZON-EXTENSIONS",
            },
            {item["item_id"] for item in horizon["work_items"]},
        )

    def test_release_role_separates_design_from_canonical_execution(self) -> None:
        manifest = json.loads(
            (ROOT / "release" / "repository-role.json").read_text()
        )
        self.assertEqual("candidate_pending_promotion", manifest["release_state"])
        self.assertEqual(
            "FUTURE-REALITY-DESIGN-LIMS-2028-001",
            manifest["advisory_design"]["future_reality_id"],
        )
        self.assertEqual(
            "FUTURE-REALITY-LIMS-2028-001",
            manifest["canonical_closure"]["future_reality_id"],
        )
        self.assertEqual(
            MODULE.CANONICAL_CLOSURE_DIGEST,
            manifest["canonical_closure"]["digest"],
        )
        self.assertEqual(
            "none",
            manifest["canonical_closure"]["production_authorization_effect"],
        )
        self.assertEqual(
            MODULE.PROMOTION_RECEIPT_ID,
            manifest["promotion_coordinates"]["open_receipt_id"],
        )

    def test_forecast_precedes_observation(self) -> None:
        data = json.loads(
            (ROOT / "forecasts" / "forecast-2026-Q3-r2.json").read_text()
        )
        self.assertTrue(data["released_before_observation"])
        self.assertTrue(all(item["status"] == "unexamined" for item in data["predictions"]))
        self.assertTrue(all(item["probability_of"] for item in data["predictions"]))
        self.assertTrue(all(item["horizon"] for item in data["predictions"]))

    def test_simulation_authority_remains_advisory(self) -> None:
        data = json.loads(
            (ROOT / "forecasts" / "forecast-2026-Q3-r2.json").read_text()
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

    def test_duplicate_json_object_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = Path(temporary_directory) / "ambiguous.json"
            fixture.write_text(
                '{"receipt_id":"RCP-001","receipt_id":"RCP-002"}',
                encoding="utf-8",
            )
            original_root = MODULE.ROOT
            MODULE.ROOT = Path(temporary_directory)
            try:
                with self.assertRaises(MODULE.DuplicateObjectKeyError):
                    MODULE.load_json("ambiguous.json")
            finally:
                MODULE.ROOT = original_root

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

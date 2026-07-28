from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest import mock
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
LANGUAGE_SPEC = importlib.util.spec_from_file_location(
    "check_language", ROOT / "scripts" / "check_language.py"
)
assert LANGUAGE_SPEC and LANGUAGE_SPEC.loader
LANGUAGE = importlib.util.module_from_spec(LANGUAGE_SPEC)
sys.modules["check_language"] = LANGUAGE
LANGUAGE_SPEC.loader.exec_module(LANGUAGE)
PINNED_SPEC = importlib.util.spec_from_file_location(
    "validate_pinned_sources", ROOT / "scripts" / "validate_pinned_sources.py"
)
assert PINNED_SPEC and PINNED_SPEC.loader
PINNED = importlib.util.module_from_spec(PINNED_SPEC)
sys.modules["validate_pinned_sources"] = PINNED
PINNED_SPEC.loader.exec_module(PINNED)


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
        self.assertEqual("spec-v0.3.1", lock["specification"]["release"])
        self.assertEqual("governance-v2.0.1", lock["governance"]["release"])
        self.assertEqual(
            "implementation-v0.3.1",
            lock["implementation"]["release"],
        )
        self.assertEqual("2.0.1", lock["governance"]["schema_version"])
        self.assertEqual(
            "Control Plane Profile 0.3.0",
            lock["governance"]["profile"],
        )
        self.assertEqual("2.0.1", lock["comparison"]["receipt_schema"])
        self.assertEqual(
            MODULE.CANONICAL_RESULT_DIGEST,
            lock["simulation"]["reference_result_digest"],
        )
        self.assertEqual(
            MODULE.CANONICAL_CLOSURE_DIGEST,
            lock["simulation"]["canonical_closure_digest"],
        )
        self.assertEqual(
            MODULE.CANONICAL_AGGREGATE_ARTIFACT_DIGEST,
            lock["simulation"]["aggregate_artifact_digest"],
        )
        self.assertEqual(
            MODULE.CANONICAL_BUNDLE_FILE_DIGEST,
            lock["simulation"]["canonical_bundle_file_digest"],
        )
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

        status = MODULE.load_status()
        self.assertEqual("0.3.1", status["version"])
        self.assertEqual("spec-v0.3.1", status["planned_release"])
        self.assertEqual("governance-v2.0.1", status["governance_contract"])
        self.assertEqual("2.0.1", status["governance_schema"])
        self.assertEqual("2.0.1", status["receipt_schema"])
        self.assertIn('version = "0.3.1"', (ROOT / "pyproject.toml").read_text())

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
        bundle_path = (
            ROOT / "simulations" / "future-reality-2028-06-30-v1.json"
        )
        bundle = json.loads(bundle_path.read_text())
        self.assertEqual("2.0.1", bundle["bundle_version"])
        self.assertEqual(
            MODULE.CANONICAL_RESULT_DIGEST,
            bundle["source_result_digest"],
        )
        self.assertEqual(projection, bundle["governance_closure"])
        self.assertEqual(
            MODULE.CANONICAL_CLOSURE_DIGEST,
            bundle["governance_closure_digest"],
        )
        self.assertEqual(
            MODULE.CANONICAL_AGGREGATE_ARTIFACT_DIGEST,
            projection["aggregate_artifacts"][0]["digest"],
        )
        self.assertEqual(
            MODULE.CANONICAL_BUNDLE_FILE_DIGEST,
            MODULE.sha256_digest(
                "simulations/future-reality-2028-06-30-v1.json"
            ),
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
        self.assertEqual("2.0.1", machine_node["schema_release"])
        self.assertEqual("settling", machine_node["lifecycle_state"])
        self.assertEqual(
            "spec-v0.3.0",
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
            MODULE.CANONICAL_RESULT_DIGEST,
            manifest["canonical_closure"]["reference_result_digest"],
        )
        self.assertEqual(
            MODULE.CANONICAL_AGGREGATE_ARTIFACT_DIGEST,
            manifest["canonical_closure"]["aggregate_artifact_digest"],
        )
        self.assertEqual(
            "none",
            manifest["canonical_closure"]["production_authorization_effect"],
        )
        self.assertEqual(
            MODULE.PROMOTION_RECEIPT_ID,
            manifest["promotion_coordinates"]["receipt_id"],
        )

    def test_release_lifecycle_accepts_complete_settlement(self) -> None:
        release_role = json.loads(
            (ROOT / "release" / "repository-role.json").read_text()
        )
        machine_node = json.loads((ROOT / "machine-node.json").read_text())
        first_receipt = json.loads((ROOT / "first-receipt.json").read_text())
        horizon = json.loads((ROOT / "coordination-horizon.json").read_text())
        promotion = json.loads(
            (ROOT / "receipts" / "promotion-receipt.json").read_text()
        )
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        status = MODULE.load_status()
        receipts = json.loads(
            (ROOT / "receipts" / "open-receipts.json").read_text()
        )["receipts"]
        substantive_ids = {item["id"] for item in receipts}

        release_role = deepcopy(release_role)
        machine_node = deepcopy(machine_node)
        first_receipt = deepcopy(first_receipt)
        horizon = deepcopy(horizon)
        promotion = deepcopy(promotion)
        lock = deepcopy(lock)
        status = deepcopy(status)
        commit = "a" * 40
        tree = "git-tree-sha1:" + ("b" * 40)
        content_digest = "sha256:" + ("c" * 64)

        for coordinate in (
            lock["specification"],
            lock["simulation"],
            lock["implementation"],
            lock["comparison"],
            lock["governance"],
        ):
            coordinate["coordinate_status"] = "pinned"
            coordinate["commit"] = commit
            coordinate["digest"] = tree
        release_role["release_state"] = "released"
        release_role["release_coordinates"] = {
            "commit": commit,
            "tree_digest": tree,
            "coordinate_status": "pinned",
        }
        release_role["promotion_coordinates"]["status"] = "settled"
        machine_node["lifecycle_state"] = "reference_ready"
        machine_node["current_provenance"] = {
            "release": MODULE.PROGRAM_TAG,
            "commit": commit,
            "digest": content_digest,
        }
        machine_node["open_receipts"].remove(MODULE.PROMOTION_RECEIPT_ID)
        first_receipt["open_receipts"].remove(MODULE.PROMOTION_RECEIPT_ID)
        promotion["promotion_state"] = "released"
        promotion["evidence_mode"] = "observed"
        promotion["assurance_stage"] = "verified"
        promotion["release_coordinate"] = {
            "tag": MODULE.PROGRAM_TAG,
            "commit": commit,
            "digest": content_digest,
            "promoted_at": "2026-07-29T12:00:00Z",
            "check_contexts": ["branch-policy", "program-validation"],
            "ruleset_receipt": "governed://github/rulesets/program-main",
            "codeowner_resolution": "evidence://github/codeowners/program-main",
        }
        for item in horizon["work_items"]:
            if "promotion" in item["horizon_label"].lower():
                item["state"] = "complete"
        status["status"] = "released"
        status["release_coordinate_status"] = "pinned"
        status["governance_coordinate_status"] = "pinned"

        MODULE.validate_release_lifecycle(
            release_role=release_role,
            machine_node=machine_node,
            first_receipt=first_receipt,
            coordination_horizon=horizon,
            promotion_receipt=promotion,
            constellation_lock=lock,
            status_document=status,
            substantive_receipt_ids=substantive_ids,
        )

        machine_node["current_provenance"]["commit"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "pinned and equal"):
            MODULE.validate_release_lifecycle(
                release_role=release_role,
                machine_node=machine_node,
                first_receipt=first_receipt,
                coordination_horizon=horizon,
                promotion_receipt=promotion,
                constellation_lock=lock,
                status_document=status,
                substantive_receipt_ids=substantive_ids,
            )

    def test_core_shapes_reject_undeclared_fields(self) -> None:
        records = {
            "constellation": json.loads((ROOT / "constellation.json").read_text()),
            "constellation_lock": json.loads(
                (ROOT / "constellation.lock.json").read_text()
            ),
            "release_role": json.loads(
                (ROOT / "release" / "repository-role.json").read_text()
            ),
            "machine_node": json.loads((ROOT / "machine-node.json").read_text()),
            "first_receipt": json.loads(
                (ROOT / "first-receipt.json").read_text()
            ),
            "coordination_horizon": json.loads(
                (ROOT / "coordination-horizon.json").read_text()
            ),
            "promotion_receipt": json.loads(
                (ROOT / "receipts" / "promotion-receipt.json").read_text()
            ),
            "status_document": MODULE.load_status(),
        }
        records["constellation_lock"]["undeclared"] = "field"
        with self.assertRaisesRegex(ValueError, "undeclared"):
            MODULE.validate_core_shapes(**records)

    def test_status_parser_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = Path(temporary_directory) / "STATUS.yaml"
            fixture.write_text("name: first\nname: second\n", encoding="utf-8")
            original_root = MODULE.ROOT
            MODULE.ROOT = Path(temporary_directory)
            try:
                with self.assertRaises(MODULE.DuplicateObjectKeyError):
                    MODULE.load_status()
            finally:
                MODULE.ROOT = original_root

    def test_promotion_receipt_schema_is_closed(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "promotion-receipt.schema.json").read_text()
        )
        receipt = json.loads(
            (ROOT / "receipts" / "promotion-receipt.json").read_text()
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(receipt))
        self.assertEqual(MODULE.PROMOTION_RECEIPT_ID, receipt["promotion_receipt_id"])
        self.assertEqual("candidate_pending", receipt["promotion_state"])
        self.assertIsNone(receipt["release_coordinate"])
        candidate_contract = schema["allOf"][0]["then"]["properties"][
            "candidate_coordinate"
        ]["properties"]
        self.assertEqual(MODULE.PENDING_COMMIT, candidate_contract["commit"]["const"])
        self.assertEqual(
            "sha256:" + ("0" * 64),
            candidate_contract["digest"]["const"],
        )

    def test_pinned_source_gate_is_fail_closed(self) -> None:
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        self.assertEqual(
            [],
            PINNED.validate_sources(lock, {}, allow_pending=True),
        )
        findings = PINNED.validate_sources(lock, {}, allow_pending=False)
        self.assertEqual(5, sum("requires a pinned" in item for item in findings))

        pinned = deepcopy(lock)
        pinned["simulation"]["coordinate_status"] = "pinned"
        pinned["simulation"]["commit"] = "a" * 40
        pinned["simulation"]["digest"] = "git-tree-sha1:" + ("b" * 40)
        findings = PINNED.validate_sources(pinned, {}, allow_pending=True)
        self.assertIn(
            "simulation pinned coordinate requires a checked-out source",
            findings,
        )
        preflight = PINNED.validate_external_preflight(lock)
        self.assertTrue(preflight)
        for role in PINNED.EXTERNAL_ROLES:
            pinned[role]["coordinate_status"] = "pinned"
            pinned[role]["commit"] = "a" * 40
            pinned[role]["digest"] = "git-tree-sha1:" + ("b" * 40)
        self.assertEqual([], PINNED.validate_external_preflight(pinned))

    def test_cross_repository_artifact_checks_are_operational(self) -> None:
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        closure = json.loads(
            (
                ROOT / "simulations" / "simulated-receipt-closure.v2.json"
            ).read_text()
        )
        bundle = json.loads(
            (
                ROOT / "simulations" / "future-reality-2028-06-30-v1.json"
            ).read_text()
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            simulation = temporary_root / "simulation"
            (simulation / "build" / "simulation").mkdir(parents=True)
            (simulation / "release").mkdir()
            (
                simulation
                / "build"
                / "simulation"
                / "simulated-receipt-closure.json"
            ).write_text(json.dumps(closure), encoding="utf-8")
            (
                simulation / "build" / "simulation" / "result.json"
            ).write_text(
                json.dumps({"content_digest": "sha256:" + ("0" * 64)}),
                encoding="utf-8",
            )
            (simulation / "release" / "repository-role.json").write_text(
                json.dumps(
                    {
                        "reference_result_digest": MODULE.CANONICAL_RESULT_DIGEST,
                        "reference_closure_digest": (
                            MODULE.CANONICAL_CLOSURE_DIGEST
                        ),
                    }
                ),
                encoding="utf-8",
            )
            findings = PINNED.validate_sources(
                lock,
                {"simulation": simulation},
                allow_pending=True,
            )
            self.assertIn(
                "simulation result content digest differs from canonical bundle",
                findings,
            )

            comparison = temporary_root / "comparison"
            fixture = (
                comparison
                / "fixtures"
                / "simulated-closures"
                / "future-reality-2028-06-30-v1.json"
            )
            fixture.parent.mkdir(parents=True)
            fixture.write_text(json.dumps(bundle), encoding="utf-8")
            findings = PINNED.validate_sources(
                lock,
                {"comparison": comparison},
                allow_pending=True,
            )
            self.assertIn(
                "comparison canonical bundle bytes differ from program",
                findings,
            )

    def test_negation_aware_language_check_passes(self) -> None:
        self.assertEqual((), LANGUAGE.check_repository().findings)

    def test_language_policy_release_is_bound_to_qualified_surfaces(self) -> None:
        release = json.loads(
            (ROOT / "release" / "repository-role.json").read_text()
        )
        corpus = json.loads(
            (ROOT / "language-policy" / "corpus-v1.json").read_text()
        )
        exemptions = json.loads(
            (ROOT / "language-policy" / "exemptions.json").read_text()
        )
        manifest_path = ROOT / "language-policy" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        binding = release["contract_bindings"]["language_policy_manifest"]
        self.assertEqual(
            LANGUAGE.POLICY_RELEASE,
            release["contract_bindings"]["language_policy_release"],
        )
        self.assertEqual(LANGUAGE.POLICY_RELEASE, corpus["policy_release"])
        self.assertEqual(LANGUAGE.POLICY_RELEASE, exemptions["policy_release"])
        self.assertEqual(LANGUAGE.POLICY_RELEASE, manifest["policy_release"])
        self.assertEqual(
            "sha256:" + hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            binding["digest"],
        )
        self.assertEqual(
            "sha256:"
            + hashlib.sha256(
                (ROOT / "scripts" / "language_policy_core.py").read_bytes()
            ).hexdigest(),
            binding["core_digest"],
        )
        self.assertEqual(
            "sha256:"
            + hashlib.sha256(
                (ROOT / "language-policy" / "corpus-v1.json").read_bytes()
            ).hexdigest(),
            binding["corpus_digest"],
        )
        self.assertTrue(all(
            metadata["severity"] == "error"
            for metadata in LANGUAGE.RULES.values()
        ))

    def test_language_policy_projection_gate_proves_local_and_governance_bytes(
        self,
    ) -> None:
        self.assertEqual([], PINNED.validate_language_policy_projection())
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            program = temporary_root / "program"
            governance = temporary_root / "governance"
            for relative in (
                "language-policy/manifest.json",
                "language-policy/corpus-v1.json",
                "language-policy/exemptions.json",
                "scripts/language_policy_core.py",
            ):
                destination = program / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / relative).read_bytes())
            for mapping in PINNED.LANGUAGE_POLICY_ASSETS.values():
                source = ROOT / mapping["projection_path"]
                destination = governance / mapping["governance_path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
            for relative in ("language-policy/manifest.json",):
                destination = governance / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / relative).read_bytes())

            original_root = PINNED.ROOT
            PINNED.ROOT = program
            try:
                self.assertEqual(
                    [],
                    PINNED.validate_language_policy_projection(governance),
                )
                original_read_bytes = Path.read_bytes

                def deny_manifest(path: Path, *args, **kwargs):
                    if path == program / "language-policy" / "manifest.json":
                        raise PermissionError(
                            f"host-specific manifest path: {path}"
                        )
                    return original_read_bytes(path, *args, **kwargs)

                with mock.patch.object(
                    Path,
                    "read_bytes",
                    new=deny_manifest,
                ):
                    manifest_findings = (
                        PINNED.validate_language_policy_projection(governance)
                    )
                self.assertEqual(
                    [
                        "LANGUAGE_POLICY_MANIFEST_UNREADABLE: "
                        "language-policy projection manifest could not be loaded"
                    ],
                    manifest_findings,
                )
                self.assertNotIn(str(temporary_root), str(manifest_findings))

                def deny_projected_core(path: Path, *args, **kwargs):
                    if path == program / "scripts" / "language_policy_core.py":
                        raise PermissionError(
                            f"host-specific projected asset path: {path}"
                        )
                    return original_read_bytes(path, *args, **kwargs)

                with mock.patch.object(
                    Path,
                    "read_bytes",
                    new=deny_projected_core,
                ):
                    asset_findings = (
                        PINNED.validate_language_policy_projection(governance)
                    )
                self.assertIn(
                    "LANGUAGE_POLICY_ASSET_UNREADABLE: projected asset "
                    "language-policy-core could not be loaded",
                    asset_findings,
                )
                self.assertNotIn(str(temporary_root), str(asset_findings))

                governed_core = (
                    governance / "tools" / "language_policy_core.py"
                )
                governed_core.write_bytes(governed_core.read_bytes() + b"\n")
                self.assertIn(
                    "language-policy projected bytes differ from governance "
                    "for language-policy-core",
                    PINNED.validate_language_policy_projection(governance),
                )
                governed_core.write_bytes(
                    (program / "scripts" / "language_policy_core.py").read_bytes()
                )
                projected_corpus = (
                    program / "language-policy" / "corpus-v1.json"
                )
                projected_corpus.write_bytes(projected_corpus.read_bytes() + b"\n")
                self.assertIn(
                    "language-policy projected asset digest differs for "
                    "language-policy-qualification-corpus",
                    PINNED.validate_language_policy_projection(governance),
                )
            finally:
                PINNED.ROOT = original_root

    def test_pinned_source_identity_failure_uses_a_stable_diagnostic(
        self,
    ) -> None:
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        lock["implementation"].update(
            {
                "coordinate_status": "pinned",
                "commit": "a" * 40,
                "digest": "git-tree-sha1:" + ("b" * 40),
            }
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "implementation"
            source.mkdir()
            error = PINNED.subprocess.CalledProcessError(
                128,
                ["git", "-C", str(source), "rev-parse", "HEAD"],
            )
            with mock.patch.object(
                PINNED,
                "git_identity",
                side_effect=error,
            ):
                findings = PINNED.validate_sources(
                    lock,
                    {"implementation": source},
                    allow_pending=True,
                )
        self.assertIn(
            "SOURCE_IDENTITY_UNREADABLE: implementation source identity "
            "could not be read",
            findings,
        )
        self.assertNotIn(temporary_directory, str(findings))

    def test_pinned_source_artifact_failures_are_typed_and_path_safe(
        self,
    ) -> None:
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        original_read_bytes = Path.read_bytes
        canonical_path = (
            ROOT / "simulations" / "simulated-receipt-closure.v2.json"
        )

        def deny_canonical(path: Path, *args, **kwargs):
            if path == canonical_path:
                raise PermissionError(f"host-specific canonical path: {path}")
            return original_read_bytes(path, *args, **kwargs)

        with mock.patch.object(
            Path,
            "read_bytes",
            new=deny_canonical,
        ):
            findings = PINNED.validate_sources(
                lock,
                {},
                allow_pending=True,
            )
        self.assertIn(
            "PROGRAM_CANONICAL_CLOSURE_UNREADABLE: "
            "program canonical closure could not be loaded",
            findings,
        )
        self.assertNotIn(str(ROOT), str(findings))

        bundle_path = (
            ROOT / "simulations" / "future-reality-2028-06-30-v1.json"
        )
        strict_cases = (
            (
                canonical_path,
                b'{"identity": 1, "identity": 2}',
                "PROGRAM_CANONICAL_CLOSURE_INVALID_JSON: "
                "program canonical closure could not be loaded",
            ),
            (
                canonical_path,
                b'{"measurement": NaN}',
                "PROGRAM_CANONICAL_CLOSURE_INVALID_JSON: "
                "program canonical closure could not be loaded",
            ),
            (
                bundle_path,
                b"[]",
                "PROGRAM_CANONICAL_BUNDLE_INVALID_SHAPE: "
                "program canonical bundle requires a JSON object",
            ),
        )
        for target, replacement, expected in strict_cases:
            with self.subTest(strict_json=expected):
                def replace_policy_json(path: Path, *args, **kwargs):
                    if path == target:
                        return replacement
                    return original_read_bytes(path, *args, **kwargs)

                with mock.patch.object(
                    Path,
                    "read_bytes",
                    new=replace_policy_json,
                ):
                    strict_findings = PINNED.validate_sources(
                        lock,
                        {},
                        allow_pending=True,
                    )
                self.assertIn(expected, strict_findings)
                self.assertNotIn(str(ROOT), str(strict_findings))

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            simulation = temporary_root / "simulation"
            closure = (
                simulation
                / "build"
                / "simulation"
                / "simulated-receipt-closure.json"
            )
            closure.parent.mkdir(parents=True)
            closure.write_text("{malformed", encoding="utf-8")
            manifest = simulation / "release" / "repository-role.json"
            manifest.parent.mkdir()
            manifest.write_text("{}", encoding="utf-8")

            comparison = temporary_root / "comparison"
            fixture = (
                comparison
                / "fixtures"
                / "simulated-closures"
                / "future-reality-2028-06-30-v1.json"
            )
            fixture.parent.mkdir(parents=True)
            outside = temporary_root / "outside-bundle.json"
            outside.write_text('{"private": "external-content-sentinel"}')
            fixture.symlink_to(outside)

            governance = temporary_root / "governance"
            governance.mkdir()
            (governance / "VERSION").write_bytes(b"\xff\xfe")

            findings = PINNED.validate_sources(
                lock,
                {
                    "simulation": simulation,
                    "comparison": comparison,
                    "governance": governance,
                },
                allow_pending=True,
            )

        self.assertIn(
            "SIMULATION_CANONICAL_CLOSURE_INVALID_JSON: "
            "simulation canonical closure could not be loaded",
            findings,
        )
        self.assertIn(
            "COMPARISON_CANONICAL_BUNDLE_SYMLINK: "
            "comparison canonical bundle could not be loaded",
            findings,
        )
        self.assertIn(
            "GOVERNANCE_VERSION_ENCODING_INVALID: "
            "governance VERSION record requires valid UTF-8 text",
            findings,
        )
        self.assertNotIn(temporary_directory, str(findings))
        self.assertNotIn("external-content-sentinel", str(findings))

    def test_workflow_exposes_stable_aggregate_context(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text()
        author_job = workflow.split("  author-feedback:", 1)[1].split(
            "\n  program:",
            1,
        )[0]
        program_job = workflow.split("\n  program:", 1)[1].split(
            "\n  candidate-coordinates:",
            1,
        )[0]
        aggregate_job = workflow.split("\n  program-validation:", 1)[1]
        self.assertIn("program-validation:\n    name: program-validation", workflow)
        self.assertIn("cross-repository-contracts:", workflow)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("github.ref != 'refs/heads/main'", workflow)
        self.assertIn("secrets.CONSTELLATION_READ_TOKEN", workflow)
        self.assertIn("scripts/check_language.py", workflow)
        self.assertIn("scripts/validate_pinned_sources.py", workflow)
        self.assertIn("--preflight-external", workflow)
        self.assertLess(
            workflow.index("--preflight-external"),
            workflow.index("Resolve immutable external coordinates"),
        )
        for document in (
            "machine-node.json",
            "first-receipt.json",
            "coordination-horizon.json",
        ):
            self.assertIn(f"--document-path {document}", workflow)
        self.assertIn(
            "if: ${{ github.event_name == 'pull_request' }}",
            author_job,
        )
        self.assertIn("continue-on-error: true", author_job)
        self.assertIn(
            "VALE_ARCHIVE: vale_3.15.2_Linux_64-bit.tar.gz",
            author_job,
        )
        self.assertIn(
            "fc72e64454d6bd7af91905d4faebbf411bae3eec17bb572f4101311212bc0d9e",
            author_job,
        )
        self.assertIn(
            "https://github.com/vale-cli/vale/releases/download/"
            "v3.15.2/$VALE_ARCHIVE",
            author_job,
        )
        self.assertIn("sha256sum --check --strict", author_job)
        self.assertIn("--config=.vale.ini --no-global --no-exit", author_job)
        self.assertIn("--minAlertLevel=warning .", author_job)
        self.assertNotIn("vale", program_job.lower())
        self.assertNotIn("author-feedback", aggregate_job)
        self.assertNotIn("vale-action", workflow.lower())
        self.assertNotIn("reviewdog", workflow.lower())

        configuration = (ROOT / ".vale.ini").read_text(encoding="utf-8")
        documentation = (
            ROOT / "docs" / "AUTHOR_FEEDBACK.md"
        ).read_text(encoding="utf-8")
        self.assertIn("MinAlertLevel = suggestion", configuration)
        self.assertIn(
            "default includes both warnings and suggestions",
            documentation,
        )
        self.assertIn("CI requests `--minAlertLevel=warning`", documentation)
        self.assertIn(
            "vale --config=.vale.ini --no-global .",
            documentation,
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

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from scripts import verify_program_release_observation as OBSERVATION


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
    def database_validation_arguments(self) -> dict:
        capabilities = json.loads(
            (ROOT / "specifications" / "capabilities.json").read_text()
        )["requirements"]
        invariants = json.loads(
            (ROOT / "specifications" / "invariants.json").read_text()
        )["rules"]
        scenarios = json.loads(
            (ROOT / "examples" / "scenarios.json").read_text()
        )["scenarios"]
        roles = json.loads(
            (ROOT / "acceptance" / "roles.json").read_text()
        )["roles"]
        return {
            "ledger": json.loads(
                (ROOT / "database" / "primitive-findings.json").read_text()
            ),
            "constellation_index": json.loads(
                (
                    ROOT / "database" / "constellation-finding-index.json"
                ).read_text()
            ),
            "plan_set": json.loads(
                (
                    ROOT / "plans" / "database-modernization-plans.json"
                ).read_text()
            ),
            "data_contract": json.loads(
                (
                    ROOT / "specifications" / "data-primitives.json"
                ).read_text()
            ),
            "migration_contract": json.loads(
                (
                    ROOT / "specifications" / "database-migration.json"
                ).read_text()
            ),
            "database_receipts": json.loads(
                (
                    ROOT / "receipts" / "database-open-receipts.json"
                ).read_text()
            ),
            "database_manifest": json.loads(
                (
                    ROOT / "release" / "database-release-manifest.json"
                ).read_text()
            ),
            "release_role": json.loads(
                (ROOT / "release" / "repository-role.json").read_text()
            ),
            "status_document": MODULE.load_status(),
            "requirement_ids": {item["id"] for item in capabilities},
            "rule_ids": {item["id"] for item in invariants},
            "scenario_ids": {item["id"] for item in scenarios},
            "role_ids": {item["id"] for item in roles},
        }

    def test_complete_program_validates(self) -> None:
        summary = MODULE.validate()
        self.assertEqual(summary["proof_classes"], 4)
        self.assertEqual(summary["repositories"], 5)
        self.assertEqual(summary["requirements"], 12)
        self.assertEqual(summary["rules"], 28)
        self.assertEqual(summary["scenarios"], 24)
        self.assertEqual(summary["open_receipts"], 17)
        self.assertEqual(summary["canonical_open_receipts"], 9)
        self.assertEqual(summary["promotion_receipts"], 1)
        self.assertEqual(summary["release_observations"], 1)
        self.assertEqual(summary["operations"], 3)
        self.assertEqual(summary["probes"], 10)
        self.assertEqual(summary["simulated_closures"], 4)
        self.assertEqual(summary["governance_closure_families"], 4)
        self.assertEqual(summary["receipt_vocabulary_mappings"], 7)
        self.assertEqual(summary["database_findings"], 32)
        self.assertEqual(summary["database_constellation_findings"], 115)
        self.assertEqual(summary["database_constellation_sources"], 3)
        self.assertEqual(summary["database_plans"], 5)
        self.assertEqual(summary["database_flyway_transition_estimates"], 1)
        self.assertEqual(summary["database_ownership_boundaries"], 4)
        self.assertEqual(summary["database_stages"], 7)
        self.assertEqual(summary["data_primitive_policies"], 13)
        self.assertEqual(summary["database_reconciliation_dimensions"], 9)
        self.assertEqual(summary["database_release_gates"], 7)
        self.assertEqual(summary["database_open_receipts"], 8)
        self.assertEqual(summary["pages_sources"], 1)
        self.assertEqual(summary["public_ready_skills"], 2)
        self.assertEqual(summary["contract_package_coordinates"], 1)

    def test_database_finding_ledger_is_complete_and_contract_bound(self) -> None:
        arguments = self.database_validation_arguments()
        ledger = arguments["ledger"]
        finding_ids = {item["id"] for item in ledger["findings"]}
        self.assertEqual(32, len(finding_ids))
        self.assertEqual(
            {"critical", "high"},
            {item["severity"] for item in ledger["findings"]},
        )
        self.assertEqual(
            {"prototype-exemplars", "reference-pack"},
            {
                source["repository"]
                for item in ledger["findings"]
                for source in item["sources"]
            },
        )
        policy_findings = {
            finding_id
            for policy in arguments["data_contract"]["primitive_policies"]
            for finding_id in policy["finding_ids"]
        }
        migration_findings = set(
            arguments["migration_contract"]["finding_ids"]
        )
        self.assertEqual(finding_ids, policy_findings | migration_findings)

    def test_constellation_finding_index_binds_every_source_record(self) -> None:
        arguments = self.database_validation_arguments()
        index = arguments["constellation_index"]
        sources = {item["source_id"]: item for item in index["sources"]}
        self.assertEqual(
            {
                "PROGRAM-DISCOVERY-FINDINGS",
                "REFERENCE-PACK-FINDINGS",
                "ACTIVE-IMPLEMENTATION-FINDINGS",
            },
            set(sources),
        )
        self.assertEqual(
            115,
            sum(item["record_count"] for item in sources.values()),
        )
        self.assertEqual(
            {
                "PROGRAM-DISCOVERY-FINDINGS": 32,
                "REFERENCE-PACK-FINDINGS": 53,
                "ACTIVE-IMPLEMENTATION-FINDINGS": 30,
            },
            {
                source_id: source["record_count"]
                for source_id, source in sources.items()
            },
        )
        self.assertTrue(
            all(
                item["record_count"] == len(item["record_ids"])
                for item in sources.values()
            )
        )
        self.assertTrue(
            all(
                MODULE.MATERIAL_COMMIT_PATTERN.fullmatch(item["source_commit"])
                for item in sources.values()
            )
        )
        self.assertEqual(
            MODULE.sha256_digest("database/primitive-findings.json"),
            sources["PROGRAM-DISCOVERY-FINDINGS"]["ledger_digest"],
        )
        self.assertEqual(
            {
                "PROGRAM-DISCOVERY-FINDINGS": (
                    "fc1577a8886842c606ccbc3c115c7b812fd5dfca"
                ),
                "REFERENCE-PACK-FINDINGS": (
                    "0ed46249247c8b1c7f69c385fe82bd2052eacd63"
                ),
                "ACTIVE-IMPLEMENTATION-FINDINGS": (
                    "fc4b79dba989faeafff3f0fb871d292381fe2168"
                ),
            },
            {
                source_id: sources[source_id]["source_commit"]
                for source_id in (
                    "PROGRAM-DISCOVERY-FINDINGS",
                    "REFERENCE-PACK-FINDINGS",
                    "ACTIVE-IMPLEMENTATION-FINDINGS",
                )
            },
        )
        self.assertEqual(
            "canonical",
            sources["PROGRAM-DISCOVERY-FINDINGS"]["probability_relation"][
                "kind"
            ],
        )
        self.assertEqual(
            MODULE.DATABASE_PROBABILITY_EVENT,
            sources["PROGRAM-DISCOVERY-FINDINGS"]["probability_relation"][
                "estimated_event"
            ],
        )
        self.assertEqual(
            2,
            len(
                {
                    sources[source_id]["probability_relation"][
                        "estimated_event"
                    ]
                    for source_id in (
                        "REFERENCE-PACK-FINDINGS",
                        "ACTIVE-IMPLEMENTATION-FINDINGS",
                    )
                }
            ),
        )
        self.assertEqual(
            {"conditional_derivative"},
            {
                sources[source_id]["probability_relation"]["kind"]
                for source_id in (
                    "REFERENCE-PACK-FINDINGS",
                    "ACTIVE-IMPLEMENTATION-FINDINGS",
                )
            },
        )

    def test_database_plan_set_declares_one_event_and_seven_interstitials(
        self,
    ) -> None:
        plan_set = self.database_validation_arguments()["plan_set"]
        self.assertEqual(
            MODULE.DATABASE_PROBABILITY_EVENT,
            plan_set["probability_of"],
        )
        self.assertEqual(
            MODULE.DATABASE_PROBABILITY_ASSUMPTIONS,
            tuple(
                plan_set["estimation_posture"]["conditioning_assumptions"]
            ),
        )
        transition = plan_set["flyway_transition_estimate"]
        self.assertEqual(
            MODULE.FLYWAY_TRANSITION_EVENT,
            transition["probability_of"],
        )
        self.assertEqual(0.91, transition["estimated_probability"])
        self.assertEqual([0.84, 0.96], transition["credible_range"])
        modernization_doc = (ROOT / "docs" / "DATABASE_MODERNIZATION.md").read_text(
            encoding="utf-8"
        )
        constellation_doc = (
            ROOT / "docs" / "DATABASE_CONSTELLATION_LEDGER.md"
        ).read_text(encoding="utf-8")
        normalized_event = " ".join(MODULE.DATABASE_PROBABILITY_EVENT.split())
        self.assertIn(
            normalized_event,
            " ".join(modernization_doc.replace("> ", "").split()),
        )
        self.assertIn(
            normalized_event,
            " ".join(constellation_doc.replace("> ", "").split()),
        )
        normalized_transition = " ".join(MODULE.FLYWAY_TRANSITION_EVENT.split())
        self.assertIn(
            normalized_transition,
            " ".join(modernization_doc.replace("> ", "").split()),
        )
        self.assertEqual(5, len(plan_set["plans"]))
        self.assertEqual(
            {
                "DB-PLAN-01": 0.54,
                "DB-PLAN-02": 0.83,
                "DB-PLAN-03": 0.71,
                "DB-PLAN-04": 0.89,
                "DB-PLAN-05": 0.78,
            },
            {item["id"]: item["probability"] for item in plan_set["plans"]},
        )
        synthesis = plan_set["recommended_synthesis"]
        self.assertEqual(
            {item["id"] for item in plan_set["plans"]},
            {item["plan_id"] for item in synthesis["composition"]},
        )
        stages = plan_set["chain_of_action"]
        self.assertEqual(
            list(range(1, 8)),
            [item["sequence"] for item in stages],
        )
        self.assertTrue(
            all(
                item["interstitial"]["question"]
                and item["interstitial"]["signals"]
                and item["interstitial"]["response"]
                for item in stages
            )
        )

    def test_database_migration_contract_selects_flyway_with_owned_boundaries(
        self,
    ) -> None:
        migration = self.database_validation_arguments()["migration_contract"]
        self.assertEqual(
            {
                "DB-OWNER-PROGRAM-SCHEMA",
                "DB-OWNER-VENDOR-LIFECYCLE",
                "DB-OWNER-CROSS-VENDOR-MOVEMENT",
                "DB-OWNER-RELEASE-EVIDENCE",
            },
            {
                boundary["boundary_id"]
                for boundary in migration["ownership_boundaries"]
            },
        )
        profile = migration["selected_implementation_profile"]
        self.assertEqual("Flyway Community", profile["product"])
        self.assertEqual("13.0.0", profile["version"])
        self.assertEqual(
            "Flyway-owned public.flyway_schema_history",
            profile["history_relation"],
        )
        self.assertIn("baselineOnMigrate=false", profile["configuration_policy"])
        self.assertEqual(
            {
                "flyway validate -outputType=json",
                "flyway info -outputType=json",
                "flyway migrate -outputType=json",
            },
            set(profile["commands"]),
        )
        self.assertEqual(
            "FLYWAY-TRANSITION-EQUIVALENCE-001",
            profile["transition_receipt"]["probability_event_id"],
        )

    def test_database_contract_references_resolve(self) -> None:
        arguments = self.database_validation_arguments()
        data = arguments["data_contract"]
        migration = arguments["migration_contract"]
        receipt_ids = {
            item["id"] for item in arguments["database_receipts"]["receipts"]
        }
        for contract in (data, migration):
            bindings = contract["program_bindings"]
            self.assertLessEqual(
                set(bindings["requirement_ids"]), arguments["requirement_ids"]
            )
            self.assertLessEqual(
                set(bindings["rule_ids"]), arguments["rule_ids"]
            )
            self.assertLessEqual(
                set(bindings["scenario_ids"]), arguments["scenario_ids"]
            )
        self.assertEqual(
            receipt_ids,
            set(data["program_bindings"]["open_receipt_ids"])
            | set(migration["program_bindings"]["open_receipt_ids"]),
        )

    def test_database_receipts_and_release_manifest_preserve_boundaries(
        self,
    ) -> None:
        arguments = self.database_validation_arguments()
        receipts = arguments["database_receipts"]["receipts"]
        manifest = arguments["database_manifest"]
        self.assertEqual(8, len(receipts))
        for receipt in receipts:
            self.assertEqual("open", receipt["status"])
            self.assertEqual("observed", receipt["evidence_mode"])
            self.assertGreaterEqual(len(receipt["accountable_roles"]), 4)
            self.assertGreaterEqual(len(receipt["required_evidence"]), 4)
            self.assertGreaterEqual(len(receipt["requalification_triggers"]), 4)
        self.assertEqual(
            "pending_implementation_projection",
            manifest["migration_coordinate"]["status"],
        )
        self.assertEqual(
            "tool_neutral_capability_contract",
            manifest["migration_coordinate"]["contract_posture"],
        )
        self.assertEqual(
            "Flyway Community 13.0.0",
            manifest["migration_coordinate"]["selected_profile"],
        )
        self.assertEqual(
            "pending_observed_evidence",
            manifest["migration_coordinate"]["executable_digest"],
        )
        self.assertEqual(4, len(manifest["deferred_boundaries"]))
        for binding in manifest["artifact_bindings"]:
            self.assertEqual(
                MODULE.sha256_digest(binding["path"]), binding["digest"]
            )

        release_bindings = arguments["release_role"]["contract_bindings"]
        machine_contracts = {
            item["contract_id"]: item
            for item in json.loads((ROOT / "machine-node.json").read_text())[
                "contracts"
            ]
        }
        first_contracts = {
            item["contract_id"]: item
            for item in json.loads((ROOT / "first-receipt.json").read_text())[
                "contract_state"
            ]
        }
        for binding_name in (
            "data_primitive_finding_ledger",
            "database_constellation_finding_index",
            "database_modernization_plan_set",
            "data_contract",
            "database_migration_contract",
            "database_open_receipts",
            "database_release_manifest",
        ):
            binding = release_bindings[binding_name]
            self.assertEqual(
                MODULE.sha256_digest(binding["path"]), binding["digest"]
            )
            self.assertEqual(
                binding["digest"],
                machine_contracts[binding["contract_id"]]["digest"],
            )
            self.assertEqual(
                binding["digest"],
                first_contracts[binding["contract_id"]]["digest"],
            )

    def test_database_validator_rejects_contract_drift(self) -> None:
        missing_finding = self.database_validation_arguments()
        missing_finding["ledger"]["findings"].pop()
        with self.assertRaises(ValueError):
            MODULE.validate_database_program(**missing_finding)

        stale_digest = self.database_validation_arguments()
        stale_digest["database_manifest"]["artifact_bindings"][0][
            "digest"
        ] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "manifest digest differs"):
            MODULE.validate_database_program(**stale_digest)

        unknown_rule = self.database_validation_arguments()
        unknown_rule["data_contract"]["primitive_policies"][0][
            "rule_ids"
        ].append("RULE-UNPUBLISHED-001")
        with self.assertRaisesRegex(ValueError, "unknown rules"):
            MODULE.validate_database_program(**unknown_rule)

        stale_source = self.database_validation_arguments()
        stale_source["constellation_index"]["sources"][1]["source_commit"] = (
            "0" * 40
        )
        with self.assertRaisesRegex(ValueError, "immutable commit"):
            MODULE.validate_database_program(**stale_source)

        stale_retrieval = self.database_validation_arguments()
        stale_retrieval["constellation_index"]["sources"][1][
            "retrieval_url"
        ] = "https://raw.githubusercontent.com/example/repository/main/ledger.json"
        with self.assertRaisesRegex(ValueError, "retrieval coordinate differs"):
            MODULE.validate_database_program(**stale_retrieval)

        future_dated_index = self.database_validation_arguments()
        future_dated_index["constellation_index"]["metadata"]["created_at"] = (
            "2099-01-01T00:00:00Z"
        )
        with self.assertRaisesRegex(ValueError, "observed finalization instant"):
            MODULE.validate_database_program(**future_dated_index)

        empty_external_digest = self.database_validation_arguments()
        empty_external_digest["constellation_index"]["sources"][1][
            "ledger_digest"
        ] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "material digest"):
            MODULE.validate_database_program(**empty_external_digest)

        missing_external_record = self.database_validation_arguments()
        missing_external_record["constellation_index"]["sources"][1][
            "record_ids"
        ].pop()
        with self.assertRaisesRegex(ValueError, "record identities differ"):
            MODULE.validate_database_program(**missing_external_record)

        redistributed_source_count = self.database_validation_arguments()
        redistributed_source_count["constellation_index"]["sources"][1][
            "record_count"
        ] -= 1
        with self.assertRaisesRegex(ValueError, "released count differs"):
            MODULE.validate_database_program(**redistributed_source_count)

        wrong_flyway = self.database_validation_arguments()
        wrong_flyway["migration_contract"]["selected_implementation_profile"][
            "version"
        ] = "12.0.0"
        with self.assertRaisesRegex(ValueError, "Flyway implementation profile"):
            MODULE.validate_database_program(**wrong_flyway)

        automatic_baseline = self.database_validation_arguments()
        automatic_baseline["migration_contract"]["selected_implementation_profile"][
            "configuration_policy"
        ][0] = "baselineOnMigrate=true"
        with self.assertRaisesRegex(ValueError, "explicit baseline adoption"):
            MODULE.validate_database_program(**automatic_baseline)

        wrong_transition_event = self.database_validation_arguments()
        wrong_transition_event["plan_set"]["flyway_transition_estimate"][
            "probability_of"
        ] = "A different event."
        with self.assertRaisesRegex(ValueError, "transition probability event"):
            MODULE.validate_database_program(**wrong_transition_event)

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
        self.assertEqual(MODULE.GOVERNANCE_TAG, lock["governance"]["release"])
        self.assertEqual(
            "implementation-v0.3.2",
            lock["implementation"]["release"],
        )
        self.assertEqual(
            MODULE.IMPLEMENTATION_REPOSITORY_RELEASE,
            lock["implementation"]["repository_release"],
        )
        self.assertEqual(
            MODULE.CANONICAL_CLOSURE_DIGEST,
            lock["implementation"]["selected_future_closure_digest"],
        )
        self.assertEqual(
            MODULE.IMPLEMENTATION_CONTRACT_BINDINGS,
            lock["implementation"]["contract_bindings"],
        )
        self.assertEqual(
            MODULE.IMPLEMENTATION_SOURCE_ARTIFACT_BINDINGS,
            lock["implementation"]["source_artifact_bindings"],
        )
        self.assertEqual(
            MODULE.GOVERNANCE_RELEASE,
            lock["governance"]["schema_version"],
        )
        self.assertEqual(
            "Control Plane Profile 0.3.0",
            lock["governance"]["profile"],
        )
        self.assertEqual(
            MODULE.COMPARISON_RECEIPT_SCHEMA,
            lock["comparison"]["receipt_schema"],
        )
        self.assertEqual(
            MODULE.COMPARISON_HISTORICAL_GOVERNANCE_SCHEMA,
            lock["comparison"]["historical_governance_schema"],
        )
        for role, expected_subject in MODULE.EXTERNAL_RELEASE_SUBJECTS.items():
            self.assertEqual(
                expected_subject,
                {key: lock[role][key] for key in expected_subject},
            )
        self.assertEqual(
            {
                "tag_object": MODULE.GOVERNANCE_TAG_OBJECT,
                "commit": MODULE.GOVERNANCE_COMMIT,
                "digest": MODULE.GOVERNANCE_TREE_DIGEST,
                "archive_format": MODULE.GOVERNANCE_ARCHIVE_FORMAT,
                "archive_digest": MODULE.GOVERNANCE_ARCHIVE_DIGEST,
                "coordinate_status": "pinned",
            },
            {
                key: lock["governance"][key]
                for key in (
                    "tag_object",
                    "commit",
                    "digest",
                    "archive_format",
                    "archive_digest",
                    "coordinate_status",
                )
            },
        )
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
        self.assertEqual(MODULE.GOVERNANCE_TAG, status["governance_contract"])
        self.assertEqual(MODULE.GOVERNANCE_RELEASE, status["governance_schema"])
        self.assertEqual(MODULE.GOVERNANCE_RELEASE, status["receipt_schema"])
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
        self.assertEqual(MODULE.GOVERNANCE_RELEASE, machine_node["schema_release"])
        self.assertEqual(
            {MODULE.GOVERNANCE_RELEASE},
            {
                item["marking_schema_version"]
                for item in machine_node["campaigns"]
            },
        )
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
                "HORIZON-DATABASE-CONTRACT",
                "HORIZON-DATABASE-IMPLEMENTATION",
                "HORIZON-DATABASE-REHEARSAL",
                "HORIZON-DATABASE-RELEASE",
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
        self.assertEqual(
            MODULE.STANDING_BRANCH_CONTROLS,
            manifest["promotion_controls"]["standing_branch_controls"],
        )
        self.assertEqual(
            MODULE.RELEASE_REVIEW_ROUTE,
            manifest["promotion_controls"]["release_review_route"],
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
        release_observation = json.loads(
            (
                ROOT
                / "receipts"
                / "promotion-observation-spec-v0.3.1.json"
            ).read_text()
        )
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        status = MODULE.load_status()
        receipts = json.loads(
            (ROOT / "receipts" / "open-receipts.json").read_text()
        )["receipts"]
        database_receipts = json.loads(
            (ROOT / "receipts" / "database-open-receipts.json").read_text()
        )["receipts"]
        substantive_ids = {
            item["id"] for item in receipts + database_receipts
        }

        release_role = deepcopy(release_role)
        machine_node = deepcopy(machine_node)
        first_receipt = deepcopy(first_receipt)
        horizon = deepcopy(horizon)
        promotion = deepcopy(promotion)
        release_observation = deepcopy(release_observation)
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
            "check_contexts": ["program-validation"],
            "pull_request": 1,
            "review_observation": deepcopy(MODULE.RELEASE_REVIEW_ROUTE),
        }
        release_observation.update(
            {
                "observation_state": "release_observed",
                "evidence_mode": "observed",
                "assurance_stage": "verified",
                "candidate_source": {
                    "commit_oid": "d" * 40,
                    "tree_oid": "b" * 40,
                },
                "release_subject": {
                    "git_object_format": "sha1",
                    "tag": MODULE.PROGRAM_TAG,
                    "tag_object_oid": "e" * 40,
                    "commit_oid": commit,
                    "tree_oid": "b" * 40,
                    "archive_format": "git-archive-tar",
                    "archive_digest": "sha256:" + ("f" * 64),
                    "promoted_at": "2026-07-29T12:00:00Z",
                },
                "signature_observation": {
                    "verification": "valid",
                    "trusted_signers_path": "release/trusted-release-signers",
                    "trusted_signers_digest": "sha256:" + ("1" * 64),
                },
                "workflow_observation": {
                    "workflow_path": ".github/workflows/validate.yml",
                    "workflow_name": "Validate program specification",
                    "check_context": "program-validation",
                    "run_id": "123",
                    "job_id": "456",
                    "conclusion": "success",
                },
                "review_observation": {
                    "pull_request": 1,
                    **MODULE.RELEASE_REVIEW_ROUTE,
                },
            }
        )
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
            release_observation=release_observation,
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
                release_observation=release_observation,
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
        hosted_contexts = schema["$defs"]["releaseCoordinate"]["properties"][
            "check_contexts"
        ]
        self.assertEqual(0, hosted_contexts["minItems"])
        self.assertEqual(["program-validation"], hosted_contexts["items"]["enum"])
        route_schema = schema["$defs"]["reviewRoute"]
        self.assertEqual(
            MODULE.RELEASE_REVIEW_ROUTE,
            {
                key: route_schema["properties"][key]["const"]
                for key in MODULE.RELEASE_REVIEW_ROUTE
            },
        )
        self.assertEqual(
            MODULE.RELEASE_REVIEW_ROUTE,
            receipt["release_review_route"],
        )
        relabeled_route = deepcopy(receipt["release_review_route"])
        relabeled_route["github_review_record"] = "formal_review_submitted"
        with self.assertRaisesRegex(
            ValueError,
            "differs from the authorized release route",
        ):
            MODULE.validate_release_review_route(
                relabeled_route,
                "promotion_receipt.release_review_route",
            )

    def test_release_observation_has_pending_and_observed_contracts(self) -> None:
        schema = json.loads(
            (
                ROOT
                / "schemas"
                / "program-release-observation.v1.schema.json"
            ).read_text()
        )
        observation = json.loads(
            (
                ROOT
                / "receipts"
                / "promotion-observation-spec-v0.3.1.json"
            ).read_text()
        )
        candidate_digest = "sha256:" + hashlib.sha256(
            (ROOT / "receipts" / "promotion-receipt.json").read_bytes()
        ).hexdigest()
        signer_digest = "sha256:" + hashlib.sha256(
            (ROOT / "release" / "trusted-release-signers").read_bytes()
        ).hexdigest()
        OBSERVATION.validate_observation_schema(
            schema,
            candidate_receipt_digest=candidate_digest,
            trusted_signers_digest=signer_digest,
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(observation))
        self.assertEqual(
            "pending_post_tag",
            OBSERVATION.validate_observation_document(
                observation,
                candidate_receipt_digest=candidate_digest,
                trusted_signers_digest=signer_digest,
            ),
        )
        self.assertEqual(
            {
                "status": "pending_post_tag",
                "target_release": MODULE.PROGRAM_TAG,
                "observation_carrier_commit": None,
            },
            OBSERVATION.verify(ROOT),
        )
        with self.assertRaisesRegex(
            OBSERVATION.ObservationError,
            "ready for post-tag evidence",
        ):
            OBSERVATION.verify(ROOT, require_observed=True)

        observed = deepcopy(observation)
        observed.update(
            {
                "observation_state": "release_observed",
                "evidence_mode": "observed",
                "assurance_stage": "verified",
                "candidate_source": {
                    "commit_oid": "a" * 40,
                    "tree_oid": "b" * 40,
                },
                "release_subject": {
                    "git_object_format": "sha1",
                    "tag": MODULE.PROGRAM_TAG,
                    "tag_object_oid": "c" * 40,
                    "commit_oid": "d" * 40,
                    "tree_oid": "b" * 40,
                    "archive_format": "git-archive-tar",
                    "archive_digest": "sha256:" + ("e" * 64),
                    "promoted_at": "2026-09-02T12:00:00Z",
                },
                "signature_observation": {
                    "verification": "valid",
                    "trusted_signers_path": "release/trusted-release-signers",
                    "trusted_signers_digest": signer_digest,
                },
                "workflow_observation": {
                    "workflow_path": ".github/workflows/validate.yml",
                    "workflow_name": "Validate program specification",
                    "check_context": "program-validation",
                    "run_id": "123",
                    "job_id": "456",
                    "conclusion": "success",
                },
                "review_observation": {
                    "pull_request": 18,
                    **OBSERVATION.RELEASE_REVIEW_ROUTE,
                },
            }
        )
        self.assertEqual(
            "release_observed",
            OBSERVATION.validate_observation_document(
                observed,
                candidate_receipt_digest=candidate_digest,
                trusted_signers_digest=signer_digest,
            ),
        )

        mutations = (
            (
                "candidate and released Program trees differ",
                ("candidate_source", "tree_oid", "f" * 40),
            ),
            (
                "release tag object requires",
                ("release_subject", "tag_object_oid", "0" * 40),
            ),
            (
                "trusted signature observation differs",
                (
                    "signature_observation",
                    "trusted_signers_digest",
                    "sha256:" + ("f" * 64),
                ),
            ),
            (
                "hosted Program proof observation differs",
                ("workflow_observation", "conclusion", "failure"),
            ),
            (
                "differs from the authorized route",
                ("review_observation", "github_review_record", "formal_review_submitted"),
            ),
        )
        for expected_error, (container, field, value) in mutations:
            with self.subTest(field=f"{container}.{field}"):
                changed = deepcopy(observed)
                changed[container][field] = value
                with self.assertRaisesRegex(
                    OBSERVATION.ObservationError,
                    expected_error,
                ):
                    OBSERVATION.validate_observation_document(
                        changed,
                        candidate_receipt_digest=candidate_digest,
                        trusted_signers_digest=signer_digest,
                    )

        changed_schema = deepcopy(schema)
        changed_schema["$defs"]["candidateReceipt"]["properties"]["digest"][
            "const"
        ] = "sha256:" + ("f" * 64)
        with self.assertRaisesRegex(
            OBSERVATION.ObservationError,
            "candidateReceipt.properties.digest.const differs",
        ):
            OBSERVATION.validate_observation_schema(
                changed_schema,
                candidate_receipt_digest=candidate_digest,
                trusted_signers_digest=signer_digest,
            )

        changed_schema = deepcopy(schema)
        changed_schema["allOf"][1]["if"]["properties"]["observation_state"][
            "const"
        ] = "released"
        with self.assertRaisesRegex(
            OBSERVATION.ObservationError,
            "lifecycle branches differ",
        ):
            OBSERVATION.validate_observation_schema(
                changed_schema,
                candidate_receipt_digest=candidate_digest,
                trusted_signers_digest=signer_digest,
            )

        schema_shape_mutations = (
            (
                ("properties", "candidate_receipt", "$ref"),
                "#/$defs/metadata",
            ),
            (("$defs", "sha1Oid", "type"), "integer"),
            (
                (
                    "$defs",
                    "candidateSource",
                    "properties",
                    "commit_oid",
                ),
                {"type": "integer"},
            ),
            (
                (
                    "$defs",
                    "releaseSubject",
                    "properties",
                    "promoted_at",
                    "type",
                ),
                "integer",
            ),
            (
                (
                    "$defs",
                    "workflowObservation",
                    "properties",
                    "run_id",
                    "type",
                ),
                "integer",
            ),
        )
        for path, value in schema_shape_mutations:
            with self.subTest(schema_path=".".join(path)):
                changed_schema = deepcopy(schema)
                current = changed_schema
                for key in path[:-1]:
                    current = current[key]
                current[path[-1]] = value
                with self.assertRaisesRegex(
                    OBSERVATION.ObservationError,
                    "canonical closed shape differs",
                ):
                    OBSERVATION.validate_observation_schema(
                        changed_schema,
                        candidate_receipt_digest=candidate_digest,
                        trusted_signers_digest=signer_digest,
                    )

    def test_observed_release_verifier_derives_the_later_carrier_commit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            observation_path = root / OBSERVATION.OBSERVATION_PATH
            observation_path.parent.mkdir(parents=True)
            (root / "release").mkdir()
            candidate_receipt_bytes = b'{"candidate":"program-0.3.1"}\n'
            signer_bytes = b"release@example.invalid ssh-ed25519 fixture\n"
            (root / OBSERVATION.PROMOTION_RECEIPT_PATH).write_bytes(
                candidate_receipt_bytes
            )
            (root / OBSERVATION.TRUSTED_SIGNERS_PATH).write_bytes(signer_bytes)
            candidate_commit = "a" * 40
            tree = "b" * 40
            tag_object = "c" * 40
            release_commit = "d" * 40
            carrier_commit = "e" * 40
            archive_bytes = b"program archive"
            observation = json.loads(
                (
                    ROOT
                    / "receipts"
                    / "promotion-observation-spec-v0.3.1.json"
                ).read_text()
            )
            observation.update(
                {
                    "observation_state": "release_observed",
                    "evidence_mode": "observed",
                    "assurance_stage": "verified",
                    "candidate_receipt": {
                        "path": "receipts/promotion-receipt.json",
                        "digest": OBSERVATION.sha256_digest(
                            candidate_receipt_bytes
                        ),
                    },
                    "candidate_source": {
                        "commit_oid": candidate_commit,
                        "tree_oid": tree,
                    },
                    "release_subject": {
                        "git_object_format": "sha1",
                        "tag": MODULE.PROGRAM_TAG,
                        "tag_object_oid": tag_object,
                        "commit_oid": release_commit,
                        "tree_oid": tree,
                        "archive_format": "git-archive-tar",
                        "archive_digest": OBSERVATION.sha256_digest(
                            archive_bytes
                        ),
                        "promoted_at": "2026-09-02T12:00:00Z",
                    },
                    "signature_observation": {
                        "verification": "valid",
                        "trusted_signers_path": "release/trusted-release-signers",
                        "trusted_signers_digest": OBSERVATION.sha256_digest(
                            signer_bytes
                        ),
                    },
                    "workflow_observation": {
                        "workflow_path": ".github/workflows/validate.yml",
                        "workflow_name": "Validate program specification",
                        "check_context": "program-validation",
                        "run_id": "123",
                        "job_id": "456",
                        "conclusion": "success",
                    },
                    "review_observation": {
                        "pull_request": 18,
                        **OBSERVATION.RELEASE_REVIEW_ROUTE,
                    },
                }
            )
            observation_path.write_text(json.dumps(observation), encoding="utf-8")
            schema = json.loads(
                (ROOT / OBSERVATION.OBSERVATION_SCHEMA_PATH).read_text()
            )
            schema["$defs"]["candidateReceipt"]["properties"]["digest"][
                "const"
            ] = OBSERVATION.sha256_digest(candidate_receipt_bytes)
            schema["$defs"]["signatureObservation"]["properties"][
                "trusted_signers_digest"
            ]["const"] = OBSERVATION.sha256_digest(signer_bytes)
            schema_path = root / OBSERVATION.OBSERVATION_SCHEMA_PATH
            schema_path.parent.mkdir(parents=True)
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            (root / OBSERVATION.PROMOTION_RECEIPT_PATH).write_bytes(
                b'{"released":"later carrier"}\n'
            )
            (root / "constellation.lock.json").write_text(
                json.dumps(
                    {
                        "specification": {
                            "commit": release_commit,
                            "digest": f"git-tree-sha1:{tree}",
                            "coordinate_status": "pinned",
                        }
                    }
                ),
                encoding="utf-8",
            )
            (root / "release" / "repository-role.json").write_text(
                json.dumps(
                    {
                        "release_coordinates": {
                            "commit": release_commit,
                            "tree_digest": f"git-tree-sha1:{tree}",
                            "coordinate_status": "pinned",
                        }
                    }
                ),
                encoding="utf-8",
            )
            carrier_bytes = observation_path.read_bytes()

            def git_result(_root: Path, *arguments: str, text: bool = True):
                command = tuple(arguments)
                values = {
                    ("rev-parse", f"{MODULE.PROGRAM_TAG}^{{tag}}"): tag_object,
                    ("rev-parse", f"{MODULE.PROGRAM_TAG}^{{commit}}"): release_commit,
                    ("rev-parse", f"{release_commit}^{{tree}}"): tree,
                    ("rev-parse", f"{candidate_commit}^{{tree}}"): tree,
                    ("rev-parse", "HEAD^{commit}"): carrier_commit,
                    ("rev-parse", "origin/main^{commit}"): release_commit,
                }
                if command == (
                    "show",
                    f"{MODULE.PROGRAM_TAG}:receipts/promotion-receipt.json",
                ):
                    return candidate_receipt_bytes
                if command == (
                    "archive",
                    "--format=tar",
                    release_commit,
                ):
                    return archive_bytes
                if command == (
                    "show",
                    "HEAD:receipts/promotion-observation-spec-v0.3.1.json",
                ):
                    return carrier_bytes
                return values[command]

            completed = mock.Mock(returncode=0)
            with mock.patch.object(
                OBSERVATION,
                "run_git",
                side_effect=git_result,
            ), mock.patch.object(
                OBSERVATION.subprocess,
                "run",
                return_value=completed,
            ) as run:
                result = OBSERVATION.verify(root, require_observed=True)
            self.assertEqual(carrier_commit, result["observation_carrier_commit"])
            self.assertEqual(release_commit, result["release_commit"])
            self.assertTrue(
                any("verify-tag" in call.args[0] for call in run.call_args_list)
            )

            def ancestry(_root: Path, ancestor: str, descendant: str) -> bool:
                return not (
                    ancestor == candidate_commit and descendant == release_commit
                )

            with mock.patch.object(
                OBSERVATION,
                "run_git",
                side_effect=git_result,
            ), mock.patch.object(
                OBSERVATION,
                "git_is_ancestor",
                side_effect=ancestry,
            ):
                with self.assertRaisesRegex(
                    OBSERVATION.ObservationError,
                    "candidate source is outside the Program release history",
                ):
                    OBSERVATION.verify(root, require_observed=True)

    def test_pinned_source_gate_is_fail_closed(self) -> None:
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        candidate_findings = PINNED.validate_sources(
            lock, {}, allow_pending=True
        )
        for role in PINNED.EXTERNAL_ROLES - {"governance"}:
            self.assertIn(
                f"{role} pinned coordinate requires a checked-out source",
                candidate_findings,
            )
        findings = PINNED.validate_sources(lock, {}, allow_pending=False)
        self.assertEqual(1, sum("requires a pinned" in item for item in findings))
        self.assertIn(
            "governance pinned coordinate requires a checked-out source",
            findings,
        )
        self.assertEqual([], PINNED.validate_external_preflight(lock))

    def test_governance_coordinate_mutations_keep_identities_distinct(self) -> None:
        governance = json.loads(
            (ROOT / "constellation.lock.json").read_text()
        )["governance"]
        self.assertEqual([], PINNED.validate_governance_coordinate(governance))
        mutations = {
            "release": "governance-v2.1.1",
            "schema_version": "2.1.1",
            "tag_object": "a" * 40,
            "commit": "b" * 40,
            "digest": "git-tree-sha1:" + ("c" * 40),
            "archive_format": "zip",
            "archive_digest": "sha256:" + ("d" * 64),
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = deepcopy(governance)
                changed[field] = value
                self.assertIn(
                    f"governance {field} differs from the accepted release",
                    PINNED.validate_governance_coordinate(changed),
                )

    def test_historical_governance_schema_coordinate_remains_untagged(self) -> None:
        compatibility = json.loads(
            (ROOT / "constellation.lock.json").read_text()
        )["comparison"]["historical_governance_schema"]
        self.assertEqual(
            [],
            PINNED.validate_historical_governance_coordinate(compatibility),
        )
        mutations = {
            "schema_version": "2.1.0",
            "coordinate_kind": "annotated_release_tag",
            "release_tag": "governance-v2.0.1",
            "commit": "a" * 40,
            "digest": "git-tree-sha1:" + ("b" * 40),
            "archive_format": "zip",
            "archive_digest": "sha256:" + ("c" * 64),
            "ancestor_of_release": "governance-v2.1.1",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = deepcopy(compatibility)
                changed[field] = value
                self.assertIn(
                    "historical Governance schema "
                    f"{field} differs from the accepted compatibility coordinate",
                    PINNED.validate_historical_governance_coordinate(changed),
                )

    def test_historical_schema_validation_executes_from_the_pinned_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            governance = temporary_root / "governance"
            comparison = temporary_root / "comparison"
            governance.mkdir()
            comparison.mkdir()
            commands = (
                ["git", "init", "--quiet"],
                ["git", "config", "user.name", "Compatibility Test"],
                [
                    "git",
                    "config",
                    "user.email",
                    "compatibility-test@example.invalid",
                ],
            )
            for command in commands:
                PINNED.subprocess.run(command, cwd=governance, check=True)
            (governance / "tools").mkdir()
            (governance / "schemas").mkdir()
            (governance / "VERSION").write_text("2.0.1\n", encoding="utf-8")
            (governance / "tools" / "validate_governance.py").write_text(
                """import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--governance-root')
parser.add_argument('--source-root')
parser.add_argument('--schema-name')
parser.add_argument('--document-path')
arguments = parser.parse_args()
document = json.loads(
    (Path(arguments.source_root) / arguments.document_path).read_text()
)
raise SystemExit(0 if document.get('schema_release') == '2.0.1' else 1)
""",
                encoding="utf-8",
            )
            for schema_name in PINNED.HISTORICAL_COMPARISON_DOCUMENTS.values():
                (governance / "schemas" / schema_name).write_text(
                    "{}\n",
                    encoding="utf-8",
                )
            PINNED.subprocess.run(
                ["git", "add", "."], cwd=governance, check=True
            )
            PINNED.subprocess.run(
                ["git", "commit", "--quiet", "-m", "Governance 2.0.1 source"],
                cwd=governance,
                check=True,
            )
            historical_commit, historical_tree = PINNED.git_identity(governance)
            coordinate = {
                "commit": historical_commit,
                "digest": historical_tree,
                "archive_digest": PINNED.git_archive_digest(
                    governance, historical_commit
                ),
                "schema_version": "2.0.1",
            }
            for document_path in PINNED.HISTORICAL_COMPARISON_DOCUMENTS:
                (comparison / document_path).write_text(
                    json.dumps({"schema_release": "2.0.1"}),
                    encoding="utf-8",
                )

            (governance / "VERSION").write_text("2.1.0\n", encoding="utf-8")
            (governance / "tools" / "validate_governance.py").write_text(
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            PINNED.subprocess.run(
                ["git", "add", "."], cwd=governance, check=True
            )
            PINNED.subprocess.run(
                ["git", "commit", "--quiet", "-m", "Governance 2.1.0 source"],
                cwd=governance,
                check=True,
            )
            current_commit, _ = PINNED.git_identity(governance)

            with mock.patch.object(PINNED, "GOVERNANCE_COMMIT", current_commit):
                self.assertEqual(
                    [],
                    PINNED.validate_historical_governance_source(
                        governance,
                        coordinate,
                    ),
                )
            self.assertEqual(
                [],
                PINNED.validate_comparison_historical_schemas(
                    governance,
                    comparison,
                    coordinate,
                ),
            )
            (comparison / "first-receipt.json").write_text(
                json.dumps({"schema_release": "2.1.0"}),
                encoding="utf-8",
            )
            self.assertIn(
                "COMPARISON_HISTORICAL_SCHEMA_INVALID: signed Comparison "
                "first-receipt.json differs from the pinned Governance 2.0.1 "
                "schema",
                PINNED.validate_comparison_historical_schemas(
                    governance,
                    comparison,
                    coordinate,
                ),
            )
            PINNED.subprocess.run(
                ["git", "tag", "governance-v2.0.1", historical_commit],
                cwd=governance,
                check=True,
            )
            with mock.patch.object(PINNED, "GOVERNANCE_COMMIT", current_commit):
                self.assertIn(
                    "historical Governance compatibility commit unexpectedly "
                    "has a release tag",
                    PINNED.validate_historical_governance_source(
                        governance,
                        coordinate,
                    ),
                )

    def test_annotated_tag_identity_includes_object_and_peeled_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            commands = (
                ["git", "init", "--quiet"],
                ["git", "config", "user.name", "Release Test"],
                ["git", "config", "user.email", "release-test@example.invalid"],
            )
            for command in commands:
                PINNED.subprocess.run(command, cwd=repository, check=True)
            (repository / "VERSION").write_text("2.1.0\n", encoding="utf-8")
            PINNED.subprocess.run(
                ["git", "add", "VERSION"], cwd=repository, check=True
            )
            PINNED.subprocess.run(
                ["git", "commit", "--quiet", "-m", "Release source"],
                cwd=repository,
                check=True,
            )
            PINNED.subprocess.run(
                [
                    "git",
                    "tag",
                    "-a",
                    "governance-v2.1.0",
                    "-m",
                    "Governance 2.1.0",
                ],
                cwd=repository,
                check=True,
            )
            expected_tag = PINNED.subprocess.run(
                ["git", "rev-parse", "refs/tags/governance-v2.1.0"],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            expected_commit = PINNED.subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(
                (expected_tag, expected_commit),
                PINNED.git_annotated_tag_identity(
                    repository,
                    "governance-v2.1.0",
                ),
            )

    def test_contract_package_coordinate_binds_reviewed_merge(self) -> None:
        coordinate = json.loads(
            (ROOT / "release" / "contract-package-coordinate.json").read_text()
        )
        MODULE.validate_contract_package_coordinate(coordinate)
        self.assertEqual("reviewed_source_available", coordinate["publication_state"])
        self.assertRegex(coordinate["source_commit"], r"^[a-f0-9]{40}$")

        candidate = deepcopy(coordinate)
        candidate["publication_state"] = "pending_reviewed_merge_commit"
        candidate["source_commit"] = None
        candidate["consumer_conformance"]["state"] = (
            "planned_after_source_commit"
        )
        MODULE.validate_contract_package_coordinate(candidate)

        premature = deepcopy(candidate)
        premature["source_commit"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "keeps its source commit open"):
            MODULE.validate_contract_package_coordinate(premature)

        changed_source = deepcopy(coordinate)
        changed_source["source_identity"]["digest"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "scoped source digest differs"):
            MODULE.validate_contract_package_coordinate(changed_source)

        incomplete = deepcopy(coordinate)
        incomplete["consumer_conformance"]["required_observations"].pop()
        with self.assertRaisesRegex(
            ValueError,
            "at least 9 non-empty strings",
        ):
            MODULE.validate_contract_package_coordinate(incomplete)

        unavailable = deepcopy(coordinate)
        unavailable["source_commit"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "commit is unavailable"):
            MODULE.validate_contract_package_coordinate(unavailable)

    def test_contract_package_source_digest_ignores_python_runtime_caches(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            package = root / "src" / "lims_eln_contracts"
            package.mkdir(parents=True)
            (root / "pyproject.toml").write_text("[project]\nname = 'example'\n")
            (package / "__init__.py").write_text("VALUE = 1\n")
            expected = MODULE.package_source_digest(root)

            cache = package / "__pycache__"
            cache.mkdir()
            (cache / "__init__.cpython-312.pyc").write_bytes(b"runtime cache")

            self.assertEqual(expected, MODULE.package_source_digest(root))

            (package / "__init__.py").write_text("VALUE = 2\n")
            self.assertNotEqual(expected, MODULE.package_source_digest(root))

            regular_package = root / "regular-package"
            package.rename(regular_package)
            package.symlink_to(regular_package, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "requires regular files"):
                MODULE.package_source_digest(root)

    def test_contract_package_git_digest_is_commit_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            package = root / "src" / "lims_eln_contracts"
            package.mkdir(parents=True)
            (root / "pyproject.toml").write_text(
                "[project]\nname = 'example'\n",
                encoding="utf-8",
            )
            module = package / "__init__.py"
            module.write_text("VALUE = 1\n", encoding="utf-8")
            commands = (
                ["git", "init", "--quiet"],
                ["git", "config", "user.name", "Package Test"],
                ["git", "config", "user.email", "package-test@example.invalid"],
                ["git", "add", "pyproject.toml", "src/lims_eln_contracts"],
                ["git", "commit", "--quiet", "-m", "Package source"],
            )
            for command in commands:
                MODULE.subprocess.run(command, cwd=root, check=True)
            commit = MODULE.subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            expected = MODULE.package_source_digest(root)

            self.assertEqual(
                expected,
                MODULE.package_source_digest_from_git(commit, root),
            )
            module.write_text("VALUE = 2\n", encoding="utf-8")
            self.assertNotEqual(expected, MODULE.package_source_digest(root))
            self.assertEqual(
                expected,
                MODULE.package_source_digest_from_git(commit, root),
            )
            with self.assertRaisesRegex(ValueError, "commit is unavailable"):
                MODULE.package_source_digest_from_git("a" * 40, root)

    def test_cross_repository_artifact_checks_are_operational(self) -> None:
        lock = json.loads((ROOT / "constellation.lock.json").read_text())
        bundle = json.loads(
            (
                ROOT / "simulations" / "future-reality-2028-06-30-v1.json"
            ).read_text()
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            simulation = temporary_root / "simulation"
            (simulation / "release").mkdir(parents=True)
            changed_bundle = deepcopy(bundle)
            changed_bundle["source_result_digest"] = "sha256:" + ("0" * 64)
            (
                simulation
                / "release"
                / "future-reality-2028-06-30-v1.json"
            ).write_text(json.dumps(changed_bundle), encoding="utf-8")
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
                "simulation source result digest differs from canonical bundle",
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

    def test_implementation_source_semantics_and_artifact_bytes_are_bound(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "implementation"
            source.mkdir()
            payloads = {
                "bounded_caller_binding_digest": (
                    "release/bounded-caller-bindings.json",
                    b'{"binding":"bounded-caller"}\n',
                ),
                "database_flyway_release_digest": (
                    "database/flyway-release.json",
                    b'{"release":"flyway"}\n',
                ),
                "external_contract_coordinate_digest": (
                    "release/external-contract-coordinates.json",
                    b'{"coordinates":[]}\n',
                ),
                "public_inspection_manifest_digest": (
                    "release/public-inspection-manifest.json",
                    b'{"projection":"public"}\n',
                ),
                "open_receipt_ledger_digest": (
                    "receipts/open-receipt-ledger.json",
                    b'{"receipts":[]}\n',
                ),
                "promotion_candidate_digest": (
                    "receipts/promotion-candidate.json",
                    b'{"candidate":"0.3.2"}\n',
                ),
            }
            artifact_bindings = {}
            for binding_name, (relative_path, payload) in payloads.items():
                artifact_path = source / relative_path
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                artifact_path.write_bytes(payload)
                artifact_bindings[binding_name] = {
                    "path": relative_path,
                    "digest": PINNED.bytes_digest(payload),
                    "equality_mode": "byte_sha256",
                }
            coordinate = {
                "release": "implementation-v0.3.2",
                "tag": "v0.3.2",
                "coordinate_status": "pinned",
                "repository_release": "0.3.2",
                "selected_future_closure_digest": MODULE.CANONICAL_CLOSURE_DIGEST,
                "contract_bindings": deepcopy(
                    MODULE.IMPLEMENTATION_CONTRACT_BINDINGS
                ),
                "source_artifact_bindings": artifact_bindings,
            }
            manifest = {
                "repository_role": "enterprise_implementation",
                "repository_release": coordinate["repository_release"],
                "external_release": coordinate["release"],
                "selected_future_closure_digest": coordinate[
                    "selected_future_closure_digest"
                ],
                "contract_bindings": coordinate["contract_bindings"],
                **{
                    binding_name: binding["digest"]
                    for binding_name, binding in artifact_bindings.items()
                    if binding_name != "promotion_candidate_digest"
                },
                "promotion_coordinates": {
                    "candidate_receipt": artifact_bindings[
                        "promotion_candidate_digest"
                    ]["path"],
                    "candidate_receipt_digest": artifact_bindings[
                        "promotion_candidate_digest"
                    ]["digest"],
                    "target_release": coordinate["tag"],
                },
            }
            manifest_path = source / "release" / "repository-role.json"
            manifest_path.write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )

            self.assertEqual(
                [],
                PINNED.validate_implementation_source(source, coordinate),
            )

            changed_manifest = deepcopy(manifest)
            changed_manifest["selected_future_closure_digest"] = (
                "sha256:" + ("0" * 64)
            )
            manifest_path.write_text(
                json.dumps(changed_manifest),
                encoding="utf-8",
            )
            self.assertIn(
                "implementation signed release selected_future_closure_digest "
                "differs from its program lock",
                PINNED.validate_implementation_source(source, coordinate),
            )

            changed_manifest = deepcopy(manifest)
            changed_manifest["external_release"] = "implementation-v0.3.1"
            manifest_path.write_text(
                json.dumps(changed_manifest),
                encoding="utf-8",
            )
            self.assertIn(
                "implementation signed release external_release differs from "
                "its program lock",
                PINNED.validate_implementation_source(source, coordinate),
            )

            changed_manifest = deepcopy(manifest)
            changed_manifest["contract_bindings"]["governance_schema"] = "2.0.1"
            manifest_path.write_text(
                json.dumps(changed_manifest),
                encoding="utf-8",
            )
            self.assertIn(
                "implementation signed release contract_bindings differs from "
                "its program lock",
                PINNED.validate_implementation_source(source, coordinate),
            )

            changed_manifest = deepcopy(manifest)
            changed_manifest["bounded_caller_binding_digest"] = (
                "sha256:" + ("f" * 64)
            )
            manifest_path.write_text(
                json.dumps(changed_manifest),
                encoding="utf-8",
            )
            self.assertIn(
                "implementation signed release bounded_caller_binding_digest "
                "differs from its program lock",
                PINNED.validate_implementation_source(source, coordinate),
            )

            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            bound_artifact = source / artifact_bindings[
                "bounded_caller_binding_digest"
            ]["path"]
            bound_artifact.write_bytes(bound_artifact.read_bytes() + b"changed")
            self.assertIn(
                "implementation source artifact bytes differ for "
                "bounded_caller_binding_digest",
                PINNED.validate_implementation_source(source, coordinate),
            )

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
                / "release"
                / "future-reality-2028-06-30-v1.json"
            )
            closure.parent.mkdir(parents=True)
            closure.write_text("{malformed", encoding="utf-8")
            manifest = simulation / "release" / "repository-role.json"
            manifest.parent.mkdir(exist_ok=True)
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
            "SIMULATION_CANONICAL_BUNDLE_INVALID_JSON: "
            "simulation canonical bundle could not be loaded",
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
        release_tag_input = workflow.split("      release_tag:", 1)[1].split(
            "\n\npermissions:",
            1,
        )[0]
        author_job = workflow.split("  author-feedback:", 1)[1].split(
            "\n  program:",
            1,
        )[0]
        program_job = workflow.split("\n  program:", 1)[1].split(
            "\n  candidate-coordinates:",
            1,
        )[0]
        candidate_job = workflow.split(
            "\n  candidate-coordinates:",
            1,
        )[1].split("\n  cross-repository-contracts:", 1)[0]
        cross_repository_job = workflow.split(
            "\n  cross-repository-contracts:",
            1,
        )[1].split("\n  program-validation:", 1)[0]
        aggregate_job = workflow.split("\n  program-validation:", 1)[1]
        candidate_gate = re.search(r"(?m)^    if:\s*(.+)$", candidate_job)
        cross_repository_gate = re.search(
            r"(?m)^    if:\s*(.+)$",
            cross_repository_job,
        )
        self.assertIsNotNone(candidate_gate)
        self.assertIsNotNone(cross_repository_gate)
        assert candidate_gate is not None
        assert cross_repository_gate is not None
        self.assertIn("program-validation:\n    name: program-validation", workflow)
        self.assertIn("cross-repository-contracts:", workflow)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("github.ref != 'refs/heads/main'", workflow)
        self.assertIn("secrets.CONSTELLATION_READ_TOKEN", workflow)
        self.assertIn("scripts/check_language.py", workflow)
        self.assertIn("scripts/validate_pinned_sources.py", workflow)
        self.assertIn(
            "python scripts/verify_program_release_observation.py",
            workflow,
        )
        self.assertIn("--preflight-external", workflow)
        self.assertIn("--preflight-external", candidate_job)
        self.assertNotIn("--allow-pending", candidate_job)
        self.assertIn("inputs.release_tag == ''", candidate_gate.group(1))
        self.assertIn("inputs.release_tag != ''", cross_repository_gate.group(1))
        feature_ref = "refs/heads/feature/program-proof-route"

        def selected_coordinate_jobs(
            ref: str,
            release_tag: str,
        ) -> tuple[bool, bool]:
            named_carrier = (
                ref == "refs/heads/main"
                or ref.startswith("refs/tags/spec-v")
                or ref.startswith("refs/heads/release/")
                or ref.startswith("refs/heads/hotfix/")
            )
            candidate_selected = release_tag == "" and not named_carrier
            cross_repository_selected = release_tag != "" or named_carrier
            return candidate_selected, cross_repository_selected

        self.assertEqual(
            (False, True),
            selected_coordinate_jobs(feature_ref, "spec-v0.3.1"),
        )
        self.assertEqual(
            (True, False),
            selected_coordinate_jobs(feature_ref, ""),
        )
        self.assertIn("Install the contract model boundary", program_job)
        self.assertIn(
            "python -m pip install --disable-pip-version-check .",
            program_job,
        )
        self.assertLess(
            program_job.index("Install the contract model boundary"),
            program_job.index("Validate stable identifiers and trace links"),
        )
        self.assertLess(
            program_job.index("Install the contract model boundary"),
            program_job.index("Exercise program contracts"),
        )
        self.assertIn(
            "Confirm private sibling read access",
            cross_repository_job,
        )
        self.assertIn(
            "GH_TOKEN: "
            "${{ secrets.CONSTELLATION_READ_TOKEN }}",
            cross_repository_job,
        )
        self.assertIn(
            'if [ -z "${GH_TOKEN:-}" ]; then',
            cross_repository_job,
        )
        self.assertIn(
            "gh api --silent user",
            cross_repository_job,
        )
        for coordinate, repository in (
            ("simulation", "driftframestudios/lims-eln-simulated-final-state"),
            (
                "implementation",
                "driftframestudios/lims-eln-enterprise-implementation",
            ),
            ("comparison", "driftframestudios/lims-eln-comparative-evidence"),
            ("governance", "driftframestudios/site-reading-governance"),
        ):
            self.assertIn(
                f'{coordinate})\n                repository="{repository}"',
                cross_repository_job,
            )
        self.assertIn(
            "commit=\"$(jq -r --arg coordinate \"$coordinate\" "
            "'.[$coordinate].commit' constellation.lock.json)\"",
            cross_repository_job,
        )
        self.assertIn(
            'gh api --silent "repos/$repository/contents?ref=$commit"',
            cross_repository_job,
        )
        self.assertIn(
            "Private sibling read access needs confirmation",
            cross_repository_job,
        )
        self.assertNotIn(
            'echo "$GH_TOKEN"',
            cross_repository_job,
        )
        self.assertLess(
            cross_repository_job.index(
                "Confirm private sibling read access"
            ),
            cross_repository_job.index("Check out the simulation coordinate"),
        )
        self.assertIn(
            ".specification.coordinate_status == "
            '\"pending_release_commit\"',
            workflow,
        )
        self.assertIn('pending_mode+=(--allow-pending)', workflow)
        self.assertIn(
            'scripts/validate_pinned_sources.py "${pending_mode[@]}"',
            workflow,
        )
        self.assertIn("historical schema compatibility", workflow)
        self.assertIn("Verify the selected Program release subject", workflow)
        self.assertIn(
            "startsWith(github.ref, 'refs/tags/spec-v')",
            workflow,
        )
        self.assertIn("release_tag:", workflow)
        self.assertIn(
            "description: Optional signed Program release tag verified by "
            "this carrier",
            release_tag_input,
        )
        self.assertIn("required: false", release_tag_input)
        self.assertIn('default: ""', release_tag_input)
        self.assertIn("type: string", release_tag_input)
        self.assertIn(
            "REQUESTED_RELEASE_TAG: ${{ inputs.release_tag }}",
            cross_repository_job,
        )
        self.assertIn(
            'selected_tag="$REQUESTED_RELEASE_TAG"',
            cross_repository_job,
        )
        self.assertIn(
            '[[ "$GITHUB_REF" == refs/tags/spec-v* ]]',
            cross_repository_job,
        )
        self.assertIn(
            'selected_tag="$GITHUB_REF_NAME"',
            cross_repository_job,
        )
        self.assertIn(
            "expected_tag=\"$(jq -r '.specification.release' "
            "constellation.lock.json)\"",
            workflow,
        )
        self.assertIn(
            'if [ "$selected_tag" != "$expected_tag" ]; then',
            cross_repository_job,
        )
        self.assertIn(
            'git cat-file -t "refs/tags/$selected_tag"',
            cross_repository_job,
        )
        self.assertIn(
            'if [ "$tag_type" != "tag" ]; then',
            cross_repository_job,
        )
        self.assertIn(
            'git rev-parse --verify "refs/tags/$selected_tag^{commit}"',
            cross_repository_job,
        )
        self.assertIn(
            'git rev-parse --verify HEAD',
            cross_repository_job,
        )
        self.assertIn(
            'if [ "$carrier_commit" != "$GITHUB_SHA" ]; then',
            cross_repository_job,
        )
        self.assertIn(
            'git merge-base --is-ancestor "$release_commit" '
            '"$carrier_commit"',
            cross_repository_job,
        )
        self.assertIn(
            "gpg.ssh.allowedSignersFile=release/trusted-release-signers",
            workflow,
        )
        self.assertIn('verify-tag "$selected_tag"', workflow)
        self.assertNotIn('echo "$REQUESTED_RELEASE_TAG"', cross_repository_job)
        self.assertNotIn('echo "$GITHUB_REF"', cross_repository_job)
        trusted_signers = (
            ROOT / "release" / "trusted-release-signers"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            'release@driftframestudios.org namespaces="git" ssh-ed25519 '
            "AAAAC3NzaC1lZDI1NTE5AAAAIDnUwCLnoD9N4f4P7IPB24xmMm45wEskkWiNScUswkcj\n",
            trusted_signers,
        )
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
            "vars.ENABLE_GITHUB_ACTIONS == 'true'",
            author_job,
        )
        self.assertIn("inputs.confirm_run", author_job)
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

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lims_eln_contracts import (  # noqa: E402
    SCHEMA_RESOURCE_NAMES,
    ScenarioContract,
    canonical_sha256,
    generated_schema_bytes,
    load_administrative_adapter_contract_example,
    load_administrative_counterfactual_example,
    load_external_administrative_contract_set,
    load_generated_schema,
    load_golden_specimen_observation_example,
    load_golden_specimen_scenario,
    load_independent_multilabel_policy_example,
    load_operation_catalog,
    model_from_strict_json,
    strict_json_loads,
)
from lims_eln_contracts.schema_artifacts import rendered_schema_artifacts  # noqa: E402


class ReleasedResourceTests(unittest.TestCase):
    def test_external_administrative_resources_load_through_public_boundary(
        self,
    ) -> None:
        contract_set = load_external_administrative_contract_set()
        adapter = load_administrative_adapter_contract_example()
        independent = load_independent_multilabel_policy_example()
        counterfactual = load_administrative_counterfactual_example()

        self.assertEqual("1.0.0", contract_set.contract_set_version)
        self.assertEqual(adapter, contract_set.adapter_contracts[0])
        self.assertEqual(adapter, independent.adapter_contracts[0])
        self.assertEqual(counterfactual, contract_set.impact_observations[0])

    def test_operation_catalog_preserves_program_operation_semantics(self) -> None:
        catalog = load_operation_catalog()
        program = strict_json_loads(
            (ROOT / "specifications" / "bounded-caller.json").read_bytes()
        )
        published = {
            item["id"]: (
                item["name"],
                item["effect_class"],
                item.get("effect_ceiling", item.get("budgets"))["max_records"],
            )
            for item in program["operations"]
        }
        shared = {
            item.operation_id: (
                item.name,
                item.effect_class.value,
                item.effect_ceiling.record_limit,
            )
            for item in catalog.operations
        }
        self.assertEqual(published, shared)

    def test_golden_scenario_links_released_sources_and_contiguous_commands(self) -> None:
        scenario = load_golden_specimen_scenario()
        published = strict_json_loads((ROOT / "examples" / "scenarios.json").read_bytes())
        published_ids = {item["id"] for item in published["scenarios"]}
        self.assertTrue(set(scenario.source_scenario_ids).issubset(published_ids))
        self.assertEqual(tuple(range(5)), tuple(c.expected_version for c in scenario.commands))
        self.assertEqual("released", scenario.expected_state.lifecycle_state)
        self.assertEqual("instrument_integration_owner", scenario.recovery_route.owner_role)

    def test_golden_examples_share_one_projection_and_retain_distinct_evidence(self) -> None:
        implementation = load_golden_specimen_observation_example("implementation")
        simulation = load_golden_specimen_observation_example("simulation")
        scenario = load_golden_specimen_scenario()

        implementation_projection = implementation.result.projection
        simulation_projection = simulation.result.projection
        expected_scenario_coordinate = (
            scenario.scenario_id,
            scenario.scenario_version,
            canonical_sha256(scenario),
        )
        self.assertEqual(
            expected_scenario_coordinate,
            implementation.scenario_coordinate(),
        )
        self.assertEqual(
            implementation.scenario_coordinate(),
            simulation.scenario_coordinate(),
        )
        self.assertEqual(
            implementation_projection.canonical_digest(),
            simulation_projection.canonical_digest(),
        )
        self.assertEqual(
            "sha256:cead042eaf3ca8f72b9c30c41d9acb0bd9255027448f3b28e3451305bed1aef1",
            implementation_projection.canonical_digest(),
        )
        self.assertNotEqual(implementation.evidence_mode, simulation.evidence_mode)
        self.assertNotEqual(
            implementation.result.producer_detail,
            simulation.result.producer_detail,
        )
        for observation in (implementation, simulation):
            with self.subTest(evidence_mode=observation.evidence_mode):
                self.assertEqual(
                    canonical_sha256(
                        observation.result.producer_detail["configuration"]
                    ),
                    observation.source.configuration_digest,
                )
                self.assertEqual(
                    canonical_sha256(observation.result),
                    observation.provenance.raw_artifact_digest,
                )

        self.assertEqual(
            scenario.specimen.tenant_id,
            implementation_projection.tenant_id,
        )
        self.assertEqual(
            scenario.specimen.specimen_id,
            implementation_projection.specimen_id,
        )
        self.assertEqual(
            scenario.expected_state.aggregate_version,
            implementation_projection.lifecycle.aggregate_version,
        )
        self.assertEqual(
            scenario.expected_state.custody_location,
            implementation_projection.custody.current_location,
        )
        self.assertEqual(
            scenario.expected_state.result.model_dump(mode="json"),
            implementation_projection.measurement.model_dump(mode="json"),
        )
        self.assertEqual(
            scenario.commands[-2].payload["review_id"],
            implementation_projection.review_resolution.review_id,
        )
        self.assertEqual(
            scenario.commands[-1].payload["approval_receipt_id"],
            implementation_projection.release.approval_receipt_id,
        )
        self.assertEqual(
            scenario.commands[-1].occurred_at,
            implementation_projection.review_resolution.resolved_at,
        )
        self.assertEqual(
            scenario.commands[-1].occurred_at,
            implementation_projection.release.released_at,
        )

    def test_scenario_detects_a_broken_revision_sequence(self) -> None:
        resource = (
            ROOT
            / "src"
            / "lims_eln_contracts"
            / "resources"
            / "scenarios"
            / "golden-specimen.v1.json"
        )
        document = strict_json_loads(resource.read_bytes())
        document["commands"][2]["expected_version"] = 9
        with self.assertRaisesRegex(ValidationError, "contiguous sequence"):
            model_from_strict_json(ScenarioContract, json.dumps(document))

    def test_golden_observation_rejects_a_changed_source_scenario_coordinate(self) -> None:
        observation = load_golden_specimen_observation_example("implementation")
        payload = observation.model_dump(mode="json")
        payload["scenario_digest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValidationError):
            model_from_strict_json(type(observation), json.dumps(payload))

        scenario = load_golden_specimen_scenario()
        changed_source = scenario.model_dump(mode="json")
        changed_source["recovery_route"]["owner_role"] = "release_recovery_owner"
        self.assertNotEqual(
            observation.scenario_digest,
            canonical_sha256(changed_source),
        )

    def test_schema_resources_are_loadable_and_identified(self) -> None:
        self.assertIn(
            "golden-specimen-result-projection.v1.schema.json",
            SCHEMA_RESOURCE_NAMES,
        )
        for name in SCHEMA_RESOURCE_NAMES:
            with self.subTest(name=name):
                schema = load_generated_schema(name)
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema",
                    schema["$schema"],
                )
                self.assertTrue(schema["$id"].startswith("urn:driftframe:lims-eln:"))
                self.assertEqual("object", schema["type"])

        projection_schema = load_generated_schema(
            "golden-specimen-result-projection.v1.schema.json"
        )
        self.assertTrue(
            {
                "projection_id",
                "projection_version",
                "comparison_compatibility",
            }.issubset(projection_schema["required"])
        )
        self.assertEqual(
            "urn:driftframe:lims-eln:golden-specimen-result",
            projection_schema["properties"]["projection_id"]["const"],
        )
        self.assertEqual(
            "1.0.0",
            projection_schema["properties"]["projection_version"]["const"],
        )
        self.assertEqual(
            "exact-version",
            projection_schema["properties"]["comparison_compatibility"]["const"],
        )
        self.assertEqual(
            [
                "review_resolution.resolved_at occurs at or before "
                "release.released_at"
            ],
            projection_schema["x-semantic-invariants"],
        )

    def test_committed_schemas_match_model_regeneration_byte_for_byte(self) -> None:
        regenerated = rendered_schema_artifacts()
        self.assertEqual(set(SCHEMA_RESOURCE_NAMES), set(regenerated))
        for name, expected in regenerated.items():
            with self.subTest(name=name):
                self.assertEqual(expected, generated_schema_bytes(name))


if __name__ == "__main__":
    unittest.main()

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
    generated_schema_bytes,
    load_generated_schema,
    load_golden_specimen_scenario,
    load_operation_catalog,
    model_from_strict_json,
    strict_json_loads,
)
from lims_eln_contracts.schema_artifacts import rendered_schema_artifacts  # noqa: E402


class ReleasedResourceTests(unittest.TestCase):
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

    def test_schema_resources_are_loadable_and_identified(self) -> None:
        self.assertEqual(6, len(SCHEMA_RESOURCE_NAMES))
        for name in SCHEMA_RESOURCE_NAMES:
            with self.subTest(name=name):
                schema = load_generated_schema(name)
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema",
                    schema["$schema"],
                )
                self.assertTrue(schema["$id"].startswith("urn:driftframe:lims-eln:"))
                self.assertEqual("object", schema["type"])

    def test_committed_schemas_match_model_regeneration_byte_for_byte(self) -> None:
        regenerated = rendered_schema_artifacts()
        self.assertEqual(set(SCHEMA_RESOURCE_NAMES), set(regenerated))
        for name, expected in regenerated.items():
            with self.subTest(name=name):
                self.assertEqual(expected, generated_schema_bytes(name))


if __name__ == "__main__":
    unittest.main()


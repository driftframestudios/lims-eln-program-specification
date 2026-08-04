from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as stream:
        return json.load(stream)


class SpecificationContractTests(unittest.TestCase):
    def assert_schema(self, document_path: str, schema_path: str) -> None:
        schema = load(schema_path)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(load(document_path))

    def test_active_documents_follow_released_json_schemas(self) -> None:
        pairs = {
            "specifications/data-primitives.json": "schemas/data-primitives.schema.json",
            "specifications/database-migration.json": "schemas/database-migration.schema.json",
            "examples/scenarios.json": "schemas/scenarios.schema.json",
            "probes/catalog.json": "schemas/probes.schema.json",
        }
        for document, schema in pairs.items():
            with self.subTest(document=document):
                self.assert_schema(document, schema)

    def test_capability_rule_and_scenario_references_resolve(self) -> None:
        capabilities = load("specifications/capabilities.json")["requirements"]
        rules = load("specifications/invariants.json")["rules"]
        scenarios = load("examples/scenarios.json")["scenarios"]
        requirement_ids = {item["id"] for item in capabilities}
        rule_ids = {item["id"] for item in rules}

        self.assertEqual(len(requirement_ids), len(capabilities))
        self.assertEqual(len(rule_ids), len(rules))
        self.assertEqual(len({item["id"] for item in scenarios}), len(scenarios))
        self.assertTrue(
            all(set(item["rule_ids"]) <= rule_ids for item in capabilities)
        )
        self.assertTrue(
            all(item["requirement_id"] in requirement_ids for item in scenarios)
        )
        self.assertTrue(all(item["rule_id"] in rule_ids for item in scenarios))

    def test_data_policy_bindings_and_vendor_checks_cover_the_contract(self) -> None:
        contract = load("specifications/data-primitives.json")
        concordance = load("specifications/data-contract-concordance.json")
        policy_ids = {item["policy_id"] for item in contract["primitive_policies"]}
        check_ids = {item["policy_id"] for item in concordance["policy_checks"]}

        self.assertEqual(len(policy_ids), len(contract["primitive_policies"]))
        self.assertEqual(policy_ids, check_ids)
        for binding in contract["entity_bindings"]:
            self.assertLessEqual(set(binding["required_policy_ids"]), policy_ids)

    def test_database_contract_uses_flyway_and_debezium_boundaries(self) -> None:
        contract = load("specifications/database-migration.json")
        self.assertEqual(contract["tool_boundary"]["product"], "Flyway Community")
        self.assertTrue(contract["configuration"]["outOfOrder"])
        self.assertEqual(
            contract["migration_naming"]["versioned_pattern"],
            "VyyyyMMddHHmmss__description.sql",
        )
        self.assertEqual(
            contract["transactional_outbox"]["delivery_framework"],
            "Debezium Outbox Event Router",
        )

    def test_machine_node_is_documentary_navigation(self) -> None:
        node = load("machine-node.json")
        self.assertEqual(node["runtime_effect"], "none")
        self.assertEqual(
            node["repository_role"],
            "vendor_evaluation_requirements_and_data_contracts",
        )
        for surface in node["primary_surfaces"]:
            self.assertTrue((ROOT / surface["path"]).is_file())
        self.assertTrue((ROOT / node["quarantine"]).is_file())

if __name__ == "__main__":
    unittest.main()

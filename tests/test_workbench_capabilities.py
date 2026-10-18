"""Independent examples and counterexamples for the composition contract."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]


class WorkbenchCapabilitiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads((ROOT / "schemas/workbench-capabilities.v1.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema)
        cls.examples = {
            name: json.loads((ROOT / f"examples/workbench-capabilities/{name}.json").read_text())
            for name in ("process-local", "postgresql")
        }

    def test_declared_adapters_and_optional_package_states(self) -> None:
        for name, document in self.examples.items():
            for compatible in (False, True):
                with self.subTest(adapter=name, compatible=compatible):
                    candidate = deepcopy(document)
                    candidate["shared_contracts"]["version_compatible"] = compatible
                    self.validator.validate(candidate)

    def test_adapter_and_lifetime_agree(self) -> None:
        for name, lifetime in (("process-local", "database"), ("postgresql", "process")):
            with self.subTest(adapter=name):
                candidate = deepcopy(self.examples[name])
                candidate["runtime"]["state_lifetime"] = lifetime
                with self.assertRaises(ValidationError):
                    self.validator.validate(candidate)

    def test_local_reference_projection_keeps_sensitive_configuration_at_its_owner(self) -> None:
        for parent in (None, "runtime", "shared_contracts"):
            with self.subTest(parent=parent):
                candidate = deepcopy(self.examples["postgresql"])
                target = candidate if parent is None else candidate[parent]
                target["connection_string"] = "fixture-only"
                with self.assertRaises(ValidationError):
                    self.validator.validate(candidate)

    def test_each_required_field_has_independent_admission(self) -> None:
        original = self.examples["process-local"]
        for key in original:
            with self.subTest(field=key):
                candidate = deepcopy(original)
                del candidate[key]
                with self.assertRaises(ValidationError):
                    self.validator.validate(candidate)

    def test_route_and_authority_counterexamples(self) -> None:
        cases = (
            (("runtime", "access_scope"), "remote_authenticated"),
            (("shared_contracts", "version_compatible"), 1),
            (("shared_contracts", "expected_package_version"), "0.6.1\n"),
            (("operations", "summary", "path"), "/administrative/studies"),
            (("operations", "golden_specimen", "tenant_context"), "implicit"),
            (("administrative_interface",), "http"),
        )
        for path, value in cases:
            with self.subTest(path=path, value=value):
                candidate = deepcopy(self.examples["process-local"])
                parent = candidate
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = value
                with self.assertRaises(ValidationError):
                    self.validator.validate(candidate)


if __name__ == "__main__":
    unittest.main()

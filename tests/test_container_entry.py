"""The installed-resource exercise requires every declared public family."""
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "infra"), str(ROOT / "src")]
spec = importlib.util.spec_from_file_location("finite_program_entry", ROOT / "infra/container_entry.py")
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)
from lims_eln_contracts import resources
from container_runtime import publish
from container_wheel_provenance import require_wheel_provenance

REQUIRED_FAMILIES = (
    "operations.v1.json",
    "scenarios/golden-specimen.v1.json",
    "observations/golden-specimen.implementation.v1.json",
    "observations/golden-specimen.simulation.v1.json",
    "external-administrative-contracts.v1.json",
    "administrative/insurance-administrative-adapter.v1.json",
    "administrative/independent-multilabel-policy.v1.json",
    "administrative/administrative-counterfactual.v1.json",
)


class ProgramEntryTests(unittest.TestCase):
    def test_installed_wheel_runs_outside_the_source_import_path(self):
        code = '''import json, pathlib, runpy, sys
from importlib.metadata import distribution, version
import lims_eln_contracts
verify = runpy.run_path(sys.argv[3])["require_wheel_provenance"]
verify(distribution("lims-eln-program-specification"), pathlib.Path(lims_eln_contracts.__file__), pathlib.Path(sys.argv[1]).parent)
sys.path.insert(0, sys.argv[1])
import container_entry as entry
from container_runtime import publish
root = pathlib.Path(sys.argv[2])
receipt = publish(entry.produce, root)
document = json.loads((root / receipt["directory"] / "payload/resources.json").read_bytes())
print(json.dumps({"installed": version("lims-eln-program-specification"),
                  "reported": document["packageVersion"],
                  "schemas": len(document["schemas"]), "families": len(document["resources"])}))
'''
        with tempfile.TemporaryDirectory() as temporary:
            observed = subprocess.run(
                [sys.executable, "-I", "-B", "-c", code, str(ROOT / "infra"), temporary, str(ROOT / "tests/container_wheel_provenance.py")],
                cwd=temporary, capture_output=True, text=True, timeout=15, check=True,
            )
            self.assertEqual(json.loads(observed.stdout), {
                "installed": "0.6.1", "reported": "0.6.1", "schemas": 12, "families": 8,
            })

    def test_provenance_distinguishes_editable_and_source_ownership(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            installed = root / "installed"
            checkout.mkdir()
            installed.mkdir()
            package = installed / "__init__.py"
            package.write_text("fixture", encoding="utf-8")
            source = checkout / "__init__.py"
            source.write_text("fixture", encoding="utf-8")
            for case in ("wheel", "editable", "source", "mismatched-owner", "missing-wheel"):
                with self.subTest(case=case):
                    class Distribution:
                        def read_text(self, name):
                            if name == "WHEEL":
                                return None if case == "missing-wheel" else "Wheel-Version: 1.0\n"
                            return json.dumps({"dir_info": {"editable": True}}) if case == "editable" else "{}"
                        def locate_file(self, _name):
                            return source if case == "source" else package
                    actual = source if case in ("source", "mismatched-owner") else package
                    if case == "wheel":
                        require_wheel_provenance(Distribution(), actual, checkout)
                    else:
                        with self.assertRaises(ValueError):
                            require_wheel_provenance(Distribution(), actual, checkout)

    def test_all_public_families_reach_the_output(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(entry, "version", return_value="fixture-version"):
            output = Path(temporary)
            entry.produce(output)
            result = json.loads((output / "resources.json").read_bytes())
            self.assertEqual(len(result["schemas"]), 12)
            self.assertEqual(set(result["resources"]), {
                "operationCatalog", "goldenScenario", "implementationObservation", "simulationObservation",
                "externalAdministrativeContractSet", "administrativeAdapter", "independentMultilabelPolicy",
                "administrativeCounterfactual",
            })
            self.assertEqual(result["packageVersion"], "fixture-version")

    def test_missing_resource_prevents_publication(self):
        original = resources._resource_bytes
        for missing in REQUIRED_FAMILIES + ("schemas/operation-catalog.v1.schema.json",):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                def selected_resource(path):
                    if path == missing:
                        raise FileNotFoundError("required-resource-fixture")
                    return original(path)
                with patch.object(resources, "_resource_bytes", selected_resource), patch.object(entry, "version", return_value="fixture-version"):
                    with self.assertRaisesRegex(FileNotFoundError, "required-resource-fixture"):
                        publish(entry.produce, root)
                self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

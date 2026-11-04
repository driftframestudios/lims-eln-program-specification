"""Installed lifecycle resources and optional dependency boundary."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LifecyclePackageTests(unittest.TestCase):
    def test_installed_api_and_authored_schema_closure(self):
        code = '''import json, pathlib, runpy, sys
from importlib.metadata import distribution
import lims_eln_contracts as package
from lims_eln_contracts import database_lifecycle as owner
root = pathlib.Path(sys.argv[1])
verify = runpy.run_path(str(root / "tests/container_wheel_provenance.py"))["require_wheel_provenance"]
verify(distribution("lims-eln-program-specification"), pathlib.Path(package.__file__), root)
assert not pathlib.Path(owner.__file__).resolve().is_relative_to(root)
assert package.__version__ == "0.7.0"
assert len(package.SCHEMA_RESOURCE_NAMES) == 12
for name in package.AUTHORED_SCHEMA_RESOURCE_NAMES:
    assert package.authored_schema_bytes(name) == (root / "schemas" / name).read_bytes()
source = owner.LifecycleSource("ref:synthetic-program-source", "1" * 40, owner.SCHEMA_DIGEST)
result = owner.admit_lifecycle_profile((root / "examples/database-lifecycle/disposable.json").read_bytes(), expected_source=source)
assert (result.resource_state, result.executed_operations, result.unresolved_resource_refs) == ("removed", 3, ())
print("installed_lifecycle_admitted")
'''
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(ROOT)], cwd=temporary, capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual("installed_lifecycle_admitted", result.stdout.strip())

    def test_base_import_keeps_lifecycle_dependency_optional(self):
        code = '''import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name == "jsonschema" or name.startswith("jsonschema."):
        raise ModuleNotFoundError("optional lifecycle dependency absent", name="jsonschema")
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import lims_eln_contracts as package
assert len(package.SCHEMA_RESOURCE_NAMES) == 12
package.load_operation_catalog()
print(package.__version__)
'''
        result = subprocess.run([sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual("0.7.0", result.stdout.strip())

    def test_cli_delegates_to_the_installed_owner(self):
        from scripts import database_lifecycle as entry
        from lims_eln_contracts import database_lifecycle as owner
        self.assertIs(owner.admit_lifecycle_profile, entry.admit_lifecycle_profile)
        self.assertIs(owner.LifecycleSource, entry.LifecycleSource)

    def test_authored_resource_selection_is_closed(self):
        from lims_eln_contracts import authored_schema_bytes
        for name in ("../database-lifecycle-profile.v1.schema.json", "scenario.v1.schema.json", "unknown.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                authored_schema_bytes(name)

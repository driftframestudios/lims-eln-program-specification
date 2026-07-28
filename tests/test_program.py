from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_program", ROOT / "scripts" / "validate_program.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProgramValidationTests(unittest.TestCase):
    def test_complete_program_validates(self) -> None:
        summary = MODULE.validate()
        self.assertEqual(summary["proof_classes"], 4)
        self.assertEqual(summary["repositories"], 5)
        self.assertGreaterEqual(summary["scenarios"], 12)

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


if __name__ == "__main__":
    unittest.main()


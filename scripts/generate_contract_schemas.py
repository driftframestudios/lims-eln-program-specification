#!/usr/bin/env python3
"""Render or verify the released JSON Schemas for the Python contract nucleus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lims_eln_contracts.schema_artifacts import rendered_schema_artifacts  # noqa: E402


SCHEMA_ROOT = ROOT / "src" / "lims_eln_contracts" / "resources" / "schemas"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep committed JSON Schemas aligned with the strict Python models."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify byte-identical committed schemas and preserve the working tree.",
    )
    arguments = parser.parse_args()

    artifacts = rendered_schema_artifacts()
    if arguments.check:
        divergent = [
            filename
            for filename, expected in artifacts.items()
            if not (SCHEMA_ROOT / filename).exists()
            or (SCHEMA_ROOT / filename).read_bytes() != expected
        ]
        if divergent:
            print(
                json.dumps(
                    {
                        "status": "schema_refresh_required",
                        "artifacts": divergent,
                        "next_action": "run scripts/generate_contract_schemas.py",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
        print(
            json.dumps(
                {"status": "schemas_current", "artifacts": len(artifacts)},
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    SCHEMA_ROOT.mkdir(parents=True, exist_ok=True)
    for filename, content in artifacts.items():
        (SCHEMA_ROOT / filename).write_bytes(content)
    print(
        json.dumps(
            {"status": "schemas_rendered", "artifacts": len(artifacts)},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


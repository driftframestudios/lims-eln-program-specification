#!/usr/bin/env python3
"""Render or verify the released JSON Schemas for the Python contract nucleus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lims_eln_contracts.resources import AUTHORED_SCHEMA_RESOURCE_NAMES  # noqa: E402
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
    authored_root = ROOT / "src/lims_eln_contracts/resources/authored-schemas"
    authored = {name: (ROOT / "schemas" / name).read_bytes() for name in AUTHORED_SCHEMA_RESOURCE_NAMES}
    destinations = {SCHEMA_ROOT / name: data for name, data in artifacts.items()}
    destinations.update({authored_root / name: data for name, data in authored.items()})
    if arguments.check:
        divergent = [
            path.relative_to(ROOT).as_posix()
            for path, expected in destinations.items()
            if not path.exists() or path.read_bytes() != expected
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
                {"status": "schemas_current", "artifacts": len(artifacts), "authored_companions": len(authored)},
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    for path, content in destinations.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(
        json.dumps(
            {"status": "schemas_rendered", "artifacts": len(artifacts), "authored_companions": len(authored)},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


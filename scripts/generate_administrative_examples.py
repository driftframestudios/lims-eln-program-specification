#!/usr/bin/env python3
"""Render or verify reader-specific administrative example projections."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "src" / "lims_eln_contracts" / "resources"
CANONICAL_BUNDLE = RESOURCE_ROOT / "external-administrative-contracts.v1.json"


def _json_bytes(document: object) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def rendered_administrative_examples() -> dict[str, bytes]:
    """Derive the three reader-specific examples from one canonical bundle."""

    bundle = json.loads(CANONICAL_BUNDLE.read_text(encoding="utf-8"))
    independent = deepcopy(bundle)
    independent["contract_set_id"] = (
        "EXTERNAL-ADMINISTRATIVE-INDEPENDENT-EXAMPLE-V1"
    )
    independent["source_manifests"] = []
    independent["provenance_assertions"] = [
        assertion
        for assertion in independent["provenance_assertions"]
        if assertion["assertion_id"] != "PROV-SOURCE-MANIFEST-001"
    ]

    return {
        "administrative/synthetic-hospital-v1.3.v1.json": _json_bytes(
            bundle["source_manifests"][0]
        ),
        "administrative/independent-multilabel-policy.v1.json": _json_bytes(
            independent
        ),
        "administrative/administrative-counterfactual.v1.json": _json_bytes(
            bundle["impact_observations"][0]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep committed administrative examples aligned with the canonical "
            "dependency-closed contract bundle."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify byte-identical projections and preserve the working tree.",
    )
    arguments = parser.parse_args()

    artifacts = rendered_administrative_examples()
    if arguments.check:
        divergent = [
            relative_path
            for relative_path, expected in artifacts.items()
            if not (RESOURCE_ROOT / relative_path).exists()
            or (RESOURCE_ROOT / relative_path).read_bytes() != expected
        ]
        if divergent:
            print(
                json.dumps(
                    {
                        "status": "administrative_example_refresh_required",
                        "artifacts": divergent,
                        "next_action": "run scripts/generate_administrative_examples.py",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "status": "administrative_examples_current",
                    "artifacts": len(artifacts),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    for relative_path, content in artifacts.items():
        target = RESOURCE_ROOT / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    print(
        json.dumps(
            {
                "status": "administrative_examples_rendered",
                "artifacts": len(artifacts),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

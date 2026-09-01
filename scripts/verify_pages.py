#!/usr/bin/env python3
"""Build Program Pages twice and verify identity, contracts, and safe output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from pages_projection import (
    ROOT,
    ProjectionError,
    build_projection,
    snapshot_projection,
    validate_projection,
    verify_clean_source,
)
from scan_secret_shapes import scan_repository


def verify_pages(
    *,
    root: Path = ROOT,
    canonical_origin: str | None = None,
    cname: str | None = None,
) -> dict[str, object]:
    """Return a normalized receipt for two complete local builds."""

    proof = verify_clean_source(root)
    with tempfile.TemporaryDirectory(prefix="program-pages-") as temporary:
        base = Path(temporary)
        first = base / "first"
        second = base / "second"
        build_projection(
            first,
            root=root,
            canonical_origin=canonical_origin,
            cname=cname,
            source_proof=proof,
        )
        build_projection(
            second,
            root=root,
            canonical_origin=canonical_origin,
            cname=cname,
            source_proof=proof,
        )
        first_summary = validate_projection(first, root=root)
        second_summary = validate_projection(second, root=root)
        if snapshot_projection(first) != snapshot_projection(second):
            raise ProjectionError("isolated builds differ by inventory or bytes")
        secret_findings = [*scan_repository(first), *scan_repository(second)]
        if secret_findings:
            raise ProjectionError(
                "generated projection contains credential-shaped values"
            )
    return {
        "deterministicBuilds": 2,
        "filesPerBuild": first_summary["files"],
        "htmlPagesPerBuild": first_summary["htmlPages"],
        "publicSkills": first_summary["publicSkills"],
        "secretShapeFindings": 0,
        "sourceRevision": proof.revision,
        "sourceStanding": proof.standing,
        "status": "valid",
        "validationReceipts": int(
            first_summary["status"] == second_summary["status"] == "valid"
        )
        * 2,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-origin")
    parser.add_argument("--cname")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = verify_pages(
            canonical_origin=args.canonical_origin,
            cname=args.cname,
        )
    except ProjectionError as error:
        raise SystemExit(f"Program Pages aggregate failed: {error}") from error
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

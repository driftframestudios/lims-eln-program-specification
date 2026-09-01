#!/usr/bin/env python3
"""Build the deterministic Program Pages candidate from repository source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pages_projection import ProjectionError, build_projection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--canonical-origin")
    parser.add_argument("--cname")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_projection(
            args.output,
            canonical_origin=args.canonical_origin,
            cname=args.cname,
        )
    except ProjectionError as error:
        raise SystemExit(f"Program Pages build failed: {error}") from error
    print(
        json.dumps(
            {
                "canonicalOrigin": manifest["canonicalOrigin"],
                "files": len(manifest["files"]),
                "sourceRevision": manifest["sourceRevision"],
                "sourceStanding": manifest["sourceStanding"],
                "status": "built",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

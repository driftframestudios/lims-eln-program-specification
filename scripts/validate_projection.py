#!/usr/bin/env python3
"""Validate one Program Pages projection against its exact repository source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pages_projection import ProjectionError, validate_projection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projection", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate_projection(args.projection)
    except ProjectionError as error:
        raise SystemExit(f"Program Pages validation failed: {error}") from error
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

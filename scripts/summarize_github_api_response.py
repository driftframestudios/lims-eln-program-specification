#!/usr/bin/env python3
"""Reduce one GitHub API response to a fixed, non-sensitive diagnostic."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Final


MAX_INPUT_BYTES: Final = 262_144
STATUS_PATTERN: Final = re.compile(
    r"^HTTP/(?:\d+(?:\.\d+)?)\s+(?P<status>\d{3})(?:\s|$)",
    re.IGNORECASE,
)
CONTENTS_READ_PATTERN: Final = re.compile(
    r"(?:^|[,;\s])contents=read(?:$|[,;\s])",
    re.IGNORECASE,
)
OBSERVED_HEADERS: Final = {
    "retry-after",
    "x-accepted-github-permissions",
    "x-github-sso",
    "x-ratelimit-remaining",
}


def _last_response_headers(text: str) -> tuple[str, dict[str, list[str]]]:
    status = "unavailable"
    headers: dict[str, list[str]] = {}
    reading_headers = False

    for line in text.splitlines():
        status_match = STATUS_PATTERN.match(line)
        if status_match:
            status = status_match.group("status")
            headers = {}
            reading_headers = True
            continue

        if not reading_headers:
            continue
        if not line.strip():
            reading_headers = False
            continue
        if line[:1] in {" ", "\t"} or ":" not in line:
            continue

        name, value = line.split(":", 1)
        normalized_name = name.strip().lower()
        if normalized_name in OBSERVED_HEADERS:
            headers.setdefault(normalized_name, []).append(value.strip())

    return status, headers


def summarize_response(text: str) -> dict[str, str]:
    status, headers = _last_response_headers(text)

    remaining_values = headers.get("x-ratelimit-remaining", [])
    if not remaining_values:
        primary_rate = "unreported"
    elif remaining_values[-1].isdigit():
        primary_rate = "zero" if int(remaining_values[-1]) == 0 else "positive"
    else:
        primary_rate = "invalid"

    accepted_values = headers.get("x-accepted-github-permissions", [])
    if not accepted_values:
        accepted_permission = "unreported"
    elif any(CONTENTS_READ_PATTERN.search(value) for value in accepted_values):
        accepted_permission = "contents_read_required"
    else:
        accepted_permission = "other_reported"

    return {
        "accepted_permission": accepted_permission,
        "primary_rate": primary_rate,
        "retry_after": (
            "present" if headers.get("retry-after") else "unreported"
        ),
        "sso": "present" if headers.get("x-github-sso") else "unreported",
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a fixed diagnostic for one captured GitHub API response."
    )
    parser.add_argument("response", type=Path)
    args = parser.parse_args()

    if args.response.is_symlink() or not args.response.is_file():
        raise SystemExit("response path must identify a regular file")
    with args.response.open("rb") as response_stream:
        response_bytes = response_stream.read(MAX_INPUT_BYTES)
    response_text = response_bytes.decode("utf-8", errors="replace")
    print(json.dumps(summarize_response(response_text), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

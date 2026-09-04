from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "summarize_github_api_response.py"
SPEC = importlib.util.spec_from_file_location("github_api_diagnostics", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GitHubApiDiagnosticTests(unittest.TestCase):
    def test_last_response_is_normalized_without_carrying_raw_material(self) -> None:
        response = """HTTP/2 301 Moved Permanently
X-RateLimit-Remaining: 41

HTTP/2 403 Forbidden
x-RaTeLiMiT-ReMaInInG: 0
Retry-After: 60
X-GitHub-SSO: required; url=https://example.invalid/private-sentinel
X-Accepted-GitHub-Permissions: metadata=read, contents=read
Authorization: diagnostic-header-sentinel

{"message":"body-sentinel"}
"""

        summary = MODULE.summarize_response(response)

        self.assertEqual(
            {
                "accepted_permission": "contents_read_required",
                "primary_rate": "zero",
                "retry_after": "present",
                "sso": "present",
                "status": "403",
            },
            summary,
        )
        serialized = json.dumps(summary, sort_keys=True)
        for sentinel in (
            "private-sentinel",
            "diagnostic-header-sentinel",
            "body-sentinel",
            "X-GitHub-SSO",
            "Retry-After",
        ):
            self.assertNotIn(sentinel, serialized)

    def test_positive_rate_and_other_permission_remain_bounded(self) -> None:
        summary = MODULE.summarize_response(
            "HTTP/2 403 Forbidden\r\n"
            "X-RateLimit-Remaining: 4999\r\n"
            "X-Accepted-GitHub-Permissions: issues=read\r\n\r\n"
        )

        self.assertEqual("positive", summary["primary_rate"])
        self.assertEqual("other_reported", summary["accepted_permission"])
        self.assertEqual("unreported", summary["retry_after"])
        self.assertEqual("unreported", summary["sso"])

    def test_unavailable_and_invalid_values_use_fixed_states(self) -> None:
        self.assertEqual(
            {
                "accepted_permission": "unreported",
                "primary_rate": "unreported",
                "retry_after": "unreported",
                "sso": "unreported",
                "status": "unavailable",
            },
            MODULE.summarize_response("response-body-only"),
        )
        summary = MODULE.summarize_response(
            "HTTP/2 403 Forbidden\nX-RateLimit-Remaining: many\n\n"
        )
        self.assertEqual("invalid", summary["primary_rate"])


if __name__ == "__main__":
    unittest.main()

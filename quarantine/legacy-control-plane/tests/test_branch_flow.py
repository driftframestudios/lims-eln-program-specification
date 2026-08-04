"""Regression tests for program branch coordinates."""

from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "program_check_branch_flow",
    ROOT / "scripts" / "check_branch_flow.py",
)
assert SPEC and SPEC.loader
check_branch_flow = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_branch_flow
SPEC.loader.exec_module(check_branch_flow)


class BranchFlowTests(unittest.TestCase):
    def invoke(self, base: str, head: str, author: str) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            result = check_branch_flow.main(
                ["--base", base, "--head", head, "--author", author]
            )
        return result, output.getvalue()

    def test_non_pull_request_and_partial_coordinates(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(0, check_branch_flow.main([]))
        self.assertIn("non-pull-request", output.getvalue())
        output = StringIO()
        with redirect_stdout(output):
            result = check_branch_flow.main(
                ["--base", "main", "--head", "release/0.3.1"]
            )
        self.assertEqual(2, result)

    def test_dependabot_requires_bot_identity_and_governed_target(self) -> None:
        head = "dependabot/github_actions/actions/setup-python-7.0.0"
        result, output = self.invoke("main", head, "dependabot[bot]")
        self.assertEqual(0, result)
        self.assertIn("Dependabot branch", output)
        self.assertEqual(1, self.invoke("main", head, "contributor")[0])
        self.assertEqual(1, self.invoke("release/0.3.1", head, "dependabot[bot]")[0])

    def test_renovate_requires_bot_identity(self) -> None:
        result, output = self.invoke(
            "develop", "renovate/github-actions-minor", "renovate[bot]"
        )
        self.assertEqual(0, result)
        self.assertIn("Renovate branch", output)
        self.assertEqual(
            1,
            self.invoke(
                "develop",
                "renovate/github-actions-minor",
                "self-hosted-renovate[bot]",
            )[0],
        )

    def test_malformed_automation_path_is_rejected(self) -> None:
        result, output = self.invoke(
            "main",
            "dependabot/github_actions/actions/../release",
            "dependabot[bot]",
        )
        self.assertEqual(1, result)
        self.assertIn("outside the branch naming contract", output)

    def test_configured_ecosystem_matches_branch_grammar(self) -> None:
        config = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        configured = {
            item.replace("-", "_")
            for item in re.findall(
                r"^\s*-\s+package-ecosystem:\s*[\"']?([a-z0-9-]+)",
                config,
                flags=re.MULTILINE,
            )
        }
        self.assertEqual(check_branch_flow.DEPENDABOT_BRANCH_ECOSYSTEMS, configured)
        self.assertNotIn("pull-request-branch-name:", config)
        self.assertEqual(
            1,
            self.invoke(
                "main",
                "dependabot/pip/urllib3-3.0.0",
                "dependabot[bot]",
            )[0],
        )

    def test_feature_branch_routes_through_develop(self) -> None:
        head = "feature/practitioner-control-plane-v0-3"
        self.assertEqual(0, self.invoke("develop", head, "contributor")[0])
        self.assertEqual(1, self.invoke("main", head, "contributor")[0])

    def test_workflow_executes_only_the_base_controlled_checker(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "branch-policy.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("pull_request_target:", workflow)
        self.assertIn(
            "ref: ${{ github.event.pull_request.base.sha }}",
            workflow,
        )
        self.assertIn("repository: ${{ github.repository }}", workflow)
        self.assertIn("path: .branch-policy-base", workflow)
        self.assertIn("sparse-checkout: scripts/check_branch_flow.py", workflow)
        self.assertIn("sparse-checkout-cone-mode: false", workflow)
        self.assertIn("working-directory: .branch-policy-base", workflow)
        self.assertIn(
            "HEAD_REF: ${{ github.event.pull_request.head.ref }}",
            workflow,
        )
        self.assertIn(
            "PR_AUTHOR: ${{ github.event.pull_request.user.login }}",
            workflow,
        )
        self.assertIn('--author "$PR_AUTHOR"', workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertEqual(1, workflow.count("actions/checkout@"))
        self.assertNotIn("github.event.pull_request.head.sha", workflow)


if __name__ == "__main__":
    unittest.main()

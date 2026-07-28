#!/usr/bin/env python3
"""Validate immutable constellation coordinates and canonical closure equality."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    "specification",
    "simulation",
    "implementation",
    "comparison",
    "governance",
}
EXTERNAL_ROLES = ROLES - {"specification"}
ZERO_COMMIT = "0" * 40
ZERO_TREE = "git-tree-sha1:" + ("0" * 40)
COMMIT = re.compile(r"^(?!0{40}$)[a-f0-9]{40}$")
TREE = re.compile(r"^git-tree-sha1:(?!0{40}$)[a-f0-9]{40}$")


def canonical_digest(document: object) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def git_identity(root: Path) -> tuple[str, str]:
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD^{tree}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return commit, f"git-tree-sha1:{tree}"


def validate_sources(
    lock: dict,
    sources: dict[str, Path],
    *,
    allow_pending: bool,
) -> list[str]:
    findings: list[str] = []
    unknown_sources = set(sources) - EXTERNAL_ROLES
    if unknown_sources:
        findings.append(
            f"source roles fall outside the external constellation: "
            f"{sorted(unknown_sources)}"
        )

    for role in sorted(ROLES):
        coordinate = lock.get(role)
        if not isinstance(coordinate, dict):
            findings.append(f"{role} coordinate is absent or malformed")
            continue
        status = coordinate.get("coordinate_status")
        commit = coordinate.get("commit")
        digest = coordinate.get("digest")
        if status == "pending_release_commit":
            if commit != ZERO_COMMIT or digest != ZERO_TREE:
                findings.append(f"{role} pending coordinate must use zero placeholders")
            if not allow_pending:
                findings.append(f"{role} requires a pinned release coordinate")
            continue
        if status != "pinned":
            findings.append(f"{role} coordinate status is unsupported")
            continue
        if not isinstance(commit, str) or COMMIT.fullmatch(commit) is None:
            findings.append(f"{role} pinned commit is malformed")
        if not isinstance(digest, str) or TREE.fullmatch(digest) is None:
            findings.append(f"{role} pinned tree digest is malformed")
        if role == "specification":
            continue
        source = sources.get(role)
        if source is None:
            findings.append(f"{role} pinned coordinate requires a checked-out source")
            continue
        if not source.is_dir():
            findings.append(f"{role} source directory is absent: {source}")
            continue
        try:
            actual_commit, actual_tree = git_identity(source)
        except (OSError, subprocess.CalledProcessError) as exc:
            findings.append(f"{role} source identity is unreadable: {exc}")
            continue
        if actual_commit != commit:
            findings.append(f"{role} source commit differs from its lock")
        if actual_tree != digest:
            findings.append(f"{role} source tree differs from its lock")

    canonical = json.loads(
        (ROOT / "simulations/simulated-receipt-closure.v2.json").read_text(
            encoding="utf-8"
        )
    )
    canonical_bundle_path = (
        ROOT / "simulations/future-reality-2028-06-30-v1.json"
    )
    canonical_bundle = json.loads(
        canonical_bundle_path.read_text(encoding="utf-8")
    )
    expected_digest = canonical_digest(canonical)
    expected_result_digest = (
        "sha256:9d42b972c77764c81ff32fefe8f02367a27406e9ba082a704587cc9b5a9da860"
    )
    expected_aggregate_digest = (
        "sha256:2d8e67ec2da8236fc23de7943e7727d2b74e0e6ee2b15afd9c765443b9c52b61"
    )
    expected_bundle_file_digest = (
        "sha256:" + hashlib.sha256(canonical_bundle_path.read_bytes()).hexdigest()
    )
    if lock.get("simulation", {}).get("canonical_closure_digest") != expected_digest:
        findings.append("simulation lock canonical closure digest differs")
    if (
        lock.get("simulation", {}).get("reference_result_digest")
        != expected_result_digest
    ):
        findings.append("simulation lock reference result digest differs")
    if (
        lock.get("simulation", {}).get("aggregate_artifact_digest")
        != expected_aggregate_digest
    ):
        findings.append("simulation lock aggregate artifact digest differs")
    if (
        lock.get("simulation", {}).get("canonical_bundle_file_digest")
        != expected_bundle_file_digest
    ):
        findings.append("simulation lock canonical bundle file digest differs")
    if lock.get("comparison", {}).get("canonical_closure_digest") != expected_digest:
        findings.append("comparison lock canonical closure digest differs")
    if (
        lock.get("comparison", {}).get("aggregate_artifact_digest")
        != expected_aggregate_digest
    ):
        findings.append("comparison lock aggregate artifact digest differs")
    if (
        canonical_bundle.get("bundle_version") != "2.0.1"
        or canonical_bundle.get("source_result_digest")
        != expected_result_digest
        or canonical_bundle.get("governance_closure") != canonical
        or canonical_bundle.get("governance_closure_digest") != expected_digest
    ):
        findings.append("program canonical bundle contract differs")

    simulation_source = sources.get("simulation")
    if simulation_source is not None:
        source_path = (
            simulation_source
            / "build"
            / "simulation"
            / "simulated-receipt-closure.json"
        )
        if not source_path.is_file():
            findings.append("simulation canonical closure artifact is absent")
        else:
            simulation_closure = json.loads(source_path.read_text(encoding="utf-8"))
            if simulation_closure != canonical:
                findings.append("simulation canonical closure differs from program")
        manifest_path = simulation_source / "release" / "repository-role.json"
        if not manifest_path.is_file():
            findings.append("simulation release manifest is absent")
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("reference_result_digest") != expected_result_digest:
                findings.append("simulation reference result digest differs")
            if manifest.get("reference_closure_digest") != expected_digest:
                findings.append("simulation reference closure digest differs")
        result_path = simulation_source / "build" / "simulation" / "result.json"
        if result_path.is_file():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("content_digest") != expected_result_digest:
                findings.append(
                    "simulation result content digest differs from canonical bundle"
                )

    comparison_source = sources.get("comparison")
    if comparison_source is not None:
        source_path = (
            comparison_source
            / "fixtures"
            / "simulated-closures"
            / "future-reality-2028-06-30-v1.json"
        )
        if not source_path.is_file():
            findings.append("comparison canonical closure fixture is absent")
        else:
            source_bytes = source_path.read_bytes()
            bundle = json.loads(source_bytes)
            if source_bytes != canonical_bundle_path.read_bytes():
                findings.append("comparison canonical bundle bytes differ from program")
            if bundle.get("governance_closure") != canonical:
                findings.append("comparison canonical closure differs from program")
            if bundle.get("governance_closure_digest") != expected_digest:
                findings.append("comparison canonical closure digest differs")

    governance_source = sources.get("governance")
    if governance_source is not None:
        version_path = governance_source / "VERSION"
        if not version_path.is_file():
            findings.append("governance VERSION record is absent")
        elif version_path.read_text(encoding="utf-8").strip() != "2.0.1":
            findings.append("governance VERSION differs from 2.0.1")

    return findings


def validate_external_preflight(lock: dict) -> list[str]:
    """Require immutable external coordinates before any repository checkout."""
    findings: list[str] = []
    for role in sorted(EXTERNAL_ROLES):
        coordinate = lock.get(role)
        if not isinstance(coordinate, dict):
            findings.append(f"{role} coordinate is absent or malformed")
            continue
        commit = coordinate.get("commit")
        digest = coordinate.get("digest")
        if coordinate.get("coordinate_status") != "pinned":
            findings.append(f"{role} external coordinate must be pinned")
        if not isinstance(commit, str) or COMMIT.fullmatch(commit) is None:
            findings.append(f"{role} external commit must be nonzero 40-hex")
        if not isinstance(digest, str) or TREE.fullmatch(digest) is None:
            findings.append(f"{role} external tree digest must be nonzero 40-hex")
    governance = lock.get("governance", {})
    if (
        governance.get("release") != "governance-v2.0.1"
        or governance.get("schema_version") != "2.0.1"
    ):
        findings.append("governance coordinate must bind governance-v2.0.1")
    return findings


def parse_source(value: str) -> tuple[str, Path]:
    role, separator, path = value.partition("=")
    if not separator or not role or not path:
        raise argparse.ArgumentTypeError("source must use role=/path syntax")
    return role, Path(path).resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="accept explicit candidate placeholders while retaining strict shapes",
    )
    parser.add_argument(
        "--preflight-external",
        action="store_true",
        help="validate pinned external coordinates before repository checkout",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        type=parse_source,
        metavar="ROLE=PATH",
    )
    arguments = parser.parse_args(argv)
    lock = json.loads((ROOT / "constellation.lock.json").read_text(encoding="utf-8"))
    if arguments.preflight_external:
        findings = validate_external_preflight(lock)
        if findings:
            print("External-coordinate preflight found settlement gaps:")
            for finding in findings:
                print(f"  - {finding}")
            return 1
        print("External-coordinate preflight passed.")
        return 0
    sources = dict(arguments.source)
    findings = validate_sources(
        lock,
        sources,
        allow_pending=arguments.allow_pending,
    )
    if findings:
        print("Pinned-source validation found settlement gaps:")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("Pinned-source validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

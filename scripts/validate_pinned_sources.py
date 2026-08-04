#!/usr/bin/env python3
"""Validate immutable constellation coordinates and canonical closure equality."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import stat
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
SHA256 = re.compile(r"^sha256:[a-f0-9]{64}$")
LANGUAGE_POLICY_RELEASE = "language-policy-v1.0.0"
LANGUAGE_POLICY_MANIFEST = Path("language-policy/manifest.json")
LANGUAGE_POLICY_EXEMPTIONS = Path("language-policy/exemptions.json")
LANGUAGE_POLICY_MANIFEST_DIGEST = (
    "sha256:95087f281455c45608981152948f8909e74528706662625b6e8a4da9e5182a96"
)
LANGUAGE_POLICY_ASSETS = {
    "language-policy-core": {
        "governance_path": "tools/language_policy_core.py",
        "projection_path": "scripts/language_policy_core.py",
    },
    "language-policy-qualification-corpus": {
        "governance_path": "language-policy/corpus-v1.json",
        "projection_path": "language-policy/corpus-v1.json",
    },
}
LANGUAGE_POLICY_MANIFEST_FIELDS = {
    "assets",
    "diagnostic_reason_codes",
    "exemption_contract",
    "exit_contract",
    "fingerprint_contract",
    "format_aliases",
    "manifest_version",
    "output_schema_version",
    "policy_release",
    "rules",
    "supported_formats",
    "surface_kinds",
}


def canonical_digest(document: object) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def bytes_digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


class DuplicateJsonKey(ValueError):
    """Signal a duplicate key in one policy-bearing JSON document."""


def strict_json_loads(content: bytes) -> object:
    """Load standards-compliant JSON with unique keys and finite numbers."""

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateJsonKey("duplicate JSON key")
            result[key] = value
        return result

    def finite_float(token: str) -> float:
        value = float(token)
        if not math.isfinite(value):
            raise ValueError("non-finite JSON number")
        return value

    return json.loads(
        content,
        object_pairs_hook=unique_object,
        parse_float=finite_float,
        parse_constant=lambda _token: (_ for _ in ()).throw(
            ValueError("non-finite JSON token")
        ),
    )


def path_resolves_within(path: Path, root: Path) -> bool:
    """Confirm that one candidate remains inside its declared source root."""
    try:
        path.absolute().relative_to(root.absolute())
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def read_regular_bytes(
    path: Path,
    *,
    root: Path | None = None,
) -> tuple[bytes | None, str | None]:
    """Read a regular file and classify host failures without leaking its path."""
    if root is not None:
        try:
            path.absolute().relative_to(root.absolute())
        except ValueError:
            return None, "OUTSIDE_ROOT"
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "UNREADABLE"
    if stat.S_ISLNK(metadata.st_mode):
        return None, "SYMLINK"
    if root is not None and not path_resolves_within(path, root):
        return None, "OUTSIDE_ROOT"
    if not stat.S_ISREG(metadata.st_mode):
        return None, "NOT_REGULAR_FILE"
    try:
        return path.read_bytes(), None
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "UNREADABLE"


def read_json_document(
    path: Path,
    *,
    root: Path,
) -> tuple[object | None, bytes | None, str | None]:
    """Read one bounded JSON document with stable failure classification."""
    content, failure = read_regular_bytes(path, root=root)
    if failure is not None:
        return None, None, failure
    assert content is not None
    try:
        return strict_json_loads(content), content, None
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        ValueError,
    ):
        return None, content, "INVALID_JSON"


def projection_diagnostic(code: str, description: str) -> str:
    """Create a stable projection finding from a bounded reason code."""
    return f"{code}: {description}"


def validate_language_policy_projection(
    governance_source: Path | None = None,
) -> list[str]:
    """Prove local manifest integrity and optional pinned-governance equality."""
    findings: list[str] = []
    manifest_path = ROOT / LANGUAGE_POLICY_MANIFEST
    manifest_bytes, manifest_failure = read_regular_bytes(
        manifest_path,
        root=ROOT,
    )
    if manifest_failure is not None:
        return [
            projection_diagnostic(
                f"LANGUAGE_POLICY_MANIFEST_{manifest_failure}",
                "language-policy projection manifest could not be loaded",
            )
        ]
    assert manifest_bytes is not None
    try:
        manifest = strict_json_loads(manifest_bytes)
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateJsonKey,
        ValueError,
    ):
        return [
            projection_diagnostic(
                "LANGUAGE_POLICY_MANIFEST_INVALID_JSON",
                "language-policy projection manifest requires valid JSON",
            )
        ]

    if bytes_digest(manifest_bytes) != LANGUAGE_POLICY_MANIFEST_DIGEST:
        findings.append("language-policy projection manifest digest differs")
    if not isinstance(manifest, dict) or set(manifest) != LANGUAGE_POLICY_MANIFEST_FIELDS:
        findings.append("language-policy projection manifest shape differs")
        return findings
    if (
        manifest.get("manifest_version") != "1.0.0"
        or manifest.get("policy_release") != LANGUAGE_POLICY_RELEASE
        or manifest.get("output_schema_version")
        != "language-policy-output-v1"
    ):
        findings.append("language-policy projection manifest version differs")

    assets = manifest.get("assets")
    if not isinstance(assets, list):
        findings.append("language-policy projection assets are malformed")
        return findings
    observed_ids: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict) or set(asset) != {
            "asset_id",
            "governance_path",
            "projection_path",
            "sha256",
        }:
            findings.append("language-policy projection asset shape differs")
            continue
        asset_id = asset.get("asset_id")
        expected = LANGUAGE_POLICY_ASSETS.get(asset_id)
        if expected is None or asset_id in observed_ids:
            findings.append("language-policy projection asset identity differs")
            continue
        observed_ids.add(asset_id)
        if (
            asset.get("governance_path") != expected["governance_path"]
            or asset.get("projection_path") != expected["projection_path"]
            or not isinstance(asset.get("sha256"), str)
            or SHA256.fullmatch(asset["sha256"]) is None
        ):
            findings.append(
                f"language-policy projection mapping differs for {asset_id}"
            )
            continue
        projected_path = ROOT / expected["projection_path"]
        projected_bytes, projected_failure = read_regular_bytes(
            projected_path,
            root=ROOT,
        )
        if projected_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"LANGUAGE_POLICY_ASSET_{projected_failure}",
                    f"projected asset {asset_id} could not be loaded",
                )
            )
            continue
        assert projected_bytes is not None
        if bytes_digest(projected_bytes) != asset["sha256"]:
            findings.append(
                f"language-policy projected asset digest differs for {asset_id}"
            )
        if governance_source is not None:
            governance_path = governance_source / expected["governance_path"]
            governance_bytes, governance_failure = read_regular_bytes(
                governance_path,
                root=governance_source,
            )
            if governance_failure is not None:
                findings.append(
                    projection_diagnostic(
                        f"GOVERNANCE_LANGUAGE_POLICY_ASSET_{governance_failure}",
                        f"governance asset {asset_id} could not be loaded",
                    )
                )
            elif projected_bytes != governance_bytes:
                findings.append(
                    f"language-policy projected bytes differ from governance "
                    f"for {asset_id}"
                )
    if observed_ids != set(LANGUAGE_POLICY_ASSETS):
        findings.append("language-policy projection asset set differs")

    exemption_path = ROOT / LANGUAGE_POLICY_EXEMPTIONS
    _, exemption_failure = read_regular_bytes(exemption_path, root=ROOT)
    if exemption_failure is not None:
        findings.append(
            projection_diagnostic(
                f"LANGUAGE_POLICY_EXEMPTION_REGISTRY_{exemption_failure}",
                "language-policy exemption registry could not be loaded",
            )
        )

    if governance_source is not None:
        governance_manifest = governance_source / LANGUAGE_POLICY_MANIFEST
        governance_manifest_bytes, governance_manifest_failure = (
            read_regular_bytes(
                governance_manifest,
                root=governance_source,
            )
        )
        if governance_manifest_failure is not None:
            findings.append(
                projection_diagnostic(
                    "GOVERNANCE_LANGUAGE_POLICY_MANIFEST_"
                    f"{governance_manifest_failure}",
                    "governance language-policy manifest could not be loaded",
                )
            )
        elif manifest_bytes != governance_manifest_bytes:
            findings.append(
                "language-policy projection manifest bytes differ from governance"
            )
    return findings


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
    findings = validate_language_policy_projection(sources.get("governance"))
    unknown_sources = set(sources) - EXTERNAL_ROLES
    if unknown_sources:
        findings.append(
            projection_diagnostic(
                "SOURCE_ROLE_UNRECOGNIZED",
                "a supplied source role falls outside the external constellation",
            )
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
        if source.is_symlink():
            findings.append(
                projection_diagnostic(
                    "SOURCE_DIRECTORY_SYMLINK",
                    f"{role} source requires a checked-out regular directory",
                )
            )
            continue
        if not source.is_dir():
            findings.append(
                projection_diagnostic(
                    "SOURCE_DIRECTORY_MISSING",
                    f"{role} source directory is absent",
                )
            )
            continue
        try:
            actual_commit, actual_tree = git_identity(source)
        except (OSError, subprocess.CalledProcessError):
            findings.append(
                projection_diagnostic(
                    "SOURCE_IDENTITY_UNREADABLE",
                    f"{role} source identity could not be read",
                )
            )
            continue
        if actual_commit != commit:
            findings.append(f"{role} source commit differs from its lock")
        if actual_tree != digest:
            findings.append(f"{role} source tree differs from its lock")

    canonical_path = ROOT / "simulations/simulated-receipt-closure.v2.json"
    canonical, _, canonical_failure = read_json_document(
        canonical_path,
        root=ROOT,
    )
    canonical_bundle_path = (
        ROOT / "simulations/future-reality-2028-06-30-v1.json"
    )
    canonical_bundle, canonical_bundle_bytes, bundle_failure = read_json_document(
        canonical_bundle_path,
        root=ROOT,
    )
    if canonical_failure is not None:
        findings.append(
            projection_diagnostic(
                f"PROGRAM_CANONICAL_CLOSURE_{canonical_failure}",
                "program canonical closure could not be loaded",
            )
        )
    if bundle_failure is not None:
        findings.append(
            projection_diagnostic(
                f"PROGRAM_CANONICAL_BUNDLE_{bundle_failure}",
                "program canonical bundle could not be loaded",
            )
        )
    if canonical_failure is not None or bundle_failure is not None:
        return findings
    if not isinstance(canonical, dict):
        findings.append(
            projection_diagnostic(
                "PROGRAM_CANONICAL_CLOSURE_INVALID_SHAPE",
                "program canonical closure requires a JSON object",
            )
        )
    if not isinstance(canonical_bundle, dict):
        findings.append(
            projection_diagnostic(
                "PROGRAM_CANONICAL_BUNDLE_INVALID_SHAPE",
                "program canonical bundle requires a JSON object",
            )
        )
    if not isinstance(canonical, dict) or not isinstance(canonical_bundle, dict):
        return findings
    assert canonical_bundle_bytes is not None
    expected_digest = canonical_digest(canonical)
    expected_result_digest = (
        "sha256:9d42b972c77764c81ff32fefe8f02367a27406e9ba082a704587cc9b5a9da860"
    )
    expected_aggregate_digest = (
        "sha256:2d8e67ec2da8236fc23de7943e7727d2b74e0e6ee2b15afd9c765443b9c52b61"
    )
    expected_bundle_file_digest = bytes_digest(canonical_bundle_bytes)
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
        simulation_closure, _, simulation_failure = read_json_document(
            source_path,
            root=simulation_source,
        )
        if simulation_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"SIMULATION_CANONICAL_CLOSURE_{simulation_failure}",
                    "simulation canonical closure could not be loaded",
                )
            )
        elif simulation_closure is not None:
            if simulation_closure != canonical:
                findings.append("simulation canonical closure differs from program")
        manifest_path = simulation_source / "release" / "repository-role.json"
        manifest, _, simulation_manifest_failure = read_json_document(
            manifest_path,
            root=simulation_source,
        )
        if simulation_manifest_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"SIMULATION_RELEASE_MANIFEST_{simulation_manifest_failure}",
                    "simulation release manifest could not be loaded",
                )
            )
        elif isinstance(manifest, dict):
            if manifest.get("reference_result_digest") != expected_result_digest:
                findings.append("simulation reference result digest differs")
            if manifest.get("reference_closure_digest") != expected_digest:
                findings.append("simulation reference closure digest differs")
        else:
            findings.append(
                projection_diagnostic(
                    "SIMULATION_RELEASE_MANIFEST_INVALID_SHAPE",
                    "simulation release manifest requires a JSON object",
                )
            )
        result_path = simulation_source / "build" / "simulation" / "result.json"
        result, _, result_failure = read_json_document(
            result_path,
            root=simulation_source,
        )
        if result_failure not in {None, "MISSING"}:
            findings.append(
                projection_diagnostic(
                    f"SIMULATION_RESULT_{result_failure}",
                    "simulation result could not be loaded",
                )
            )
        elif isinstance(result, dict):
            if result.get("content_digest") != expected_result_digest:
                findings.append(
                    "simulation result content digest differs from canonical bundle"
                )
        elif result is not None:
            findings.append(
                projection_diagnostic(
                    "SIMULATION_RESULT_INVALID_SHAPE",
                    "simulation result requires a JSON object",
                )
            )

    comparison_source = sources.get("comparison")
    if comparison_source is not None:
        source_path = (
            comparison_source
            / "fixtures"
            / "simulated-closures"
            / "future-reality-2028-06-30-v1.json"
        )
        bundle, source_bytes, comparison_failure = read_json_document(
            source_path,
            root=comparison_source,
        )
        if comparison_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"COMPARISON_CANONICAL_BUNDLE_{comparison_failure}",
                    "comparison canonical bundle could not be loaded",
                )
            )
        else:
            assert source_bytes is not None
            if source_bytes != canonical_bundle_bytes:
                findings.append("comparison canonical bundle bytes differ from program")
            if not isinstance(bundle, dict):
                findings.append(
                    projection_diagnostic(
                        "COMPARISON_CANONICAL_BUNDLE_INVALID_SHAPE",
                        "comparison canonical bundle requires a JSON object",
                    )
                )
            elif bundle.get("governance_closure") != canonical:
                findings.append("comparison canonical closure differs from program")
            if (
                isinstance(bundle, dict)
                and bundle.get("governance_closure_digest") != expected_digest
            ):
                findings.append("comparison canonical closure digest differs")

    governance_source = sources.get("governance")
    if governance_source is not None:
        version_path = governance_source / "VERSION"
        version_bytes, version_failure = read_regular_bytes(
            version_path,
            root=governance_source,
        )
        if version_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"GOVERNANCE_VERSION_{version_failure}",
                    "governance VERSION record could not be loaded",
                )
            )
        else:
            assert version_bytes is not None
            try:
                version = version_bytes.decode("utf-8").strip()
            except UnicodeError:
                findings.append(
                    projection_diagnostic(
                        "GOVERNANCE_VERSION_ENCODING_INVALID",
                        "governance VERSION record requires valid UTF-8 text",
                    )
                )
            else:
                if version != "2.0.1":
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
    return role, Path(path).absolute()


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
    lock, _, lock_failure = read_json_document(
        ROOT / "constellation.lock.json",
        root=ROOT,
    )
    if lock_failure is not None:
        print(
            projection_diagnostic(
                f"CONSTELLATION_LOCK_{lock_failure}",
                "constellation lock could not be loaded",
            )
        )
        return 1
    if not isinstance(lock, dict):
        print(
            projection_diagnostic(
                "CONSTELLATION_LOCK_INVALID_SHAPE",
                "constellation lock requires a JSON object",
            )
        )
        return 1
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

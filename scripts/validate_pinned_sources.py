#!/usr/bin/env python3
"""Validate immutable constellation coordinates and canonical closure equality."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
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
GOVERNANCE_RELEASE = "governance-v2.1.0"
GOVERNANCE_SCHEMA_VERSION = "2.1.0"
GOVERNANCE_PROFILE = "Control Plane Profile 0.3.0"
GOVERNANCE_TAG_OBJECT = "1c77396e44b71719ccab138fecd02e525089e39d"
GOVERNANCE_COMMIT = "8469c2a6b2c7f4445523cee262b961ffe3d2523b"
GOVERNANCE_TREE_DIGEST = (
    "git-tree-sha1:aed5d57120e15ceabe77d7bba700a43097200b19"
)
GOVERNANCE_ARCHIVE_FORMAT = "git-archive-tar"
GOVERNANCE_ARCHIVE_DIGEST = (
    "sha256:469ae49fca7d5ad6e1766080b3c39d76c46a840366b217f3839b9d34f2e77d32"
)
HISTORICAL_GOVERNANCE_SCHEMA_COORDINATE = {
    "schema_version": "2.0.1",
    "coordinate_kind": "historical_commit_without_release_tag",
    "release_tag": None,
    "commit": "6349919d55c25d44cfa49ecad2a6631a80db539b",
    "digest": "git-tree-sha1:16786dd2a92fb161ad1cc14b61ee80f8d3d9f31b",
    "archive_format": "git-archive-tar",
    "archive_digest": (
        "sha256:26f38102a63304f6bbdd6262aa37be6a8340d012a0ddf3034a4cd0367ab54884"
    ),
    "ancestor_of_release": GOVERNANCE_RELEASE,
}
HISTORICAL_COMPARISON_DOCUMENTS = {
    "machine-node.json": "machine-node.schema.json",
    "first-receipt.json": "first-receipt.schema.json",
}
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


def git_archive_bytes(root: Path, commit: str) -> bytes:
    """Return reproducible raw Git tar archive bytes for one commit."""
    return subprocess.run(
        ["git", "-C", str(root), "archive", "--format=tar", commit],
        check=True,
        capture_output=True,
    ).stdout


def git_archive_digest(root: Path, commit: str) -> str:
    """Return the SHA-256 identity of raw Git tar archive bytes."""
    return "sha256:" + hashlib.sha256(git_archive_bytes(root, commit)).hexdigest()


def git_annotated_tag_identity(root: Path, release: str) -> tuple[str, str]:
    """Return an annotated tag object and the commit it peels to."""
    tag_object = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "rev-parse",
            f"refs/tags/{release}^{{tag}}",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    commit = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "rev-parse",
            f"{tag_object}^{{commit}}",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return tag_object, commit


def validate_governance_coordinate(coordinate: object) -> list[str]:
    """Require the accepted Governance release, source, tree, and archive."""
    if not isinstance(coordinate, dict):
        return ["governance coordinate is absent or malformed"]
    findings: list[str] = []
    expected = {
        "release": GOVERNANCE_RELEASE,
        "profile": GOVERNANCE_PROFILE,
        "schema_version": GOVERNANCE_SCHEMA_VERSION,
        "tag_object": GOVERNANCE_TAG_OBJECT,
        "commit": GOVERNANCE_COMMIT,
        "digest": GOVERNANCE_TREE_DIGEST,
        "archive_format": GOVERNANCE_ARCHIVE_FORMAT,
        "archive_digest": GOVERNANCE_ARCHIVE_DIGEST,
        "coordinate_status": "pinned",
    }
    if set(coordinate) != set(expected):
        findings.append("governance coordinate field set differs")
        return findings
    for key, value in expected.items():
        if coordinate.get(key) != value:
            findings.append(f"governance {key} differs from the accepted release")
    return findings


def validate_historical_governance_coordinate(coordinate: object) -> list[str]:
    """Require the untagged Governance 2.0.1 compatibility coordinate."""
    if not isinstance(coordinate, dict):
        return ["historical Governance schema coordinate is absent or malformed"]
    findings: list[str] = []
    expected = HISTORICAL_GOVERNANCE_SCHEMA_COORDINATE
    if set(coordinate) != set(expected):
        return ["historical Governance schema coordinate field set differs"]
    for key, value in expected.items():
        if coordinate.get(key) != value:
            findings.append(
                f"historical Governance schema {key} differs from the "
                "accepted compatibility coordinate"
            )
    return findings


def validate_historical_governance_source(
    governance_source: Path,
    coordinate: dict,
) -> list[str]:
    """Reproduce the historical commit, tree, archive, version, and lineage."""
    findings: list[str] = []
    commit = coordinate["commit"]
    try:
        resolved_commit = subprocess.run(
            ["git", "-C", str(governance_source), "rev-parse", f"{commit}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        resolved_tree = subprocess.run(
            ["git", "-C", str(governance_source), "rev-parse", f"{commit}^{{tree}}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return [
            "HISTORICAL_GOVERNANCE_IDENTITY_UNREADABLE: historical Governance "
            "schema identity could not be reproduced"
        ]
    if resolved_commit != commit:
        findings.append("historical Governance schema commit differs from its lock")
    if f"git-tree-sha1:{resolved_tree}" != coordinate["digest"]:
        findings.append("historical Governance schema tree differs from its lock")
    try:
        archive_digest = git_archive_digest(governance_source, commit)
    except (OSError, subprocess.CalledProcessError):
        findings.append(
            "HISTORICAL_GOVERNANCE_ARCHIVE_UNREADABLE: historical Governance "
            "schema archive could not be reproduced"
        )
    else:
        if archive_digest != coordinate["archive_digest"]:
            findings.append(
                "historical Governance schema archive differs from its lock"
            )
    try:
        version_bytes = subprocess.run(
            ["git", "-C", str(governance_source), "show", f"{commit}:VERSION"],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        findings.append(
            "HISTORICAL_GOVERNANCE_VERSION_UNREADABLE: historical Governance "
            "VERSION could not be reproduced"
        )
    else:
        try:
            version = version_bytes.decode("utf-8").strip()
        except UnicodeError:
            findings.append(
                "HISTORICAL_GOVERNANCE_VERSION_ENCODING_INVALID: historical "
                "Governance VERSION requires valid UTF-8 text"
            )
        else:
            if version != coordinate["schema_version"]:
                findings.append(
                    "historical Governance VERSION differs from its schema binding"
                )
    try:
        ancestor = subprocess.run(
            [
                "git",
                "-C",
                str(governance_source),
                "merge-base",
                "--is-ancestor",
                commit,
                GOVERNANCE_COMMIT,
            ],
            check=False,
            capture_output=True,
        )
    except OSError:
        findings.append(
            "HISTORICAL_GOVERNANCE_LINEAGE_UNREADABLE: historical Governance "
            "schema lineage could not be reproduced"
        )
    else:
        if ancestor.returncode != 0:
            findings.append(
                "historical Governance schema is outside the accepted 2.1.0 lineage"
            )
    try:
        tags = subprocess.run(
            ["git", "-C", str(governance_source), "tag", "--points-at", commit],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        findings.append(
            "HISTORICAL_GOVERNANCE_TAG_STATE_UNREADABLE: historical Governance "
            "tag state could not be reproduced"
        )
    else:
        if tags:
            findings.append(
                "historical Governance compatibility commit unexpectedly has a "
                "release tag"
            )
    return findings


def materialize_git_archive(archive_bytes: bytes, destination: Path) -> None:
    """Extract one trusted pinned Git archive inside a bounded temporary root."""
    destination_root = destination.resolve()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
        members = archive.getmembers()
        for member in members:
            member_path = (destination / member.name).resolve()
            if (
                destination_root not in member_path.parents
                and member_path != destination_root
            ) or member.issym() or member.islnk():
                raise ValueError("Git archive member exceeds the materialization root")
        archive.extractall(destination, members=members, filter="data")


def validate_comparison_historical_schemas(
    governance_source: Path,
    comparison_source: Path,
    coordinate: dict,
) -> list[str]:
    """Run the pinned historical validator against signed Comparison carriers."""
    findings: list[str] = []
    try:
        archive_bytes = git_archive_bytes(governance_source, coordinate["commit"])
        with tempfile.TemporaryDirectory(
            prefix="program-governance-compatibility-"
        ) as temporary_directory:
            historical_root = Path(temporary_directory)
            materialize_git_archive(archive_bytes, historical_root)
            validator = historical_root / "tools" / "validate_governance.py"
            for document_path, schema_name in HISTORICAL_COMPARISON_DOCUMENTS.items():
                result = subprocess.run(
                    [
                        sys.executable,
                        str(validator),
                        "--governance-root",
                        str(historical_root),
                        "--source-root",
                        str(comparison_source),
                        "--schema-name",
                        schema_name,
                        "--document-path",
                        document_path,
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    findings.append(
                        "COMPARISON_HISTORICAL_SCHEMA_INVALID: "
                        f"signed Comparison {document_path} differs from the "
                        "pinned Governance 2.0.1 schema"
                    )
    except (OSError, subprocess.CalledProcessError, tarfile.TarError, ValueError):
        findings.append(
            "HISTORICAL_GOVERNANCE_VALIDATOR_UNREADABLE: the pinned Governance "
            "2.0.1 validator could not be materialized"
        )
    return findings


def validate_implementation_source(
    source: Path,
    coordinate: dict,
) -> list[str]:
    """Reconcile Implementation release semantics with its exact tagged source."""
    findings: list[str] = []
    manifest_path = source / "release" / "repository-role.json"
    manifest, _, manifest_failure = read_json_document(
        manifest_path,
        root=source,
    )
    if manifest_failure is not None:
        return [
            projection_diagnostic(
                f"IMPLEMENTATION_RELEASE_MANIFEST_{manifest_failure}",
                "implementation release manifest could not be loaded",
            )
        ]
    if not isinstance(manifest, dict):
        return [
            projection_diagnostic(
                "IMPLEMENTATION_RELEASE_MANIFEST_INVALID_SHAPE",
                "implementation release manifest requires a JSON object",
            )
        ]

    expected_semantics = {
        "repository_role": "enterprise_implementation",
        "repository_release": coordinate.get("repository_release"),
        "external_release": coordinate.get("release"),
        "selected_future_closure_digest": coordinate.get(
            "selected_future_closure_digest"
        ),
        "contract_bindings": coordinate.get("contract_bindings"),
    }
    for field, expected_value in expected_semantics.items():
        if manifest.get(field) != expected_value:
            findings.append(
                "implementation signed release "
                f"{field} differs from its program lock"
            )

    source_artifacts = coordinate.get("source_artifact_bindings")
    if not isinstance(source_artifacts, dict):
        findings.append("implementation source artifact bindings are malformed")
        return findings
    for binding_name, binding in source_artifacts.items():
        if not isinstance(binding, dict):
            findings.append(
                f"implementation source artifact binding {binding_name} is malformed"
            )
            continue
        artifact_path = binding.get("path")
        expected_digest = binding.get("digest")
        equality_mode = binding.get("equality_mode")
        if (
            not isinstance(artifact_path, str)
            or not isinstance(expected_digest, str)
            or SHA256.fullmatch(expected_digest) is None
            or equality_mode != "byte_sha256"
        ):
            findings.append(
                f"implementation source artifact binding {binding_name} is malformed"
            )
            continue
        if binding_name == "promotion_candidate_digest":
            promotion_coordinates = manifest.get("promotion_coordinates")
            manifest_digest = (
                promotion_coordinates.get("candidate_receipt_digest")
                if isinstance(promotion_coordinates, dict)
                else None
            )
            manifest_path_value = (
                promotion_coordinates.get("candidate_receipt")
                if isinstance(promotion_coordinates, dict)
                else None
            )
            if manifest_path_value != artifact_path:
                findings.append(
                    "implementation promotion candidate path differs from its "
                    "program lock"
                )
        else:
            manifest_digest = manifest.get(binding_name)
        if manifest_digest != expected_digest:
            findings.append(
                "implementation signed release "
                f"{binding_name} differs from its program lock"
            )
        artifact_bytes, artifact_failure = read_regular_bytes(
            source / artifact_path,
            root=source,
        )
        if artifact_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"IMPLEMENTATION_SOURCE_ARTIFACT_{artifact_failure}",
                    f"implementation source artifact {binding_name} could not be loaded",
                )
            )
            continue
        assert artifact_bytes is not None
        if bytes_digest(artifact_bytes) != expected_digest:
            findings.append(
                f"implementation source artifact bytes differ for {binding_name}"
            )

    promotion_coordinates = manifest.get("promotion_coordinates")
    if not isinstance(promotion_coordinates, dict):
        findings.append("implementation promotion coordinates are malformed")
    elif promotion_coordinates.get("target_release") != coordinate.get("tag"):
        findings.append(
            "implementation promotion target differs from its actual Git tag"
        )
    return findings


def validate_sources(
    lock: dict,
    sources: dict[str, Path],
    *,
    allow_pending: bool,
) -> list[str]:
    findings = validate_language_policy_projection(sources.get("governance"))
    findings.extend(validate_governance_coordinate(lock.get("governance")))
    comparison_coordinate = lock.get("comparison")
    historical_coordinate = (
        comparison_coordinate.get("historical_governance_schema")
        if isinstance(comparison_coordinate, dict)
        else None
    )
    historical_coordinate_findings = validate_historical_governance_coordinate(
        historical_coordinate
    )
    findings.extend(historical_coordinate_findings)
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
            if not (allow_pending and role == "governance"):
                findings.append(
                    f"{role} pinned coordinate requires a checked-out source"
                )
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
        release_tag = coordinate.get("tag", coordinate.get("release"))
        try:
            actual_tag_object, tagged_commit = git_annotated_tag_identity(
                source,
                release_tag,
            )
        except (OSError, subprocess.CalledProcessError):
            findings.append(
                f"{role.upper()}_TAG_IDENTITY_UNREADABLE: {role} annotated "
                "tag identity could not be reproduced"
            )
        else:
            if actual_tag_object != coordinate.get("tag_object"):
                findings.append(
                    f"{role} annotated tag object differs from its lock"
                )
            if tagged_commit != coordinate.get("commit"):
                findings.append(
                    f"{role} annotated tag peels to a different commit"
                )
        try:
            actual_archive_digest = git_archive_digest(source, actual_commit)
        except (OSError, subprocess.CalledProcessError):
            findings.append(
                f"{role.upper()}_ARCHIVE_IDENTITY_UNREADABLE: {role} archive "
                "identity could not be reproduced"
            )
        else:
            if actual_archive_digest != coordinate.get("archive_digest"):
                findings.append(f"{role} source archive differs from its lock")

    implementation_source = sources.get("implementation")
    implementation_coordinate = lock.get("implementation")
    if (
        implementation_source is not None
        and isinstance(implementation_coordinate, dict)
        and implementation_coordinate.get("coordinate_status") == "pinned"
    ):
        findings.extend(
            validate_implementation_source(
                implementation_source,
                implementation_coordinate,
            )
        )

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
        "sha256:5ed067887dc02d2a4c85845d3d25ab6b3fbee857011bed7e5b528e4e58c03861"
    )
    expected_aggregate_digest = (
        "sha256:ddbce2fe891bfcd70515005714cdabf34e6430869cc2e2a4daca59016ac6ce3b"
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
            / "release"
            / "future-reality-2028-06-30-v1.json"
        )
        simulation_bundle, simulation_bundle_bytes, simulation_failure = read_json_document(
            source_path,
            root=simulation_source,
        )
        if simulation_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"SIMULATION_CANONICAL_BUNDLE_{simulation_failure}",
                    "simulation canonical bundle could not be loaded",
                )
            )
        elif isinstance(simulation_bundle, dict):
            if simulation_bundle_bytes != canonical_bundle_bytes:
                findings.append("simulation canonical bundle bytes differ from program")
            if simulation_bundle.get("governance_closure") != canonical:
                findings.append("simulation canonical closure differs from program")
            if simulation_bundle.get("source_result_digest") != expected_result_digest:
                findings.append(
                    "simulation source result digest differs from canonical bundle"
                )
        else:
            findings.append(
                projection_diagnostic(
                    "SIMULATION_CANONICAL_BUNDLE_INVALID_SHAPE",
                    "simulation canonical bundle requires a JSON object",
                )
            )
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
        manifest_path = comparison_source / "release" / "repository-role.json"
        manifest, _, manifest_failure = read_json_document(
            manifest_path,
            root=comparison_source,
        )
        if manifest_failure is not None:
            findings.append(
                projection_diagnostic(
                    f"COMPARISON_RELEASE_MANIFEST_{manifest_failure}",
                    "comparison release manifest could not be loaded",
                )
            )
        elif not isinstance(manifest, dict):
            findings.append(
                projection_diagnostic(
                    "COMPARISON_RELEASE_MANIFEST_INVALID_SHAPE",
                    "comparison release manifest requires a JSON object",
                )
            )
        elif (
            manifest.get("contract_bindings", {}).get("governance_schema")
            != lock.get("comparison", {}).get("receipt_schema")
        ):
            findings.append(
                "comparison signed schema binding differs from its program lock"
            )

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
                if version != GOVERNANCE_SCHEMA_VERSION:
                    findings.append(
                        "governance VERSION differs from the selected 2.1.0 release"
                    )
        if not historical_coordinate_findings:
            assert isinstance(historical_coordinate, dict)
            findings.extend(
                validate_historical_governance_source(
                    governance_source,
                    historical_coordinate,
                )
            )
            if comparison_source is not None:
                findings.extend(
                    validate_comparison_historical_schemas(
                        governance_source,
                        comparison_source,
                        historical_coordinate,
                    )
                )

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
        release_tag = coordinate.get("tag", coordinate.get("release"))
        if not isinstance(release_tag, str) or not release_tag:
            findings.append(f"{role} external release tag must be explicit")
        if (
            not isinstance(coordinate.get("tag_object"), str)
            or COMMIT.fullmatch(coordinate["tag_object"]) is None
        ):
            findings.append(f"{role} external tag object must be nonzero 40-hex")
        if coordinate.get("archive_format") != "git-archive-tar":
            findings.append(f"{role} external archive format must be git-archive-tar")
        if (
            not isinstance(coordinate.get("archive_digest"), str)
            or SHA256.fullmatch(coordinate["archive_digest"]) is None
        ):
            findings.append(f"{role} external archive digest must be SHA-256")
    findings.extend(validate_governance_coordinate(lock.get("governance")))
    comparison_coordinate = lock.get("comparison")
    historical_coordinate = (
        comparison_coordinate.get("historical_governance_schema")
        if isinstance(comparison_coordinate, dict)
        else None
    )
    findings.extend(validate_historical_governance_coordinate(historical_coordinate))
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

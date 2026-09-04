from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from automation_contract import (
    MISSING_AUTOMATION_CONTROLS,
    validate_repository_automation,
)
from pages_projection import validate_source_contract
from verify_program_release_observation import (
    OBSERVATION_SCHEMA_PATH,
    candidate_receipt_digest,
    validate_observation_document,
    validate_observation_schema,
)


PROGRAM_RELEASE = "0.3.1"
PROGRAM_TAG = f"spec-v{PROGRAM_RELEASE}"
PACKAGE_SOURCE_DIGEST_ALGORITHM = "path-length-bytes-sha256-v1"
PACKAGE_SOURCE_DIGEST_CANONICALIZATION = {
    "file_selection": (
        "pyproject.toml and every regular file below src/lims_eln_contracts"
    ),
    "path_encoding": "UTF-8 POSIX relative paths",
    "path_order": "ascending UTF-8 byte order",
    "length_encoding": "unsigned 8-byte big-endian",
    "record_fields": [
        "path_length",
        "path_bytes",
        "content_length",
        "content_bytes",
    ],
    "exclusions": [
        "directory entries",
        "paths below __pycache__",
        "files ending in .pyc or .pyo",
    ],
    "symlink_behavior": "reject the scope root or any selected entry",
}
GOVERNANCE_RELEASE = "2.1.0"
GOVERNANCE_TAG = f"governance-v{GOVERNANCE_RELEASE}"
GOVERNANCE_TAG_OBJECT = "1c77396e44b71719ccab138fecd02e525089e39d"
GOVERNANCE_COMMIT = "8469c2a6b2c7f4445523cee262b961ffe3d2523b"
GOVERNANCE_TREE_DIGEST = (
    "git-tree-sha1:aed5d57120e15ceabe77d7bba700a43097200b19"
)
GOVERNANCE_ARCHIVE_FORMAT = "git-archive-tar"
GOVERNANCE_ARCHIVE_DIGEST = (
    "sha256:469ae49fca7d5ad6e1766080b3c39d76c46a840366b217f3839b9d34f2e77d32"
)
EXTERNAL_RELEASE_SUBJECTS = {
    "simulation": {
        "release": "forecast-2028-FR-v1",
        "tag_object": "73fc89690b6cc9df7a99ea495e580e7f4e2caedc",
        "commit": "37c3861b5411db8e772feedf41e4abf1fb7829bc",
        "digest": "git-tree-sha1:595ae59f25f522732577c5f8e00709f023464a6d",
        "archive_format": "git-archive-tar",
        "archive_digest": "sha256:c6a062a6efb6786c53dc9e7298a9dd881fcc2301d807db5cecf84663c98438e2",
        "coordinate_status": "pinned",
    },
    "implementation": {
        "release": "implementation-v0.3.2",
        "tag": "v0.3.2",
        "tag_object": "c3db01079b88622f06e8714c8bcbdf0dc1803a10",
        "commit": "fe0bd2a08ac1697ce18ca583d9631faae7db7132",
        "digest": "git-tree-sha1:eb8eadb27a9e07c6069a1946f115a0083d94af5c",
        "archive_format": "git-archive-tar",
        "archive_digest": "sha256:0ea3db3099e3485f65d238fb2e194c6bfd9b9a90f6642431c4a96974ebcc3c16",
        "coordinate_status": "pinned",
        "source_binding_status": "accepted_package_source",
    },
    "comparison": {
        "release": "comparison-v0.3.1",
        "tag_object": "4c29f6ca410eb4400c55ad77fc34ada2960d1972",
        "commit": "b5c13689a32739d29437e209816bf0cd6a878976",
        "digest": "git-tree-sha1:10a784b8a677ee6eb524d2860ff5ee7151d6050b",
        "archive_format": "git-archive-tar",
        "archive_digest": "sha256:92c2d57bd9e75c650365db4b481a22a6580b201926ba1c666fcf8cb8c9311a2e",
        "coordinate_status": "pinned",
    },
}
IMPLEMENTATION_REPOSITORY_RELEASE = "0.3.2"
IMPLEMENTATION_CONTRACT_BINDINGS = {
    "governance_schema": GOVERNANCE_RELEASE,
    "governance_release": GOVERNANCE_RELEASE,
    "program_contract_package": PROGRAM_RELEASE,
    "control_plane_profile": "0.3.0",
    "execution_receipt_schema": "1.1.0",
    "provenance_schema": "1.0.0",
    "runtime_setting_catalog_schema": "1.0.0",
    "bounded_caller_binding": "0.3.2",
    "database_flyway_release": "1.0.0",
    "open_receipt_ledger": "2.0.0",
}
IMPLEMENTATION_SOURCE_ARTIFACT_BINDINGS = {
    "bounded_caller_binding_digest": {
        "path": "release/bounded-caller-bindings.json",
        "digest": (
            "sha256:d141061bf028fdd63cc879ab455b0a68853d369da98edbeb17421a35714ed796"
        ),
        "equality_mode": "byte_sha256",
    },
    "database_flyway_release_digest": {
        "path": "database/flyway-release.json",
        "digest": (
            "sha256:a4fafe7ebb50da1efbad47df24d6d7af741130039ba8c90b8d6457e9d1d107b9"
        ),
        "equality_mode": "byte_sha256",
    },
    "external_contract_coordinate_digest": {
        "path": "release/external-contract-coordinates.json",
        "digest": (
            "sha256:ad699b5d7cb6c24e0d86b2dfbae5d3104d03fec8ee08cdd04c33f444376bcde1"
        ),
        "equality_mode": "byte_sha256",
    },
    "public_inspection_manifest_digest": {
        "path": "release/public-inspection-manifest.json",
        "digest": (
            "sha256:73a062069301c694df26196a7384184d7229089885d97279cb989244ca7435c8"
        ),
        "equality_mode": "byte_sha256",
    },
    "open_receipt_ledger_digest": {
        "path": "receipts/open-receipt-ledger.json",
        "digest": (
            "sha256:41fabadcf31d22439f410575af3bb041b37ac0124927508484aca0818ecaefad"
        ),
        "equality_mode": "byte_sha256",
    },
    "promotion_candidate_digest": {
        "path": "receipts/promotion-candidate.json",
        "digest": (
            "sha256:c78f16df5832f6c7b39ea1b0d9a61316b26d90cd1552fd8b2c39043436a94340"
        ),
        "equality_mode": "byte_sha256",
    },
}
COMPARISON_RECEIPT_SCHEMA = "2.0.1"
COMPARISON_HISTORICAL_GOVERNANCE_SCHEMA = {
    "schema_version": COMPARISON_RECEIPT_SCHEMA,
    "coordinate_kind": "historical_commit_without_release_tag",
    "release_tag": None,
    "commit": "6349919d55c25d44cfa49ecad2a6631a80db539b",
    "digest": "git-tree-sha1:16786dd2a92fb161ad1cc14b61ee80f8d3d9f31b",
    "archive_format": "git-archive-tar",
    "archive_digest": (
        "sha256:26f38102a63304f6bbdd6262aa37be6a8340d012a0ddf3034a4cd0367ab54884"
    ),
    "ancestor_of_release": GOVERNANCE_TAG,
}
CONTROL_PLANE_PROFILE = "0.3.0"
CANONICAL_BUNDLE_VERSION = "2.0.1"
RECEIPT_VOCABULARY_RELEASE = "1.0.0"
LANGUAGE_POLICY_RELEASE = "language-policy-v1.0.0"
DATABASE_PROBABILITY_EVENT = (
    "Given a capable hybrid team, two implementation increments, the stated "
    "gates, and a representative PostgreSQL rehearsal, the route yields a "
    "reviewable enterprise-grade database release candidate that preserves "
    "qualified scientific semantics, tenant isolation, audit reconstruction, "
    "and recoverability and passes independent principal-engineer, database, "
    "security, operations, and scientific review with follow-up limited to "
    "accepted non-critical items."
)
DATABASE_PROBABILITY_ASSUMPTIONS = (
    "A capable hybrid team has named owners for scientific semantics, database "
    "engineering, security, operations, and delivery coordination.",
    "The delivery horizon contains two implementation increments with capacity "
    "for implementation, independent review, and bounded remediation.",
    "The stated contract and release gates remain stable through the estimation "
    "horizon or trigger recalibration when they change.",
    "A representative PostgreSQL rehearsal environment and representative data "
    "are available early enough to inform the second increment.",
    "Independent reviewers apply shared acceptance criteria, and accepted "
    "non-critical follow-up receives an owner and Coordination Horizon.",
)
FLYWAY_TRANSITION_EVENT = (
    "Given the reviewed versioned PostgreSQL SQL, existing end-to-end integration "
    "suite, parameterized migration scenarios, Flyway Community 13.0.0, and one "
    "corrective tranche, the implementation replaces bespoke migration "
    "orchestration while preserving clean installation, populated predecessor "
    "upgrade, failure atomicity, replay, zero-pending-work, and clean-versus-upgrade "
    "convergence evidence without a critical domain-contract regression."
)
DATABASE_CONSTELLATION_FINDING_TOTAL = 115
PROMOTION_RECEIPT_ID = "RCP-PROGRAM-PROMOTION-003"
RELEASE_REVIEW_ROUTE = {
    "merge_admission": "configured_ordinary_bypass",
    "independent_review": "deputized_independent_review_completed",
    "github_review_record": "no_formal_review_submitted",
}
STANDING_BRANCH_CONTROLS = {
    "protected_branch": "main",
    "required_approvals": 1,
    "code_owner_review": True,
    "dismiss_stale_reviews_on_push": True,
    "last_push_approval": True,
    "review_thread_resolution": True,
    "branch_deletion_guard": True,
    "non_fast_forward_guard": True,
}
CANONICAL_CLOSURE_DIGEST = (
    "sha256:33bcc14da24309b7716728b3f0204008e8f7ebf58de75f9e40a5986b421f06b5"
)
CANONICAL_RESULT_DIGEST = (
    "sha256:5ed067887dc02d2a4c85845d3d25ab6b3fbee857011bed7e5b528e4e58c03861"
)
CANONICAL_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:ddbce2fe891bfcd70515005714cdabf34e6430869cc2e2a4daca59016ac6ce3b"
)
CANONICAL_BUNDLE_FILE_DIGEST = (
    "sha256:a72810e850c88f7a06c6e86fb94c1026a22d859089ee70ef31d4413b086fd098"
)
PENDING_COMMIT = "0" * 40
PENDING_TREE_DIGEST = "git-tree-sha1:" + ("0" * 40)
RELEASE_PATTERNS = {
    "specification": re.compile(r"^spec-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "simulation": re.compile(
        r"^forecast-(?:[0-9]{4}-Q[1-4]-r[1-9][0-9]*|"
        r"[0-9]{4}-FR-v[1-9][0-9]*)$"
    ),
    "implementation": re.compile(
        r"^implementation-v[0-9]+\.[0-9]+\.[0-9]+$"
    ),
    "comparison": re.compile(r"^comparison-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "governance": re.compile(r"^governance-v[0-9]+\.[0-9]+\.[0-9]+$"),
}
COMMIT_PATTERN = re.compile(r"^[a-f0-9]{40}$")
MATERIAL_COMMIT_PATTERN = re.compile(r"^(?!0{40}$)[a-f0-9]{40}$")
TREE_DIGEST_PATTERN = re.compile(r"^git-tree-sha1:[a-f0-9]{40}$")
MATERIAL_TREE_DIGEST_PATTERN = re.compile(
    r"^git-tree-sha1:(?!0{40}$)[a-f0-9]{40}$"
)
SHA256_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
MATERIAL_SHA256_PATTERN = re.compile(r"^sha256:(?!0{64}$)[a-f0-9]{64}$")

CORE_ROOT_KEYS = {
    "constellation": {
        "constellation_id",
        "version",
        "repositories",
        "dependency_rule",
        "learning_rule",
    },
    "constellation_lock": {
        "constellation_version",
        "recorded_at",
        "content_identity",
        "specification",
        "simulation",
        "implementation",
        "comparison",
        "governance",
        "seed_lineage",
        "seed",
    },
    "release_role": {
        "manifest_version",
        "repository_role",
        "repository_release",
        "external_release",
        "release_state",
        "authority_posture",
        "canonical_closure",
        "advisory_design",
        "contract_bindings",
        "automation_controls",
        "promotion_controls",
        "orientation_surfaces",
        "seed_lineage",
        "release_coordinates",
        "promotion_coordinates",
    },
    "machine_node": {
        "machine_node_id",
        "canonical_identity",
        "title",
        "purpose",
        "control_plane_profile",
        "schema_release",
        "repository_role",
        "authority",
        "lifecycle_state",
        "coordination_horizon_id",
        "contracts",
        "campaigns",
        "seed_lineage",
        "current_provenance",
        "first_receipt_contract_id",
        "open_receipts",
        "invalidation_conditions",
        "downstream_consumers",
        "source_boundaries",
        "metadata",
    },
    "first_receipt": {
        "first_receipt_id",
        "machine_node_id",
        "as_of",
        "orientation_purpose",
        "authority_posture",
        "contract_state",
        "evidence_posture",
        "coordination_horizon_id",
        "current_horizon_summary",
        "open_receipts",
        "invalidation_conditions",
        "source_permissions",
        "handoff",
        "metadata",
    },
    "coordination_horizon": {
        "horizon_id",
        "title",
        "objective",
        "as_of",
        "current_item_ids",
        "work_items",
        "reentry_capsule",
        "retained_effects",
        "consequential_questions",
        "metadata",
    },
}
STATUS_KEYS = {
    "name",
    "version",
    "status",
    "evidence_mode",
    "assurance_stage",
    "default_branch",
    "integration_branch",
    "as_of",
    "source_seed",
    "released_baseline",
    "released_commit",
    "planned_release",
    "governance_contract",
    "governance_profile",
    "governance_schema",
    "receipt_schema",
    "release_coordinate_status",
    "governance_coordinate_status",
    "coordination_horizon",
    "bounded_caller_contract",
    "practitioner_probe_catalog",
    "advisory_future_reality_design",
    "canonical_simulated_closure",
    "receipt_vocabulary_map",
    "database_finding_ledger",
    "data_contract",
    "database_migration_contract",
    "database_release_manifest",
    "database_open_receipts",
    "simulated_receipt_classes_closed",
    "future_observed_receipt_classes_open",
}
PROMOTION_RECEIPT_KEYS = {
    "promotion_receipt_id",
    "repository",
    "target_release",
    "promotion_state",
    "evidence_mode",
    "assurance_stage",
    "candidate_coordinate",
    "release_coordinate",
    "release_review_route",
    "required_evidence",
    "accountable_role",
    "metadata",
}


class NonFiniteNumberError(ValueError):
    """Signal a numeric token outside the JSON number grammar."""


class DuplicateObjectKeyError(ValueError):
    """Signal an object whose keys do not form one unambiguous mapping."""


def reject_non_finite(token: str) -> None:
    raise NonFiniteNumberError(f"non-finite numeric token {token!r} is outside JSON")


def require_unique_object_keys(pairs: list[tuple[str, object]]) -> dict:
    """Build one JSON object after proving that every key is unique."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateObjectKeyError(
                f"JSON object key {key!r} appears more than once; "
                "each object key must be unique"
            )
        result[key] = value
    return result


def parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise NonFiniteNumberError(
            f"numeric token {token!r} exceeds the finite JSON domain"
        )
    return value


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open(encoding="utf-8") as handle:
        return json.load(
            handle,
            object_pairs_hook=require_unique_object_keys,
            parse_constant=reject_non_finite,
            parse_float=parse_finite_float,
        )


def parse_status_scalar(value: str) -> str | int | bool | None:
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"(?:0|[1-9][0-9]*)", value):
        return int(value)
    return value


def load_status(relative_path: str = "STATUS.yaml") -> dict[str, Any]:
    """Parse the deliberately restricted two-level status mapping."""
    path = ROOT / relative_path
    result: dict[str, Any] = {}
    active_section: str | None = None
    for number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indentation = len(raw_line) - len(raw_line.lstrip(" "))
        if indentation not in {0, 2}:
            raise ValueError(
                f"{relative_path}:{number} uses an unsupported indentation depth"
            )
        key, separator, raw_value = raw_line.strip().partition(":")
        if not separator or not key:
            raise ValueError(f"{relative_path}:{number} requires key: value syntax")
        value = raw_value.strip()
        if indentation == 0:
            if key in result:
                raise DuplicateObjectKeyError(
                    f"{relative_path} key {key!r} appears more than once"
                )
            if value:
                result[key] = parse_status_scalar(value)
                active_section = None
            else:
                result[key] = {}
                active_section = key
            continue
        if active_section is None:
            raise ValueError(
                f"{relative_path}:{number} nested value lacks a parent mapping"
            )
        section = result[active_section]
        if not isinstance(section, dict):
            raise ValueError(
                f"{relative_path}:{number} parent {active_section!r} is scalar"
            )
        if key in section:
            raise DuplicateObjectKeyError(
                f"{relative_path} key {active_section}.{key} appears more than once"
            )
        if not value:
            raise ValueError(
                f"{relative_path}:{number} supports two mapping levels only"
            )
        section[key] = parse_status_scalar(value)
    return result


def require_exact_object(
    value: Any,
    expected_keys: set[str],
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    actual_keys = set(value)
    if actual_keys != expected_keys:
        raise ValueError(
            f"{label} fields differ: missing={sorted(expected_keys - actual_keys)}, "
            f"undeclared={sorted(actual_keys - expected_keys)}"
        )
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def require_string_list(value: Any, label: str, *, minimum: int = 0) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) < minimum
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise ValueError(
            f"{label} must contain at least {minimum} non-empty strings"
        )
    if len(value) != len(set(value)):
        raise ValueError(f"{label} must contain unique strings")
    return value


def validate_release_review_route(value: Any, label: str) -> dict[str, Any]:
    """Keep release admission, independent review, and GitHub record distinct."""
    route = require_exact_object(value, set(RELEASE_REVIEW_ROUTE), label)
    if route != RELEASE_REVIEW_ROUTE:
        raise ValueError(f"{label} differs from the authorized release route")
    return route


def package_source_digest(root: Path = ROOT) -> str:
    """Digest package metadata and import source with stable path boundaries."""
    metadata_path = root / "pyproject.toml"
    source_root = root / "src" / "lims_eln_contracts"
    if metadata_path.is_symlink() or source_root.is_symlink():
        raise ValueError("contract package source scope requires regular files")
    if not metadata_path.is_file() or not source_root.is_dir():
        raise ValueError("contract package source scope is incomplete")

    files = [metadata_path]
    for path in source_root.rglob("*"):
        relative_source_path = path.relative_to(source_root)
        if (
            "__pycache__" in relative_source_path.parts
            or path.suffix in {".pyc", ".pyo"}
        ):
            continue
        if path.is_symlink():
            raise ValueError("contract package source scope requires regular files")
        if path.is_file():
            files.append(path)
    files.sort(key=lambda path: path.relative_to(root).as_posix().encode("utf-8"))

    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return "sha256:" + digest.hexdigest()


def package_source_digest_from_git(commit: str, root: Path = ROOT) -> str:
    """Reproduce the scoped package digest from one locally available commit."""
    try:
        resolved_commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", f"{commit}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        listing = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-tree",
                "-r",
                "-z",
                commit,
                "--",
                "pyproject.toml",
                "src/lims_eln_contracts",
            ],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError(
            "reviewed contract package commit is unavailable"
        ) from error
    if resolved_commit != commit:
        raise ValueError(
            "reviewed contract package coordinate requires the commit object"
        )

    records: list[tuple[bytes, bytes]] = []
    observed_metadata = False
    observed_package_file = False
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        try:
            identity, raw_path = entry.split(b"\t", 1)
            mode, object_type, object_id = identity.split(b" ", 2)
            relative_path = raw_path.decode("utf-8")
        except (UnicodeError, ValueError) as error:
            raise ValueError(
                "reviewed contract package tree is malformed"
            ) from error
        if relative_path == "pyproject.toml":
            observed_metadata = True
        elif relative_path.startswith("src/lims_eln_contracts/"):
            package_relative = relative_path.removeprefix(
                "src/lims_eln_contracts/"
            )
            package_parts = package_relative.split("/")
            if (
                "__pycache__" in package_parts
                or relative_path.endswith((".pyc", ".pyo"))
            ):
                continue
            observed_package_file = True
        else:
            continue
        if mode not in {b"100644", b"100755"} or object_type != b"blob":
            raise ValueError(
                "reviewed contract package scope requires regular files"
            )
        try:
            content = subprocess.run(
                ["git", "-C", str(root), "cat-file", "blob", object_id],
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as error:
            raise ValueError(
                "reviewed contract package content is unavailable"
            ) from error
        records.append((raw_path, content))
    if not observed_metadata or not observed_package_file:
        raise ValueError("reviewed contract package source scope is incomplete")

    digest = hashlib.sha256()
    for relative, content in sorted(records, key=lambda record: record[0]):
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return "sha256:" + digest.hexdigest()


def validate_contract_package_coordinate(coordinate: dict) -> None:
    """Validate the reviewed-source distribution route without inventing its commit."""
    require_exact_object(
        coordinate,
        {
            "coordinate_version",
            "distribution_name",
            "import_name",
            "package_version",
            "repository",
            "publication_owner",
            "publication_state",
            "source_commit",
            "source_identity",
            "transport",
            "authentication_posture",
            "authenticated_pep_508_template",
            "editable_sibling_install",
            "consumer_conformance",
            "replacement_rule",
        },
        "contract_package_coordinate",
    )
    expected_strings = {
        "coordinate_version": "1.0.0",
        "distribution_name": "lims-eln-program-specification",
        "import_name": "lims_eln_contracts",
        "package_version": PROGRAM_RELEASE,
        "repository": "driftframestudios/lims-eln-program-specification",
        "publication_owner": "Program repository owners",
        "transport": "git+https",
        "authentication_posture": (
            "Git supplies credentials through a configured credential helper "
            "or short-lived GitHub App token; the requirement text carries no "
            "credential."
        ),
        "authenticated_pep_508_template": (
            "lims-eln-program-specification @ git+https://github.com/"
            "driftframestudios/lims-eln-program-specification.git@{full_commit}"
        ),
        "editable_sibling_install": (
            "python3 -m pip install -e ../lims-eln-program-specification"
        ),
        "replacement_rule": (
            "A later full commit may replace this coordinate at the same "
            "package version when its scoped package digest is identical; a "
            "package-content change advances the version and digest, and "
            "consumers adopt either replacement through review."
        ),
    }
    for key, expected in expected_strings.items():
        if coordinate.get(key) != expected:
            raise ValueError(
                f"contract package {key} differs from its distribution contract"
            )

    source_identity = require_exact_object(
        coordinate.get("source_identity"),
        {"scope", "algorithm", "canonicalization", "digest"},
        "contract_package_coordinate.source_identity",
    )
    if source_identity.get("scope") != [
        "pyproject.toml",
        "src/lims_eln_contracts",
    ]:
        raise ValueError("contract package source scope differs")
    if source_identity.get("algorithm") != PACKAGE_SOURCE_DIGEST_ALGORITHM:
        raise ValueError("contract package source digest algorithm differs")
    if (
        source_identity.get("canonicalization")
        != PACKAGE_SOURCE_DIGEST_CANONICALIZATION
    ):
        raise ValueError("contract package source canonicalization differs")
    if source_identity.get("digest") != package_source_digest():
        raise ValueError("contract package scoped source digest differs")

    state = coordinate.get("publication_state")
    source_commit = coordinate.get("source_commit")
    if state == "pending_reviewed_merge_commit":
        if source_commit is not None:
            raise ValueError(
                "pending contract package coordinate keeps its source commit open"
            )
        expected_conformance_state = "planned_after_source_commit"
    elif state == "reviewed_source_available":
        if (
            not isinstance(source_commit, str)
            or MATERIAL_COMMIT_PATTERN.fullmatch(source_commit) is None
        ):
            raise ValueError(
                "reviewed contract package coordinate requires a full source commit"
            )
        if package_source_digest_from_git(source_commit) != source_identity["digest"]:
            raise ValueError(
                "reviewed contract package commit differs from its scoped digest"
            )
        expected_conformance_state = "required"
    else:
        raise ValueError("contract package publication state is unsupported")

    conformance = require_exact_object(
        coordinate.get("consumer_conformance"),
        {
            "state",
            "first_consumer",
            "environment",
            "direct_url_record",
            "required_observations",
        },
        "contract_package_coordinate.consumer_conformance",
    )
    if (
        conformance.get("state") != expected_conformance_state
        or conformance.get("first_consumer")
        != "driftframestudios/lims-eln-enterprise-implementation"
        or conformance.get("environment") != "clean Python 3.12 environment"
        or conformance.get("direct_url_record") != "PEP 610 direct_url.json"
    ):
        raise ValueError("contract package consumer conformance state differs")
    observations = require_string_list(
        conformance.get("required_observations"),
        "contract_package_coordinate.consumer_conformance.required_observations",
        minimum=9,
    )
    if set(observations) != {
        f"installed distribution version is {PROGRAM_RELEASE}",
        f"lims_eln_contracts.__version__ is {PROGRAM_RELEASE}",
        "lims_eln_contracts.CONTRACT_VERSION is 1.0.0",
        "vcs_info.commit_id equals the reviewed full commit",
        "the scoped package source digest matches the reviewed binding",
        "the released operation catalog loads",
        "the Golden Specimen scenario loads",
        "the implementation and simulation shaped observations load",
        "every released schema in SCHEMA_RESOURCE_NAMES loads as a JSON object",
    }:
        raise ValueError("contract package consumer observations differ")

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project_match = re.search(
        r"(?ms)^\[project\]\s*(.*?)(?=^\[|\Z)",
        pyproject,
    )
    if project_match is None:
        raise ValueError("contract package distribution metadata is absent")
    project = {
        key: match.group(1)
        for key in ("name", "version")
        if (
            match := re.search(
                rf'(?m)^{key}\s*=\s*"([^"]+)"\s*$',
                project_match.group(1),
            )
        )
    }
    if (
        project.get("name") != coordinate["distribution_name"]
        or project.get("version") != coordinate["package_version"]
    ):
        raise ValueError("contract package distribution metadata differs")
    if not (ROOT / "src" / coordinate["import_name"]).is_dir():
        raise ValueError("contract package import directory is absent")


def validate_core_shapes(
    *,
    constellation: dict,
    constellation_lock: dict,
    release_role: dict,
    machine_node: dict,
    first_receipt: dict,
    coordination_horizon: dict,
    promotion_receipt: dict,
    status_document: dict,
) -> None:
    """Reject undeclared fields and type drift at the release control boundary."""
    records = {
        "constellation": constellation,
        "constellation_lock": constellation_lock,
        "release_role": release_role,
        "machine_node": machine_node,
        "first_receipt": first_receipt,
        "coordination_horizon": coordination_horizon,
    }
    for label, record in records.items():
        require_exact_object(record, CORE_ROOT_KEYS[label], label)

    require_exact_object(status_document, STATUS_KEYS, "STATUS.yaml")
    require_exact_object(
        status_document["source_seed"],
        {"repository", "pull_request", "source_commit", "merge_commit"},
        "STATUS.yaml.source_seed",
    )
    numeric_status_keys = {
        "simulated_receipt_classes_closed",
        "future_observed_receipt_classes_open",
        "database_open_receipts",
    }
    for key in STATUS_KEYS - {
        "source_seed",
        *numeric_status_keys,
    }:
        require_string(status_document[key], f"STATUS.yaml.{key}")
    for key in numeric_status_keys:
        if type(status_document[key]) is not int or status_document[key] < 0:
            raise ValueError(f"STATUS.yaml.{key} must be a non-negative integer")

    coordinate_keys = {
        "specification": {
            "release",
            "commit",
            "digest",
            "coordinate_status",
        },
        "simulation": {
            "release",
            "tag_object",
            "commit",
            "digest",
            "archive_format",
            "archive_digest",
            "coordinate_status",
            "canonical_closure_digest",
            "reference_result_digest",
            "aggregate_artifact_digest",
            "canonical_bundle_file_digest",
        },
        "implementation": {
            "release",
            "tag",
            "tag_object",
            "commit",
            "digest",
            "archive_format",
            "archive_digest",
            "coordinate_status",
            "source_binding_status",
            "repository_release",
            "selected_future_closure_digest",
            "contract_bindings",
            "source_artifact_bindings",
        },
        "comparison": {
            "release",
            "tag_object",
            "commit",
            "digest",
            "archive_format",
            "archive_digest",
            "coordinate_status",
            "canonical_closure_digest",
            "aggregate_artifact_digest",
            "receipt_schema",
            "historical_governance_schema",
        },
        "governance": {
            "release",
            "profile",
            "schema_version",
            "tag_object",
            "commit",
            "digest",
            "archive_format",
            "archive_digest",
            "coordinate_status",
        },
    }
    for role, expected_keys in coordinate_keys.items():
        coordinate = require_exact_object(
            constellation_lock[role],
            expected_keys,
            f"constellation_lock.{role}",
        )
        string_keys = expected_keys - {
            "contract_bindings",
            "historical_governance_schema",
            "source_artifact_bindings",
        }
        for key in string_keys:
            require_string(coordinate[key], f"constellation_lock.{role}.{key}")
    implementation_contract_bindings = require_exact_object(
        constellation_lock["implementation"]["contract_bindings"],
        set(IMPLEMENTATION_CONTRACT_BINDINGS),
        "constellation_lock.implementation.contract_bindings",
    )
    for key in implementation_contract_bindings:
        require_string(
            implementation_contract_bindings[key],
            f"constellation_lock.implementation.contract_bindings.{key}",
        )
    implementation_source_artifacts = require_exact_object(
        constellation_lock["implementation"]["source_artifact_bindings"],
        set(IMPLEMENTATION_SOURCE_ARTIFACT_BINDINGS),
        "constellation_lock.implementation.source_artifact_bindings",
    )
    for binding_name, binding in implementation_source_artifacts.items():
        binding = require_exact_object(
            binding,
            {"path", "digest", "equality_mode"},
            (
                "constellation_lock.implementation.source_artifact_bindings."
                f"{binding_name}"
            ),
        )
        for key in binding:
            require_string(
                binding[key],
                (
                    "constellation_lock.implementation.source_artifact_bindings."
                    f"{binding_name}.{key}"
                ),
            )
    historical_governance_schema = require_exact_object(
        constellation_lock["comparison"]["historical_governance_schema"],
        set(COMPARISON_HISTORICAL_GOVERNANCE_SCHEMA),
        "constellation_lock.comparison.historical_governance_schema",
    )
    for key in set(COMPARISON_HISTORICAL_GOVERNANCE_SCHEMA) - {"release_tag"}:
        require_string(
            historical_governance_schema[key],
            f"constellation_lock.comparison.historical_governance_schema.{key}",
        )
    if historical_governance_schema["release_tag"] is not None:
        raise ValueError(
            "historical Governance compatibility coordinate requires a null "
            "release tag"
        )
    require_string_list(
        [
            item.get("repository_role", "")
            for item in constellation_lock["seed_lineage"]
            if isinstance(item, dict)
        ],
        "constellation_lock.seed_lineage repository roles",
        minimum=5,
    )

    require_exact_object(
        release_role["release_coordinates"],
        {"commit", "tree_digest", "coordinate_status"},
        "release_role.release_coordinates",
    )
    require_exact_object(
        release_role["promotion_coordinates"],
        {
            "status",
            "receipt_id",
            "receipt_path",
            "observation_path",
            "observation_schema_path",
            "required_roles",
        },
        "release_role.promotion_coordinates",
    )
    require_string_list(
        release_role["promotion_coordinates"]["required_roles"],
        "release_role.promotion_coordinates.required_roles",
        minimum=5,
    )
    for key in {
        "manifest_version",
        "repository_role",
        "repository_release",
        "external_release",
        "release_state",
        "authority_posture",
    }:
        require_string(release_role[key], f"release_role.{key}")
    canonical_closure = require_exact_object(
        release_role["canonical_closure"],
        {
            "closure_id",
            "future_reality_id",
            "digest",
            "reference_result_digest",
            "aggregate_artifact_digest",
            "bundle_path",
            "bundle_file_digest",
            "authority",
            "production_authorization_effect",
        },
        "release_role.canonical_closure",
    )
    advisory_design = require_exact_object(
        release_role["advisory_design"],
        {"simulation_id", "future_reality_id", "digest", "authority"},
        "release_role.advisory_design",
    )
    contract_bindings = require_exact_object(
        release_role["contract_bindings"],
        {
            "governance_schema",
            "control_plane_profile",
            "language_policy_release",
            "language_policy_manifest",
            "bounded_caller_contract",
            "practitioner_probe_catalog",
            "proof_class_registry",
            "receipt_vocabulary_map",
            "data_primitive_finding_ledger",
            "database_constellation_finding_index",
            "database_modernization_plan_set",
            "data_contract",
            "database_migration_contract",
            "database_open_receipts",
            "database_release_manifest",
        },
        "release_role.contract_bindings",
    )
    require_exact_object(
        release_role["automation_controls"],
        {"contract_version", "pull_request", "dependabot"},
        "release_role.automation_controls",
    )
    promotion_controls = require_exact_object(
        release_role["promotion_controls"],
        {"standing_branch_controls", "release_review_route"},
        "release_role.promotion_controls",
    )
    standing_branch_controls = require_exact_object(
        promotion_controls["standing_branch_controls"],
        set(STANDING_BRANCH_CONTROLS),
        "release_role.promotion_controls.standing_branch_controls",
    )
    if standing_branch_controls != STANDING_BRANCH_CONTROLS:
        raise ValueError(
            "release_role standing branch controls differ from their current record"
        )
    validate_release_review_route(
        promotion_controls["release_review_route"],
        "release_role.promotion_controls.release_review_route",
    )
    receipt_binding = require_exact_object(
        contract_bindings["receipt_vocabulary_map"],
        {"contract_id", "version", "digest"},
        "release_role.contract_bindings.receipt_vocabulary_map",
    )
    language_policy_binding = require_exact_object(
        contract_bindings["language_policy_manifest"],
        {"path", "digest", "core_digest", "corpus_digest"},
        "release_role.contract_bindings.language_policy_manifest",
    )
    for binding_name in (
        "data_primitive_finding_ledger",
        "database_constellation_finding_index",
        "database_modernization_plan_set",
        "data_contract",
        "database_migration_contract",
        "database_open_receipts",
        "database_release_manifest",
    ):
        binding = require_exact_object(
            contract_bindings[binding_name],
            {"contract_id", "version", "path", "digest"},
            f"release_role.contract_bindings.{binding_name}",
        )
        for key, value in binding.items():
            require_string(
                value,
                f"release_role.contract_bindings.{binding_name}.{key}",
            )
    require_exact_object(
        release_role["orientation_surfaces"],
        {
            "machine_node",
            "first_receipt",
            "coordination_horizon",
            "constellation_lock",
        },
        "release_role.orientation_surfaces",
    )
    require_exact_object(
        release_role["seed_lineage"],
        {"release", "commit", "digest", "digest_scope"},
        "release_role.seed_lineage",
    )
    for label, mapping in (
        ("release_role.canonical_closure", canonical_closure),
        ("release_role.advisory_design", advisory_design),
        ("release_role.contract_bindings", contract_bindings),
        (
            "release_role.contract_bindings.receipt_vocabulary_map",
            receipt_binding,
        ),
        (
            "release_role.contract_bindings.language_policy_manifest",
            language_policy_binding,
        ),
        ("release_role.orientation_surfaces", release_role["orientation_surfaces"]),
        ("release_role.seed_lineage", release_role["seed_lineage"]),
        ("release_role.release_coordinates", release_role["release_coordinates"]),
    ):
        for key, value in mapping.items():
            if isinstance(value, dict):
                continue
            require_string(value, f"{label}.{key}")

    require_exact_object(
        constellation_lock["seed"],
        {"repository", "source_commit", "merge_commit"},
        "constellation_lock.seed",
    )
    if not isinstance(constellation_lock["seed_lineage"], list):
        raise ValueError("constellation_lock.seed_lineage must be a list")
    for index, item in enumerate(constellation_lock["seed_lineage"]):
        if not isinstance(item, dict):
            raise ValueError(
                f"constellation_lock.seed_lineage[{index}] must be an object"
            )
        expected_keys = (
            {"repository_role", "release", "commit", "digest", "digest_scope"}
            if "digest" in item
            else {"repository_role", "release", "commit", "coordinate_status"}
        )
        require_exact_object(
            item,
            expected_keys,
            f"constellation_lock.seed_lineage[{index}]",
        )
        for key, value in item.items():
            require_string(
                value,
                f"constellation_lock.seed_lineage[{index}].{key}",
            )

    require_exact_object(
        promotion_receipt,
        PROMOTION_RECEIPT_KEYS,
        "promotion_receipt",
    )
    candidate_coordinate = require_exact_object(
        promotion_receipt["candidate_coordinate"],
        {"release", "commit", "digest"},
        "promotion_receipt.candidate_coordinate",
    )
    for key in candidate_coordinate:
        require_string(
            candidate_coordinate[key],
            f"promotion_receipt.candidate_coordinate.{key}",
        )
    release_coordinate = promotion_receipt["release_coordinate"]
    validate_release_review_route(
        promotion_receipt["release_review_route"],
        "promotion_receipt.release_review_route",
    )
    if release_coordinate is not None:
        release_coordinate = require_exact_object(
            release_coordinate,
            {
                "tag",
                "commit",
                "digest",
                "promoted_at",
                "check_contexts",
                "pull_request",
                "review_observation",
            },
            "promotion_receipt.release_coordinate",
        )
        require_string_list(
            release_coordinate["check_contexts"],
            "promotion_receipt.release_coordinate.check_contexts",
            minimum=0,
        )
        for key in {"tag", "commit", "digest", "promoted_at"}:
            require_string(
                release_coordinate[key],
                f"promotion_receipt.release_coordinate.{key}",
            )
        if (
            type(release_coordinate["pull_request"]) is not int
            or release_coordinate["pull_request"] < 1
        ):
            raise ValueError(
                "promotion_receipt.release_coordinate.pull_request must be positive"
            )
        validate_release_review_route(
            release_coordinate["review_observation"],
            "promotion_receipt.release_coordinate.review_observation",
        )
    require_string_list(
        promotion_receipt["required_evidence"],
        "promotion_receipt.required_evidence",
        minimum=4,
    )
    require_string(
        promotion_receipt["accountable_role"],
        "promotion_receipt.accountable_role",
    )
    promotion_metadata = require_exact_object(
        promotion_receipt["metadata"],
        {"schema_version", "created_at", "updated_at", "owner"},
        "promotion_receipt.metadata",
    )
    promotion_owner = require_exact_object(
        promotion_metadata["owner"],
        {"actor_id", "display_name", "role"},
        "promotion_receipt.metadata.owner",
    )
    for key in {"schema_version", "created_at", "updated_at"}:
        require_string(
            promotion_metadata[key],
            f"promotion_receipt.metadata.{key}",
        )
    for key, value in promotion_owner.items():
        require_string(value, f"promotion_receipt.metadata.owner.{key}")

    repositories = constellation["repositories"]
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("constellation.repositories must be a populated list")
    for index, repository in enumerate(repositories):
        require_exact_object(
            repository,
            {"role", "repository", "authority"},
            f"constellation.repositories[{index}]",
        )
        for key in repository:
            require_string(
                repository[key],
                f"constellation.repositories[{index}].{key}",
            )


def validate_release_lifecycle(
    *,
    release_role: dict,
    machine_node: dict,
    first_receipt: dict,
    coordination_horizon: dict,
    promotion_receipt: dict,
    release_observation: dict,
    constellation_lock: dict,
    status_document: dict,
    substantive_receipt_ids: set[str],
) -> None:
    """Validate both candidate and settled release states without mixed evidence."""
    state = release_role["release_state"]
    release_coordinates = release_role["release_coordinates"]
    promotion_coordinates = release_role["promotion_coordinates"]
    promotion_controls = release_role["promotion_controls"]
    provenance = machine_node["current_provenance"]
    promotion_id = promotion_receipt["promotion_receipt_id"]
    promotion_items = [
        item
        for item in coordination_horizon["work_items"]
        if "promotion"
        in " ".join(
            str(item.get(field, ""))
            for field in ("item_id", "horizon_label", "desired_state")
        ).lower()
    ]
    if (
        promotion_id != PROMOTION_RECEIPT_ID
        or promotion_receipt["repository"]
        != "driftframestudios/lims-eln-program-specification"
        or promotion_receipt["target_release"] != PROGRAM_TAG
        or promotion_coordinates["receipt_id"] != promotion_id
        or promotion_coordinates["receipt_path"]
        != "receipts/promotion-receipt.json"
        or promotion_coordinates["observation_path"]
        != "receipts/promotion-observation-spec-v0.3.1.json"
        or promotion_coordinates["observation_schema_path"]
        != "schemas/program-release-observation.v1.schema.json"
        or release_observation["promotion_receipt_id"] != promotion_id
        or release_observation["target_release"] != PROGRAM_TAG
        or promotion_receipt["release_review_route"] != RELEASE_REVIEW_ROUTE
        or promotion_controls["release_review_route"] != RELEASE_REVIEW_ROUTE
    ):
        raise ValueError(
            "promotion receipt or release observation identity differs"
        )
    if promotion_receipt["candidate_coordinate"] != {
        "release": f"candidate-{PROGRAM_TAG}",
        "commit": PENDING_COMMIT,
        "digest": "sha256:" + ("0" * 64),
    }:
        raise ValueError("promotion receipt candidate coordinate differs")

    node_receipts = set(machine_node["open_receipts"])
    first_receipts = set(first_receipt["open_receipts"])
    if node_receipts != first_receipts:
        raise ValueError("Machine Node and first receipt open sets differ")

    if state == "candidate_pending_promotion":
        expected_open = substantive_receipt_ids | {PROMOTION_RECEIPT_ID}
        if node_receipts != expected_open:
            raise ValueError(
                "candidate orientation must include substantive and promotion receipts"
            )
        if (
            release_coordinates
            != {
                "commit": PENDING_COMMIT,
                "tree_digest": PENDING_TREE_DIGEST,
                "coordinate_status": "pending_release_commit",
            }
            or constellation_lock["specification"]["coordinate_status"]
            != "pending_release_commit"
            or constellation_lock["specification"]["commit"] != PENDING_COMMIT
            or constellation_lock["specification"]["digest"]
            != PENDING_TREE_DIGEST
        ):
            raise ValueError("candidate release coordinates require zero placeholders")
        if (
            machine_node["lifecycle_state"] != "settling"
            or provenance["commit"] != PENDING_COMMIT
            or provenance["digest"] != "sha256:" + ("0" * 64)
            or provenance["release"] != f"candidate-{PROGRAM_TAG}"
            or "seed_lineage" not in machine_node
        ):
            raise ValueError(
                "candidate Machine Node requires settling placeholder provenance"
            )
        expected_promotion_status = (
            "ready_for_authorized_promotion"
            if all(
                constellation_lock[role]["coordinate_status"] == "pinned"
                for role in RELEASE_PATTERNS
                if role != "specification"
            )
            else "pending_cross_repository_settlement"
        )
        if (
            promotion_receipt["promotion_state"] != "candidate_pending"
            or promotion_receipt["evidence_mode"] != "planned"
            or promotion_receipt["assurance_stage"] != "specified"
            or promotion_receipt["candidate_coordinate"] != provenance
            or promotion_receipt["release_coordinate"] is not None
            or promotion_coordinates["status"] != expected_promotion_status
            or release_observation["observation_state"] != "pending_post_tag"
        ):
            raise ValueError(
                "candidate promotion and release observation posture differs"
            )
        current_ids = set(coordination_horizon["current_item_ids"])
        if not any(
            item.get("item_id") in current_ids
            and item.get("state") == "settling"
            for item in promotion_items
        ):
            raise ValueError(
                "candidate lifecycle requires a current settling promotion item"
            )
        if (
            status_document["status"] != "settling"
            or status_document["release_coordinate_status"]
            != "pending_release_commit"
        ):
            raise ValueError("candidate STATUS lifecycle differs")
        return

    if state != "released":
        raise ValueError(
            "release_state must be candidate_pending_promotion or released"
        )
    expected_open = substantive_receipt_ids
    if node_receipts != expected_open:
        raise ValueError("released orientation must close the promotion receipt")
    if (
        release_coordinates["coordinate_status"] != "pinned"
        or MATERIAL_COMMIT_PATTERN.fullmatch(release_coordinates["commit"]) is None
        or MATERIAL_TREE_DIGEST_PATTERN.fullmatch(
            release_coordinates["tree_digest"]
        )
        is None
        or constellation_lock["specification"]["coordinate_status"] != "pinned"
        or constellation_lock["specification"]["commit"]
        != release_coordinates["commit"]
        or constellation_lock["specification"]["digest"]
        != release_coordinates["tree_digest"]
        or provenance["commit"] != release_coordinates["commit"]
    ):
        raise ValueError("released specification coordinates must be pinned and equal")
    for role in RELEASE_PATTERNS:
        if constellation_lock[role]["coordinate_status"] != "pinned":
            raise ValueError(
                "released program state requires every constellation coordinate pinned"
            )
    release_coordinate = promotion_receipt["release_coordinate"]
    release_subject = release_observation["release_subject"]
    workflow_observation = release_observation["workflow_observation"]
    review_observation = release_observation["review_observation"]
    if (
        machine_node["lifecycle_state"] not in {"reference_ready", "active"}
        or provenance["release"] != PROGRAM_TAG
        or MATERIAL_COMMIT_PATTERN.fullmatch(provenance["commit"]) is None
        or MATERIAL_SHA256_PATTERN.fullmatch(provenance["digest"]) is None
        or promotion_receipt["promotion_state"] != "released"
        or promotion_receipt["evidence_mode"] != "observed"
        or promotion_receipt["assurance_stage"] == "specified"
        or not isinstance(release_coordinate, dict)
        or release_coordinate.get("tag") != PROGRAM_TAG
        or release_coordinate.get("commit") != provenance["commit"]
        or release_coordinate.get("digest") != provenance["digest"]
        or not set(release_coordinate.get("check_contexts", [])).issubset(
            {"program-validation"}
        )
        or release_observation["observation_state"] != "release_observed"
        or not isinstance(release_subject, dict)
        or release_subject.get("tag") != PROGRAM_TAG
        or release_subject.get("commit_oid") != provenance["commit"]
        or release_subject.get("tree_oid")
        != release_coordinates["tree_digest"].removeprefix("git-tree-sha1:")
        or not isinstance(workflow_observation, dict)
        or workflow_observation.get("check_context")
        not in release_coordinate.get("check_contexts", [])
        or not isinstance(review_observation, dict)
        or review_observation.get("pull_request")
        != release_coordinate.get("pull_request")
        or {
            key: review_observation.get(key)
            for key in RELEASE_REVIEW_ROUTE
        }
        != release_coordinate.get("review_observation")
        or release_coordinate.get("review_observation")
        != RELEASE_REVIEW_ROUTE
        or promotion_coordinates["status"] != "settled"
    ):
        raise ValueError("released promotion evidence or Machine Node posture differs")
    if not promotion_items or any(
        item.get("state") != "complete" for item in promotion_items
    ):
        raise ValueError("released lifecycle requires completed promotion work")
    if (
        status_document["status"] != "released"
        or status_document["release_coordinate_status"] != "pinned"
        or status_document["governance_coordinate_status"] != "pinned"
    ):
        raise ValueError("released STATUS lifecycle differs")


def sha256_digest(relative_path: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def canonical_json_digest(document: dict) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def unique_ids(records: list[dict], label: str) -> set[str]:
    values = [record["id"] for record in records]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} identifiers contain duplicates")
    return set(values)


def validate_database_program(
    *,
    ledger: dict,
    constellation_index: dict,
    plan_set: dict,
    data_contract: dict,
    migration_contract: dict,
    database_receipts: dict,
    database_manifest: dict,
    release_role: dict,
    status_document: dict,
    requirement_ids: set[str],
    rule_ids: set[str],
    scenario_ids: set[str],
    role_ids: set[str],
) -> dict[str, int]:
    """Validate the database program as one closed, traceable contract surface."""
    require_exact_object(
        ledger,
        {
            "ledger_id",
            "version",
            "status",
            "scope",
            "severity_vocabulary",
            "findings",
            "evidence_sources",
            "metadata",
        },
        "database primitive finding ledger",
    )
    if (
        ledger["ledger_id"] != "LIMS-ELN-DATA-PRIMITIVE-LEDGER-001"
        or ledger["version"] != "1.0.0"
        or ledger["status"] != "accepted_for_program_projection"
    ):
        raise ValueError("database primitive finding ledger identity differs")
    severity_vocabulary = require_exact_object(
        ledger["severity_vocabulary"],
        {"critical", "high"},
        "database primitive severity vocabulary",
    )
    for severity, meaning in severity_vocabulary.items():
        require_string(meaning, f"database severity {severity}")
    finding_ids: set[str] = set()
    finding_categories: set[str] = set()
    finding_repositories: set[str] = set()
    finding_bindings: dict[str, set[str]] = {}
    allowed_finding_bindings = {
        "DATA-CONTRACT-001",
        "DATABASE-MIGRATION-CONTRACT-001",
        "DATABASE-RELEASE-MANIFEST-001",
    }
    for index, finding in enumerate(ledger["findings"]):
        finding = require_exact_object(
            finding,
            {
                "id",
                "severity",
                "category",
                "sources",
                "observation",
                "material_risk",
                "target_state",
                "correction",
                "binding_ids",
            },
            f"database finding[{index}]",
        )
        finding_id = require_string(finding["id"], f"finding[{index}].id")
        if re.fullmatch(r"DBF-[A-Z]+-[0-9]{3}", finding_id) is None:
            raise ValueError(f"database finding identifier {finding_id!r} differs")
        if finding_id in finding_ids:
            raise ValueError(f"database finding {finding_id} appears more than once")
        finding_ids.add(finding_id)
        if finding["severity"] not in severity_vocabulary:
            raise ValueError(f"{finding_id} uses an undeclared severity")
        category = require_string(finding["category"], f"{finding_id}.category")
        finding_categories.add(category)
        for field in ("observation", "material_risk", "target_state", "correction"):
            require_string(finding[field], f"{finding_id}.{field}")
        binding_ids = set(
            require_string_list(
                finding["binding_ids"],
                f"{finding_id}.binding_ids",
                minimum=1,
            )
        )
        if not binding_ids <= allowed_finding_bindings:
            raise ValueError(f"{finding_id} references an unknown contract binding")
        finding_bindings[finding_id] = binding_ids
        if not isinstance(finding["sources"], list) or not finding["sources"]:
            raise ValueError(f"{finding_id}.sources requires at least one location")
        for source_index, source in enumerate(finding["sources"]):
            source = require_exact_object(
                source,
                {"repository", "path", "lines"},
                f"{finding_id}.sources[{source_index}]",
            )
            for key, value in source.items():
                require_string(value, f"{finding_id}.sources[{source_index}].{key}")
            finding_repositories.add(source["repository"])
    required_categories = {
        "temporal_semantics",
        "identifiers",
        "digests",
        "numeric_precision_units",
        "controlled_vocabularies",
        "json_contracts",
        "nullability_constraints",
        "relational_integrity",
        "audit_immutability",
        "tenancy_rls",
        "indexing_partitioning",
        "idempotency",
        "migration_lifecycle",
        "reconciliation",
        "tests_validation",
        "fork_divergence",
    }
    if not required_categories <= finding_categories:
        raise ValueError(
            "database finding ledger category coverage differs: "
            f"missing={sorted(required_categories - finding_categories)}"
        )
    if finding_repositories != {"prototype-exemplars", "reference-pack"}:
        raise ValueError("database finding ledger repository coverage differs")
    if len(finding_ids) != 32:
        raise ValueError("database finding ledger requires 32 stable findings")

    require_exact_object(
        constellation_index,
        {
            "index_id",
            "version",
            "authority",
            "counting_semantics",
            "canonical_probability_event",
            "sources",
            "total_record_count",
            "metadata",
        },
        "database constellation finding index",
    )
    if (
        constellation_index["index_id"]
        != "DATABASE-CONSTELLATION-FINDING-INDEX-001"
        or constellation_index["version"] != "1.0.0"
        or constellation_index["authority"]
        != "cross_repository_discovery_index"
    ):
        raise ValueError("database constellation finding index identity differs")
    require_string(
        constellation_index["counting_semantics"],
        "database constellation counting semantics",
    )
    probability_event = require_exact_object(
        constellation_index["canonical_probability_event"],
        {"event_id", "plan_set_id", "probability_of"},
        "database constellation canonical probability event",
    )
    if probability_event != {
        "event_id": "DATABASE-ENTERPRISE-RELEASE-CANDIDATE-001",
        "plan_set_id": "DATABASE-MODERNIZATION-PLAN-SET-001",
        "probability_of": DATABASE_PROBABILITY_EVENT,
    }:
        raise ValueError("database constellation probability event differs")
    constellation_metadata = require_exact_object(
        constellation_index["metadata"],
        {"created_at", "evidence_mode", "authority", "revalidation_trigger"},
        "database constellation metadata",
    )
    if (
        constellation_metadata["evidence_mode"] != "repository_observed"
        or constellation_metadata["authority"] != "program_index_only"
    ):
        raise ValueError("database constellation evidence authority differs")
    created_at = require_string(
        constellation_metadata["created_at"],
        "database constellation created_at",
    )
    try:
        created_at_instant = datetime.strptime(
            created_at, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError(
            "database constellation created_at requires canonical RFC 3339 UTC"
        ) from error
    if created_at_instant > datetime.now(timezone.utc):
        raise ValueError(
            "database constellation created_at requires an observed finalization instant"
        )
    require_string(
        constellation_metadata["revalidation_trigger"],
        "database constellation revalidation trigger",
    )
    if not isinstance(constellation_index["sources"], list):
        raise ValueError("database constellation sources require an array")

    expected_sources = {
        "PROGRAM-DISCOVERY-FINDINGS": {
            "repository": "driftframestudios/lims-eln-program-specification",
            "pull_request": (
                "https://github.com/driftframestudios/"
                "lims-eln-program-specification/pull/11"
            ),
            "head_ref": "feature/corrective-integrity-v0-3-1",
            "source_commit": "fc1577a8886842c606ccbc3c115c7b812fd5dfca",
            "coordinate_kind": "same_release_artifact_digest",
            "ledger_path": "database/primitive-findings.json",
            "ledger_format": "json_findings",
            "ledger_digest": sha256_digest("database/primitive-findings.json"),
            "record_ids": finding_ids,
            "probability_kind": "canonical",
            "probability_event": DATABASE_PROBABILITY_EVENT,
            "probability_surface": "plans/database-modernization-plans.json",
        },
        "REFERENCE-PACK-FINDINGS": {
            "repository": "driftframestudios/prototype-exemplars",
            "pull_request": (
                "https://github.com/driftframestudios/"
                "prototype-exemplars/pull/4"
            ),
            "head_ref": "agent/lims-eln-data-primitives-v0-2",
            "source_commit": "0ed46249247c8b1c7f69c385fe82bd2052eacd63",
            "coordinate_kind": "pull_request_head",
            "ledger_path": (
                "lims-eln-enterprise-reference-v0.1/database/"
                "data-primitive-ledger.json"
            ),
            "ledger_format": "json_findings",
            "ledger_digest": (
                "sha256:69d09afa87ff9e869f386d6b3ba666a8c765f910377146b327"
                "a191fa640ea74f"
            ),
            "record_count": 53,
            "record_id_prefix": "DB-",
            "probability_kind": "conditional_derivative",
            "probability_event": (
                "What is the probability that one implementation tranche reaches a "
                "promotion-ready database-definition state in which every critical "
                "and high primitive finding has an accepted disposition, clean "
                "installation and every supported upgrade path converge to one "
                "canonical semantic fingerprint, migration evidence retains its "
                "independently computed fingerprint, representative migration and "
                "restore rehearsals pass, and accountable reviewers bind their "
                "decisions to the same evidence bundle?"
            ),
            "probability_surface": (
                "lims-eln-enterprise-reference-v0.1/docs/"
                "database-refactor-plan.md"
            ),
        },
        "ACTIVE-IMPLEMENTATION-FINDINGS": {
            "repository": "driftframestudios/lims-eln-enterprise-implementation",
            "pull_request": (
                "https://github.com/driftframestudios/"
                "lims-eln-enterprise-implementation/pull/10"
            ),
            "head_ref": "feature/corrective-integrity-v0-3-1",
            "source_commit": "fc4b79dba989faeafff3f0fb871d292381fe2168",
            "coordinate_kind": "pull_request_head",
            "ledger_path": "docs/data-primitive-corrective-ledger.md",
            "ledger_format": "markdown_table",
            "ledger_digest": (
                "sha256:f4537dc88317056b91376ff50721b009d571a2d2c747d8f6fe7"
                "935a0266efb38"
            ),
            "record_count": 30,
            "record_id_prefix": "DP-",
            "probability_kind": "conditional_derivative",
            "probability_event": (
                "Given a capable delivery team, one release cycle, the stated gates, "
                "and a representative PostgreSQL rehearsal, what is the probability "
                "that the plan reaches a release candidate which passes independent "
                "principal-engineer, database, security, operations, and scientific "
                "review with only bounded follow-up?"
            ),
            "probability_surface": "docs/data-primitive-corrective-ledger.md",
        },
    }
    observed_source_ids: set[str] = set()
    aggregate_record_ids: set[tuple[str, str]] = set()
    for index, source in enumerate(constellation_index["sources"]):
        source = require_exact_object(
            source,
            {
                "source_id",
                "repository",
                "pull_request",
                "head_ref",
                "source_commit",
                "coordinate_kind",
                "ledger_path",
                "retrieval_url",
                "ledger_format",
                "ledger_digest",
                "record_count",
                "record_ids",
                "probability_relation",
            },
            f"database constellation source[{index}]",
        )
        source_id = require_string(source["source_id"], f"source[{index}].id")
        if source_id in observed_source_ids or source_id not in expected_sources:
            raise ValueError(f"database constellation source {source_id!r} differs")
        observed_source_ids.add(source_id)
        expected = expected_sources[source_id]
        coordinate_fields = [
            "repository",
            "pull_request",
            "head_ref",
            "coordinate_kind",
            "ledger_path",
            "ledger_format",
        ]
        coordinate_fields.extend(
            field
            for field in ("source_commit", "ledger_digest")
            if field in expected
        )
        if MATERIAL_COMMIT_PATTERN.fullmatch(source["source_commit"]) is None:
            raise ValueError(
                f"database constellation source {source_id} requires an immutable commit"
            )
        if MATERIAL_SHA256_PATTERN.fullmatch(source["ledger_digest"]) is None:
            raise ValueError(
                f"database constellation source {source_id} requires a material digest"
            )
        for field in coordinate_fields:
            if source[field] != expected[field]:
                raise ValueError(
                    f"database constellation source {source_id} {field} differs"
                )
        expected_retrieval_url = (
            "https://raw.githubusercontent.com/"
            f"{source['repository']}/{source['source_commit']}/"
            f"{source['ledger_path']}"
        )
        if source["retrieval_url"] != expected_retrieval_url:
            raise ValueError(
                f"database constellation source {source_id} retrieval coordinate differs"
            )
        if type(source["record_count"]) is not int or source["record_count"] < 1:
            raise ValueError(
                f"database constellation source {source_id} requires a positive count"
            )
        if source["record_count"] != expected.get(
            "record_count", len(expected.get("record_ids", ()))
        ):
            raise ValueError(
                f"database constellation source {source_id} released count differs"
            )
        record_ids = require_string_list(
            source["record_ids"], f"{source_id}.record_ids", minimum=1
        )
        if "record_ids" in expected:
            expected_record_ids = expected["record_ids"]
        else:
            expected_record_ids = {
                f"{expected['record_id_prefix']}{number:03d}"
                for number in range(1, expected["record_count"] + 1)
            }
        if set(record_ids) != expected_record_ids:
            raise ValueError(
                f"database constellation source {source_id} record identities differ"
            )
        if source["record_count"] != len(record_ids):
            raise ValueError(
                f"database constellation source {source_id} record count differs"
            )
        aggregate_record_ids.update((source_id, item) for item in record_ids)
        probability_relation = require_exact_object(
            source["probability_relation"],
            {"kind", "estimated_event", "surface", "interpretation"},
            f"{source_id}.probability_relation",
        )
        if (
            probability_relation["kind"] != expected["probability_kind"]
            or probability_relation["estimated_event"]
            != expected["probability_event"]
            or probability_relation["surface"]
            != expected["probability_surface"]
        ):
            raise ValueError(
                f"database constellation source {source_id} probability relation differs"
            )
        require_string(
            probability_relation["interpretation"],
            f"{source_id}.probability_relation.interpretation",
        )
    if observed_source_ids != set(expected_sources):
        raise ValueError("database constellation source inventory differs")
    if (
        constellation_index["total_record_count"]
        != DATABASE_CONSTELLATION_FINDING_TOTAL
        or len(aggregate_record_ids) != DATABASE_CONSTELLATION_FINDING_TOTAL
    ):
        raise ValueError(
            "database constellation index requires the released bound-record total"
        )

    require_exact_object(
        plan_set,
        {
            "plan_set_id",
            "version",
            "probability_of",
            "estimation_posture",
            "flyway_transition_estimate",
            "plans",
            "recommended_synthesis",
            "chain_of_action",
            "metadata",
        },
        "database modernization plan set",
    )
    if (
        plan_set["plan_set_id"] != "DATABASE-MODERNIZATION-PLAN-SET-001"
        or plan_set["version"] != "1.0.0"
    ):
        raise ValueError("database modernization plan set identity differs")
    if plan_set["probability_of"] != DATABASE_PROBABILITY_EVENT:
        raise ValueError("database plan set probability event differs")
    estimation_posture = require_exact_object(
        plan_set["estimation_posture"],
        {
            "method",
            "interpretation",
            "conditioning_assumptions",
            "recalibration_triggers",
        },
        "database estimation posture",
    )
    require_string(estimation_posture["method"], "database estimation method")
    require_string(
        estimation_posture["interpretation"],
        "database estimation interpretation",
    )
    assumptions = tuple(
        require_string_list(
            estimation_posture["conditioning_assumptions"],
            "database probability assumptions",
            minimum=5,
        )
    )
    if assumptions != DATABASE_PROBABILITY_ASSUMPTIONS:
        raise ValueError("database probability conditioning assumptions differ")
    require_string_list(
        estimation_posture["recalibration_triggers"],
        "database probability recalibration triggers",
        minimum=4,
    )
    transition = require_exact_object(
        plan_set["flyway_transition_estimate"],
        {
            "event_id",
            "probability_of",
            "estimated_probability",
            "credible_range",
            "relationship_to_canonical_event",
            "basis",
            "falsifiers",
            "recalibration_triggers",
        },
        "Flyway transition estimate",
    )
    if (
        transition["event_id"] != "FLYWAY-TRANSITION-EQUIVALENCE-001"
        or transition["probability_of"] != FLYWAY_TRANSITION_EVENT
    ):
        raise ValueError("Flyway transition probability event differs")
    transition_lower, transition_upper = transition["credible_range"]
    if not (
        0
        <= transition_lower
        <= transition["estimated_probability"]
        <= transition_upper
        <= 1
    ):
        raise ValueError("Flyway transition probability range differs")
    require_string(
        transition["relationship_to_canonical_event"],
        "Flyway transition probability relationship",
    )
    for field in ("basis", "falsifiers", "recalibration_triggers"):
        require_string_list(
            transition[field], f"Flyway transition {field}", minimum=4
        )
    if len(plan_set["plans"]) != 5:
        raise ValueError("database plan set requires five comparative routes")
    plan_ids: set[str] = set()
    for index, plan in enumerate(plan_set["plans"]):
        plan = require_exact_object(
            plan,
            {
                "id",
                "name",
                "probability",
                "credible_range",
                "route",
                "strengths",
                "tradeoffs",
                "best_fit",
                "falsifiers",
            },
            f"database plan[{index}]",
        )
        plan_id = require_string(plan["id"], f"database plan[{index}].id")
        if plan_id in plan_ids:
            raise ValueError(f"database plan {plan_id} appears more than once")
        plan_ids.add(plan_id)
        lower, upper = plan["credible_range"]
        probability = plan["probability"]
        if not (0 <= lower <= probability <= upper <= 1):
            raise ValueError(f"{plan_id} probability range differs")
        for field in ("name", "route", "best_fit"):
            require_string(plan[field], f"{plan_id}.{field}")
        for field in ("strengths", "tradeoffs", "falsifiers"):
            require_string_list(plan[field], f"{plan_id}.{field}", minimum=2)
    if plan_ids != {f"DB-PLAN-0{index}" for index in range(1, 6)}:
        raise ValueError("database comparative route identifiers differ")
    synthesis = require_exact_object(
        plan_set["recommended_synthesis"],
        {
            "recommendation_id",
            "estimated_probability",
            "credible_range",
            "composition",
            "rationale",
        },
        "database recommended synthesis",
    )
    lower, upper = synthesis["credible_range"]
    if not (0 <= lower <= synthesis["estimated_probability"] <= upper <= 1):
        raise ValueError("database synthesis probability range differs")
    synthesis_plan_ids = {
        item["plan_id"] for item in synthesis["composition"]
    }
    if synthesis_plan_ids != plan_ids:
        raise ValueError("database synthesis plan coverage differs")
    stages = plan_set["chain_of_action"]
    if [item["sequence"] for item in stages] != list(range(1, 8)):
        raise ValueError("database action chain requires ordered stages 1 through 7")
    stage_ids: set[str] = set()
    for index, stage in enumerate(stages):
        stage = require_exact_object(
            stage,
            {
                "stage_id",
                "sequence",
                "name",
                "actions",
                "completion_evidence",
                "interstitial",
            },
            f"database stage[{index}]",
        )
        stage_id = require_string(stage["stage_id"], f"database stage[{index}].id")
        if stage_id in stage_ids:
            raise ValueError(f"database stage {stage_id} appears more than once")
        stage_ids.add(stage_id)
        require_string_list(stage["actions"], f"{stage_id}.actions", minimum=3)
        require_string_list(
            stage["completion_evidence"],
            f"{stage_id}.completion_evidence",
            minimum=3,
        )
        interstitial = require_exact_object(
            stage["interstitial"],
            {"question", "signals", "response"},
            f"{stage_id}.interstitial",
        )
        require_string(interstitial["question"], f"{stage_id}.question")
        require_string(interstitial["response"], f"{stage_id}.response")
        require_string_list(
            interstitial["signals"], f"{stage_id}.signals", minimum=3
        )
    if stage_ids != {f"DB-STAGE-0{index}" for index in range(1, 8)}:
        raise ValueError("database action-chain stage identifiers differ")

    require_exact_object(
        data_contract,
        {
            "contract_id",
            "version",
            "status",
            "authority",
            "target_platform",
            "primitive_policies",
            "entity_bindings",
            "program_bindings",
            "metadata",
        },
        "data primitive contract",
    )
    if (
        data_contract["contract_id"] != "DATA-CONTRACT-001"
        or data_contract["version"] != "1.0.0"
        or data_contract["status"] != "specified"
    ):
        raise ValueError("data primitive contract identity differs")
    policy_ids = {
        item["policy_id"] for item in data_contract["primitive_policies"]
    }
    required_policy_ids = {
        "DATA-TIME-001",
        "DATA-ID-001",
        "DATA-DIGEST-001",
        "DATA-MEASURE-001",
        "DATA-UNIT-001",
        "DATA-VOCAB-001",
        "DATA-JSON-001",
        "DATA-NULL-001",
        "DATA-TENANT-001",
        "DATA-EVENT-001",
        "DATA-IO-001",
        "DATA-EVIDENCE-001",
        "DATA-ACCESS-001",
    }
    if policy_ids != required_policy_ids:
        raise ValueError("data primitive policy coverage differs")
    policy_finding_ids: set[str] = set()
    for policy in data_contract["primitive_policies"]:
        require_exact_object(
            policy,
            {
                "policy_id",
                "primitive",
                "storage",
                "validation",
                "rule_ids",
                "finding_ids",
            },
            f"data policy {policy['policy_id']}",
        )
        require_string(policy["primitive"], f"{policy['policy_id']}.primitive")
        require_string(policy["storage"], f"{policy['policy_id']}.storage")
        require_string_list(
            policy["validation"], f"{policy['policy_id']}.validation", minimum=3
        )
        if not set(policy["rule_ids"]) <= rule_ids:
            raise ValueError(f"{policy['policy_id']} references unknown rules")
        if not set(policy["finding_ids"]) <= finding_ids:
            raise ValueError(f"{policy['policy_id']} references unknown findings")
        policy_finding_ids.update(policy["finding_ids"])
    for binding in data_contract["entity_bindings"]:
        require_exact_object(
            binding,
            {"entity", "system_of_record", "required_policy_ids"},
            f"data entity binding {binding.get('entity', '<missing>')}",
        )
        if not set(binding["required_policy_ids"]) <= policy_ids:
            raise ValueError(
                f"{binding['entity']} references unknown data primitive policies"
            )
    data_program = require_exact_object(
        data_contract["program_bindings"],
        {"requirement_ids", "rule_ids", "scenario_ids", "open_receipt_ids"},
        "data contract program bindings",
    )
    if not set(data_program["requirement_ids"]) <= requirement_ids:
        raise ValueError("data contract references unknown requirements")
    if not set(data_program["rule_ids"]) <= rule_ids:
        raise ValueError("data contract references unknown rules")
    if not set(data_program["scenario_ids"]) <= scenario_ids:
        raise ValueError("data contract references unknown scenarios")

    require_exact_object(
        migration_contract,
        {
            "migration_contract_id",
            "version",
            "status",
            "authority",
            "data_contract_id",
            "finding_ids",
            "engine_contract",
            "ownership_boundaries",
            "schema_migration_requirements",
            "selected_implementation_profile",
            "phases",
            "reconciliation_dimensions",
            "release_gates",
            "verification_matrix",
            "program_bindings",
            "metadata",
        },
        "database migration contract",
    )
    if (
        migration_contract["migration_contract_id"]
        != "DATABASE-MIGRATION-CONTRACT-001"
        or migration_contract["version"] != "1.0.0"
        or migration_contract["data_contract_id"] != data_contract["contract_id"]
    ):
        raise ValueError("database migration contract identity differs")
    migration_finding_ids = set(migration_contract["finding_ids"])
    if not migration_finding_ids <= finding_ids:
        raise ValueError("database migration contract references unknown findings")
    if policy_finding_ids | migration_finding_ids != finding_ids:
        raise ValueError(
            "database contracts differ from complete finding coverage: "
            f"unbound={sorted(finding_ids - policy_finding_ids - migration_finding_ids)}"
        )
    ledger_migration_finding_ids = {
        finding_id
        for finding_id, binding_ids in finding_bindings.items()
        if "DATABASE-MIGRATION-CONTRACT-001" in binding_ids
    }
    if migration_finding_ids != ledger_migration_finding_ids:
        raise ValueError("database migration finding bindings differ from ledger")
    if any(
        "DATA-CONTRACT-001" not in finding_bindings[finding_id]
        for finding_id in policy_finding_ids
    ):
        raise ValueError("data primitive policy finding bindings differ from ledger")
    ownership_ids: set[str] = set()
    for index, boundary in enumerate(migration_contract["ownership_boundaries"]):
        boundary = require_exact_object(
            boundary,
            {
                "boundary_id",
                "scope",
                "owner",
                "responsibilities",
                "evidence",
            },
            f"database ownership boundary[{index}]",
        )
        boundary_id = require_string(
            boundary["boundary_id"], f"database ownership boundary[{index}].id"
        )
        ownership_ids.add(boundary_id)
        require_string(boundary["scope"], f"{boundary_id}.scope")
        require_string(boundary["owner"], f"{boundary_id}.owner")
        require_string_list(
            boundary["responsibilities"], f"{boundary_id}.responsibilities", minimum=3
        )
        require_string_list(boundary["evidence"], f"{boundary_id}.evidence", minimum=3)
    if ownership_ids != {
        "DB-OWNER-PROGRAM-SCHEMA",
        "DB-OWNER-VENDOR-LIFECYCLE",
        "DB-OWNER-CROSS-VENDOR-MOVEMENT",
        "DB-OWNER-RELEASE-EVIDENCE",
    }:
        raise ValueError("database ownership boundary coverage differs")
    migration_requirements = require_exact_object(
        migration_contract["schema_migration_requirements"],
        {
            "tool_posture",
            "required_capabilities",
            "review_policy",
            "catalog_gate",
            "recovery_policy",
            "scope_boundary",
        },
        "schema migration requirements",
    )
    for field in (
        "tool_posture",
        "review_policy",
        "catalog_gate",
        "recovery_policy",
        "scope_boundary",
    ):
        require_string(migration_requirements[field], f"schema migration {field}")
    required_capabilities = set(
        require_string_list(
            migration_requirements["required_capabilities"],
            "schema migration required capabilities",
            minimum=7,
        )
    )
    if len(required_capabilities) != 7:
        raise ValueError("schema migration capability inventory differs")
    flyway_profile = require_exact_object(
        migration_contract["selected_implementation_profile"],
        {
            "profile_id",
            "product",
            "version",
            "release_date",
            "selection_status",
            "version_policy",
            "migration_pattern",
            "history_relation",
            "commands",
            "configuration_policy",
            "baseline_policy",
            "history_policy",
            "transaction_policy",
            "coordination_policy",
            "community_boundary",
            "transition_receipt",
        },
        "selected Flyway implementation profile",
    )
    if (
        flyway_profile["profile_id"] != "FLYWAY-COMMUNITY-POSTGRESQL-001"
        or flyway_profile["product"] != "Flyway Community"
        or flyway_profile["version"] != "13.0.0"
        or flyway_profile["release_date"] != "2026-07-20"
        or flyway_profile["selection_status"]
        != "selected_for_corrective_transition"
    ):
        raise ValueError("selected Flyway implementation profile differs")
    for field in (
        "version_policy",
        "migration_pattern",
        "history_relation",
        "baseline_policy",
        "history_policy",
        "transaction_policy",
        "coordination_policy",
        "community_boundary",
    ):
        require_string(flyway_profile[field], f"Flyway profile {field}")
    if set(flyway_profile["commands"]) != {
        "flyway validate -outputType=json",
        "flyway info -outputType=json",
        "flyway migrate -outputType=json",
    }:
        raise ValueError("Flyway profile command surface differs")
    configuration_policy = set(
        require_string_list(
            flyway_profile["configuration_policy"],
            "Flyway configuration policy",
            minimum=5,
        )
    )
    if "baselineOnMigrate=false" not in configuration_policy:
        raise ValueError("Flyway profile requires explicit baseline adoption")
    transition_receipt = require_exact_object(
        flyway_profile["transition_receipt"],
        {"receipt_id", "probability_event_id", "required_evidence"},
        "Flyway transition receipt",
    )
    if (
        transition_receipt["receipt_id"] != "RCP-DB-MIGRATION-001"
        or transition_receipt["probability_event_id"]
        != transition["event_id"]
    ):
        raise ValueError("Flyway transition receipt binding differs")
    require_string_list(
        transition_receipt["required_evidence"],
        "Flyway transition receipt evidence",
        minimum=5,
    )
    phases = migration_contract["phases"]
    if len(phases) != 5 or len({item["phase_id"] for item in phases}) != 5:
        raise ValueError("database migration phase coverage differs")
    dimension_ids = {
        item["dimension_id"]
        for item in migration_contract["reconciliation_dimensions"]
    }
    if len(dimension_ids) != 9:
        raise ValueError("database reconciliation dimension coverage differs")
    gate_ids = {item["gate_id"] for item in migration_contract["release_gates"]}
    if len(gate_ids) != 7:
        raise ValueError("database release gate coverage differs")
    if len(migration_contract["verification_matrix"]) < 10:
        raise ValueError("database verification matrix requires ten checks")
    migration_program = require_exact_object(
        migration_contract["program_bindings"],
        {"requirement_ids", "rule_ids", "scenario_ids", "open_receipt_ids"},
        "database migration program bindings",
    )
    if not set(migration_program["requirement_ids"]) <= requirement_ids:
        raise ValueError("database migration contract references unknown requirements")
    if not set(migration_program["rule_ids"]) <= rule_ids:
        raise ValueError("database migration contract references unknown rules")
    if not set(migration_program["scenario_ids"]) <= scenario_ids:
        raise ValueError("database migration contract references unknown scenarios")

    require_exact_object(
        database_receipts,
        {
            "registry_id",
            "version",
            "evidence_posture",
            "receipts",
            "closure_boundary",
            "metadata",
        },
        "database receipt registry",
    )
    if (
        database_receipts["registry_id"] != "DATABASE-OPEN-RECEIPTS-001"
        or database_receipts["version"] != "1.0.0"
        or database_receipts["evidence_posture"] != "future_observed_closure"
    ):
        raise ValueError("database receipt registry identity differs")
    database_receipt_ids: set[str] = set()
    for index, receipt in enumerate(database_receipts["receipts"]):
        receipt = require_exact_object(
            receipt,
            {
                "id",
                "component",
                "status",
                "evidence_mode",
                "success_event",
                "accountable_roles",
                "required_evidence",
                "requalification_triggers",
            },
            f"database receipt[{index}]",
        )
        receipt_id = require_string(receipt["id"], f"database receipt[{index}].id")
        if receipt_id in database_receipt_ids:
            raise ValueError(f"database receipt {receipt_id} appears more than once")
        database_receipt_ids.add(receipt_id)
        if receipt["status"] != "open" or receipt["evidence_mode"] != "observed":
            raise ValueError(f"{receipt_id} future observed posture differs")
        if not set(receipt["accountable_roles"]) <= role_ids:
            raise ValueError(f"{receipt_id} references unknown accountable roles")
        require_string_list(
            receipt["required_evidence"],
            f"{receipt_id}.required_evidence",
            minimum=4,
        )
        require_string_list(
            receipt["requalification_triggers"],
            f"{receipt_id}.requalification_triggers",
            minimum=4,
        )
    if len(database_receipt_ids) != 8:
        raise ValueError("database receipt registry requires eight open receipts")
    bound_receipt_ids = set(data_program["open_receipt_ids"]) | set(
        migration_program["open_receipt_ids"]
    )
    if bound_receipt_ids != database_receipt_ids:
        raise ValueError("database contract receipt coverage differs")

    require_exact_object(
        database_manifest,
        {
            "manifest_id",
            "version",
            "release_state",
            "authority",
            "artifact_bindings",
            "migration_coordinate",
            "reconciliation_binding",
            "required_receipt_ids",
            "required_gate_ids",
            "specification_by_example",
            "settlement_policy",
            "deferred_boundaries",
            "metadata",
        },
        "database release manifest",
    )
    if (
        database_manifest["manifest_id"] != "DATABASE-RELEASE-MANIFEST-001"
        or database_manifest["version"] != "1.0.0"
        or database_manifest["release_state"] != "candidate_contract_surface"
        or database_manifest["authority"] != "program_specification_only"
    ):
        raise ValueError("database release manifest identity differs")
    migration_coordinate = require_exact_object(
        database_manifest["migration_coordinate"],
        {
            "contract_posture",
            "selected_profile",
            "engine_family",
            "status",
            "implementation_release",
            "migration_head",
            "catalog_digest",
            "executable_digest",
        },
        "database release migration coordinate",
    )
    if (
        migration_coordinate["contract_posture"]
        != "tool_neutral_capability_contract"
        or migration_coordinate["selected_profile"]
        != "Flyway Community 13.0.0"
        or migration_coordinate["engine_family"] != "PostgreSQL"
        or migration_coordinate["status"] != "pending_implementation_projection"
        or migration_coordinate["implementation_release"]
        != EXTERNAL_RELEASE_SUBJECTS["implementation"]["release"]
    ):
        raise ValueError("database release migration coordinate differs")
    for field in ("migration_head", "catalog_digest", "executable_digest"):
        if migration_coordinate[field] != "pending_observed_evidence":
            raise ValueError(
                f"database release migration {field} evidence posture differs"
            )
    expected_artifacts = {
        "LIMS-ELN-DATA-PRIMITIVE-LEDGER-001": "database/primitive-findings.json",
        "DATABASE-CONSTELLATION-FINDING-INDEX-001": "database/constellation-finding-index.json",
        "DATABASE-MODERNIZATION-PLAN-SET-001": "plans/database-modernization-plans.json",
        "DATA-CONTRACT-001": "specifications/data-primitives.json",
        "DATABASE-MIGRATION-CONTRACT-001": "specifications/database-migration.json",
        "DATABASE-OPEN-RECEIPTS-001": "receipts/database-open-receipts.json",
        "PROGRAM-CAPABILITIES-0.3.1": "specifications/capabilities.json",
        "PROGRAM-INVARIANTS-0.3.1": "specifications/invariants.json",
        "PROGRAM-SCENARIOS-0.3.1": "examples/scenarios.json",
    }
    observed_artifacts: dict[str, str] = {}
    for index, binding in enumerate(database_manifest["artifact_bindings"]):
        binding = require_exact_object(
            binding,
            {"artifact_id", "version", "path", "digest"},
            f"database manifest artifact[{index}]",
        )
        artifact_id = binding["artifact_id"]
        if artifact_id in observed_artifacts:
            raise ValueError(f"database manifest artifact {artifact_id} repeats")
        observed_artifacts[artifact_id] = binding["path"]
        if binding["digest"] != sha256_digest(binding["path"]):
            raise ValueError(f"database manifest digest differs for {artifact_id}")
    if observed_artifacts != expected_artifacts:
        raise ValueError("database manifest artifact inventory differs")
    if set(database_manifest["required_receipt_ids"]) != database_receipt_ids:
        raise ValueError("database manifest receipt binding differs")
    if set(database_manifest["required_gate_ids"]) != gate_ids:
        raise ValueError("database manifest gate binding differs")
    if not set(database_manifest["specification_by_example"]) <= scenario_ids:
        raise ValueError("database manifest references unknown scenarios")
    reconciliation = database_manifest["reconciliation_binding"]
    if set(reconciliation["required_dimension_ids"]) != dimension_ids:
        raise ValueError("database manifest reconciliation binding differs")

    release_bindings = release_role["contract_bindings"]
    binding_map = {
        "data_primitive_finding_ledger": (
            ledger["ledger_id"],
            "database/primitive-findings.json",
        ),
        "database_constellation_finding_index": (
            constellation_index["index_id"],
            "database/constellation-finding-index.json",
        ),
        "database_modernization_plan_set": (
            plan_set["plan_set_id"],
            "plans/database-modernization-plans.json",
        ),
        "data_contract": (
            data_contract["contract_id"],
            "specifications/data-primitives.json",
        ),
        "database_migration_contract": (
            migration_contract["migration_contract_id"],
            "specifications/database-migration.json",
        ),
        "database_open_receipts": (
            database_receipts["registry_id"],
            "receipts/database-open-receipts.json",
        ),
        "database_release_manifest": (
            database_manifest["manifest_id"],
            "release/database-release-manifest.json",
        ),
    }
    for binding_name, (contract_id, path) in binding_map.items():
        binding = release_bindings[binding_name]
        if (
            binding["contract_id"] != contract_id
            or binding["version"] != "1.0.0"
            or binding["path"] != path
            or binding["digest"] != sha256_digest(path)
        ):
            raise ValueError(f"release role database binding differs for {binding_name}")
    if (
        status_document["database_finding_ledger"] != ledger["ledger_id"]
        or status_document["data_contract"] != data_contract["contract_id"]
        or status_document["database_migration_contract"]
        != migration_contract["migration_contract_id"]
        or status_document["database_release_manifest"]
        != database_manifest["manifest_id"]
        or status_document["database_open_receipts"] != len(database_receipt_ids)
    ):
        raise ValueError("STATUS database bindings differ")
    return {
        "database_findings": len(finding_ids),
        "database_constellation_findings": len(aggregate_record_ids),
        "database_constellation_sources": len(observed_source_ids),
        "database_plans": len(plan_ids),
        "database_flyway_transition_estimates": 1,
        "database_ownership_boundaries": len(ownership_ids),
        "database_stages": len(stage_ids),
        "data_primitive_policies": len(policy_ids),
        "database_reconciliation_dimensions": len(dimension_ids),
        "database_release_gates": len(gate_ids),
        "database_open_receipts": len(database_receipt_ids),
    }
def workflow_trigger_keys(workflow: str) -> set[str]:
    """Read exact top-level workflow triggers without adding a YAML dependency."""
    lines = workflow.splitlines()
    start = lines.index("on:") + 1
    triggers: set[str] = set()
    for line in lines[start:]:
        if line and not line.startswith(" "):
            break
        match = re.fullmatch(r"""  ["']?([A-Za-z0-9_-]+)["']?:.*""", line)
        if match:
            triggers.add(match.group(1))
    return triggers


def runner_job_blocks(workflow: str) -> dict[str, str]:
    """Return every workflow job that allocates a hosted runner."""
    lines = workflow.splitlines()
    start = lines.index("jobs:") + 1
    job_starts = [
        (index, match.group(1))
        for index in range(start, len(lines))
        if (match := re.fullmatch(r"  ([A-Za-z0-9_-]+):", lines[index]))
    ]
    blocks: dict[str, str] = {}
    for position, (index, name) in enumerate(job_starts):
        end = (
            job_starts[position + 1][0]
            if position + 1 < len(job_starts)
            else len(lines)
        )
        block = "\n".join(lines[index:end])
        if re.search(r"(?m)^    runs-on:", block):
            blocks[name] = block
    return blocks


def validate() -> dict[str, int]:
    capabilities = load_json("specifications/capabilities.json")["requirements"]
    invariants = load_json("specifications/invariants.json")["rules"]
    scenarios = load_json("examples/scenarios.json")["scenarios"]
    database_ledger = load_json("database/primitive-findings.json")
    database_constellation_index = load_json(
        "database/constellation-finding-index.json"
    )
    database_plan_set = load_json("plans/database-modernization-plans.json")
    data_contract = load_json("specifications/data-primitives.json")
    database_migration_contract = load_json(
        "specifications/database-migration.json"
    )
    database_receipts = load_json("receipts/database-open-receipts.json")
    database_manifest = load_json("release/database-release-manifest.json")
    forecast_document = load_json("forecasts/forecast-2026-Q3-r2.json")
    forecasts = forecast_document["predictions"]
    roles = load_json("acceptance/roles.json")["roles"]
    proof_classes = load_json("acceptance/proof-classes.json")["proof_classes"]
    receipts = load_json("receipts/open-receipts.json")["receipts"]
    bounded_caller = load_json("specifications/bounded-caller.json")
    operations = bounded_caller["operations"]
    probes_document = load_json("probes/catalog.json")
    probes = probes_document["probes"]
    coordination_horizon = load_json("coordination-horizon.json")
    future_reality = load_json(
        "simulations/future-reality-closure-v0.3.json"
    )
    governance_closure = load_json(
        "simulations/simulated-receipt-closure.v2.json"
    )
    canonical_bundle = load_json(
        "simulations/future-reality-2028-06-30-v1.json"
    )
    receipt_vocabulary = load_json(
        "specifications/receipt-vocabulary-map.v1.json"
    )
    simulated_closures = future_reality["closures"]
    constellation = load_json("constellation.json")
    constellation_lock = load_json("constellation.lock.json")
    machine_node = load_json("machine-node.json")
    first_receipt = load_json("first-receipt.json")
    release_role = load_json("release/repository-role.json")
    contract_package_coordinate = load_json(
        "release/contract-package-coordinate.json"
    )
    promotion_receipt = load_json("receipts/promotion-receipt.json")
    release_observation = load_json(
        "receipts/promotion-observation-spec-v0.3.1.json"
    )
    release_observation_schema = load_json(OBSERVATION_SCHEMA_PATH.as_posix())
    status_document = load_status()
    pages_context = validate_source_contract(ROOT)

    validate_core_shapes(
        constellation=constellation,
        constellation_lock=constellation_lock,
        release_role=release_role,
        machine_node=machine_node,
        first_receipt=first_receipt,
        coordination_horizon=coordination_horizon,
        promotion_receipt=promotion_receipt,
        status_document=status_document,
    )
    validate_contract_package_coordinate(contract_package_coordinate)
    receipt_digest = candidate_receipt_digest(ROOT, release_observation)
    signers_digest = sha256_digest("release/trusted-release-signers")
    validate_observation_schema(
        release_observation_schema,
        candidate_receipt_digest=receipt_digest,
        trusted_signers_digest=signers_digest,
    )
    validate_observation_document(
        release_observation,
        candidate_receipt_digest=receipt_digest,
        trusted_signers_digest=signers_digest,
    )

    requirement_ids = unique_ids(capabilities, "requirement")
    rule_ids = unique_ids(invariants, "rule")
    scenario_ids = unique_ids(scenarios, "scenario")
    role_ids = unique_ids(roles, "role")
    proof_class_ids = unique_ids(proof_classes, "proof class")
    receipt_ids = unique_ids(receipts, "receipt")
    database_receipt_ids = unique_ids(
        database_receipts["receipts"], "database receipt"
    )
    operation_ids = unique_ids(operations, "operation")
    probe_ids = unique_ids(probes, "probe")
    closure_ids = unique_ids(simulated_closures, "simulated closure")
    closure_proof_class_by_id = {
        item["id"]: item["proof_class"] for item in simulated_closures
    }

    database_summary = validate_database_program(
        ledger=database_ledger,
        constellation_index=database_constellation_index,
        plan_set=database_plan_set,
        data_contract=data_contract,
        migration_contract=database_migration_contract,
        database_receipts=database_receipts,
        database_manifest=database_manifest,
        release_role=release_role,
        status_document=status_document,
        requirement_ids=requirement_ids,
        rule_ids=rule_ids,
        scenario_ids=scenario_ids,
        role_ids=role_ids,
    )

    for requirement in capabilities:
        unknown_rules = set(requirement["rule_ids"]) - rule_ids
        if unknown_rules:
            raise ValueError(f"{requirement['id']} references unknown rules: {sorted(unknown_rules)}")

    for scenario in scenarios:
        if scenario["requirement_id"] not in requirement_ids:
            raise ValueError(f"{scenario['id']} references an unknown requirement")
        if scenario["rule_id"] not in rule_ids:
            raise ValueError(f"{scenario['id']} references an unknown rule")
        unknown_roles = set(scenario["acceptance_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{scenario['id']} references unknown roles: {sorted(unknown_roles)}")
        operation_id = scenario.get("operation_id")
        if operation_id is not None:
            if operation_id not in operation_ids:
                raise ValueError(
                    f"{scenario['id']} references unknown operation {operation_id}"
                )
            operation = next(
                item for item in operations if item["id"] == operation_id
            )
            if scenario.get("effect_class") != operation["effect_class"]:
                raise ValueError(
                    f"{scenario['id']} effect class differs from {operation_id}"
                )
    scenario_operation_ids = {
        item["operation_id"]
        for item in scenarios
        if "operation_id" in item
    }
    if scenario_operation_ids != operation_ids:
        raise ValueError(
            "specification-by-example scenarios must cover every bounded operation"
        )

    for forecast in forecasts:
        unknown_scenarios = set(forecast["scenario_ids"]) - scenario_ids
        if unknown_scenarios:
            raise ValueError(f"{forecast['id']} references unknown scenarios: {sorted(unknown_scenarios)}")
        probability = forecast["probability"]
        lower, upper = forecast["range"]
        if not (0 <= lower <= probability <= upper <= 1):
            raise ValueError(
                f"{forecast['id']} probability or range falls outside ordered "
                "[0, 1] bounds"
            )
        for field in (
            "probability_of",
            "horizon",
            "estimation_basis",
            "recalibration_trigger",
        ):
            value = (
                forecast_document[field]
                if field == "estimation_basis"
                else forecast[field]
            )
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{forecast['id']} requires a substantive {field}"
                )

    for proof_class in proof_classes:
        unknown_roles = set(proof_class["required_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{proof_class['id']} references unknown roles: {sorted(unknown_roles)}")
        if proof_class["simulated_closure_id"] not in closure_ids:
            raise ValueError(
                f"{proof_class['id']} references an unknown simulated closure"
            )

    for receipt in receipts:
        if receipt["proof_class"] not in proof_class_ids:
            raise ValueError(f"{receipt['id']} references an unknown proof class")
        unknown_roles = set(receipt["accountable_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{receipt['id']} references unknown roles: {sorted(unknown_roles)}")
        if receipt.get("status") != "open":
            raise ValueError(
                f"{receipt['id']} preserves open status for future observed closure"
            )
        simulation = receipt.get("simulation", {})
        observed = receipt.get("future_observed_closure", {})
        if (
            simulation.get("evidence_mode") != "simulated"
            or simulation.get("status") != "closed_in_future_reality"
            or simulation.get("closure_id") not in closure_ids
        ):
            raise ValueError(
                f"{receipt['id']} lacks a valid simulated future-reality closure"
            )
        if (
            closure_proof_class_by_id[simulation["closure_id"]]
            != receipt["proof_class"]
        ):
            raise ValueError(
                f"{receipt['id']} points to a closure for another proof class"
            )
        if (
            observed.get("evidence_mode") != "observed"
            or observed.get("status") != "open"
        ):
            raise ValueError(
                f"{receipt['id']} lacks a separate open observed successor"
            )

    effect_classes = {item["id"] for item in bounded_caller["effect_classes"]}
    expected_effect_classes = {
        "read",
        "narrow_idempotent_write",
        "approval_gated_broad_write",
    }
    if effect_classes != expected_effect_classes:
        raise ValueError(
            "bounded caller effect classes differ from the three-class contract"
        )
    operation_effect_classes = {item["effect_class"] for item in operations}
    if operation_effect_classes != expected_effect_classes:
        raise ValueError(
            "bounded caller operations do not exercise every effect class"
        )
    for operation in operations:
        if operation["input_schema"].get("additional_properties") is not False:
            raise ValueError(
                f"{operation['id']} input contract must reject undeclared fields"
            )
        if not operation["input_schema"].get("required"):
            raise ValueError(f"{operation['id']} requires explicit input fields")

    expected_veracity = set(probes_document["veracity_vocabulary"])
    required_veracity = {
        "verified",
        "source_supported",
        "source_specific",
        "draft_probe",
        "local_measurement_needed",
        "correction_needed",
        "hold_for_resilience_pass",
    }
    if expected_veracity != required_veracity:
        raise ValueError("Practitioner Probe veracity vocabulary is incomplete")
    for probe in probes:
        level_numbers = [item["level"] for item in probe["levels"]]
        if level_numbers != [1, 2, 3, 4, 5]:
            raise ValueError(
                f"{probe['id']} must contain ordered Levels 1 through 5"
            )
        if probe["veracity"]["status"] not in expected_veracity:
            raise ValueError(f"{probe['id']} uses an unknown veracity status")
        links = probe["evidence_links"]
        unknown_requirements = set(links["requirement_ids"]) - requirement_ids
        unknown_rules = set(links["rule_ids"]) - rule_ids
        unknown_scenarios = set(links["scenario_ids"]) - scenario_ids
        unknown_receipts = set(links["receipt_ids"]) - receipt_ids
        if any(
            (
                unknown_requirements,
                unknown_rules,
                unknown_scenarios,
                unknown_receipts,
            )
        ):
            raise ValueError(
                f"{probe['id']} has unknown evidence links: "
                f"requirements={sorted(unknown_requirements)}, "
                f"rules={sorted(unknown_rules)}, "
                f"scenarios={sorted(unknown_scenarios)}, "
                f"receipts={sorted(unknown_receipts)}"
            )

    canonical_successor = future_reality.get("canonical_execution_successor", {})
    canonical_future = governance_closure.get("future_reality", {})
    aggregate_artifacts = governance_closure.get("aggregate_artifacts", [])
    if (
        canonical_bundle.get("bundle_version") != CANONICAL_BUNDLE_VERSION
        or canonical_bundle.get("source_result_digest")
        != CANONICAL_RESULT_DIGEST
        or canonical_bundle.get("governance_closure") != governance_closure
        or canonical_bundle.get("governance_closure_digest")
        != CANONICAL_CLOSURE_DIGEST
        or canonical_json_digest(governance_closure)
        != CANONICAL_CLOSURE_DIGEST
        or len(aggregate_artifacts) != 1
        or aggregate_artifacts[0].get("digest")
        != CANONICAL_AGGREGATE_ARTIFACT_DIGEST
        or sha256_digest("simulations/future-reality-2028-06-30-v1.json")
        != CANONICAL_BUNDLE_FILE_DIGEST
    ):
        raise ValueError(
            "canonical bundle, closure, aggregate artifact, or byte identity differs"
        )
    if (
        future_reality.get("evidence_mode") != "simulated"
        or future_reality.get("authority") != "advisory_design_only"
        or future_reality.get("artifact_role") != "program_design_simulation"
        or future_reality.get("design_status") != "advisory_design"
        or future_reality.get("simulation_id")
        != "DESIGN-FUTURE-REALITY-CLOSURE-001"
        or future_reality.get("design_future_reality_id")
        == canonical_future.get("future_reality_id")
    ):
        raise ValueError(
            "future-reality design must remain simulated, advisory, and "
            "distinct from the canonical executed simulation"
        )
    if (
        canonical_successor.get("closure_id")
        != governance_closure.get("closure_id")
        or canonical_successor.get("future_reality_id")
        != canonical_future.get("future_reality_id")
        or canonical_successor.get("digest") != CANONICAL_CLOSURE_DIGEST
        or canonical_successor.get("authority")
        != "definitive_within_selected_future_reality"
        or canonical_successor.get("production_authorization_effect") != "none"
    ):
        raise ValueError(
            "advisory design must identify the exact canonical executed successor"
        )
    closure_by_id = {item["id"]: item for item in simulated_closures}
    receipt_ids_by_class: dict[str, set[str]] = {
        proof_class_id: {
            item["id"]
            for item in receipts
            if item["proof_class"] == proof_class_id
        }
        for proof_class_id in proof_class_ids
    }
    for closure in simulated_closures:
        if closure["proof_class"] not in proof_class_ids:
            raise ValueError(
                f"{closure['id']} references an unknown proof class"
            )
        if closure.get("status") != "closed_in_simulation":
            raise ValueError(
                f"{closure['id']} must declare closed_in_simulation"
            )
        if not closure.get("probability_of"):
            raise ValueError(f"{closure['id']} must name its probability event")
        if not 0 <= closure.get("probability", -1) <= 1:
            raise ValueError(f"{closure['id']} probability falls outside [0, 1]")
        if set(closure["covered_receipt_ids"]) != receipt_ids_by_class[
            closure["proof_class"]
        ]:
            raise ValueError(
                f"{closure['id']} receipt coverage differs from its proof class"
            )
        observed = closure.get("future_observed_closure", {})
        if (
            observed.get("evidence_mode") != "observed"
            or observed.get("status") != "open"
        ):
            raise ValueError(
                f"{closure['id']} must preserve an open observed successor"
            )
        for decision in closure.get("synthetic_decisions", []):
            if decision["role"] not in role_ids:
                raise ValueError(
                    f"{closure['id']} references unknown synthetic decision role"
                )
        proof_class = next(
            item
            for item in proof_classes
            if item["id"] == closure["proof_class"]
        )
        decision_roles = {
            item["role"] for item in closure.get("synthetic_decisions", [])
        }
        missing_decision_roles = set(proof_class["required_roles"]) - decision_roles
        if missing_decision_roles:
            raise ValueError(
                f"{closure['id']} lacks simulated decisions for required roles: "
                f"{sorted(missing_decision_roles)}"
            )
    for proof_class in proof_classes:
        closure = closure_by_id[proof_class["simulated_closure_id"]]
        if closure["proof_class"] != proof_class["id"]:
            raise ValueError(
                f"{proof_class['id']} points to a closure for another class"
            )

    if (
        receipt_vocabulary.get("contract_id")
        != "RECEIPT-VOCABULARY-MAP-001"
        or receipt_vocabulary.get("version") != RECEIPT_VOCABULARY_RELEASE
    ):
        raise ValueError("receipt vocabulary contract identity differs")
    family_mappings = receipt_vocabulary["family_mappings"]
    expected_individual_families = {
        "configured_vendor",
        "migration_restore",
        "security_observability",
        "scientific_acceptance_support",
        "quality_acceptance_support",
        "regulatory_acceptance_support",
        "engineering_verification",
    }
    if {
        item["individual_receipt_family"] for item in family_mappings
    } != expected_individual_families:
        raise ValueError("receipt vocabulary omits an individual receipt family")
    governance_family_to_proof_class = {
        item["grouped_canonical_family"]: item["program_proof_class"]
        for item in family_mappings
        if item["grouped_canonical_family"] != "explicit_family_required"
    }
    if set(governance_family_to_proof_class.values()) != proof_class_ids:
        raise ValueError(
            "receipt vocabulary differs from the program proof-class registry"
        )
    engineering_mapping = next(
        item
        for item in family_mappings
        if item["individual_receipt_family"] == "engineering_verification"
    )
    if set(engineering_mapping["allowed_grouped_canonical_families"]) != set(
        governance_family_to_proof_class
    ):
        raise ValueError(
            "cross-cutting engineering verification must name every eligible "
            "canonical family and select none implicitly"
        )
    status_mappings = {
        (
            item["source_scope"],
            item["source_status"],
            item["target_scope"],
            item["target_status"],
        )
        for item in receipt_vocabulary["status_mappings"]
    }
    if status_mappings != {
        (
            "program individual receipt simulation link",
            "closed_in_future_reality",
            "canonical selected-future closure",
            "closed_in_simulation",
        ),
        (
            "future environment-observed individual receipt",
            "open",
            "canonical environment-observed aggregate state",
            "separate_unasserted_state",
        ),
    }:
        raise ValueError("receipt status vocabulary differs from the two-state map")
    projected_families = {
        item["family"] for item in governance_closure["receipt_closures"]
    }
    if projected_families != set(governance_family_to_proof_class):
        raise ValueError(
            "governance closure projection must contain exactly four families"
        )
    if {
        governance_family_to_proof_class[item]
        for item in projected_families
    } != proof_class_ids:
        raise ValueError(
            "governance closure projection differs from the proof-class registry"
        )
    if (
        governance_closure.get("evidence_mode") != "simulated"
        or governance_closure.get("closure_status")
        != "closed_in_simulation"
        or governance_closure.get("environment_observed_closure")
        != "separate_unasserted_state"
        or governance_closure.get("production_authorization_effect") != "none"
    ):
        raise ValueError(
            "governance closure projection collapses evidence or authority state"
        )
    if (
        governance_closure.get("closure_id")
        != "CLOSURE-SIM-SUBSTANTIVE-2028-V1"
        or canonical_future.get("future_reality_id")
        != "FUTURE-REALITY-LIMS-2028-001"
        or canonical_json_digest(governance_closure)
        != CANONICAL_CLOSURE_DIGEST
    ):
        raise ValueError(
            "program canonical closure differs from the released simulation closure"
        )
    projected_scenario_ids = {
        scenario_id
        for closure in governance_closure["receipt_closures"]
        for scenario_id in closure["scenario_ids"]
    }
    if (
        len(projected_scenario_ids) != 12
        or any(
            not scenario_id.startswith("SCENARIO-")
            for scenario_id in projected_scenario_ids
        )
    ):
        raise ValueError(
            "canonical closure must preserve its twelve executable simulation "
            "scenario identifiers; program design scenarios remain a distinct "
            "namespace"
        )
    if (
        release_role.get("repository_role") != "program_specification"
        or release_role.get("repository_release") != PROGRAM_RELEASE
        or release_role.get("external_release") != PROGRAM_TAG
        or release_role["canonical_closure"]["digest"]
        != CANONICAL_CLOSURE_DIGEST
        or release_role["canonical_closure"]["reference_result_digest"]
        != CANONICAL_RESULT_DIGEST
        or release_role["canonical_closure"]["aggregate_artifact_digest"]
        != CANONICAL_AGGREGATE_ARTIFACT_DIGEST
        or release_role["canonical_closure"]["bundle_path"]
        != "simulations/future-reality-2028-06-30-v1.json"
        or release_role["canonical_closure"]["bundle_file_digest"]
        != CANONICAL_BUNDLE_FILE_DIGEST
        or release_role["canonical_closure"]["authority"]
        != "definitive_within_selected_future_reality"
        or release_role["canonical_closure"]["production_authorization_effect"]
        != "none"
        or release_role["advisory_design"]["future_reality_id"]
        != future_reality["design_future_reality_id"]
        or release_role["advisory_design"]["digest"]
        != sha256_digest("simulations/future-reality-closure-v0.3.json")
        or release_role["advisory_design"]["authority"]
        != "advisory_design_only"
        or release_role["contract_bindings"]["receipt_vocabulary_map"]["digest"]
        != sha256_digest("specifications/receipt-vocabulary-map.v1.json")
    ):
        raise ValueError("repository release role collapses design and execution")

    horizon_item_ids = {
        item["item_id"] for item in coordination_horizon["work_items"]
    }
    expected_horizon_item_ids = {
        "HORIZON-CONTRACTS",
        "HORIZON-DATABASE-CONTRACT",
        "HORIZON-DATABASE-IMPLEMENTATION",
        "HORIZON-DATABASE-REHEARSAL",
        "HORIZON-DATABASE-RELEASE",
        "HORIZON-VERTICAL-SLICE",
        "HORIZON-EXTENSIONS",
    }
    if horizon_item_ids != expected_horizon_item_ids:
        raise ValueError(
            "Coordination Horizon differs from the seven-item program contract"
        )
    if not set(coordination_horizon["current_item_ids"]) <= horizon_item_ids:
        raise ValueError(
            "Coordination Horizon current items reference unknown work"
        )
    if (
        coordination_horizon["metadata"]["schema_version"]
        != GOVERNANCE_RELEASE
    ):
        raise ValueError("Coordination Horizon schema binding differs")

    repository_roles = {entry["role"] for entry in constellation["repositories"]}
    expected_roles = {"program", "actual", "simulation", "comparison", "governance"}
    if repository_roles != expected_roles:
        raise ValueError(
            "constellation repository roles differ from the five-part contract: "
            f"expected={sorted(expected_roles)}, actual={sorted(repository_roles)}"
        )

    if (
        machine_node["schema_release"] != GOVERNANCE_RELEASE
        or machine_node["control_plane_profile"] != CONTROL_PLANE_PROFILE
        or machine_node["repository_role"] != "program_specification"
    ):
        raise ValueError("Machine Node governance schema binding differs")
    program_seed = next(
        item
        for item in constellation_lock["seed_lineage"]
        if item["repository_role"] == "program_specification"
    )
    expected_seed = {
        "release": "spec-v0.3.0",
        "commit": "895b7a02ebddc9f7c2b63a2d03432775a120c119",
        "digest": "sha256:a73935fcd6bd2cd5e8aeda48739f74f90c2d5b0faec50d8341d7315378ef5ff2",
        "digest_scope": "seed Machine Node",
    }
    if (
        release_role["seed_lineage"] != expected_seed
        or machine_node["seed_lineage"]
        != {key: expected_seed[key] for key in {"release", "commit", "digest"}}
        or {
            key: program_seed[key]
            for key in {"release", "commit", "digest", "digest_scope"}
        }
        != expected_seed
        or status_document["released_baseline"] != expected_seed["release"]
        or status_document["released_commit"] != expected_seed["commit"]
    ):
        raise ValueError("program 0.3.0 seed lineage differs across control surfaces")
    if (
        machine_node["coordination_horizon_id"]
        != coordination_horizon["horizon_id"]
        or machine_node["authority"]["mode"] != "orientation_only"
    ):
        raise ValueError("Machine Node orientation posture differs")
    if (
        machine_node["first_receipt_contract_id"]
        != first_receipt["first_receipt_id"]
        or first_receipt["machine_node_id"] != machine_node["machine_node_id"]
        or first_receipt["coordination_horizon_id"]
        != coordination_horizon["horizon_id"]
    ):
        raise ValueError("First receipt orientation coordinates differ")
    if (
        first_receipt["authority_posture"]["mode"] != "orientation_only"
    ):
        raise ValueError("First receipt authority or open-receipt posture differs")

    promotion_coordinates = release_role.get("promotion_coordinates", {})
    expected_promotion_roles = {
        "site_reading_governance",
        "program_specification",
        "enterprise_implementation",
        "simulated_final_state",
        "comparative_evidence",
    }
    if set(promotion_coordinates.get("required_roles", [])) != expected_promotion_roles:
        raise ValueError(
            "release manifest promotion coordinates differ from the "
            "candidate-promotion receipt"
        )

    validate_release_lifecycle(
        release_role=release_role,
        machine_node=machine_node,
        first_receipt=first_receipt,
        coordination_horizon=coordination_horizon,
        promotion_receipt=promotion_receipt,
        release_observation=release_observation,
        constellation_lock=constellation_lock,
        status_document=status_document,
        substantive_receipt_ids=receipt_ids | database_receipt_ids,
    )

    contract_paths = {
        "CALLER-CONTRACT-001": (
            "specifications/bounded-caller.json",
            "file",
        ),
        "LIMS-ELN-PRACTITIONER-PROBES-001": (
            "probes/catalog.json",
            "file",
        ),
        "LIMS-ELN-PROOF-CLASSES-001": (
            "acceptance/proof-classes.json",
            "file",
        ),
        "DESIGN-FUTURE-REALITY-CLOSURE-001": (
            "simulations/future-reality-closure-v0.3.json",
            "file",
        ),
        "SIMULATED-SUBSTANTIVE-CLOSURE-2028-V1": (
            "simulations/simulated-receipt-closure.v2.json",
            "canonical_json",
        ),
        "RECEIPT-VOCABULARY-MAP-001": (
            "specifications/receipt-vocabulary-map.v1.json",
            "file",
        ),
        "LIMS-ELN-DATA-PRIMITIVE-LEDGER-001": (
            "database/primitive-findings.json",
            "file",
        ),
        "DATABASE-CONSTELLATION-FINDING-INDEX-001": (
            "database/constellation-finding-index.json",
            "file",
        ),
        "DATABASE-MODERNIZATION-PLAN-SET-001": (
            "plans/database-modernization-plans.json",
            "file",
        ),
        "DATA-CONTRACT-001": (
            "specifications/data-primitives.json",
            "file",
        ),
        "DATABASE-MIGRATION-CONTRACT-001": (
            "specifications/database-migration.json",
            "file",
        ),
        "DATABASE-OPEN-RECEIPTS-001": (
            "receipts/database-open-receipts.json",
            "file",
        ),
        "DATABASE-RELEASE-MANIFEST-001": (
            "release/database-release-manifest.json",
            "file",
        ),
    }
    machine_contracts = {
        item["contract_id"]: item for item in machine_node["contracts"]
    }
    first_receipt_contracts = {
        item["contract_id"]: item for item in first_receipt["contract_state"]
    }
    if (
        set(machine_contracts) != set(contract_paths)
        or set(first_receipt_contracts) != set(contract_paths)
    ):
        raise ValueError("Machine Node or first receipt contract set differs")
    for contract_id, (path, digest_mode) in contract_paths.items():
        expected_digest = (
            canonical_json_digest(load_json(path))
            if digest_mode == "canonical_json"
            else sha256_digest(path)
        )
        if (
            machine_contracts[contract_id]["digest"] != expected_digest
            or first_receipt_contracts[contract_id]["digest"] != expected_digest
        ):
            raise ValueError(
                f"{contract_id} orientation digest differs from {path}"
            )

    for role, pattern in RELEASE_PATTERNS.items():
        release = constellation_lock[role]["release"]
        if pattern.fullmatch(release) is None:
            raise ValueError(
                f"{role} release {release!r} falls outside its protected tag family"
            )

    versioned_documents = {
        "specifications/capabilities.json": load_json(
            "specifications/capabilities.json"
        ),
        "specifications/invariants.json": load_json(
            "specifications/invariants.json"
        ),
        "specifications/bounded-caller.json": bounded_caller,
        "examples/scenarios.json": load_json("examples/scenarios.json"),
        "receipts/open-receipts.json": load_json("receipts/open-receipts.json"),
        "probes/catalog.json": probes_document,
        "simulations/future-reality-closure-v0.3.json": future_reality,
        "forecasts/forecast-2026-Q3-r2.json": forecast_document,
        "acceptance/roles.json": load_json("acceptance/roles.json"),
        "acceptance/proof-classes.json": load_json(
            "acceptance/proof-classes.json"
        ),
        "constellation.json": constellation,
    }
    for path, document in versioned_documents.items():
        if document.get("version") != PROGRAM_RELEASE:
            raise ValueError(
                f"{path} version differs from planned program release "
                f"{PROGRAM_RELEASE}"
            )
    if constellation_lock.get("constellation_version") != PROGRAM_RELEASE:
        raise ValueError(
            "constellation lock version differs from the planned program release"
        )
    if constellation_lock["specification"]["release"] != PROGRAM_TAG:
        raise ValueError(
            f"specification lock release differs from planned {PROGRAM_TAG}"
        )
    if constellation_lock["governance"]["release"] != GOVERNANCE_TAG:
        raise ValueError(
            f"governance lock release differs from {GOVERNANCE_TAG}"
        )
    if (
        constellation_lock["governance"].get("schema_version")
        != GOVERNANCE_RELEASE
        or constellation_lock["governance"].get("profile")
        != f"Control Plane Profile {CONTROL_PLANE_PROFILE}"
    ):
        raise ValueError(
            "governance lock binding differs from the selected control-plane profile"
        )
    if constellation_lock["governance"] != {
        "release": GOVERNANCE_TAG,
        "profile": f"Control Plane Profile {CONTROL_PLANE_PROFILE}",
        "schema_version": GOVERNANCE_RELEASE,
        "tag_object": GOVERNANCE_TAG_OBJECT,
        "commit": GOVERNANCE_COMMIT,
        "digest": GOVERNANCE_TREE_DIGEST,
        "archive_format": GOVERNANCE_ARCHIVE_FORMAT,
        "archive_digest": GOVERNANCE_ARCHIVE_DIGEST,
        "coordinate_status": "pinned",
    }:
        raise ValueError(
            "governance lock differs from the accepted tag, source, tree, or archive"
        )
    for role, expected_subject in EXTERNAL_RELEASE_SUBJECTS.items():
        observed_subject = {
            key: constellation_lock[role].get(key)
            for key in expected_subject
        }
        if observed_subject != expected_subject:
            raise ValueError(
                f"{role} release subject differs from the accepted signed coordinate"
            )
    implementation_coordinate = constellation_lock["implementation"]
    if (
        implementation_coordinate["repository_release"]
        != IMPLEMENTATION_REPOSITORY_RELEASE
        or implementation_coordinate["selected_future_closure_digest"]
        != CANONICAL_CLOSURE_DIGEST
        or implementation_coordinate["contract_bindings"]
        != IMPLEMENTATION_CONTRACT_BINDINGS
        or implementation_coordinate["source_artifact_bindings"]
        != IMPLEMENTATION_SOURCE_ARTIFACT_BINDINGS
    ):
        raise ValueError(
            "implementation semantic bindings differ from the accepted signed source"
        )
    if (
        constellation_lock["comparison"]["receipt_schema"]
        != COMPARISON_RECEIPT_SCHEMA
    ):
        raise ValueError(
            "comparison receipt schema differs from its signed release binding"
        )
    if (
        constellation_lock["comparison"]["historical_governance_schema"]
        != COMPARISON_HISTORICAL_GOVERNANCE_SCHEMA
    ):
        raise ValueError(
            "comparison historical Governance schema coordinate differs"
        )
    if (
        constellation_lock["simulation"]["canonical_closure_digest"]
        != CANONICAL_CLOSURE_DIGEST
        or constellation_lock["simulation"]["reference_result_digest"]
        != CANONICAL_RESULT_DIGEST
        or constellation_lock["simulation"]["aggregate_artifact_digest"]
        != CANONICAL_AGGREGATE_ARTIFACT_DIGEST
        or constellation_lock["simulation"]["canonical_bundle_file_digest"]
        != CANONICAL_BUNDLE_FILE_DIGEST
        or constellation_lock["comparison"]["canonical_closure_digest"]
        != CANONICAL_CLOSURE_DIGEST
        or constellation_lock["comparison"]["aggregate_artifact_digest"]
        != CANONICAL_AGGREGATE_ARTIFACT_DIGEST
    ):
        raise ValueError("constellation canonical artifact bindings differ")

    for role in RELEASE_PATTERNS:
        coordinate = constellation_lock[role]
        status = coordinate.get("coordinate_status")
        if status == "pending_release_commit":
            if (
                coordinate.get("commit") != PENDING_COMMIT
                or coordinate.get("digest") != PENDING_TREE_DIGEST
            ):
                raise ValueError(
                    f"{role} pending coordinate differs from the explicit "
                    "zero-placeholder contract"
                )
        elif status == "pinned":
            if (
                not isinstance(coordinate.get("commit"), str)
                or MATERIAL_COMMIT_PATTERN.fullmatch(coordinate["commit"]) is None
                or not isinstance(coordinate.get("digest"), str)
                or MATERIAL_TREE_DIGEST_PATTERN.fullmatch(coordinate["digest"])
                is None
            ):
                raise ValueError(
                    f"{role} pinned coordinate requires observed commit and tree"
                )
        else:
            raise ValueError(
                f"{role} coordinate status must be pending_release_commit or pinned"
            )

    if (
        release_role["manifest_version"] != GOVERNANCE_RELEASE
        or release_role["contract_bindings"]["governance_schema"]
        != GOVERNANCE_RELEASE
        or release_role["contract_bindings"]["control_plane_profile"]
        != CONTROL_PLANE_PROFILE
        or release_role["contract_bindings"]["language_policy_release"]
        != LANGUAGE_POLICY_RELEASE
        or release_role["contract_bindings"]["language_policy_manifest"]["path"]
        != "language-policy/manifest.json"
        or release_role["contract_bindings"]["language_policy_manifest"]["digest"]
        != sha256_digest("language-policy/manifest.json")
        or release_role["contract_bindings"]["language_policy_manifest"][
            "core_digest"
        ]
        != sha256_digest("scripts/language_policy_core.py")
        or release_role["contract_bindings"]["language_policy_manifest"][
            "corpus_digest"
        ]
        != sha256_digest("language-policy/corpus-v1.json")
        or promotion_receipt["metadata"]["schema_version"] != "1.0.0"
        or status_document["version"] != PROGRAM_RELEASE
        or status_document["planned_release"] != PROGRAM_TAG
        or status_document["governance_contract"] != GOVERNANCE_TAG
        or status_document["governance_schema"] != GOVERNANCE_RELEASE
        or status_document["receipt_schema"] != GOVERNANCE_RELEASE
        or status_document["governance_profile"]
        != f"Control Plane Profile {CONTROL_PLANE_PROFILE}"
    ):
        raise ValueError("release, promotion, or status version binding differs")

    required_paths = [
        ".agents/skills/constellation-coherence-reconciliation/SKILL.md",
        ".agents/skills/source-authority-mapping/SKILL.md",
        "AGENTS.md",
        "CHANGELOG.md",
        "README.md",
        "BRANCHING.md",
        "GOVERNANCE.md",
        "SECURITY.md",
        "constellation.lock.json",
        "coordination-horizon.json",
        "first-receipt.json",
        "release/repository-role.json",
        "release/trusted-release-signers",
        "release/contract-package-coordinate.json",
        "receipts/promotion-receipt.json",
        "receipts/promotion-observation-spec-v0.3.1.json",
        "schemas/promotion-receipt.schema.json",
        "schemas/program-release-observation.v1.schema.json",
        "specifications/bounded-caller.json",
        "specifications/receipt-vocabulary-map.v1.json",
        "probes/catalog.json",
        "simulations/future-reality-closure-v0.3.json",
        "simulations/future-reality-2028-06-30-v1.json",
        "simulations/simulated-receipt-closure.v2.json",
        ".github/workflows/pull-request.yml",
        ".github/workflows/validate.yml",
        ".github/dependabot.yml",
        ".github/AUTOMATION.md",
        "CODEOWNERS",
        ".github/pull_request_template.md",
        "scripts/automation_contract.py",
        "scripts/check_branch_flow.py",
        "scripts/check_language.py",
        "scripts/language_policy_core.py",
        "docs/LANGUAGE_POLICY.md",
        "language-policy/corpus-v1.json",
        "language-policy/exemptions.json",
        "language-policy/manifest.json",
        "scripts/validate_pinned_sources.py",
        "scripts/summarize_github_api_response.py",
        "scripts/verify_program_release_observation.py",
        "docs/migrations/0.3.0-to-0.3.1.md",
        "docs/DATABASE_MODERNIZATION.md",
        "docs/DATABASE_CONSTELLATION_LEDGER.md",
        "pages/README.md",
        "pages/program-content.json",
        "database/primitive-findings.json",
        "database/constellation-finding-index.json",
        "plans/database-modernization-plans.json",
        "specifications/data-primitives.json",
        "specifications/database-migration.json",
        "receipts/database-open-receipts.json",
        "release/database-release-manifest.json",
        "tests/test_branch_flow.py",
        "tests/test_github_api_diagnostics.py",
        "tests/test_language_policy.py",
        "tests/test_pages_projection.py",
        "scripts/build_pages.py",
        "scripts/pages_projection.py",
        "scripts/validate_projection.py",
        "scripts/verify_pages.py",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    if missing:
        raise ValueError(f"required collaboration surfaces are absent: {missing}")

    active_trigger_paths = [".github/workflows/branch-policy.yml"]
    active_triggers = [path for path in active_trigger_paths if (ROOT / path).exists()]
    if active_triggers:
        raise ValueError(
            "automation catalog contains an undeclared trigger file: "
            f"{active_triggers}"
        )

    workflow_directory = ROOT / ".github" / "workflows"
    workflow_paths = sorted(
        [*workflow_directory.glob("*.yml"), *workflow_directory.glob("*.yaml")]
    )
    if [path.name for path in workflow_paths] != ["pull-request.yml", "validate.yml"]:
        raise ValueError(
            "program proof catalog differs from ['pull-request.yml', 'validate.yml']: "
            f"{[path.name for path in workflow_paths]}"
        )
    workflows = {
        path.name: path.read_text(encoding="utf-8") for path in workflow_paths
    }
    workflow = workflows["validate.yml"]
    required_activation_fragments = (
        "workflow_dispatch:",
        "confirm_run:",
        "release_tag:",
        "vars.ENABLE_GITHUB_ACTIONS == 'true'",
        "inputs.confirm_run",
        "permissions:\n  contents: read",
        "timeout-minutes: 10",
        "Install the contract model boundary",
        "python -m pip install --disable-pip-version-check .",
        "Confirm private sibling read access",
        "GH_TOKEN: ${{ secrets.CONSTELLATION_READ_TOKEN }}",
        "gh api --silent user",
        'gh api --include "repos/$repository"',
        'gh api --include "repos/$repository/contents?ref=$commit"',
        "scripts/summarize_github_api_response.py",
        "Normalized GitHub API Contents response",
        "Private sibling Contents request is forbidden",
        "Private sibling coordinate is unavailable to this credential",
        "python scripts/verify_program_release_observation.py",
    )
    missing_fragments = [
        fragment for fragment in required_activation_fragments if fragment not in workflow
    ]
    if missing_fragments:
        raise ValueError(
            "manual program proof differs from its activation boundary: "
            f"{missing_fragments}"
        )
    sibling_coordinate_fragments = (
        'simulation)\n                repository="driftframestudios/'
        'lims-eln-simulated-final-state"',
        'implementation)\n                repository="driftframestudios/'
        'lims-eln-enterprise-implementation"',
        'comparison)\n                repository="driftframestudios/'
        'lims-eln-comparative-evidence"',
        'governance)\n                repository="driftframestudios/'
        'site-reading-governance"',
        'commit="$(jq -r --arg coordinate "$coordinate" '
        "'.[$coordinate].commit' constellation.lock.json)\"",
    )
    missing_sibling_fragments = [
        fragment
        for fragment in sibling_coordinate_fragments
        if fragment not in workflow
    ]
    if missing_sibling_fragments:
        raise ValueError(
            "private sibling read-access mapping differs from the Program lock: "
            f"{missing_sibling_fragments}"
        )
    release_subject_fragments = (
        "Verify the selected Program release subject",
        "startsWith(github.ref, 'refs/tags/spec-v')",
        "REQUESTED_RELEASE_TAG: ${{ inputs.release_tag }}",
        'selected_tag="$REQUESTED_RELEASE_TAG"',
        '[[ "$GITHUB_REF" == refs/tags/spec-v* ]]',
        'selected_tag="$GITHUB_REF_NAME"',
        "expected_tag=\"$(jq -r '.specification.release' constellation.lock.json)\"",
        'if [ "$selected_tag" != "$expected_tag" ]; then',
        'git cat-file -t "refs/tags/$selected_tag"',
        'if [ "$tag_type" != "tag" ]; then',
        'git rev-parse --verify "refs/tags/$selected_tag^{commit}"',
        'git rev-parse --verify HEAD',
        'if [ "$carrier_commit" != "$GITHUB_SHA" ]; then',
        'git merge-base --is-ancestor "$release_commit" "$carrier_commit"',
        "gpg.ssh.allowedSignersFile=release/trusted-release-signers",
        'verify-tag "$selected_tag"',
        "Verified signed release subject: tag=$selected_tag "
        "release_commit=$release_commit carrier_commit=$carrier_commit",
    )
    missing_release_subject_fragments = [
        fragment
        for fragment in release_subject_fragments
        if fragment not in workflow
    ]
    if missing_release_subject_fragments:
        raise ValueError(
            "Program release-subject proof differs from its signed-tag boundary: "
            f"{missing_release_subject_fragments}"
        )
    unsafe_release_subject_output = (
        'echo "$REQUESTED_RELEASE_TAG"',
        'echo "$GITHUB_REF"',
    )
    present_unsafe_release_subject_output = [
        fragment
        for fragment in unsafe_release_subject_output
        if fragment in workflow
    ]
    if present_unsafe_release_subject_output:
        raise ValueError(
            "Program release-subject proof exposes unvalidated workflow input: "
            f"{present_unsafe_release_subject_output}"
        )
    expected_signer = (
        'release@driftframestudios.org namespaces="git" ssh-ed25519 '
        "AAAAC3NzaC1lZDI1NTE5AAAAIDnUwCLnoD9N4f4P7IPB24xmMm45wEskkWiNScUswkcj\n"
    )
    if (ROOT / "release" / "trusted-release-signers").read_text(
        encoding="utf-8"
    ) != expected_signer:
        raise ValueError("Program trusted release signer differs")
    triggers = workflow_trigger_keys(workflow)
    if triggers != {"workflow_dispatch"}:
        raise ValueError(
            "manual program proof trigger allowlist differs: "
            f"expected ['workflow_dispatch'], available {sorted(triggers)}"
        )
    runner_jobs = runner_job_blocks(workflow)
    if not runner_jobs:
        raise ValueError("manual program proof requires at least one runner job")
    for name, block in runner_jobs.items():
        gate = re.search(r"(?m)^    if:\s*(.+)$", block)
        if gate is None or not all(
            fragment in gate.group(1)
            for fragment in (
                "vars.ENABLE_GITHUB_ACTIONS == 'true'",
                "inputs.confirm_run",
            )
        ):
            raise ValueError(
                f"manual program proof job {name!r} requires the variable and "
                "confirmation gate"
            )
    candidate_job = runner_jobs.get("candidate-coordinates")
    cross_repository_job = runner_jobs.get("cross-repository-contracts")
    candidate_gate = (
        re.search(r"(?m)^    if:\s*(.+)$", candidate_job)
        if candidate_job is not None
        else None
    )
    cross_repository_gate = (
        re.search(r"(?m)^    if:\s*(.+)$", cross_repository_job)
        if cross_repository_job is not None
        else None
    )
    if (
        candidate_gate is None
        or "inputs.release_tag == ''" not in candidate_gate.group(1)
        or cross_repository_gate is None
        or "inputs.release_tag != ''" not in cross_repository_gate.group(1)
    ):
        raise ValueError(
            "manual program proof release-tag input requires complementary "
            "candidate and cross-repository routing"
        )

    pull_request_workflow = workflows["pull-request.yml"]

    action_reference = re.compile(r"^\s*uses:\s*([^#\s]+)", re.MULTILINE)
    immutable_action = re.compile(r"^[^@]+@[a-f0-9]{40}$")
    for path in workflow_paths:
        content = workflows[path.name]
        for reference in action_reference.findall(content):
            if immutable_action.fullmatch(reference) is None:
                raise ValueError(
                    f"workflow action reference requires an immutable SHA: {reference!r}"
                )
        if content.count("persist-credentials: false") < content.count(
            "actions/checkout@"
        ):
            raise ValueError(
                f"workflow checkout credentials require bounded handling: {path.name}"
            )

    manual_dependency_path = ROOT / ".github" / "dependabot.manual.yml"
    if manual_dependency_path.exists():
        raise ValueError(
            "monthly dependency upkeep uses the active dependabot.yml source"
        )
    dependency_config = (ROOT / ".github/dependabot.yml").read_text(
        encoding="utf-8"
    )
    automation_findings = validate_repository_automation(
        pull_request_workflow,
        dependency_config,
        release_role.get(
            "automation_controls",
            MISSING_AUTOMATION_CONTROLS,
        ),
    )
    if automation_findings:
        raise ValueError(
            "bounded pull-request automation differs from its semantic contract: "
            f"{automation_findings}"
        )

    codeowners = (ROOT / "CODEOWNERS").read_text(encoding="utf-8")
    if "/.github/dependabot.yml @driftframestudios" not in codeowners:
        raise ValueError("CODEOWNERS requires the active dependency configuration")
    if "/scripts/automation_contract.py @driftframestudios" not in codeowners:
        raise ValueError("CODEOWNERS requires the automation contract owner")
    if (
        "/scripts/verify_program_release_observation.py @driftframestudios"
        not in codeowners
    ):
        raise ValueError("CODEOWNERS requires the release observation verifier owner")
    pages_owner_paths = (
        "/pages/ @driftframestudios",
        "/scripts/build_pages.py @driftframestudios",
        "/scripts/pages_projection.py @driftframestudios",
        "/scripts/validate_projection.py @driftframestudios",
        "/scripts/verify_pages.py @driftframestudios",
        "/tests/test_pages_projection.py @driftframestudios",
    )
    missing_pages_owners = [
        path for path in pages_owner_paths if path not in codeowners
    ]
    if missing_pages_owners:
        raise ValueError(
            "CODEOWNERS requires every Program Pages source owner: "
            f"{missing_pages_owners}"
        )
    if "dependabot.manual.yml" in codeowners:
        raise ValueError("CODEOWNERS should route the active dependency source")

    automation_note = (ROOT / ".github/AUTOMATION.md").read_text(encoding="utf-8")
    required_automation_fragments = (
        "100–300 GitHub Actions runner\nminutes per month",
        "Pull requests targeting `develop` or `main`",
        "Superseded runs cancel",
        "## Deliberate full proof",
        "`ENABLE_GITHUB_ACTIONS=true`",
        "verify_program_release_observation.py --require-observed",
        "## Recovery",
        "`.github/dependabot.manual.yml` returns dependency scheduling",
    )
    missing_automation_fragments = [
        fragment
        for fragment in required_automation_fragments
        if fragment not in automation_note
    ]
    if missing_automation_fragments:
        raise ValueError(
            "automation orientation differs from the funded proof and recovery route: "
            f"{missing_automation_fragments}"
        )

    return {
        "requirements": len(requirement_ids),
        "rules": len(rule_ids),
        "scenarios": len(scenario_ids),
        "operations": len(operation_ids),
        "probes": len(probe_ids),
        "simulated_closures": len(closure_ids),
        "governance_closure_families": len(projected_families),
        "receipt_vocabulary_mappings": len(family_mappings),
        "roles": len(role_ids),
        "proof_classes": len(proof_class_ids),
        "open_receipts": len(receipts) + len(database_receipt_ids),
        "canonical_open_receipts": len(receipts),
        "promotion_receipts": int(
            promotion_receipt["promotion_receipt_id"] == PROMOTION_RECEIPT_ID
        ),
        "release_observations": int(
            release_observation["release_observation_id"]
            == "OBS-PROGRAM-RELEASE-003"
        ),
        "repositories": len(repository_roles),
        "pages_sources": 1,
        "public_ready_skills": len(pages_context.public_skills),
        "contract_package_coordinates": 1,
        **database_summary,
    }


if __name__ == "__main__":
    summary = validate()
    print(json.dumps({"status": "valid", **summary}, indent=2, sort_keys=True))

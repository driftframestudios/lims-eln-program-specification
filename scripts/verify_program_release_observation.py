#!/usr/bin/env python3
"""Verify the Program's candidate or post-tag release observation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from copy import deepcopy
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBSERVATION_PATH = Path("receipts/promotion-observation-spec-v0.3.1.json")
OBSERVATION_SCHEMA_PATH = Path("schemas/program-release-observation.v1.schema.json")
PROMOTION_RECEIPT_PATH = Path("receipts/promotion-receipt.json")
TRUSTED_SIGNERS_PATH = Path("release/trusted-release-signers")
PROGRAM_TAG = "spec-v0.3.1"
OBSERVATION_KEYS = {
    "$schema",
    "schema_version",
    "release_observation_id",
    "promotion_receipt_id",
    "repository",
    "target_release",
    "observation_state",
    "evidence_mode",
    "assurance_stage",
    "candidate_receipt",
    "candidate_source",
    "release_subject",
    "signature_observation",
    "workflow_observation",
    "review_observation",
    "accountable_role",
    "metadata",
}
SHA1_OID = re.compile(r"^(?!0{40}$)[a-f0-9]{40}$")
SHA256_DIGEST = re.compile(r"^sha256:(?!0{64}$)[a-f0-9]{64}$")
POSITIVE_DECIMAL = re.compile(r"^[1-9][0-9]*$")
RELEASE_REVIEW_ROUTE = {
    "merge_admission": "configured_ordinary_bypass",
    "independent_review": "deputized_independent_review_completed",
    "github_review_record": "no_formal_review_submitted",
}
OBSERVATION_SCHEMA_CONTRACT_DIGEST = (
    "sha256:63f45b8ed2849b8fb479fdbc48aa51a6c5f587dff9fb562aeb2cc61001ccfa09"
)
SCHEMA_DYNAMIC_MARKERS = {
    (
        "$defs",
        "candidateReceipt",
        "properties",
        "digest",
        "const",
    ): "<candidate-receipt-sha256>",
    (
        "$defs",
        "signatureObservation",
        "properties",
        "trusted_signers_digest",
        "const",
    ): "<trusted-signers-sha256>",
}


class ObservationError(ValueError):
    """Signal a release-observation mismatch with a stable public message."""


def sha256_digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    document = {}
    for key, value in pairs:
        if key in document:
            raise ObservationError("release observation contains a duplicate key")
        document[key] = value
    return document


def reject_non_finite(token: str) -> None:
    raise ObservationError(f"release observation contains {token}")


def load_json(path: Path) -> dict:
    document = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_non_finite,
    )
    if not isinstance(document, dict):
        raise ObservationError("release observation requires a JSON object")
    return document


def require_exact(document: object, keys: set[str], label: str) -> dict:
    if not isinstance(document, dict) or set(document) != keys:
        raise ObservationError(f"{label} field set differs")
    return document


def require_oid(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA1_OID.fullmatch(value) is None:
        raise ObservationError(f"{label} requires a material SHA-1 object id")
    return value


def require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256_DIGEST.fullmatch(value) is None:
        raise ObservationError(f"{label} requires a material SHA-256 digest")
    return value


def require_datetime(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ObservationError(f"{label} requires an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ObservationError(
            f"{label} requires an ISO 8601 timestamp"
        ) from error
    if parsed.tzinfo is None:
        raise ObservationError(f"{label} requires an offset-aware timestamp")
    return value


def schema_value(schema: dict, *path: str) -> object:
    current: object = schema
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise ObservationError(
                "release observation schema is missing " + ".".join(path)
            )
        current = current[key]
    return current


def require_closed_schema_object(
    fragment: object,
    keys: set[str],
    label: str,
) -> dict:
    if (
        not isinstance(fragment, dict)
        or fragment.get("type") != "object"
        or fragment.get("additionalProperties") is not False
        or set(fragment.get("required", [])) != keys
        or set(fragment.get("properties", {})) != keys
    ):
        raise ObservationError(f"release observation schema {label} shape differs")
    return fragment


def normalized_schema_contract_digest(schema: dict) -> str:
    """Bind the complete closed schema while normalizing material digests."""
    normalized = deepcopy(schema)
    for path, marker in SCHEMA_DYNAMIC_MARKERS.items():
        current: object = normalized
        for key in path[:-1]:
            if not isinstance(current, dict) or key not in current:
                raise ObservationError(
                    "release observation schema is missing " + ".".join(path)
                )
            current = current[key]
        if not isinstance(current, dict) or path[-1] not in current:
            raise ObservationError(
                "release observation schema is missing " + ".".join(path)
            )
        current[path[-1]] = marker
    canonical = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256_digest(canonical)


def validate_observation_schema(
    schema: dict,
    *,
    candidate_receipt_digest: str,
    trusted_signers_digest: str,
) -> None:
    """Bind every decision-changing schema constant to the manual verifier."""
    require_closed_schema_object(schema, OBSERVATION_KEYS, "root")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != (
            "https://schemas.driftframestudios.org/"
            "lims-eln-program-specification/v0.3.1/"
            "program-release-observation.v1.schema.json"
        )
    ):
        raise ObservationError("release observation schema identity differs")

    defs = schema.get("$defs")
    if not isinstance(defs, dict):
        raise ObservationError("release observation schema definitions differ")
    closed_definitions = {
        "candidateReceipt": {"path", "digest"},
        "candidateSource": {"commit_oid", "tree_oid"},
        "releaseSubject": {
            "git_object_format",
            "tag",
            "tag_object_oid",
            "commit_oid",
            "tree_oid",
            "archive_format",
            "archive_digest",
            "promoted_at",
        },
        "signatureObservation": {
            "verification",
            "trusted_signers_path",
            "trusted_signers_digest",
        },
        "workflowObservation": {
            "workflow_path",
            "workflow_name",
            "check_context",
            "run_id",
            "job_id",
            "conclusion",
        },
        "releaseReviewObservation": {
            "pull_request",
            *RELEASE_REVIEW_ROUTE,
        },
        "metadata": {"schema_version", "created_at", "updated_at", "owner"},
    }
    for name, keys in closed_definitions.items():
        require_closed_schema_object(defs.get(name), keys, name)
    require_closed_schema_object(
        schema_value(schema, "$defs", "metadata", "properties", "owner"),
        {"actor_id", "display_name", "role"},
        "metadata.owner",
    )

    expected_values = {
        ("properties", "$schema", "const"): (
            "../schemas/program-release-observation.v1.schema.json"
        ),
        ("properties", "schema_version", "const"): "1.0.0",
        ("properties", "release_observation_id", "const"): (
            "OBS-PROGRAM-RELEASE-003"
        ),
        ("properties", "promotion_receipt_id", "const"): (
            "RCP-PROGRAM-PROMOTION-003"
        ),
        ("properties", "repository", "const"): (
            "driftframestudios/lims-eln-program-specification"
        ),
        ("properties", "target_release", "const"): PROGRAM_TAG,
        ("properties", "observation_state", "enum"): [
            "pending_post_tag",
            "release_observed",
        ],
        ("properties", "evidence_mode", "enum"): ["planned", "observed"],
        ("properties", "assurance_stage", "enum"): ["specified", "verified"],
        ("properties", "accountable_role", "const"): (
            "Program release stewardship"
        ),
        ("$defs", "sha1Oid", "pattern"): SHA1_OID.pattern,
        ("$defs", "sha256Digest", "pattern"): SHA256_DIGEST.pattern,
        ("$defs", "candidateReceipt", "properties", "path", "const"): (
            PROMOTION_RECEIPT_PATH.as_posix()
        ),
        ("$defs", "candidateReceipt", "properties", "digest", "const"): (
            candidate_receipt_digest
        ),
        ("$defs", "releaseSubject", "properties", "git_object_format", "const"): (
            "sha1"
        ),
        ("$defs", "releaseSubject", "properties", "tag", "const"): PROGRAM_TAG,
        ("$defs", "releaseSubject", "properties", "archive_format", "const"): (
            "git-archive-tar"
        ),
        ("$defs", "signatureObservation", "properties", "verification", "const"): (
            "valid"
        ),
        (
            "$defs",
            "signatureObservation",
            "properties",
            "trusted_signers_path",
            "const",
        ): TRUSTED_SIGNERS_PATH.as_posix(),
        (
            "$defs",
            "signatureObservation",
            "properties",
            "trusted_signers_digest",
            "const",
        ): trusted_signers_digest,
        ("$defs", "workflowObservation", "properties", "workflow_path", "const"): (
            ".github/workflows/validate.yml"
        ),
        ("$defs", "workflowObservation", "properties", "workflow_name", "const"): (
            "Validate program specification"
        ),
        ("$defs", "workflowObservation", "properties", "check_context", "const"): (
            "program-validation"
        ),
        ("$defs", "workflowObservation", "properties", "run_id", "pattern"): (
            POSITIVE_DECIMAL.pattern
        ),
        ("$defs", "workflowObservation", "properties", "job_id", "pattern"): (
            POSITIVE_DECIMAL.pattern
        ),
        ("$defs", "workflowObservation", "properties", "conclusion", "const"): (
            "success"
        ),
        (
            "$defs",
            "releaseReviewObservation",
            "properties",
            "pull_request",
            "minimum",
        ): 1,
        ("$defs", "metadata", "properties", "schema_version", "const"): "1.0.0",
        ("$defs", "metadata", "properties", "created_at", "format"): "date-time",
        ("$defs", "metadata", "properties", "updated_at", "format"): "date-time",
        (
            "$defs",
            "metadata",
            "properties",
            "owner",
            "properties",
            "actor_id",
            "const",
        ): "OWNER-PROGRAM-RELEASE-OBSERVATION-003",
        (
            "$defs",
            "metadata",
            "properties",
            "owner",
            "properties",
            "display_name",
            "const",
        ): "Program release stewardship role",
        (
            "$defs",
            "metadata",
            "properties",
            "owner",
            "properties",
            "role",
            "const",
        ): "Release observation owner",
    }
    for field, expected in RELEASE_REVIEW_ROUTE.items():
        expected_values[
            (
                "$defs",
                "releaseReviewObservation",
                "properties",
                field,
                "const",
            )
        ] = expected
    for path, expected in expected_values.items():
        if schema_value(schema, *path) != expected:
            raise ObservationError(
                "release observation schema " + ".".join(path) + " differs"
            )

    nullable_refs = {
        "candidate_source": "#/$defs/candidateSource",
        "release_subject": "#/$defs/releaseSubject",
        "signature_observation": "#/$defs/signatureObservation",
        "workflow_observation": "#/$defs/workflowObservation",
        "review_observation": "#/$defs/releaseReviewObservation",
    }
    for field, reference in nullable_refs.items():
        if schema_value(schema, "properties", field, "oneOf") != [
            {"type": "null"},
            {"$ref": reference},
        ]:
            raise ObservationError(
                f"release observation schema {field} lifecycle differs"
            )
    expected_lifecycle = [
        {
            "if": {
                "properties": {
                    "observation_state": {"const": "pending_post_tag"}
                }
            },
            "then": {
                "properties": {
                    "evidence_mode": {"const": "planned"},
                    "assurance_stage": {"const": "specified"},
                    **{field: {"type": "null"} for field in nullable_refs},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "observation_state": {"const": "release_observed"}
                }
            },
            "then": {
                "properties": {
                    "evidence_mode": {"const": "observed"},
                    "assurance_stage": {"const": "verified"},
                    **{
                        field: {"$ref": reference}
                        for field, reference in nullable_refs.items()
                    },
                }
            },
        },
    ]
    if schema.get("allOf") != expected_lifecycle:
        raise ObservationError("release observation schema lifecycle branches differ")
    if normalized_schema_contract_digest(schema) != OBSERVATION_SCHEMA_CONTRACT_DIGEST:
        raise ObservationError(
            "release observation schema canonical closed shape differs"
        )


def validate_observation_document(
    observation: dict,
    *,
    candidate_receipt_digest: str,
    trusted_signers_digest: str,
) -> str:
    """Validate the closed data contract and return its lifecycle state."""
    require_exact(observation, OBSERVATION_KEYS, "release observation")
    expected_identity = {
        "$schema": "../schemas/program-release-observation.v1.schema.json",
        "schema_version": "1.0.0",
        "release_observation_id": "OBS-PROGRAM-RELEASE-003",
        "promotion_receipt_id": "RCP-PROGRAM-PROMOTION-003",
        "repository": "driftframestudios/lims-eln-program-specification",
        "target_release": PROGRAM_TAG,
        "accountable_role": "Program release stewardship",
    }
    for field, expected in expected_identity.items():
        if observation.get(field) != expected:
            raise ObservationError(f"release observation {field} differs")

    candidate_receipt = require_exact(
        observation["candidate_receipt"],
        {"path", "digest"},
        "candidate receipt binding",
    )
    if (
        candidate_receipt["path"] != PROMOTION_RECEIPT_PATH.as_posix()
        or candidate_receipt["digest"] != candidate_receipt_digest
    ):
        raise ObservationError("candidate promotion receipt binding differs")

    metadata = require_exact(
        observation["metadata"],
        {"schema_version", "created_at", "updated_at", "owner"},
        "release observation metadata",
    )
    owner = require_exact(
        metadata["owner"],
        {"actor_id", "display_name", "role"},
        "release observation owner",
    )
    if (
        metadata["schema_version"] != "1.0.0"
        or owner
        != {
            "actor_id": "OWNER-PROGRAM-RELEASE-OBSERVATION-003",
            "display_name": "Program release stewardship role",
            "role": "Release observation owner",
        }
    ):
        raise ObservationError("release observation metadata differs")
    require_datetime(metadata["created_at"], "release observation created_at")
    require_datetime(metadata["updated_at"], "release observation updated_at")

    state = observation.get("observation_state")
    dependent_fields = (
        "candidate_source",
        "release_subject",
        "signature_observation",
        "workflow_observation",
        "review_observation",
    )
    if state == "pending_post_tag":
        if (
            observation.get("evidence_mode") != "planned"
            or observation.get("assurance_stage") != "specified"
            or any(observation.get(field) is not None for field in dependent_fields)
        ):
            raise ObservationError("pending release observation posture differs")
        return state
    if state != "release_observed":
        raise ObservationError("release observation state differs")
    if (
        observation.get("evidence_mode") != "observed"
        or observation.get("assurance_stage") != "verified"
    ):
        raise ObservationError("observed release evidence posture differs")

    candidate_source = require_exact(
        observation["candidate_source"],
        {"commit_oid", "tree_oid"},
        "candidate source",
    )
    require_oid(candidate_source["commit_oid"], "candidate source commit")
    candidate_tree = require_oid(
        candidate_source["tree_oid"],
        "candidate source tree",
    )
    release_subject = require_exact(
        observation["release_subject"],
        {
            "git_object_format",
            "tag",
            "tag_object_oid",
            "commit_oid",
            "tree_oid",
            "archive_format",
            "archive_digest",
            "promoted_at",
        },
        "release subject",
    )
    if (
        release_subject["git_object_format"] != "sha1"
        or release_subject["tag"] != PROGRAM_TAG
        or release_subject["archive_format"] != "git-archive-tar"
    ):
        raise ObservationError("release subject identity posture differs")
    require_oid(release_subject["tag_object_oid"], "release tag object")
    require_oid(release_subject["commit_oid"], "release commit")
    release_tree = require_oid(release_subject["tree_oid"], "release tree")
    require_digest(release_subject["archive_digest"], "release archive")
    require_datetime(release_subject["promoted_at"], "release promotion time")
    if candidate_tree != release_tree:
        raise ObservationError("candidate and released Program trees differ")

    signature = require_exact(
        observation["signature_observation"],
        {"verification", "trusted_signers_path", "trusted_signers_digest"},
        "signature observation",
    )
    if (
        signature["verification"] != "valid"
        or signature["trusted_signers_path"] != TRUSTED_SIGNERS_PATH.as_posix()
        or signature["trusted_signers_digest"] != trusted_signers_digest
    ):
        raise ObservationError("trusted signature observation differs")

    workflow = require_exact(
        observation["workflow_observation"],
        {
            "workflow_path",
            "workflow_name",
            "check_context",
            "run_id",
            "job_id",
            "conclusion",
        },
        "workflow observation",
    )
    if (
        workflow["workflow_path"] != ".github/workflows/validate.yml"
        or workflow["workflow_name"] != "Validate program specification"
        or workflow["check_context"] != "program-validation"
        or workflow["conclusion"] != "success"
    ):
        raise ObservationError("hosted Program proof observation differs")
    for field in ("run_id", "job_id"):
        if (
            not isinstance(workflow[field], str)
            or POSITIVE_DECIMAL.fullmatch(workflow[field]) is None
        ):
            raise ObservationError(f"workflow {field} requires a positive id")

    review = require_exact(
        observation["review_observation"],
        {"pull_request", *RELEASE_REVIEW_ROUTE},
        "release review observation",
    )
    if type(review["pull_request"]) is not int or review["pull_request"] < 1:
        raise ObservationError(
            "release review observation requires a pull request number"
        )
    if {key: review[key] for key in RELEASE_REVIEW_ROUTE} != RELEASE_REVIEW_ROUTE:
        raise ObservationError(
            "release review observation differs from the authorized route"
        )
    return state


def run_git(root: Path, *arguments: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=text,
    )
    return result.stdout.strip() if text else result.stdout


def candidate_receipt_digest(root: Path, observation: dict) -> str:
    """Resolve the candidate receipt from its lifecycle-owned source."""
    state = observation.get("observation_state")
    target_tag = observation.get("target_release")
    if state == "release_observed" and isinstance(target_tag, str):
        candidate_receipt_bytes = run_git(
            root,
            "show",
            f"{target_tag}:{PROMOTION_RECEIPT_PATH.as_posix()}",
            text=False,
        )
        assert isinstance(candidate_receipt_bytes, bytes)
    else:
        candidate_receipt_bytes = (root / PROMOTION_RECEIPT_PATH).read_bytes()
    return sha256_digest(candidate_receipt_bytes)


def git_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def verify(root: Path = ROOT, *, require_observed: bool = False) -> dict:
    observation_path = root / OBSERVATION_PATH
    observation = load_json(observation_path)
    schema = load_json(root / OBSERVATION_SCHEMA_PATH)
    trusted_signers_bytes = (root / TRUSTED_SIGNERS_PATH).read_bytes()
    receipt_digest = candidate_receipt_digest(root, observation)
    signers_digest = sha256_digest(trusted_signers_bytes)
    validate_observation_schema(
        schema,
        candidate_receipt_digest=receipt_digest,
        trusted_signers_digest=signers_digest,
    )
    state = validate_observation_document(
        observation,
        candidate_receipt_digest=receipt_digest,
        trusted_signers_digest=signers_digest,
    )
    if state == "pending_post_tag":
        if require_observed:
            raise ObservationError(
                "the release observation is ready for post-tag evidence"
            )
        return {
            "status": state,
            "target_release": PROGRAM_TAG,
            "observation_carrier_commit": None,
        }

    subject = observation["release_subject"]
    candidate = observation["candidate_source"]
    assert isinstance(subject, dict) and isinstance(candidate, dict)
    actual_tag_object = run_git(root, "rev-parse", f"{PROGRAM_TAG}^{{tag}}")
    actual_commit = run_git(root, "rev-parse", f"{PROGRAM_TAG}^{{commit}}")
    actual_tree = run_git(root, "rev-parse", f"{actual_commit}^{{tree}}")
    candidate_tree = run_git(
        root,
        "rev-parse",
        f"{candidate['commit_oid']}^{{tree}}",
    )
    archive = run_git(
        root,
        "archive",
        "--format=tar",
        str(actual_commit),
        text=False,
    )
    assert isinstance(archive, bytes)
    if (
        actual_tag_object != subject["tag_object_oid"]
        or actual_commit != subject["commit_oid"]
        or actual_tree != subject["tree_oid"]
        or candidate_tree != candidate["tree_oid"]
        or sha256_digest(archive) != subject["archive_digest"]
    ):
        raise ObservationError("recorded Program release subject differs from Git")
    if not git_is_ancestor(root, str(candidate["commit_oid"]), str(actual_commit)):
        raise ObservationError("candidate source is outside the Program release history")
    subprocess.run(
        [
            "git",
            "-c",
            "gpg.format=ssh",
            "-c",
            "gpg.minTrustLevel=fully",
            "-c",
            f"gpg.ssh.allowedSignersFile={root / TRUSTED_SIGNERS_PATH}",
            "-c",
            "gpg.ssh.revocationFile=/dev/null",
            "verify-tag",
            PROGRAM_TAG,
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    head = run_git(root, "rev-parse", "HEAD^{commit}")
    main_commit = run_git(root, "rev-parse", "origin/main^{commit}")
    if head == actual_commit:
        raise ObservationError("release observation requires a later carrier commit")
    for descendant, label in (
        (str(main_commit), "accepted main"),
        (str(head), "observation carrier"),
    ):
        if not git_is_ancestor(root, str(actual_commit), descendant):
            raise ObservationError(
                f"Program release subject is outside the {label} history"
            )
    carrier_bytes = run_git(
        root,
        "show",
        f"HEAD:{OBSERVATION_PATH.as_posix()}",
        text=False,
    )
    assert isinstance(carrier_bytes, bytes)
    if carrier_bytes != observation_path.read_bytes():
        raise ObservationError("current Git HEAD carries different observation bytes")

    lock = load_json(root / "constellation.lock.json")
    release_role = load_json(root / "release" / "repository-role.json")
    specification = lock.get("specification")
    release_coordinates = release_role.get("release_coordinates")
    if (
        not isinstance(specification, dict)
        or specification.get("commit") != actual_commit
        or specification.get("digest") != f"git-tree-sha1:{actual_tree}"
        or specification.get("coordinate_status") != "pinned"
        or not isinstance(release_coordinates, dict)
        or release_coordinates.get("commit") != actual_commit
        or release_coordinates.get("tree_digest") != f"git-tree-sha1:{actual_tree}"
        or release_coordinates.get("coordinate_status") != "pinned"
    ):
        raise ObservationError("Program release carriers differ from the signed subject")
    return {
        "status": state,
        "target_release": PROGRAM_TAG,
        "release_commit": actual_commit,
        "release_tree": actual_tree,
        "observation_carrier_commit": head,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-observed",
        action="store_true",
        help="Require a completed post-tag observation.",
    )
    arguments = parser.parse_args()
    print(
        json.dumps(
            verify(require_observed=arguments.require_observed),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

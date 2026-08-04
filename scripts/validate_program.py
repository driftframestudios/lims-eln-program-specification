from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_RELEASE = "0.3.2"
PROGRAM_TAG = f"spec-v{PROGRAM_RELEASE}"
GOVERNANCE_RELEASE = "2.0.2"
GOVERNANCE_TAG = f"governance-v{GOVERNANCE_RELEASE}"
CANONICAL_BUNDLE_SCHEMA_RELEASE = "2.0.1"
CONTROL_PLANE_PROFILE = "0.3.0"
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
CANONICAL_CLOSURE_DIGEST = (
    "sha256:c402e7a72d9066424d5b83c8fda51ca2fad43c025d017a5f5535126239c96ffb"
)
CANONICAL_RESULT_DIGEST = (
    "sha256:9d42b972c77764c81ff32fefe8f02367a27406e9ba082a704587cc9b5a9da860"
)
CANONICAL_AGGREGATE_ARTIFACT_DIGEST = (
    "sha256:2d8e67ec2da8236fc23de7943e7727d2b74e0e6ee2b15afd9c765443b9c52b61"
)
CANONICAL_BUNDLE_FILE_DIGEST = (
    "sha256:b868604412039c3705d4b60e649c43da2f51592ca0215d22ebe4477b75016ef4"
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
    "data_contract_concordance",
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
            "commit",
            "digest",
            "coordinate_status",
            "canonical_closure_digest",
            "reference_result_digest",
            "aggregate_artifact_digest",
            "canonical_bundle_file_digest",
        },
        "implementation": {
            "release",
            "commit",
            "digest",
            "coordinate_status",
            "source_binding_status",
        },
        "comparison": {
            "release",
            "commit",
            "digest",
            "coordinate_status",
            "canonical_closure_digest",
            "aggregate_artifact_digest",
            "receipt_schema",
        },
        "governance": {
            "release",
            "profile",
            "schema_version",
            "commit",
            "digest",
            "coordinate_status",
        },
    }
    for role, expected_keys in coordinate_keys.items():
        coordinate = require_exact_object(
            constellation_lock[role],
            expected_keys,
            f"constellation_lock.{role}",
        )
        for key in expected_keys:
            require_string(coordinate[key], f"constellation_lock.{role}.{key}")
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
        {"status", "receipt_id", "receipt_path", "required_roles"},
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
            "data_contract_concordance",
            "database_migration_contract",
            "database_open_receipts",
            "database_release_manifest",
        },
        "release_role.contract_bindings",
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
        "data_contract_concordance",
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
    if release_coordinate is not None:
        release_coordinate = require_exact_object(
            release_coordinate,
            {
                "tag",
                "commit",
                "digest",
                "promoted_at",
                "check_contexts",
                "ruleset_receipt",
                "codeowner_resolution",
            },
            "promotion_receipt.release_coordinate",
        )
        require_string_list(
            release_coordinate["check_contexts"],
            "promotion_receipt.release_coordinate.check_contexts",
            minimum=2,
        )
        for key in {
            "tag",
            "commit",
            "digest",
            "promoted_at",
            "ruleset_receipt",
            "codeowner_resolution",
        }:
            require_string(
                release_coordinate[key],
                f"promotion_receipt.release_coordinate.{key}",
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
    constellation_lock: dict,
    status_document: dict,
    substantive_receipt_ids: set[str],
) -> None:
    """Validate both candidate and settled release states without mixed evidence."""
    state = release_role["release_state"]
    release_coordinates = release_role["release_coordinates"]
    promotion_coordinates = release_role["promotion_coordinates"]
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
    ):
        raise ValueError("promotion receipt identity or manifest locator differs")
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
        if (
            promotion_receipt["promotion_state"] != "candidate_pending"
            or promotion_receipt["evidence_mode"] != "planned"
            or promotion_receipt["assurance_stage"] != "specified"
            or promotion_receipt["candidate_coordinate"] != provenance
            or promotion_receipt["release_coordinate"] is not None
            or promotion_coordinates["status"]
            != "pending_cross_repository_settlement"
        ):
            raise ValueError("candidate promotion receipt posture differs")
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
        or set(release_coordinate.get("check_contexts", []))
        != {"branch-policy", "program-validation"}
        or promotion_coordinates["status"] != "settled"
    ):
        raise ValueError("released promotion evidence or Machine Node posture differs")
    for locator in {
        release_coordinate["ruleset_receipt"],
        release_coordinate["codeowner_resolution"],
    }:
        if re.fullmatch(r"(?:governed|evidence)://[a-z0-9][a-z0-9._/-]*", locator) is None:
            raise ValueError("released promotion evidence locator is malformed")
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
    data_concordance: dict,
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
            "contract_concordance",
            "total_record_count",
            "metadata",
        },
        "database constellation finding index",
    )
    if (
        constellation_index["index_id"]
        != "DATABASE-CONSTELLATION-FINDING-INDEX-001"
        or constellation_index["version"] != "1.1.0"
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

    index_concordance = require_exact_object(
        constellation_index["contract_concordance"],
        {"concordance_id", "version", "path", "digest", "representation_ids"},
        "database constellation contract concordance",
    )
    if (
        index_concordance["concordance_id"] != "DATA-CONTRACT-CONCORDANCE-001"
        or index_concordance["version"] != "1.0.0"
        or index_concordance["path"]
        != "specifications/data-contract-concordance.json"
        or index_concordance["digest"]
        != sha256_digest("specifications/data-contract-concordance.json")
    ):
        raise ValueError("database constellation concordance binding differs")

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
        or data_contract["version"] != "1.1.0"
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
    target_platform = data_contract["target_platform"]
    if (
        target_platform.get("qualified_major") != 17
        or target_platform.get("supported_predecessor_major") != 16
        or target_platform.get("forward_compatibility_rehearsal_major") != 18
        or target_platform.get("digest_storage")
        != "one SHA-256 semantic value represented as exactly 32-byte bytea or constrained lowercase 64-character hexadecimal text with algorithm canonicalization schema and scope metadata"
        or not str(target_platform.get("decimal_envelope", "")).startswith(
            "numeric(38,18)"
        )
    ):
        raise ValueError("data contract engine or primitive target differs")
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
        data_concordance,
        {
            "concordance_id",
            "version",
            "status",
            "authority",
            "canonical_contract",
            "completion_claim",
            "target_decisions",
            "representations",
            "accepted_divergences",
            "release_gates",
            "metadata",
        },
        "data contract concordance",
    )
    if (
        data_concordance["concordance_id"]
        != "DATA-CONTRACT-CONCORDANCE-001"
        or data_concordance["version"] != "1.0.0"
        or data_concordance["status"] != "specified"
        or data_concordance["authority"] != "program_specification"
    ):
        raise ValueError("data contract concordance identity differs")
    canonical_contract = require_exact_object(
        data_concordance["canonical_contract"],
        {"contract_id", "version", "path"},
        "data contract concordance canonical contract",
    )
    if canonical_contract != {
        "contract_id": data_contract["contract_id"],
        "version": data_contract["version"],
        "path": "specifications/data-primitives.json",
    }:
        raise ValueError("data contract concordance canonical binding differs")
    completion_claim = require_exact_object(
        data_concordance["completion_claim"],
        {
            "current_claim",
            "current_evidence_stage",
            "operational_claim_gate",
            "production_authorization_effect",
        },
        "data contract concordance completion claim",
    )
    for field in ("current_claim", "current_evidence_stage", "operational_claim_gate"):
        require_string(completion_claim[field], f"data concordance claim {field}")
    if completion_claim["production_authorization_effect"] != "none":
        raise ValueError("data concordance candidate grants production authority")

    expected_decision_topics = {
        "completion_claim",
        "first_durable_environment",
        "execution_receipt",
        "release_promotion",
        "semantic_crosswalk",
        "identity",
        "digest_representation",
        "scientific_numeric_profiles",
        "measurement_provenance",
        "conditional_acceptance_and_supersession",
        "vendor_release_scope",
        "cutover_restore_and_data_exit",
        "postgresql_support_and_evidence_authority",
    }
    decision_ids: set[str] = set()
    decision_topics: set[str] = set()
    for index, decision in enumerate(data_concordance["target_decisions"]):
        decision = require_exact_object(
            decision,
            {"decision_id", "topic", "decision", "acceptance_criteria"},
            f"data concordance decision[{index}]",
        )
        decision_id = require_string(
            decision["decision_id"], f"data concordance decision[{index}].id"
        )
        if decision_id in decision_ids:
            raise ValueError(f"data concordance decision {decision_id} repeats")
        decision_ids.add(decision_id)
        decision_topics.add(
            require_string(decision["topic"], f"{decision_id}.topic")
        )
        require_string(decision["decision"], f"{decision_id}.decision")
        require_string_list(
            decision["acceptance_criteria"],
            f"{decision_id}.acceptance_criteria",
            minimum=3,
        )
    if (
        decision_ids != {f"DCC-DECISION-{index:03d}" for index in range(1, 14)}
        or decision_topics != expected_decision_topics
    ):
        raise ValueError("data concordance decision coverage differs")

    expected_representations = {
        "REP-PROGRAM-DATA-CONTRACT-001": (
            "specification",
            "canonical_program_contract",
            "specified",
            "program_specification",
        ),
        "REP-REFERENCE-DATABASE-RELEASE-001": (
            "reference_pack",
            "executable_reference_schema",
            "repository_observed",
            "reference_implementation",
        ),
        "REP-IMPLEMENTATION-DATABASE-RELEASE-001": (
            "implementation",
            "active_release_projection",
            "observed_execution_synthetic_environment",
            "implementation_execution",
        ),
        "REP-SIMULATION-DATABASE-ORACLE-V2": (
            "simulation",
            "simulated_oracle",
            "simulated",
            "simulation_only",
        ),
        "REP-GOVERNANCE-DATA-CONTRACT-001": (
            "governance",
            "generic_executable_contract_example",
            "example",
            "governance_schema_example",
        ),
    }
    representation_ids: set[str] = set()
    representation_divergences: dict[str, set[str]] = {}
    for index, representation in enumerate(data_concordance["representations"]):
        representation = require_exact_object(
            representation,
            {
                "representation_id",
                "repository",
                "constellation_role",
                "representation_kind",
                "artifact_path",
                "native_artifact_id",
                "native_artifact_version",
                "artifact_sha256",
                "coordinate_status",
                "coordinate_binding",
                "conformance_state",
                "evidence_mode",
                "authority",
                "actual_acceptance_required",
                "policy_ids",
                "accepted_divergence_ids",
            },
            f"data concordance representation[{index}]",
        )
        representation_id = require_string(
            representation["representation_id"],
            f"data concordance representation[{index}].id",
        )
        if (
            representation_id in representation_ids
            or representation_id not in expected_representations
        ):
            raise ValueError(
                f"data concordance representation {representation_id!r} differs"
            )
        representation_ids.add(representation_id)
        role, kind, evidence_mode, authority = expected_representations[
            representation_id
        ]
        if (
            representation["constellation_role"] != role
            or representation["representation_kind"] != kind
            or representation["evidence_mode"] != evidence_mode
            or representation["authority"] != authority
            or representation["actual_acceptance_required"] is not True
            or set(representation["policy_ids"]) != policy_ids
        ):
            raise ValueError(
                f"data concordance representation {representation_id} posture differs"
            )
        for field in (
            "repository",
            "artifact_path",
            "native_artifact_id",
            "native_artifact_version",
            "coordinate_status",
            "coordinate_binding",
            "conformance_state",
        ):
            require_string(representation[field], f"{representation_id}.{field}")
        if MATERIAL_SHA256_PATTERN.fullmatch(representation["artifact_sha256"]) is None:
            raise ValueError(
                f"data concordance representation {representation_id} requires a material artifact digest"
            )
        if (
            representation_id == "REP-PROGRAM-DATA-CONTRACT-001"
            and representation["artifact_sha256"]
            != sha256_digest("specifications/data-primitives.json")
        ):
            raise ValueError("program data concordance artifact digest differs")
        if (
            representation_id == "REP-REFERENCE-DATABASE-RELEASE-001"
            and representation["coordinate_binding"]
            != "git:318161f2cbb8e80383662949cb9e36b2b1c9a61f"
        ):
            raise ValueError("reference data concordance coordinate differs")
        representation_divergences[representation_id] = set(
            representation["accepted_divergence_ids"]
        )
    if representation_ids != set(expected_representations):
        raise ValueError("data concordance representation coverage differs")
    if set(index_concordance["representation_ids"]) != representation_ids:
        raise ValueError("database constellation representation coverage differs")

    divergence_ids: set[str] = set()
    reciprocal_divergences: dict[str, set[str]] = {
        representation_id: set() for representation_id in representation_ids
    }
    for index, divergence in enumerate(data_concordance["accepted_divergences"]):
        divergence = require_exact_object(
            divergence,
            {
                "divergence_id",
                "title",
                "representation_ids",
                "policy_ids",
                "status",
                "conditions",
                "requalification_trigger",
            },
            f"data concordance divergence[{index}]",
        )
        divergence_id = require_string(
            divergence["divergence_id"],
            f"data concordance divergence[{index}].id",
        )
        if divergence_id in divergence_ids:
            raise ValueError(f"data concordance divergence {divergence_id} repeats")
        divergence_ids.add(divergence_id)
        bound_representations = set(
            require_string_list(
                divergence["representation_ids"],
                f"{divergence_id}.representation_ids",
                minimum=1,
            )
        )
        if not bound_representations <= representation_ids:
            raise ValueError(f"{divergence_id} references an unknown representation")
        if not set(divergence["policy_ids"]) <= policy_ids:
            raise ValueError(f"{divergence_id} references an unknown policy")
        require_string(divergence["title"], f"{divergence_id}.title")
        require_string(divergence["status"], f"{divergence_id}.status")
        require_string_list(
            divergence["conditions"], f"{divergence_id}.conditions", minimum=3
        )
        require_string(
            divergence["requalification_trigger"],
            f"{divergence_id}.requalification_trigger",
        )
        for representation_id in bound_representations:
            reciprocal_divergences[representation_id].add(divergence_id)
    if divergence_ids != {
        f"DCC-DIVERGENCE-{index:03d}" for index in range(1, 9)
    }:
        raise ValueError("data concordance divergence coverage differs")
    if representation_divergences != reciprocal_divergences:
        raise ValueError("data concordance divergence bindings are not reciprocal")

    gate_ids = {
        require_string(gate["gate_id"], "data concordance gate id")
        for gate in data_concordance["release_gates"]
        if require_exact_object(
            gate,
            {"gate_id", "criterion"},
            f"data concordance gate {gate.get('gate_id', '<missing>')}",
        )
    }
    if gate_ids != {
        "DCC-GATE-COVERAGE",
        "DCC-GATE-PINNED-BYTES",
        "DCC-GATE-AUTHORITY",
        "DCC-GATE-OBSERVED-RELEASE",
    }:
        raise ValueError("data concordance release gate coverage differs")
    for gate in data_concordance["release_gates"]:
        require_string(gate["criterion"], f"{gate['gate_id']}.criterion")

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
        or migration_contract["version"] != "1.1.0"
        or migration_contract["data_contract_id"] != data_contract["contract_id"]
    ):
        raise ValueError("database migration contract identity differs")
    engine_contract = migration_contract["engine_contract"]
    if (
        engine_contract.get("family") != "PostgreSQL"
        or engine_contract.get("qualified_major") != 17
        or engine_contract.get("supported_predecessor_major") != 16
        or engine_contract.get("forward_compatibility_rehearsal_major") != 18
        or engine_contract.get("reference_majors") != [16, 17, 18]
    ):
        raise ValueError("database migration engine qualification matrix differs")
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
        or database_receipts["version"] != "1.1.0"
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
        or database_manifest["version"] != "1.1.0"
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
        != "implementation-v0.3.2"
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
        "DATA-CONTRACT-CONCORDANCE-001": "specifications/data-contract-concordance.json",
        "DATABASE-MIGRATION-CONTRACT-001": "specifications/database-migration.json",
        "DATABASE-OPEN-RECEIPTS-001": "receipts/database-open-receipts.json",
        "PROGRAM-CAPABILITIES-0.3.2": "specifications/capabilities.json",
        "PROGRAM-INVARIANTS-0.3.2": "specifications/invariants.json",
        "PROGRAM-SCENARIOS-0.3.2": "examples/scenarios.json",
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
            ledger["version"],
            "database/primitive-findings.json",
        ),
        "database_constellation_finding_index": (
            constellation_index["index_id"],
            constellation_index["version"],
            "database/constellation-finding-index.json",
        ),
        "database_modernization_plan_set": (
            plan_set["plan_set_id"],
            plan_set["version"],
            "plans/database-modernization-plans.json",
        ),
        "data_contract": (
            data_contract["contract_id"],
            data_contract["version"],
            "specifications/data-primitives.json",
        ),
        "data_contract_concordance": (
            data_concordance["concordance_id"],
            data_concordance["version"],
            "specifications/data-contract-concordance.json",
        ),
        "database_migration_contract": (
            migration_contract["migration_contract_id"],
            migration_contract["version"],
            "specifications/database-migration.json",
        ),
        "database_open_receipts": (
            database_receipts["registry_id"],
            database_receipts["version"],
            "receipts/database-open-receipts.json",
        ),
        "database_release_manifest": (
            database_manifest["manifest_id"],
            database_manifest["version"],
            "release/database-release-manifest.json",
        ),
    }
    for binding_name, (contract_id, contract_version, path) in binding_map.items():
        binding = release_bindings[binding_name]
        if (
            binding["contract_id"] != contract_id
            or binding["version"] != contract_version
            or binding["path"] != path
            or binding["digest"] != sha256_digest(path)
        ):
            raise ValueError(f"release role database binding differs for {binding_name}")
    if (
        status_document["database_finding_ledger"] != ledger["ledger_id"]
        or status_document["data_contract"] != data_contract["contract_id"]
        or status_document["data_contract_concordance"]
        != data_concordance["concordance_id"]
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
        "data_contract_decisions": len(decision_ids),
        "data_contract_representations": len(representation_ids),
        "data_contract_divergences": len(divergence_ids),
        "database_plans": len(plan_ids),
        "database_flyway_transition_estimates": 1,
        "database_ownership_boundaries": len(ownership_ids),
        "database_stages": len(stage_ids),
        "data_primitive_policies": len(policy_ids),
        "database_reconciliation_dimensions": len(dimension_ids),
        "database_release_gates": len(gate_ids),
        "database_open_receipts": len(database_receipt_ids),
    }


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
    data_contract_concordance = load_json(
        "specifications/data-contract-concordance.json"
    )
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
    promotion_receipt = load_json("receipts/promotion-receipt.json")
    status_document = load_status()

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
        data_concordance=data_contract_concordance,
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
        canonical_bundle.get("bundle_version") != CANONICAL_BUNDLE_SCHEMA_RELEASE
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
        "DATA-CONTRACT-CONCORDANCE-001": (
            "specifications/data-contract-concordance.json",
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
        constellation_lock["implementation"]["release"]
        != f"implementation-v{PROGRAM_RELEASE}"
    ):
        raise ValueError(
            "implementation lock release differs from the canonical external candidate"
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
    if constellation_lock["comparison"]["receipt_schema"] != GOVERNANCE_RELEASE:
        raise ValueError(
            f"receipt schema differs from governance {GOVERNANCE_RELEASE}"
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
        "CHANGELOG.md",
        "README.md",
        "BRANCHING.md",
        "GOVERNANCE.md",
        "SECURITY.md",
        "constellation.lock.json",
        "coordination-horizon.json",
        "first-receipt.json",
        "release/repository-role.json",
        "receipts/promotion-receipt.json",
        "schemas/promotion-receipt.schema.json",
        "specifications/bounded-caller.json",
        "specifications/receipt-vocabulary-map.v1.json",
        "probes/catalog.json",
        "simulations/future-reality-closure-v0.3.json",
        "simulations/future-reality-2028-06-30-v1.json",
        "simulations/simulated-receipt-closure.v2.json",
        ".github/workflows/validate.yml",
        ".github/workflows/branch-policy.yml",
        ".github/dependabot.yml",
        ".github/pull_request_template.md",
        "scripts/check_branch_flow.py",
        "scripts/check_language.py",
        "scripts/language_policy_core.py",
        "docs/LANGUAGE_POLICY.md",
        "language-policy/corpus-v1.json",
        "language-policy/exemptions.json",
        "language-policy/manifest.json",
        "scripts/validate_pinned_sources.py",
        "docs/migrations/0.3.0-to-0.3.1.md",
        "docs/migrations/0.3.1-to-0.3.2.md",
        "docs/DATABASE_MODERNIZATION.md",
        "docs/DATABASE_CONSTELLATION_LEDGER.md",
        "database/primitive-findings.json",
        "database/constellation-finding-index.json",
        "plans/database-modernization-plans.json",
        "specifications/data-primitives.json",
        "specifications/data-contract-concordance.json",
        "specifications/database-migration.json",
        "receipts/database-open-receipts.json",
        "release/database-release-manifest.json",
        "tests/test_branch_flow.py",
        "tests/test_language_policy.py",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    if missing:
        raise ValueError(f"required collaboration surfaces are absent: {missing}")

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
        "repositories": len(repository_roles),
        **database_summary,
    }


if __name__ == "__main__":
    summary = validate()
    print(json.dumps({"status": "valid", **summary}, indent=2, sort_keys=True))

"""Source-only admission for one database lifecycle; runtime owns all effects."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Literal

from jsonschema import Draft202012Validator

from lims_eln_contracts.canonical import (
    DuplicateObjectKeyError,
    NonFiniteNumberError,
    canonical_json_bytes,
    strict_json_loads,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ID = "urn:driftframe:lims-eln:database-lifecycle-profile:1.0.0"
SCHEMA_BYTES = (ROOT / "schemas/database-lifecycle-profile.v1.schema.json").read_bytes()
SCHEMA_DIGEST = "sha256:" + hashlib.sha256(SCHEMA_BYTES).hexdigest()
CAPABILITY_SCHEMA_BYTES = (ROOT / "schemas/workbench-capabilities.v1.schema.json").read_bytes()
CAPABILITY_SCHEMA_DIGEST = "sha256:c4b5859d2b543b26970fb3b5b577b11e5f50415be7484c891257f4d2d0d83808"
_PROFILE_VALIDATOR = Draft202012Validator(strict_json_loads(SCHEMA_BYTES))
_CAPABILITY_VALIDATOR = Draft202012Validator(strict_json_loads(CAPABILITY_SCHEMA_BYTES))
MAX_INPUT_BYTES = 131072

FindingCode = Literal[
    "input_bytes", "utf8", "json_duplicate_key", "json_number", "json_syntax",
    "json_structure", "contract_shape", "source_binding", "stale_source",
    "stale_schema", "unsupported_version", "composition_unresolved",
    "composition_digest", "composition_contract", "composition_mismatch",
    "ownership_profile", "wrong_owner", "owner_decision_required",
    "destructive_authority_required", "external_cleanup_forbidden",
    "external_owner_action_required", "unowned_cleanup", "action_not_permitted",
    "duplicate_operation", "invalid_transition", "operation_evidence",
    "compatibility_required", "compatibility_mismatch", "unresolved_resources",
    "input_unavailable",
]


class LifecycleAdmissionError(ValueError):
    """A fixed finding code; the caller retains raw input and diagnostics."""

    def __init__(self, code: FindingCode) -> None:
        self.code = code
        super().__init__(f"{code}: retain the record and use the lifecycle guide's recovery route.")


@dataclass(frozen=True, slots=True)
class LifecycleSource:
    """Receiver-selected source trust, supplied independently of incoming bytes."""

    source_ref: str
    revision: str
    schema_digest: str

    def __post_init__(self) -> None:
        for value, pattern in (
            (self.source_ref, r"ref:[a-z][a-z0-9-]{0,63}"),
            (self.revision, r"(?!0{40}$)[a-f0-9]{40}"),
            (self.schema_digest, r"sha256:[a-f0-9]{64}"),
        ):
            if type(value) is not str or re.fullmatch(pattern, value) is None:
                raise LifecycleAdmissionError("source_binding")


@dataclass(frozen=True, slots=True)
class AdmittedLifecycleProfile:
    canonical_bytes: bytes
    resource_state: str
    unresolved_resource_refs: tuple[str, ...]
    executed_operations: int
    requested_operations: int


def _decode(payload: bytes) -> dict:
    if type(payload) is not bytes or len(payload) > MAX_INPUT_BYTES:
        raise LifecycleAdmissionError("input_bytes")
    try:
        text = payload.decode("utf-8")
        document = strict_json_loads(text)
    except UnicodeDecodeError:
        raise LifecycleAdmissionError("utf8") from None
    except DuplicateObjectKeyError:
        raise LifecycleAdmissionError("json_duplicate_key") from None
    except NonFiniteNumberError:
        raise LifecycleAdmissionError("json_number") from None
    except RecursionError:
        raise LifecycleAdmissionError("json_structure") from None
    except ValueError:
        raise LifecycleAdmissionError("json_syntax") from None
    if type(document) is not dict:
        raise LifecycleAdmissionError("contract_shape")
    return document


def _validate(validator: Draft202012Validator, document: dict, code: FindingCode) -> None:
    try:
        error = next(validator.iter_errors(document), None)
    except RecursionError:
        raise LifecycleAdmissionError("json_structure") from None
    if error is not None:
        raise LifecycleAdmissionError(code)


def _composition(document: dict, capability_payload: bytes | None) -> None:
    composition = document["composition"]
    if composition["state"] == "not_observed":
        if capability_payload is not None:
            raise LifecycleAdmissionError("composition_mismatch")
        return
    if capability_payload is None:
        raise LifecycleAdmissionError("composition_unresolved")
    capability = _decode(capability_payload)
    if "sha256:" + hashlib.sha256(CAPABILITY_SCHEMA_BYTES).hexdigest() != CAPABILITY_SCHEMA_DIGEST:
        raise LifecycleAdmissionError("stale_schema")
    if "sha256:" + hashlib.sha256(capability_payload).hexdigest() != composition["capability_digest"]:
        raise LifecycleAdmissionError("composition_digest")
    _validate(_CAPABILITY_VALIDATOR, capability, "composition_contract")
    if capability["runtime"]["state_adapter"] != "postgresql":
        raise LifecycleAdmissionError("composition_mismatch")


def _ownership(document: dict) -> None:
    profile, resource, invocation = (document[key] for key in ("requested_profile", "resource", "invocation"))
    expected = {
        "disposable": ("current_invocation_owned", "invocation_runtime"),
        "retained": ("explicit_owner_decision", "operator_runtime"),
        "external": ("external_owner_only", "external_owner_runtime"),
    }[profile["disposition"]]
    if (profile["cleanup_policy"], profile["credential_receiver_class"]) != expected:
        raise LifecycleAdmissionError("ownership_profile")
    if profile["disposition"] == "disposable" and (
        resource["initial_state"] != "absent"
        or resource["owner_ref"] != invocation["owner_ref"]
        or resource["creation_owner_ref"] != invocation["owner_ref"]
        or resource["created_by_invocation_ref"] != invocation["invocation_ref"]
        or "retain" in profile["permitted_actions"]
    ):
        raise LifecycleAdmissionError("ownership_profile")
    if profile["disposition"] == "external" and resource["creation_owner_ref"] != resource["owner_ref"]:
        raise LifecycleAdmissionError("ownership_profile")


def _operation_authority(document: dict, operation: dict, created_here: bool) -> None:
    profile, resource, invocation = (document[key] for key in ("requested_profile", "resource", "invocation"))
    action, authority = operation["action"], operation["authority"]
    disposition = profile["disposition"]
    if action not in profile["permitted_actions"]:
        raise LifecycleAdmissionError("action_not_permitted")
    if disposition == "external" and action == "cleanup" and (
        authority["actor_ref"] != resource["owner_ref"] or authority["basis"] != "explicit_owner_decision"
    ):
        raise LifecycleAdmissionError("external_cleanup_forbidden")
    owner = resource["creation_owner_ref"] if action == "create" else resource["owner_ref"]
    if authority["owner_ref"] != owner or authority["actor_ref"] not in {
        invocation["owner_ref"], resource["owner_ref"], resource["creation_owner_ref"]
    }:
        raise LifecycleAdmissionError("wrong_owner")
    if authority["basis"] == "invocation_owned" and (
        disposition != "disposable" or authority["actor_ref"] != invocation["owner_ref"]
    ):
        raise LifecycleAdmissionError("owner_decision_required")
    if authority["destructive_authorized"] != (action in {"restore", "cleanup"}):
        raise LifecycleAdmissionError("destructive_authority_required")
    if disposition == "external" and action in {"create", "migrate", "restore", "retain"} and authority["actor_ref"] != owner:
        raise LifecycleAdmissionError("external_owner_action_required")
    if action == "create" and (
        resource["created_by_invocation_ref"] != invocation["invocation_ref"]
        or authority["actor_ref"] != resource["creation_owner_ref"]
    ):
        raise LifecycleAdmissionError("wrong_owner")
    if disposition == "disposable" and action == "cleanup" and not created_here:
        raise LifecycleAdmissionError("unowned_cleanup")


def _operations(document: dict) -> tuple[int, int]:
    """One bounded pass over at most 64 events, with invocation-local state."""
    resource, profile = document["resource"], document["requested_profile"]
    state, created_here, cleanup_attempted = resource["initial_state"], False, False
    seen: set[str] = set()
    executed = requested = 0
    starts = {
        "create": {"absent"}, "migrate": {"present"}, "restore": {"present", "retained", "unresolved"},
        "retain": {"present"}, "cleanup": {"present", "retained", "unresolved"},
        "inspect": {"absent", "present", "retained", "removed", "unresolved"},
        "stop": {"absent", "present", "retained", "removed", "unresolved"},
    }
    for operation in document["operations"]:
        action, outcome = operation["action"], operation["outcome"]
        if operation["operation_ref"] in seen:
            raise LifecycleAdmissionError("duplicate_operation")
        seen.add(operation["operation_ref"])
        _operation_authority(document, operation, created_here)
        if operation["from_state"] != state or state not in starts[action]:
            raise LifecycleAdmissionError("invalid_transition")
        expected_failure = (
            f"{action}_failed" if outcome == "failed" else
            "resource_unresolved" if outcome == "unresolved" else None
        )
        if operation["failure_code"] != expected_failure or (
            (operation["evidence_ref"] is None) != (outcome == "requested")
        ):
            raise LifecycleAdmissionError("operation_evidence")
        compatibility = operation["compatibility"]
        if compatibility["state"] == "compatible" and (
            compatibility["engine_major"] != profile["engine_major"]
            or compatibility["migration_ref"] != profile["migration_ref"]
        ):
            raise LifecycleAdmissionError("compatibility_mismatch")
        if action in {"migrate", "restore"} and outcome == "succeeded" and compatibility["state"] != "compatible":
            raise LifecycleAdmissionError("compatibility_required")
        if outcome == "requested" or action == "stop":
            targets = {state}
        elif outcome in {"failed", "unresolved"}:
            targets = {"unresolved"}
        elif action == "inspect":
            targets = {state} if state != "unresolved" else {"absent", "present"}
            if state == "unresolved" and cleanup_attempted:
                targets.add("removed")
        else:
            targets = {{"create": "present", "migrate": "present", "restore": "present", "retain": "retained", "cleanup": "removed"}[action]}
        if operation["to_state"] not in targets:
            raise LifecycleAdmissionError("invalid_transition")
        created_here = created_here or (action == "create" and outcome == "succeeded")
        cleanup_attempted = cleanup_attempted or (action == "cleanup" and outcome != "requested")
        state = operation["to_state"]
        requested += outcome == "requested"
        executed += outcome != "requested"
    if resource["state"] != state:
        raise LifecycleAdmissionError("invalid_transition")
    unresolved = [resource["resource_ref"]] if state == "unresolved" else []
    if document["unresolved_resource_refs"] != unresolved:
        raise LifecycleAdmissionError("unresolved_resources")
    return executed, requested


def admit_lifecycle_profile(
    payload: bytes, *, expected_source: LifecycleSource, capability_payload: bytes | None = None,
) -> AdmittedLifecycleProfile:
    """Validate documentary consistency; authenticated runtime decisions own action admission.

    Incoming bytes are bounded before strict parsing. The closed schema bounds
    strings and events before semantic traversal and canonical serialization.
    The return owns immutable bytes and scalars; caller inputs stay unchanged.
    """
    if type(expected_source) is not LifecycleSource:
        raise LifecycleAdmissionError("source_binding")
    if expected_source.schema_digest != SCHEMA_DIGEST:
        raise LifecycleAdmissionError("stale_schema")
    document = _decode(payload)
    if "schema_version" in document and document["schema_version"] != "1.0.0":
        raise LifecycleAdmissionError("unsupported_version")
    if "schema_ref" in document and document["schema_ref"] != SCHEMA_ID:
        raise LifecycleAdmissionError("stale_schema")
    _validate(_PROFILE_VALIDATOR, document, "contract_shape")
    if document["source"] != {"source_ref": expected_source.source_ref, "revision": expected_source.revision}:
        raise LifecycleAdmissionError("stale_source")
    _composition(document, capability_payload)
    _ownership(document)
    executed, requested = _operations(document)
    return AdmittedLifecycleProfile(
        canonical_json_bytes(document), document["resource"]["state"],
        tuple(document["unresolved_resource_refs"]), executed, requested,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--schema-digest", required=True)
    parser.add_argument("--capabilities", type=Path)
    arguments = parser.parse_args()
    try:
        source = LifecycleSource(arguments.source_ref, arguments.source_revision, arguments.schema_digest)
        # Bound reads before parsing while leaving runtime file locations local.
        with arguments.profile.open("rb") as stream:
            payload = stream.read(MAX_INPUT_BYTES + 1)
        capability_payload = None
        if arguments.capabilities is not None:
            with arguments.capabilities.open("rb") as stream:
                capability_payload = stream.read(MAX_INPUT_BYTES + 1)
        admitted = admit_lifecycle_profile(payload, expected_source=source, capability_payload=capability_payload)
    except OSError:
        print("input_unavailable: select the retained input through its local owner.")
        return 1
    except LifecycleAdmissionError as error:
        print(str(error))
        return 1
    print(f"profile_admitted: state={admitted.resource_state}; unresolved={len(admitted.unresolved_resource_refs)}; recorded_operations={admitted.executed_operations}; requested_operations={admitted.requested_operations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

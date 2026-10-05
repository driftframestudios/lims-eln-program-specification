"""Explicit resource admission for UTF-8 administrative contract documents.

Existing model and loader APIs retain their v1 acceptance contract. This
opt-in API owns resource policy, safe boundary errors, and complete output;
it performs no filesystem, network, or publication operations.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Any

from pydantic import ValidationError

from .canonical import (
    ContractJsonError,
    DuplicateObjectKeyError,
    NonFiniteNumberError,
    strict_json_loads,
)
from .external_administrative import ExternalAdministrativeContractSet


_RECORD_FAMILIES = (
    "source_observations",
    "adapter_contracts",
    "population_scenarios",
    "administrative_contexts",
    "insurance_classifications",
    "coverage_enrollments",
    "policy_rule_sets",
    "administrative_decisions",
    "impact_observations",
    "provenance_assertions",
)
_MAX_PROFILE_INTEGER = (1 << 63) - 1
_MAX_JSON_DEPTH = 128


class AdministrativeAdmissionError(ValueError):
    """A bounded diagnostic with a fixed code and numeric resource information."""

    def __init__(
        self,
        code: str,
        *,
        limit: int | None = None,
        observed: int | None = None,
    ) -> None:
        self.code = code
        self.limit = limit
        self.observed = observed
        if limit is not None:
            message = (
                f"{code}: observed {observed}; selected maximum {limit}. "
                "Reduce the admitted batch or select a reviewed larger profile."
            )
        else:
            message = (
                f"{code}: provide a UTF-8 JSON document satisfying the "
                "administrative contract; inspect the retained input locally."
            )
        super().__init__(message)


@dataclass(frozen=True, slots=True, kw_only=True)
class AdministrativeAdmissionLimits:
    """Caller-owned finite budgets; no workload thresholds are inferred.

    JSON depth counts containers, with the root at one. The supported decoder
    envelope is 128 containers; graph depth is independent of JSON depth.
    Graph steps are a conservative structural bound, rather than CPU time.
    """

    max_input_bytes: int
    max_json_depth: int
    max_decoded_values: int
    max_records: int
    max_provenance_edges: int
    max_graph_steps: int
    max_output_bytes: int

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            minimum = 0 if field.name in {
                "max_provenance_edges", "max_graph_steps"
            } else 1
            if type(value) is not int or not minimum <= value <= _MAX_PROFILE_INTEGER:
                raise ValueError(
                    f"{field.name} uses an integer from {minimum} "
                    f"through {_MAX_PROFILE_INTEGER}"
                )
        if self.max_json_depth > _MAX_JSON_DEPTH:
            raise ValueError("max_json_depth selects at most 128 containers")


@dataclass(frozen=True, slots=True)
class AdministrativeAdmissionUsage:
    input_bytes: int
    json_depth: int
    decoded_values: int
    records: int
    provenance_vertices: int
    provenance_edges: int
    calibrated_scenarios: int
    graph_steps: int
    output_bytes: int


@dataclass(frozen=True, slots=True)
class AdmittedAdministrativeContract:
    contract: ExternalAdministrativeContractSet
    canonical_bytes: bytes
    usage: AdministrativeAdmissionUsage


def _within(code: str, observed: int, limit: int) -> None:
    if observed > limit:
        raise AdministrativeAdmissionError(code, limit=limit, observed=observed)


def _json_depth(text: str, limit: int) -> int:
    """O(B) lexical preflight, O(1) auxiliary space; JSON owns full syntax.

    UTF-8 decoding precedes this stage. Strings and escaped characters keep
    their delimiters literal. Excess depth is rejected before JSON decoding.
    """
    depth = 0
    maximum = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "{[":
            depth += 1
            maximum = max(maximum, depth)
            _within("json_depth", depth, limit)
        elif character in "}]":
            depth -= 1
            if depth < 0:
                raise AdministrativeAdmissionError("json_syntax")
    return maximum


def _decoded_values(value: Any, limit: int) -> int:
    """Count every container, scalar, and member name in O(N) time/O(D) space."""
    count = 0
    stack = [iter((value,))]
    while stack:
        try:
            item = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        count += 1
        _within("decoded_values", count, limit)
        if isinstance(item, dict):
            # Member names count as values without copying a flattened list.
            def members(mapping: dict):
                for key, child in mapping.items():
                    yield key
                    yield child
            stack.append(members(item))
        elif isinstance(item, list):
            stack.append(iter(item))
    return count


def _graph_envelope(document: Any, limits: AdministrativeAdmissionLimits) -> tuple[int, int, int, int, int]:
    """O(N) pre-model structure accounting; model validation owns shape/meaning."""
    if not isinstance(document, dict):
        raise AdministrativeAdmissionError("contract_root")
    records = sum(
        len(document[name])
        for name in _RECORD_FAMILIES
        if isinstance(document.get(name), list)
    )
    _within("records", records, limits.max_records)
    provenance = document.get("provenance_assertions", [])
    scenarios = document.get("population_scenarios", [])
    provenance = provenance if isinstance(provenance, list) else []
    scenarios = scenarios if isinstance(scenarios, list) else []
    edges = sum(
        len(item["derived_from_assertion_refs"])
        for item in provenance
        if isinstance(item, dict)
        and isinstance(item.get("derived_from_assertion_refs"), list)
    )
    _within("provenance_edges", edges, limits.max_provenance_edges)
    calibrated = 0
    roots = 0
    for scenario in scenarios:
        if isinstance(scenario, dict) and scenario.get("calibration_standing") != "not_calibrated":
            calibrated += 1
            references = scenario.get("calibration_evidence_refs")
            if isinstance(references, list):
                roots += len(references)
    steps = (calibrated + 1) * (len(provenance) + edges) + roots
    _within("graph_steps", steps, limits.max_graph_steps)
    return records, len(provenance), edges, calibrated, steps


def _canonical_output(contract: ExternalAdministrativeContractSet, limit: int) -> bytes:
    """O(output) encoding; accumulated bytes are bounded before each append.

    The model's JSON projection and a single encoder chunk have their own
    input-bounded allocations. The output budget bounds accumulated bytes,
    rather than claiming a process-memory or elapsed-time ceiling.
    """
    encoder = json.JSONEncoder(
        allow_nan=False, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    result = bytearray()
    for chunk in encoder.iterencode(contract.model_dump(mode="json", by_alias=True)):
        encoded = chunk.encode("utf-8")
        _within("output_bytes", len(result) + len(encoded), limit)
        result.extend(encoded)
    return bytes(result)


def admit_administrative_contract(
    payload: bytes,
    *,
    limits: AdministrativeAdmissionLimits,
) -> AdmittedAdministrativeContract:
    """Admit one complete contract and output, with no mutation or publication.

    Byte/depth limits precede decoding; decoded-value and graph envelopes
    precede model construction. Existing strict JSON checks and JSON-mode
    model semantics retain their separate passes. Rejection messages contain
    fixed boundary names and counts, while the caller retains the raw input.
    """
    if type(limits) is not AdministrativeAdmissionLimits:
        raise TypeError("limits uses AdministrativeAdmissionLimits")
    if type(payload) is not bytes:
        raise TypeError("payload uses immutable UTF-8 bytes")
    _within("input_bytes", len(payload), limits.max_input_bytes)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        raise AdministrativeAdmissionError("utf8") from None
    depth = _json_depth(text, limits.max_json_depth)
    try:
        document = strict_json_loads(text)
    except DuplicateObjectKeyError:
        raise AdministrativeAdmissionError("json_duplicate_key") from None
    except NonFiniteNumberError:
        raise AdministrativeAdmissionError("json_number") from None
    except RecursionError:
        raise AdministrativeAdmissionError("decoder_capacity") from None
    except (ValueError, ContractJsonError):
        raise AdministrativeAdmissionError("json_syntax") from None
    values = _decoded_values(document, limits.max_decoded_values)
    records, vertices, edges, calibrated, steps = _graph_envelope(document, limits)
    try:
        contract = ExternalAdministrativeContractSet.model_validate_json(text, strict=True)
    except ValidationError:
        raise AdministrativeAdmissionError("contract_validation") from None
    try:
        output = _canonical_output(contract, limits.max_output_bytes)
    except (UnicodeError, ValueError) as error:
        if isinstance(error, AdministrativeAdmissionError):
            raise
        raise AdministrativeAdmissionError("canonical_output") from None
    return AdmittedAdministrativeContract(
        contract=contract,
        canonical_bytes=output,
        usage=AdministrativeAdmissionUsage(
            input_bytes=len(payload),
            json_depth=depth,
            decoded_values=values,
            records=records,
            provenance_vertices=vertices,
            provenance_edges=edges,
            calibrated_scenarios=calibrated,
            graph_steps=steps,
            output_bytes=len(output),
        ),
    )


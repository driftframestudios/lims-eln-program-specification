"""Bounded synthetic study plans and observations, separate from expected outcomes.

Indexing and relationship checks are expected O(R + F) for runs and factor
assignments, plus canonical serialization of their bounded text. Pair comparison
is O(R + F + output text). All retained values are immutable owned records.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, Field, StringConstraints, ValidationError, model_validator

from .administrative_admission import (
    AdministrativeAdmissionError,
    _canonical_output,
    _decoded_values,
    _json_depth,
)
from .canonical import canonical_sha256, strict_json_loads
from .primitives import ContractModel, FieldName, Identifier, SemanticVersion, Sha256Digest, UtcTimestamp


STUDY_SCHEMA_ID = "urn:driftframe:lims-eln:administrative-study:1.0.0"
STUDY_SEMANTIC_INVARIANTS = (
    "run and observation identities are unique; every pair has arms a and b",
    "observations bind their declared run, study specification and input digests",
    "factors resolve exactly to the specification and retain explicit absence states",
    "completed runs contain both complete outputs; other statuses preserve their own fields",
    "expected output invariants remain separate from admission of actual outcomes",
)


def _content(value: str) -> str:
    if not value.strip():
        raise ValueError("text retains source characters and includes content")
    return value


Text = Annotated[str, StringConstraints(min_length=1, max_length=16384), AfterValidator(_content)]
ShortText = Annotated[str, StringConstraints(min_length=1, max_length=1024), AfterValidator(_content)]
Index = Annotated[int, Field(ge=0, le=1000000)]
Family = Literal["scientific", "administrative"]
RunStatus = Literal["pending", "completed", "abstained", "timeout", "cancelled", "invalid_response", "failed", "excluded"]


class StudyBinding(ContractModel):
    """Identity/version and digest of the source-owned artifact."""

    artifact_id: Identifier
    version: SemanticVersion
    digest: Sha256Digest


class SyntheticStudySource(ContractModel):
    """A provenance assertion; artifact review establishes its truth."""

    data_class: Literal["synthetic"]
    construction: Literal["authored_fixture", "synthetic_generator"]
    artifact: StudyBinding
    review_ref: Identifier
    purpose: ShortText


class StudyExecution(ContractModel):
    provider_id: Identifier
    model_id: Identifier
    adapter_version: SemanticVersion
    prompt_digest: Sha256Digest
    configuration_digest: Sha256Digest


class StudySpecification(ContractModel):
    study_id: Identifier
    version: SemanticVersion
    question: ShortText
    requested_return: ShortText
    primary_endpoint: ShortText
    scoring: StudyBinding
    source: SyntheticStudySource
    catalog: StudyBinding
    policy: StudyBinding
    expected_execution: StudyExecution
    factor_names: Annotated[tuple[FieldName, ...], Field(min_length=1, max_length=32)]
    controlled_factors: Annotated[tuple[FieldName, ...], Field(max_length=32)] = ()
    controlled_fields: Annotated[tuple[Literal["scientific_evidence", "subject_id", "episode_id"], ...], Field(max_length=3)] = ("scientific_evidence", "subject_id", "episode_id")
    expected_invariant_outputs: Annotated[tuple[Family, ...], Field(max_length=2)] = ("scientific",)
    stopping_rule: ShortText
    max_attempts_per_run: Annotated[int, Field(ge=1, le=8)] = 1

    @model_validator(mode="after")
    def distinct_dimensions(self) -> Self:
        for name in ("factor_names", "controlled_factors", "controlled_fields", "expected_invariant_outputs"):
            values = getattr(self, name)
            if len(set(values)) != len(values):
                raise ValueError("study dimensions use distinct names")
        if not set(self.controlled_factors) <= set(self.factor_names):
            raise ValueError("controlled factors resolve to declared factors")
        return self


class StudyFactor(ContractModel):
    name: FieldName
    standing: Literal["specified", "unknown", "omitted", "unmeasured", "withheld"]
    value: ShortText | None = None

    @model_validator(mode="after")
    def explicit_absence(self) -> Self:
        if (self.standing == "specified") != (self.value is not None):
            raise ValueError("specified factors carry a value; absence states carry null")
        return self


class StudyRunPlan(ContractModel):
    run_id: Identifier
    pair_id: Identifier
    arm: Literal["a", "b"]
    scenario_id: Identifier
    subject_id: Identifier
    episode_id: Identifier
    repeat_index: Index
    factors: Annotated[tuple[StudyFactor, ...], Field(min_length=1, max_length=32)]
    scientific_evidence: Text
    administrative_input: Text


class StudyOutput(ContractModel):
    text: Text
    digest: Sha256Digest
    completeness: Literal["complete", "partial"]

    @model_validator(mode="after")
    def bound_text(self) -> Self:
        if canonical_sha256(self.text) != self.digest:
            raise ValueError("output digest binds the source-exact text")
        return self


class StudyRunObservation(ContractModel):
    observation_id: Identifier
    run_id: Identifier
    attempt: Annotated[int, Field(ge=1, le=8)]
    specification_digest: Sha256Digest
    input_digest: Sha256Digest
    status: RunStatus
    execution: StudyExecution | None = None
    execution_order: Index | None = None
    started_at: UtcTimestamp | None = None
    finished_at: UtcTimestamp | None = None
    reason_code: Identifier | None = None
    scientific_output: StudyOutput | None = None
    administrative_output: StudyOutput | None = None

    @model_validator(mode="after")
    def status_fields(self) -> Self:
        runtime = (self.execution, self.execution_order, self.started_at, self.finished_at)
        outputs = (self.scientific_output, self.administrative_output)
        if self.status in {"pending", "excluded"} or (self.status == "cancelled" and self.started_at is None):
            if any(value is not None for value in (*runtime, *outputs)):
                raise ValueError("unexecuted statuses retain empty runtime and output fields")
        else:
            if any(value is None for value in runtime):
                raise ValueError("attempted runs carry execution identity, order and both times")
            if datetime.fromisoformat(self.started_at) > datetime.fromisoformat(self.finished_at):
                raise ValueError("run completion follows its start")
        if self.status == "completed":
            if any(value is None or value.completeness != "complete" for value in outputs):
                raise ValueError("completed runs carry both complete outputs")
        if self.status in {"completed", "pending"}:
            if self.reason_code is not None:
                raise ValueError("completed and pending statuses keep reason_code empty")
        elif self.reason_code is None:
            raise ValueError("held or unsuccessful runs carry a bounded reason code")
        return self


class ExpectedStudyPair(ContractModel):
    """An authored oracle; observed values remain independently admissible."""

    pair_id: Identifier
    scientific_changed: bool
    administrative_changed: bool
    rationale: ShortText


class AdministrativeStudy(ContractModel):
    schema_id: Literal[STUDY_SCHEMA_ID] = Field(alias="$schema")
    specification: StudySpecification
    runs: Annotated[tuple[StudyRunPlan, ...], Field(min_length=2, max_length=512)]
    observations: Annotated[tuple[StudyRunObservation, ...], Field(max_length=4096)] = ()
    expected_pairs: Annotated[tuple[ExpectedStudyPair, ...], Field(max_length=256)] = ()

    @model_validator(mode="after")
    def bound_relationships(self) -> Self:
        runs: dict[str, StudyRunPlan] = {}
        pairs: dict[str, dict[str, StudyRunPlan]] = {}
        factors = set(self.specification.factor_names)
        for run in self.runs:
            if run.run_id in runs:
                raise ValueError("run identities are unique")
            runs[run.run_id] = run
            names = tuple(factor.name for factor in run.factors)
            if len(set(names)) != len(names) or set(names) != factors:
                raise ValueError("run factors resolve exactly to the declared dimensions")
            pair = pairs.setdefault(run.pair_id, {})
            if run.arm in pair:
                raise ValueError("each pair has one planned run per arm")
            pair[run.arm] = run
        for pair in pairs.values():
            if set(pair) != {"a", "b"}:
                raise ValueError("every planned pair carries arms a and b")
            if pair["a"].repeat_index != pair["b"].repeat_index or pair["a"].scenario_id != pair["b"].scenario_id:
                raise ValueError("paired runs share scenario and repeat identity")
        observation_ids: set[str] = set()
        orders: set[int] = set()
        attempts: dict[str, list[StudyRunObservation]] = {}
        specification_digest = canonical_sha256(self.specification)
        input_digests = {key: canonical_sha256(run) for key, run in runs.items()}
        for observation in self.observations:
            if observation.observation_id in observation_ids:
                raise ValueError("observation identities are unique")
            observation_ids.add(observation.observation_id)
            if observation.run_id not in runs:
                raise ValueError("observation run references resolve")
            if observation.specification_digest != specification_digest or observation.input_digest != input_digests[observation.run_id]:
                raise ValueError("observation digests bind the declared specification and run")
            attempts.setdefault(observation.run_id, []).append(observation)
            if observation.execution_order is not None:
                if observation.execution_order in orders:
                    raise ValueError("execution order identities are unique")
                orders.add(observation.execution_order)
        for values in attempts.values():
            ordered = sorted(values, key=lambda value: value.attempt)
            if len(ordered) > self.specification.max_attempts_per_run or tuple(value.attempt for value in ordered) != tuple(range(1, len(ordered) + 1)):
                raise ValueError("attempts follow a bounded contiguous sequence")
            for prior, current in zip(ordered, ordered[1:]):
                if prior.status in {"pending", "completed", "abstained", "excluded"}:
                    raise ValueError("additional attempts follow retryable terminal failures")
            executed = tuple(value for value in ordered if value.execution_order is not None)
            for prior, current in zip(executed, executed[1:]):
                if datetime.fromisoformat(prior.finished_at) > datetime.fromisoformat(current.started_at):
                    raise ValueError("a retry starts after the preceding attempt finishes")
                if current.execution_order <= prior.execution_order:
                    raise ValueError("executed retry order increases with attempt identity")
        expected_ids: set[str] = set()
        for expected in self.expected_pairs:
            if expected.pair_id not in pairs or expected.pair_id in expected_ids:
                raise ValueError("expected pair references resolve uniquely")
            expected_ids.add(expected.pair_id)
        return self


class StudyPairComparison(ContractModel):
    pair_id: Identifier
    standing: Literal["comparable", "controlled_input_mismatch", "execution_mismatch", "incomplete"]
    reason_fields: tuple[ShortText, ...]
    scientific_changed: bool | None
    administrative_changed: bool | None
    expected_invariant_violations: tuple[Family, ...]
    oracle_agrees: bool | None

    @model_validator(mode="after")
    def findings_follow_comparability(self) -> Self:
        if len(set(self.reason_fields)) != len(self.reason_fields) or len(set(self.expected_invariant_violations)) != len(self.expected_invariant_violations):
            raise ValueError("comparison reasons and invariant findings are unique")
        if self.standing == "comparable":
            if self.reason_fields or self.scientific_changed is None or self.administrative_changed is None:
                raise ValueError("comparable pairs carry both output findings and an empty reason list")
            changes = {"scientific": self.scientific_changed, "administrative": self.administrative_changed}
            if any(not changes[family] for family in self.expected_invariant_violations):
                raise ValueError("invariant findings identify changed output families")
        elif not self.reason_fields or self.scientific_changed is not None or self.administrative_changed is not None or self.oracle_agrees is not None or self.expected_invariant_violations:
            raise ValueError("non-comparable pairs carry reasons while output findings remain unset")
        return self


class StudyComparisonReport(ContractModel):
    schema_id: Literal["urn:driftframe:lims-eln:administrative-study-comparison:1.0.0"] = Field(alias="$schema")
    study_digest: Sha256Digest
    planned: Annotated[int, Field(strict=True, ge=2, le=512)]
    attempted: Annotated[int, Field(strict=True, ge=0, le=512)]
    completed: Annotated[int, Field(strict=True, ge=0, le=512)]
    pending: Annotated[int, Field(strict=True, ge=0, le=512)]
    abstained: Annotated[int, Field(strict=True, ge=0, le=512)]
    failed: Annotated[int, Field(strict=True, ge=0, le=512)]
    cancelled: Annotated[int, Field(strict=True, ge=0, le=512)]
    excluded: Annotated[int, Field(strict=True, ge=0, le=512)]
    comparisons: Annotated[tuple[StudyPairComparison, ...], Field(min_length=1, max_length=256)]
    evidence_scope: Literal["synthetic_output_identity_comparison"] = "synthetic_output_identity_comparison"

    @model_validator(mode="after")
    def counts_partition_planned_runs(self) -> Self:
        if self.planned != self.completed + self.pending + self.abstained + self.failed + self.cancelled + self.excluded:
            raise ValueError("final status counts partition the planned runs")
        if not self.completed + self.abstained + self.failed <= self.attempted <= self.planned:
            raise ValueError("attempted counts include executed final states within the planned denominator")
        if self.planned != 2 * len(self.comparisons) or len({item.pair_id for item in self.comparisons}) != len(self.comparisons):
            raise ValueError("planned runs resolve to unique paired comparisons")
        complete_pairs = sum(item.standing in {"comparable", "execution_mismatch"} for item in self.comparisons)
        incomplete_pairs = sum(item.standing == "incomplete" for item in self.comparisons)
        if 2 * complete_pairs > self.completed:
            raise ValueError("completed-arm comparisons resolve within completed runs")
        if incomplete_pairs > self.planned - self.completed:
            raise ValueError("each incomplete pair includes a non-completed run")
        return self


def compare_administrative_study(study: AdministrativeStudy) -> StudyComparisonReport:
    """Derive final-attempt counts and paired byte-identity findings, not scores.

    All prior attempts remain in the study. A final failed retry remains a
    failure. Expected oracle disagreement is a reported observation.
    """
    latest: dict[str, StudyRunObservation] = {}
    attempted: set[str] = set()
    for observation in study.observations:
        prior = latest.get(observation.run_id)
        if prior is None or observation.attempt > prior.attempt:
            latest[observation.run_id] = observation
        if observation.started_at is not None:
            attempted.add(observation.run_id)
    counts = dict.fromkeys(("completed", "pending", "abstained", "failed", "cancelled", "excluded"), 0)
    pairs: dict[str, dict[str, StudyRunPlan]] = {}
    for run in study.runs:
        observation = latest.get(run.run_id)
        status = observation.status if observation else "pending"
        counts[status if status in counts else "failed"] += 1
        pairs.setdefault(run.pair_id, {})[run.arm] = run
    oracles = {expected.pair_id: expected for expected in study.expected_pairs}
    comparisons = []
    for pair_id, pair in pairs.items():
        a, b = pair["a"], pair["b"]
        changed = [name for name in study.specification.controlled_fields if getattr(a, name) != getattr(b, name)]
        af = {factor.name: factor for factor in a.factors}
        bf = {factor.name: factor for factor in b.factors}
        changed.extend("factor:" + name for name in study.specification.controlled_factors if af[name] != bf[name])
        oa, ob = latest.get(a.run_id), latest.get(b.run_id)
        standing = "comparable"
        reasons = tuple(changed)
        scientific = administrative = agrees = None
        violations: tuple[Family, ...] = ()
        if changed:
            standing = "controlled_input_mismatch"
        elif oa is None or ob is None or oa.status != "completed" or ob.status != "completed":
            standing, reasons = "incomplete", ("both completed arms required",)
        elif oa.execution != study.specification.expected_execution or ob.execution != study.specification.expected_execution:
            standing, reasons = "execution_mismatch", ("actual execution differs from the study specification",)
        else:
            scientific = oa.scientific_output.digest != ob.scientific_output.digest
            administrative = oa.administrative_output.digest != ob.administrative_output.digest
            differences = {"scientific": scientific, "administrative": administrative}
            violations = tuple(name for name in study.specification.expected_invariant_outputs if differences[name])
            oracle = oracles.get(pair_id)
            if oracle:
                agrees = (scientific, administrative) == (oracle.scientific_changed, oracle.administrative_changed)
        comparisons.append(StudyPairComparison(pair_id=pair_id, standing=standing, reason_fields=reasons, scientific_changed=scientific, administrative_changed=administrative, expected_invariant_violations=violations, oracle_agrees=agrees))
    return StudyComparisonReport(schema_id="urn:driftframe:lims-eln:administrative-study-comparison:1.0.0", study_digest=canonical_sha256(study), planned=len(study.runs), attempted=len(attempted), comparisons=tuple(comparisons), **counts)


def admit_administrative_study(payload: bytes, *, max_input_bytes: int = 2097152, max_output_bytes: int = 4194304) -> AdministrativeStudy:
    """Reuse the package's lexical/resource guards before strict model admission.

    Fixed depth/value and model cardinality bounds cover this offline profile.
    Byte limits cap accumulated input/output, not process memory or elapsed time.
    Diagnostics use fixed codes; the caller retains rejected input locally.
    """
    for value in (max_input_bytes, max_output_bytes):
        if type(value) is not int or not 1 <= value <= 33554432:
            raise ValueError("study byte budgets use integers from 1 through 33554432")
    if type(payload) is not bytes:
        raise TypeError("study payload uses immutable UTF-8 bytes")
    if len(payload) > max_input_bytes:
        raise AdministrativeAdmissionError("study_input_bytes", limit=max_input_bytes, observed=len(payload))
    try:
        text = payload.decode("utf-8")
        _json_depth(text, 32)
        document = strict_json_loads(text)
        _decoded_values(document, 100000)
        study = AdministrativeStudy.model_validate_json(text, strict=True)
        _canonical_output(study, max_output_bytes)
    except AdministrativeAdmissionError:
        raise
    except (ValueError, RecursionError, ValidationError):
        raise AdministrativeAdmissionError("study_validation") from None
    return study

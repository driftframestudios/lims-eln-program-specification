"""Derived eligibility for declared controls, separate from measured validity.

Projection indexes runs/attempts once: expected O(R + A + F + P log P), plus
bounded canonical serialization, with O(R + F + P) retained space. Sorting
pairs and controls provides stable interpretation under reordered source arrays;
the source digest continues to identify the exact admitted document.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .administrative_study import (
    AdministrativeStudy, ShortText, StudyComparisonReport, StudyFactor,
    compare_administrative_study,
)
from .canonical import canonical_sha256
from .primitives import ContractModel, FieldName, Identifier, SemanticVersion, Sha256Digest


INTERPRETATION_SCHEMA_ID = "urn:driftframe:lims-eln:study-interpretation:1.0.0"
Count = Annotated[int, Field(ge=0, le=512)]


class StudyAnalysisProfile(ContractModel):
    profile_id: Identifier = "declared-input-comparison"
    version: SemanticVersion = "1.0.0"
    required_specified_controls: Annotated[tuple[FieldName, ...], Field(max_length=32)] = ()
    require_expected_pair: bool = False

    @model_validator(mode="after")
    def unique_controls(self) -> Self:
        if len(set(self.required_specified_controls)) != len(self.required_specified_controls):
            raise ValueError("profile control identities are unique")
        return self


class ControlCoverage(ContractModel):
    a: StudyFactor
    b: StudyFactor

    @model_validator(mode="after")
    def same_dimension(self) -> Self:
        if self.a.name != self.b.name:
            raise ValueError("control arms name the same declared factor")
        return self


class PairEligibility(ContractModel):
    pair_id: Identifier
    controls: Annotated[tuple[ControlCoverage, ...], Field(max_length=32)]
    declared_input_equal: bool
    execution: Literal["matched", "mismatched", "unavailable"]
    usable_arms: Annotated[int, Field(ge=0, le=2)]
    expected_pair_available: bool
    reasons: Annotated[tuple[ShortText, ...], Field(max_length=36)]
    eligible: bool


def _reasons(pair: PairEligibility, profile: StudyAnalysisProfile) -> tuple[str, ...]:
    reasons = []
    if not pair.declared_input_equal:
        reasons.append("controlled_input_mismatch")
    if pair.execution != "matched":
        reasons.append("execution_" + pair.execution)
    if pair.usable_arms != 2:
        reasons.append("output_unavailable")
    required = set(profile.required_specified_controls)
    for control in pair.controls:
        if control.a.name in required and (control.a.standing != "specified" or control.b.standing != "specified"):
            reasons.append("required_control_unspecified:" + control.a.name)
    if profile.require_expected_pair and not pair.expected_pair_available:
        reasons.append("expected_pair_unavailable")
    return tuple(sorted(reasons))


class StudyInterpretation(ContractModel):
    schema_id: Literal[INTERPRETATION_SCHEMA_ID] = Field(alias="$schema")
    study_digest: Sha256Digest
    profile: StudyAnalysisProfile
    comparison: StudyComparisonReport
    pairs: Annotated[tuple[PairEligibility, ...], Field(min_length=1, max_length=256)]
    planned_pairs: Count
    eligible_pairs: Count
    excluded_pairs: Count
    expected_pairs_available: Count
    usable_runs: Count
    evidence_scope: Literal["declared_controls_and_recorded_execution"] = "declared_controls_and_recorded_execution"

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        originals = {item.pair_id: item for item in self.comparison.comparisons}
        if self.study_digest != self.comparison.study_digest:
            raise ValueError("interpretation and comparison bind the same study")
        ids = tuple(pair.pair_id for pair in self.pairs)
        if len(set(ids)) != len(ids) or set(ids) != set(originals):
            raise ValueError("interpretation covers every compared pair exactly once")
        for pair in self.pairs:
            names = tuple(control.a.name for control in pair.controls)
            if len(set(names)) != len(names) or not set(self.profile.required_specified_controls) <= set(names):
                raise ValueError("required controls resolve uniquely within each pair")
            if pair.declared_input_equal and any(control.a != control.b for control in pair.controls):
                raise ValueError("declared equality preserves control differences")
            original = originals[pair.pair_id]
            if pair.usable_arms == 2 and pair.execution == "unavailable":
                raise ValueError("completed arms carry execution identities")
            if original.standing == "comparable" and pair.expected_pair_available != (original.oracle_agrees is not None):
                raise ValueError("comparable oracle availability agrees with the comparison")
            expected_standing = (
                "controlled_input_mismatch" if not pair.declared_input_equal else
                "incomplete" if pair.usable_arms != 2 else
                "execution_mismatch" if pair.execution != "matched" else "comparable"
            )
            if original.standing != expected_standing:
                raise ValueError("eligibility preserves the accepted comparison standing")
            reasons = _reasons(pair, self.profile)
            if pair.reasons != reasons or pair.eligible != (not reasons):
                raise ValueError("eligibility and reasons follow the named profile")
        expected = (len(self.pairs), sum(p.eligible for p in self.pairs), sum(not p.eligible for p in self.pairs), sum(p.expected_pair_available for p in self.pairs), sum(p.usable_arms for p in self.pairs))
        if (self.planned_pairs, self.eligible_pairs, self.excluded_pairs, self.expected_pairs_available, self.usable_runs) != expected or self.usable_runs != self.comparison.completed:
            raise ValueError("interpretation counts reconcile to their pair and run denominators")
        return self


def interpret_administrative_study(study: AdministrativeStudy, profile: StudyAnalysisProfile | None = None) -> StudyInterpretation:
    """Project declared coverage; specified text itself supplies no measurement proof."""
    profile = profile if profile is not None else StudyAnalysisProfile()
    if not set(profile.required_specified_controls) <= set(study.specification.controlled_factors):
        raise ValueError("profile requirements resolve to declared controlled factors")
    latest = {}
    for observation in study.observations:
        previous = latest.get(observation.run_id)
        if previous is None or observation.attempt > previous.attempt:
            latest[observation.run_id] = observation
    plans = {}
    for run in study.runs:
        plans.setdefault(run.pair_id, {})[run.arm] = run
    expected = {item.pair_id for item in study.expected_pairs}
    result = []
    for pair_id in sorted(plans):
        a, b = plans[pair_id]["a"], plans[pair_id]["b"]
        af, bf = {f.name: f for f in a.factors}, {f.name: f for f in b.factors}
        controls = tuple(ControlCoverage(a=af[name], b=bf[name]) for name in sorted(study.specification.controlled_factors))
        observations = (latest.get(a.run_id), latest.get(b.run_id))
        execution = "matched"
        if any(o is None or o.execution is None for o in observations):
            execution = "unavailable"
        elif any(o.execution != study.specification.expected_execution for o in observations):
            execution = "mismatched"
        pair = PairEligibility(
            pair_id=pair_id, controls=controls,
            declared_input_equal=all(getattr(a, field) == getattr(b, field) for field in study.specification.controlled_fields) and all(c.a == c.b for c in controls),
            execution=execution, usable_arms=sum(o is not None and o.status == "completed" for o in observations),
            expected_pair_available=pair_id in expected, reasons=(), eligible=False,
        )
        reasons = _reasons(pair, profile)
        result.append(pair.model_copy(update={"reasons": reasons, "eligible": not reasons}))
    return StudyInterpretation(
        schema_id=INTERPRETATION_SCHEMA_ID, study_digest=canonical_sha256(study), profile=profile,
        comparison=compare_administrative_study(study), pairs=tuple(result), planned_pairs=len(result),
        eligible_pairs=sum(p.eligible for p in result), excluded_pairs=sum(not p.eligible for p in result),
        expected_pairs_available=sum(p.expected_pair_available for p in result), usable_runs=sum(p.usable_arms for p in result),
    )

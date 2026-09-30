"""Administrative-adapter and administrative-context contracts.

The objects in this module keep source formation, clinical evidence,
administrative interpretation, and accountable decisions independently
inspectable.  Open domain vocabularies travel as identified records; enums are
reserved for closed lifecycle and evidence states.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal
from pydantic import AfterValidator, Field, PositiveInt, StringConstraints, model_validator

from .canonical import canonical_sha256
from .primitives import (
    ContractModel,
    FieldName,
    Identifier,
    NonEmptyText,
    SemanticVersion,
    Sha256Digest,
    UtcTimestamp,
)


def _calendar_date_remains_valid(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("date names a valid ISO 8601 calendar day") from error
    return value


def _utc_instant(value: str) -> datetime:
    return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")


CalendarDate = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"),
    AfterValidator(_calendar_date_remains_valid),
]
RepositoryPath = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=512,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._/-]*$",
    ),
]
Confidence = Annotated[float, Field(strict=True, ge=0.0, le=1.0)]


class IdentifiedTerm(ContractModel):
    """One open vocabulary term whose identity does not depend on its label."""

    term_id: Identifier
    label: NonEmptyText
    vocabulary_id: Identifier
    vocabulary_version: NonEmptyText


class VersionedArtifactRef(ContractModel):
    artifact_id: Identifier
    version: NonEmptyText
    digest: Sha256Digest


class EffectiveInterval(ContractModel):
    starts_on: CalendarDate
    ends_on: CalendarDate | None = None

    @model_validator(mode="after")
    def interval_progresses_forward(self) -> "EffectiveInterval":
        if self.ends_on is not None and self.ends_on < self.starts_on:
            raise ValueError("effective interval ends on or after its start")
        return self


class ReviewDisposition(StrEnum):
    ACCEPT = "accept"
    REVISE = "revise"
    DECLINE = "decline"


class AccountableReview(ContractModel):
    review_id: Identifier
    reviewer_id: Identifier
    reviewer_role: IdentifiedTerm
    disposition: ReviewDisposition
    reviewed_at: UtcTimestamp
    evidence_refs: tuple[Identifier, ...] = Field(min_length=1)
    rationale: NonEmptyText

    @model_validator(mode="after")
    def evidence_refs_remain_unique(self) -> "AccountableReview":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("review evidence references remain unique")
        return self


class ReleaseScopedIdentifier(ContractModel):
    """A record locator whose meaning is bounded to one named release."""

    namespace_id: Identifier
    release_id: NonEmptyText
    record_type: IdentifiedTerm
    local_id: NonEmptyText
    source_observation_ref: Identifier | None = None


class SourceIntegrityStanding(StrEnum):
    REPORTED_DIGEST = "reported_digest"
    LOCALLY_COMPUTED_DIGEST = "locally_computed_digest"


class SourceObservationClaim(StrEnum):
    SOURCE_FIELD_PROVENANCE = "source_field_provenance"
    ADMINISTRATIVE_CONTEXT = "administrative_context"
    POPULATION_CALIBRATION = "population_calibration"


class SourceObservation(ContractModel):
    """Source-neutral integrity observation used only when a claim needs it."""

    observation_version: Literal["1.0.0"] = "1.0.0"
    observation_id: Identifier
    source_id: Identifier
    source_version: NonEmptyText
    observed_at: UtcTimestamp
    integrity_standing: SourceIntegrityStanding
    content_digest: Sha256Digest
    payload_observed: bool
    execution_observed: bool
    supported_claims: tuple[SourceObservationClaim, ...] = Field(min_length=1)
    claim_boundary: NonEmptyText

    @model_validator(mode="after")
    def integrity_evidence_remains_explicit(self) -> "SourceObservation":
        if len(self.supported_claims) != len(set(self.supported_claims)):
            raise ValueError("source observation supported claims remain unique")
        if (
            self.integrity_standing
            is SourceIntegrityStanding.LOCALLY_COMPUTED_DIGEST
            and not self.payload_observed
        ):
            raise ValueError(
                "a locally computed digest carries a payload observation"
            )
        if self.execution_observed and not self.payload_observed:
            raise ValueError("an execution observation carries a payload observation")
        return self


class AdapterFieldValue(ContractModel):
    field_name: FieldName
    value: NonEmptyText | bool | None


class AdapterInputRecord(ContractModel):
    record_id: Identifier
    input_version: NonEmptyText
    values: tuple[AdapterFieldValue, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def field_names_remain_unique(self) -> "AdapterInputRecord":
        field_names = [item.field_name for item in self.values]
        if len(field_names) != len(set(field_names)):
            raise ValueError("adapter input field names remain unique")
        return self


class AdapterStageKind(StrEnum):
    EXTRACT = "extract"
    VALIDATE = "validate"
    NORMALIZE = "normalize"
    CLASSIFY = "classify"
    MAP_CONTRACT = "map_contract"
    EMIT = "emit"


class AdapterStage(ContractModel):
    stage_id: Identifier
    sequence: PositiveInt
    kind: AdapterStageKind
    input_resource: Identifier
    output_resource: Identifier
    operation: NonEmptyText
    implementation_pattern: Literal["declarative_contract", "idempotent_script"]
    idempotent: Literal[True] = True


class AdapterIdempotencyContract(ContractModel):
    key_fields: tuple[FieldName, ...] = Field(min_length=1)
    duplicate_input_effect: Literal["same_output_no_additional_effect"] = (
        "same_output_no_additional_effect"
    )
    replay_scope: NonEmptyText
    checkpoint_strategy: NonEmptyText
    retry_behavior: NonEmptyText

    @model_validator(mode="after")
    def key_fields_remain_unique(self) -> "AdapterIdempotencyContract":
        if len(self.key_fields) != len(set(self.key_fields)):
            raise ValueError("adapter idempotency key fields remain unique")
        return self


AdapterOutputObject = Literal[
    "AdministrativeContext",
    "InsuranceClassification",
    "CoverageEnrollment",
]


class AdapterEnrichmentSource(StrEnum):
    RECEIVER_CONFIGURATION = "receiver_configuration"
    AUTHORIZED_RUNTIME_INPUT = "authorized_runtime_input"
    GOVERNED_VOCABULARY = "governed_vocabulary"
    ACCOUNTABLE_REVIEW = "accountable_review"


class AdapterEnrichmentRequirement(ContractModel):
    field_name: FieldName
    source: AdapterEnrichmentSource
    purpose: NonEmptyText


class AdministrativeAdapterContract(ContractModel):
    """Source-neutral, replay-safe design for an administrative data adapter."""

    adapter_contract_version: Literal["1.0.0"] = "1.0.0"
    adapter_id: Identifier
    name: NonEmptyText
    description: NonEmptyText
    data_standing: Literal["program_authored_synthetic"]
    execution_standing: Literal["design_only"] = "design_only"
    input_contract_id: Identifier
    representative_records: tuple[AdapterInputRecord, ...] = Field(min_length=1)
    stages: tuple[AdapterStage, ...] = Field(min_length=1)
    idempotency: AdapterIdempotencyContract
    output_bundle_id: Identifier
    output_object_names: tuple[AdapterOutputObject, ...] = Field(min_length=1)
    required_enrichments: tuple[AdapterEnrichmentRequirement, ...] = Field(
        min_length=1
    )
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)
    claim_boundary: NonEmptyText

    @model_validator(mode="after")
    def modular_replay_contract_remains_coherent(
        self,
    ) -> "AdministrativeAdapterContract":
        record_ids = [item.record_id for item in self.representative_records]
        stage_ids = [item.stage_id for item in self.stages]
        output_names = list(self.output_object_names)
        enrichment_names = [item.field_name for item in self.required_enrichments]
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("representative adapter record identifiers remain unique")
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("adapter stage identifiers remain unique")
        if len(output_names) != len(set(output_names)):
            raise ValueError("adapter output object names remain unique")
        if set(output_names) != {
            "AdministrativeContext",
            "InsuranceClassification",
            "CoverageEnrollment",
        }:
            raise ValueError(
                "adapter output names the context, classification, and enrollment objects"
            )
        if len(enrichment_names) != len(set(enrichment_names)):
            raise ValueError("adapter enrichment field names remain unique")
        expected_kinds = (
            AdapterStageKind.EXTRACT,
            AdapterStageKind.VALIDATE,
            AdapterStageKind.NORMALIZE,
            AdapterStageKind.CLASSIFY,
            AdapterStageKind.MAP_CONTRACT,
            AdapterStageKind.EMIT,
        )
        if tuple(item.kind for item in self.stages) != expected_kinds:
            raise ValueError(
                "adapter stages retain extract, validate, normalize, classify, "
                "contract-map, and emit order"
            )
        if tuple(item.sequence for item in self.stages) != tuple(
            range(1, len(self.stages) + 1)
        ):
            raise ValueError("adapter stage sequence remains contiguous from one")
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("adapter provenance references remain unique")
        if self.stages[0].input_resource != self.input_contract_id:
            raise ValueError(
                "the first adapter stage begins at the declared input contract"
            )
        if self.stages[-1].output_resource != self.output_bundle_id:
            raise ValueError(
                "the final adapter stage ends at the declared output bundle"
            )
        for previous, current in zip(self.stages, self.stages[1:]):
            if previous.output_resource != current.input_resource:
                raise ValueError("adjacent adapter stages share one resource boundary")
        if set(self.idempotency.key_fields) != {"record_id", "input_version"}:
            raise ValueError(
                "adapter replay identity uses record_id and input_version"
            )
        return self


class PopulationPurpose(StrEnum):
    WORKFLOW = "workflow"
    ACCESSIBILITY = "accessibility"
    POLICY_MECHANICS = "policy_mechanics"
    POPULATION_DISTRIBUTION = "population_distribution"


class PopulationCalibrationStanding(StrEnum):
    NOT_CALIBRATED = "not_calibrated"
    SOURCE_CALIBRATED = "source_calibrated"


class SmallCellHandling(StrEnum):
    SUPPRESS = "suppress"
    AGGREGATE = "aggregate"
    NOT_APPLICABLE = "not_applicable"


class SmallCellPolicy(ContractModel):
    handling: SmallCellHandling
    threshold: PositiveInt | None = None
    rationale: NonEmptyText

    @model_validator(mode="after")
    def threshold_matches_handling(self) -> "SmallCellPolicy":
        if self.handling is SmallCellHandling.NOT_APPLICABLE and self.threshold is not None:
            raise ValueError("not-applicable small-cell handling carries no threshold")
        if self.handling is not SmallCellHandling.NOT_APPLICABLE and self.threshold is None:
            raise ValueError("suppress or aggregate handling names its positive threshold")
        return self


class ReviewParticipant(ContractModel):
    participant_id: Identifier
    role: IdentifiedTerm
    contribution: NonEmptyText


class MethodKind(StrEnum):
    DETERMINISTIC_TRANSFORM = "deterministic_transform"
    ONTOLOGY_RESOLUTION = "ontology_resolution"
    LLM_PROPOSAL = "llm_proposal"
    HUMAN_CURATED = "human_curated"
    GENERATED_FIXTURE = "generated_fixture"


class MethodCoordinate(ContractModel):
    method_id: Identifier
    method_version: NonEmptyText
    kind: MethodKind
    code: VersionedArtifactRef | None = None
    prompt: VersionedArtifactRef | None = None
    model: VersionedArtifactRef | None = None

    @model_validator(mode="after")
    def implementation_coordinates_match_method(self) -> "MethodCoordinate":
        if self.kind in {
            MethodKind.DETERMINISTIC_TRANSFORM,
            MethodKind.ONTOLOGY_RESOLUTION,
        } and self.code is None:
            raise ValueError("deterministic and ontology methods name versioned code")
        if self.kind is MethodKind.LLM_PROPOSAL and (
            self.prompt is None or self.model is None
        ):
            raise ValueError("LLM proposals name prompt and model versions independently")
        return self


class PopulationScenario(ContractModel):
    scenario_version: Literal["1.0.0"] = "1.0.0"
    scenario_id: Identifier
    title: NonEmptyText
    purpose: PopulationPurpose
    construction_method: MethodCoordinate
    dimensions: tuple[IdentifiedTerm, ...] = Field(min_length=1)
    omissions: tuple[NonEmptyText, ...] = Field(min_length=1)
    review_participants: tuple[ReviewParticipant, ...] = Field(min_length=1)
    small_cell_policy: SmallCellPolicy
    calibration_standing: PopulationCalibrationStanding
    calibration_source_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    calibration_evidence_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    claim_boundary: NonEmptyText
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def scenario_members_remain_unique(self) -> "PopulationScenario":
        dimension_ids = [term.term_id for term in self.dimensions]
        participant_ids = [item.participant_id for item in self.review_participants]
        if len(dimension_ids) != len(set(dimension_ids)):
            raise ValueError("population scenario dimensions remain unique")
        if len(participant_ids) != len(set(participant_ids)):
            raise ValueError("population review participants remain unique")
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("population provenance references remain unique")
        if len(self.calibration_source_refs) != len(
            set(self.calibration_source_refs)
        ):
            raise ValueError("population calibration source references remain unique")
        if len(self.calibration_evidence_refs) != len(
            set(self.calibration_evidence_refs)
        ):
            raise ValueError("population calibration evidence references remain unique")
        if self.calibration_standing is PopulationCalibrationStanding.NOT_CALIBRATED:
            if self.calibration_source_refs or self.calibration_evidence_refs:
                raise ValueError(
                    "uncalibrated population scenarios leave calibration references empty"
                )
        elif not self.calibration_source_refs or not self.calibration_evidence_refs:
            raise ValueError(
                "source-calibrated population scenarios name source and evidence references"
            )
        return self


class AdministrativeSourceClass(StrEnum):
    OBSERVED_EXTERNAL_SOURCE = "observed_external_source"
    INDEPENDENTLY_AUTHORED_SYNTHETIC = "independently_authored_synthetic"
    AUTHORIZED_OPERATIONAL = "authorized_operational"


class DisclosureStanding(StrEnum):
    PUBLIC_SYNTHETIC = "public_synthetic"
    CONTROLLED_SYNTHETIC = "controlled_synthetic"
    AUTHORIZED_RESTRICTED = "authorized_restricted"


class ContextEvidenceStanding(StrEnum):
    SOURCE_REPORTED = "source_reported"
    ARTIFACT_VERIFIED = "artifact_verified"
    INDEPENDENTLY_AUTHORED = "independently_authored"
    OPERATIONALLY_OBSERVED = "operationally_observed"


class AdministrativeContext(ContractModel):
    context_version: Literal["1.0.0"] = "1.0.0"
    context_id: Identifier
    subject: ReleaseScopedIdentifier
    episode: ReleaseScopedIdentifier
    source_class: AdministrativeSourceClass
    effective_interval: EffectiveInterval
    jurisdiction: IdentifiedTerm
    population_scenario_ref: Identifier
    disclosure_standing: DisclosureStanding
    evidence_standing: ContextEvidenceStanding
    clinical_evidence_digest: Sha256Digest
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def source_scope_remains_explicit(self) -> "AdministrativeContext":
        if self.subject.namespace_id != self.episode.namespace_id:
            raise ValueError("subject and episode retain one release namespace")
        if self.subject.release_id != self.episode.release_id:
            raise ValueError("subject and episode retain one release identity")
        source_refs = {
            self.subject.source_observation_ref,
            self.episode.source_observation_ref,
        }
        if self.source_class is AdministrativeSourceClass.OBSERVED_EXTERNAL_SOURCE:
            if None in source_refs or len(source_refs) != 1:
                raise ValueError(
                    "an externally observed context retains one source observation"
                )
            if self.evidence_standing not in {
                ContextEvidenceStanding.SOURCE_REPORTED,
                ContextEvidenceStanding.ARTIFACT_VERIFIED,
            }:
                raise ValueError(
                    "an externally observed context retains source-reported or artifact-verified evidence"
                )
        elif any(reference is not None for reference in source_refs):
            raise ValueError(
                "local synthetic and operational contexts use their local release namespace"
            )
        elif (
            self.source_class
            is AdministrativeSourceClass.INDEPENDENTLY_AUTHORED_SYNTHETIC
            and self.evidence_standing
            is not ContextEvidenceStanding.INDEPENDENTLY_AUTHORED
        ):
            raise ValueError(
                "independently authored contexts retain independently authored evidence"
            )
        elif (
            self.source_class is AdministrativeSourceClass.AUTHORIZED_OPERATIONAL
            and self.evidence_standing
            is not ContextEvidenceStanding.OPERATIONALLY_OBSERVED
        ):
            raise ValueError(
                "authorized operational contexts retain operationally observed evidence"
            )
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("administrative-context provenance references remain unique")
        return self


class ClassificationState(StrEnum):
    CLASSIFIED = "classified"
    UNKNOWN = "unknown"
    AMBIGUOUS = "ambiguous"
    ABSTAINED = "abstained"


class ClassificationDisposition(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REVISED = "revised"
    DECLINED = "declined"


class InsuranceClassification(ContractModel):
    classification_version: Literal["1.0.0"] = "1.0.0"
    classification_id: Identifier
    context_ref: Identifier
    raw_label: NonEmptyText | None
    raw_label_field: NonEmptyText
    assigned_terms: tuple[IdentifiedTerm, ...] = Field(default_factory=tuple)
    candidate_terms: tuple[IdentifiedTerm, ...] = Field(default_factory=tuple)
    state: ClassificationState
    multiple: bool
    method: MethodCoordinate
    confidence: Confidence | None = None
    ambiguity: NonEmptyText | None = None
    disposition: ClassificationDisposition
    review: AccountableReview | None = None
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def raw_and_classified_states_remain_distinct(self) -> "InsuranceClassification":
        assigned_ids = [term.term_id for term in self.assigned_terms]
        candidate_ids = [term.term_id for term in self.candidate_terms]
        if len(assigned_ids) != len(set(assigned_ids)):
            raise ValueError("assigned insurance terms remain unique")
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidate insurance terms remain unique")
        if set(assigned_ids) & set(candidate_ids):
            raise ValueError("assigned and candidate insurance terms remain distinct")
        if self.raw_label is None and self.state is not ClassificationState.UNKNOWN:
            raise ValueError("only unknown classifications may omit the raw label")
        if self.state is ClassificationState.CLASSIFIED:
            if not self.assigned_terms or self.candidate_terms:
                raise ValueError("classified labels carry assigned terms only")
        elif self.state is ClassificationState.AMBIGUOUS:
            if self.assigned_terms or len(self.candidate_terms) < 2:
                raise ValueError("ambiguous labels carry at least two candidate terms")
        elif self.state is ClassificationState.UNKNOWN:
            if self.assigned_terms or self.candidate_terms:
                raise ValueError("unknown labels carry no assigned or candidate terms")
            if self.ambiguity is None:
                raise ValueError("unknown classifications explain the evidence boundary")
        elif self.assigned_terms:
            raise ValueError("abstained labels carry no assigned terms")
        if self.multiple != (len(self.assigned_terms) > 1):
            raise ValueError("multiple is true exactly when several terms are assigned")
        if self.state in {ClassificationState.AMBIGUOUS, ClassificationState.ABSTAINED}:
            if self.ambiguity is None:
                raise ValueError("ambiguous and abstained classifications explain the boundary")
        final_dispositions = {
            ClassificationDisposition.ACCEPTED: ReviewDisposition.ACCEPT,
            ClassificationDisposition.REVISED: ReviewDisposition.REVISE,
            ClassificationDisposition.DECLINED: ReviewDisposition.DECLINE,
        }
        if self.disposition is ClassificationDisposition.PROPOSED:
            if self.review is not None:
                raise ValueError("proposed classification awaits accountable review")
        else:
            expected = final_dispositions[self.disposition]
            if self.review is None or self.review.disposition is not expected:
                raise ValueError(
                    "final classification carries the matching accountable review"
                )
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("classification provenance references remain unique")
        return self


class EnrollmentBasis(StrEnum):
    DECLARED_ENROLLMENT = "declared_enrollment"
    SYNTHETIC_ELIGIBILITY = "synthetic_eligibility"


class EnrollmentState(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class EnrollmentStanding(StrEnum):
    SOURCE_REPORTED = "source_reported"
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    AUTHORIZED_RECORD = "authorized_record"


class CoverageEnrollment(ContractModel):
    enrollment_version: Literal["1.0.0"] = "1.0.0"
    enrollment_id: Identifier
    context_ref: Identifier
    basis: EnrollmentBasis
    state: EnrollmentState
    payer: IdentifiedTerm | None = None
    program: IdentifiedTerm | None = None
    plan: IdentifiedTerm | None = None
    member_relationship: IdentifiedTerm
    effective_interval: EffectiveInterval
    standing: EnrollmentStanding
    payer_decision_effect: Literal["none"] = "none"
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def enrollment_identity_remains_present(self) -> "CoverageEnrollment":
        if self.payer is None and self.program is None and self.plan is None:
            raise ValueError("coverage enrollment names a payer, program, or plan")
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("enrollment provenance references remain unique")
        return self


class PredicateOperator(StrEnum):
    EQUALS = "equals"
    CONTAINS_ANY = "contains_any"
    CONTAINS_ALL = "contains_all"
    PRESENT = "present"


class PolicyPredicate(ContractModel):
    input_id: FieldName
    operator: PredicateOperator
    values: tuple[NonEmptyText, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def values_match_operator(self) -> "PolicyPredicate":
        if self.operator is PredicateOperator.PRESENT and self.values:
            raise ValueError("present predicates carry no comparison values")
        if self.operator is not PredicateOperator.PRESENT and not self.values:
            raise ValueError("comparison predicates carry at least one value")
        if len(self.values) != len(set(self.values)):
            raise ValueError("predicate comparison values remain unique")
        return self


class PolicyInputRequirement(ContractModel):
    input_id: FieldName
    description: NonEmptyText
    required: bool


POLICY_INPUT_DIGEST_PROFILE = (
    "urn:driftframe:lims-eln:policy-input-digest:1.0.0"
)


class PolicyInputAvailability(StrEnum):
    PRESENT = "present"
    MISSING = "missing"


class PolicyInputSource(ContractModel):
    record_ref: Identifier
    record_version: SemanticVersion


class PolicyInputValue(ContractModel):
    source_ref: Identifier
    match_value: NonEmptyText
    vocabulary_id: Identifier | None = None
    vocabulary_version: NonEmptyText | None = None

    @model_validator(mode="after")
    def vocabulary_coordinate_remains_complete(self) -> "PolicyInputValue":
        if (self.vocabulary_id is None) != (self.vocabulary_version is None):
            raise ValueError(
                "policy input vocabulary identity and version remain paired"
            )
        return self


class NamedPolicyInput(ContractModel):
    input_id: FieldName
    availability: PolicyInputAvailability
    sources: tuple[PolicyInputSource, ...] = Field(default_factory=tuple)
    values: tuple[PolicyInputValue, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def availability_matches_sources(self) -> "NamedPolicyInput":
        source_ids = [source.record_ref for source in self.sources]
        value_keys = [
            (
                value.source_ref,
                value.vocabulary_id or "",
                value.vocabulary_version or "",
                value.match_value,
            )
            for value in self.values
        ]
        if source_ids != sorted(source_ids) or len(source_ids) != len(
            set(source_ids)
        ):
            raise ValueError("policy input sources remain unique and ordered")
        if value_keys != sorted(value_keys) or len(value_keys) != len(set(value_keys)):
            raise ValueError("policy input values remain unique and ordered")
        if any(value.source_ref not in set(source_ids) for value in self.values):
            raise ValueError("policy input values retain a named source record")
        if self.availability is PolicyInputAvailability.MISSING:
            if self.sources or self.values:
                raise ValueError("missing policy inputs carry no sources or values")
        elif not self.sources:
            raise ValueError("present policy inputs carry at least one source record")
        return self


class PolicyInputDigestMaterial(ContractModel):
    profile: Literal[
        "urn:driftframe:lims-eln:policy-input-digest:1.0.0"
    ] = POLICY_INPUT_DIGEST_PROFILE
    context_ref: Identifier
    inputs: tuple[NamedPolicyInput, ...] = Field(min_length=1)

    def calculated_digest(self) -> str:
        return canonical_sha256(self.model_dump(mode="json"))


class PolicyRule(ContractModel):
    rule_id: Identifier
    description: NonEmptyText
    when_all: tuple[PolicyPredicate, ...] = Field(min_length=1)
    outcome: IdentifiedTerm


class MissingInputBehavior(StrEnum):
    ABSTAIN = "abstain"
    REQUIRE_REVIEW = "require_review"


class ConflictBehavior(StrEnum):
    HIGHEST_PRECEDENCE = "highest_precedence"
    ABSTAIN = "abstain"
    REQUIRE_REVIEW = "require_review"


class PolicyRuleSet(ContractModel):
    policy_schema_version: Literal["1.0.0"] = "1.0.0"
    policy_id: Identifier
    policy_version: SemanticVersion
    owner: IdentifiedTerm
    jurisdiction: IdentifiedTerm
    product: IdentifiedTerm
    effective_interval: EffectiveInterval
    input_requirements: tuple[PolicyInputRequirement, ...] = Field(min_length=1)
    rules: tuple[PolicyRule, ...] = Field(min_length=1)
    precedence: tuple[Identifier, ...] = Field(min_length=1)
    missing_input_behavior: MissingInputBehavior
    conflict_behavior: ConflictBehavior
    policy_digest: Sha256Digest
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)

    def calculated_digest(self) -> str:
        return canonical_sha256(
            self.model_dump(mode="json", exclude={"policy_digest"})
        )

    @model_validator(mode="after")
    def policy_is_complete_and_digest_bound(self) -> "PolicyRuleSet":
        input_ids = [item.input_id for item in self.input_requirements]
        rule_ids = [item.rule_id for item in self.rules]
        if len(input_ids) != len(set(input_ids)):
            raise ValueError("policy input identifiers remain unique")
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("policy rule identifiers remain unique")
        if len(self.precedence) != len(set(self.precedence)):
            raise ValueError("policy precedence references remain unique")
        if set(self.precedence) != set(rule_ids):
            raise ValueError("policy precedence orders every declared rule exactly once")
        known_inputs = set(input_ids)
        for rule in self.rules:
            for predicate in rule.when_all:
                if predicate.input_id not in known_inputs:
                    raise ValueError(
                        f"policy rule {rule.rule_id!r} uses a declared input requirement"
                    )
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("policy provenance references remain unique")
        if self.policy_digest != self.calculated_digest():
            raise ValueError("policy_digest binds the complete declared rule set")
        return self


class PolicyEvaluationState(StrEnum):
    ASSIGNED = "assigned"
    ABSTAINED = "abstained"
    REVIEW_REQUIRED = "review_required"


class PolicyEvaluation(ContractModel):
    evaluation_id: Identifier
    policy_rule_set_ref: Identifier
    policy_digest: Sha256Digest
    input_digest_profile: Literal[
        "urn:driftframe:lims-eln:policy-input-digest:1.0.0"
    ]
    input_material: PolicyInputDigestMaterial
    input_digest: Sha256Digest
    matched_rule_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    selected_rule_ref: Identifier | None = None
    missing_input_ids: tuple[FieldName, ...] = Field(default_factory=tuple)
    conflicting_rule_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    state: PolicyEvaluationState
    outcome: IdentifiedTerm | None = None
    evaluated_at: UtcTimestamp

    @model_validator(mode="after")
    def evaluation_state_remains_explicit(self) -> "PolicyEvaluation":
        for values, label in (
            (self.matched_rule_refs, "matched policy rule references"),
            (self.missing_input_ids, "missing policy inputs"),
            (self.conflicting_rule_refs, "conflicting policy rule references"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} remain unique")
        if not set(self.conflicting_rule_refs).issubset(self.matched_rule_refs):
            raise ValueError("conflicting rules remain a subset of matched rules")
        if self.conflicting_rule_refs and len(self.conflicting_rule_refs) < 2:
            raise ValueError("a policy conflict names at least two matched rules")
        if self.state is PolicyEvaluationState.ASSIGNED:
            if self.outcome is None or self.selected_rule_ref is None:
                raise ValueError("assigned policy evaluations name an outcome and rule")
            if self.selected_rule_ref not in self.matched_rule_refs:
                raise ValueError("selected policy rule remains among the matched rules")
        elif self.outcome is not None or self.selected_rule_ref is not None:
            raise ValueError(
                "abstained and review-required evaluations leave assignment unset"
            )
        return self


class DecisionState(StrEnum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    FINAL = "final"


class DecisionEffect(StrEnum):
    ADVISORY_ONLY = "advisory_only"
    SYNTHETIC_ONLY = "synthetic_only"
    AUTHORIZED_ADMINISTRATIVE = "authorized_administrative"


class DecisionActorClass(StrEnum):
    HUMAN = "human"
    DETERMINISTIC_ENGINE = "deterministic_engine"
    AI_PROPOSAL = "ai_proposal"
    RELEASED_WORKFLOW = "released_workflow"


class DecisionActor(ContractModel):
    actor_id: Identifier
    actor_class: DecisionActorClass
    authority_scope: IdentifiedTerm


class DecisionTransition(ContractModel):
    from_state: DecisionState
    to_state: DecisionState
    transitioned_at: UtcTimestamp
    actor_id: Identifier

    @model_validator(mode="after")
    def transition_follows_released_state_machine(self) -> "DecisionTransition":
        allowed = {
            (DecisionState.DRAFT, DecisionState.PROPOSED),
            (DecisionState.PROPOSED, DecisionState.UNDER_REVIEW),
            (DecisionState.UNDER_REVIEW, DecisionState.FINAL),
        }
        if (self.from_state, self.to_state) not in allowed:
            raise ValueError("decision transition follows draft, proposal, review, and final")
        return self


class RecourseRoute(ContractModel):
    route_id: Identifier
    owner_role: IdentifiedTerm
    instructions: NonEmptyText
    deadline: CalendarDate | None = None


class AdministrativeDecision(ContractModel):
    decision_version: Literal["1.0.0"] = "1.0.0"
    decision_id: Identifier
    context_ref: Identifier
    decision_type: IdentifiedTerm
    outcome: IdentifiedTerm
    reason_terms: tuple[IdentifiedTerm, ...] = Field(min_length=1)
    classification_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    enrollment_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    policy_evaluation: PolicyEvaluation
    actor: DecisionActor
    state: DecisionState
    transitions: tuple[DecisionTransition, ...] = Field(min_length=1)
    effect: DecisionEffect
    recourse: RecourseRoute
    review: AccountableReview | None = None
    evidence_refs: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def decision_history_and_review_remain_accountable(self) -> "AdministrativeDecision":
        if not self.classification_refs and not self.enrollment_refs:
            raise ValueError("administrative decision names classification or enrollment input")
        for values, label in (
            (self.classification_refs, "decision classification references"),
            (self.enrollment_refs, "decision enrollment references"),
            (self.evidence_refs, "decision evidence references"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} remain unique")
        if self.transitions[0].from_state is not DecisionState.DRAFT:
            raise ValueError("decision transition history begins at draft")
        for previous, following in zip(self.transitions, self.transitions[1:]):
            if previous.to_state is not following.from_state:
                raise ValueError("decision transitions form one contiguous state history")
            if _utc_instant(previous.transitioned_at) > _utc_instant(
                following.transitioned_at
            ):
                raise ValueError("decision transition timestamps progress monotonically")
        if self.transitions[-1].to_state is not self.state:
            raise ValueError("decision state equals the final recorded transition")
        if self.transitions[0].actor_id != self.actor.actor_id:
            raise ValueError(
                "decision proposal transition uses the declared decision actor"
            )
        if _utc_instant(self.policy_evaluation.evaluated_at) > _utc_instant(
            self.transitions[0].transitioned_at
        ):
            raise ValueError(
                "policy evaluation occurs no later than the decision proposal"
            )
        if self.state is DecisionState.FINAL:
            if self.review is None:
                raise ValueError("final administrative decision carries accountable review")
            if self.review.disposition not in {
                ReviewDisposition.ACCEPT,
                ReviewDisposition.REVISE,
            }:
                raise ValueError(
                    "final administrative decision carries an authorizing review disposition"
                )
            if self.review.reviewer_id == self.actor.actor_id:
                raise ValueError(
                    "final administrative decision keeps reviewer and decision actor distinct"
                )
            if any(
                transition.actor_id != self.review.reviewer_id
                for transition in self.transitions[1:]
            ):
                raise ValueError(
                    "review and final transitions use the accountable reviewer"
                )
            if _utc_instant(self.review.reviewed_at) > _utc_instant(
                self.transitions[-1].transitioned_at
            ):
                raise ValueError(
                    "accountable review occurs no later than decision finalization"
                )
            review_opened_at = next(
                transition.transitioned_at
                for transition in self.transitions
                if transition.to_state is DecisionState.UNDER_REVIEW
            )
            if _utc_instant(self.review.reviewed_at) < _utc_instant(
                review_opened_at
            ):
                raise ValueError(
                    "accountable review occurs after the decision enters review"
                )
        elif self.review is not None:
            raise ValueError("non-final administrative decision awaits accountable review")
        return self


class ImpactDesign(StrEnum):
    ADMINISTRATIVE_ONLY_COUNTERFACTUAL = "administrative_only_counterfactual"


class DivergenceClass(StrEnum):
    ADMINISTRATIVE_ONLY = "administrative_only"
    CLINICAL_AND_ADMINISTRATIVE = "clinical_and_administrative"
    NONE = "none"


class EvidenceCeiling(StrEnum):
    SYNTHETIC_MECHANISM_ONLY = "synthetic_mechanism_only"
    LOCALLY_REPRODUCED = "locally_reproduced"
    CONFIGURED_ENVIRONMENT = "configured_environment"


class NamedDigest(ContractModel):
    name: FieldName
    digest: Sha256Digest


class ChangedAdministrativeVariable(ContractModel):
    variable_id: FieldName
    baseline_digest: Sha256Digest
    counterfactual_digest: Sha256Digest

    @model_validator(mode="after")
    def variable_changes_between_arms(self) -> "ChangedAdministrativeVariable":
        if self.baseline_digest == self.counterfactual_digest:
            raise ValueError("changed administrative variable carries differing digests")
        return self


class DecisionImpactArm(ContractModel):
    arm_id: Identifier
    context_ref: Identifier
    decision_ref: Identifier
    clinical_evidence_digest: Sha256Digest
    clinical_output_digest: Sha256Digest
    administrative_input_digest_profile: Literal[
        "urn:driftframe:lims-eln:policy-input-digest:1.0.0"
    ]
    administrative_input_digest: Sha256Digest
    administrative_output_digest_profile: Literal[
        "urn:driftframe:lims-eln:administrative-decision-digest:1.0.0"
    ]
    administrative_output_digest: Sha256Digest


class DecisionImpactObservation(ContractModel):
    observation_version: Literal["1.0.0"] = "1.0.0"
    observation_id: Identifier
    design: ImpactDesign
    population_scenario_ref: Identifier
    task: VersionedArtifactRef
    controlled_inputs: tuple[NamedDigest, ...] = Field(min_length=1)
    changed_variable: ChangedAdministrativeVariable
    baseline: DecisionImpactArm
    counterfactual: DecisionImpactArm
    divergence_class: DivergenceClass
    evidence_ceiling: EvidenceCeiling
    interpretation: NonEmptyText
    provenance_refs: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def counterfactual_keeps_clinical_outputs_fixed(self) -> "DecisionImpactObservation":
        controlled_names = [item.name for item in self.controlled_inputs]
        if len(controlled_names) != len(set(controlled_names)):
            raise ValueError("controlled input names remain unique")
        if self.baseline.arm_id == self.counterfactual.arm_id:
            raise ValueError("counterfactual arms carry distinct identities")
        if self.design is ImpactDesign.ADMINISTRATIVE_ONLY_COUNTERFACTUAL:
            if self.baseline.context_ref == self.counterfactual.context_ref:
                raise ValueError(
                    "administrative-only counterfactual uses distinct contexts"
                )
            if self.baseline.decision_ref == self.counterfactual.decision_ref:
                raise ValueError(
                    "administrative-only counterfactual uses distinct decisions"
                )
            if (
                self.baseline.clinical_evidence_digest
                != self.counterfactual.clinical_evidence_digest
            ):
                raise ValueError(
                    "administrative-only counterfactual keeps clinical evidence unchanged"
                )
            if (
                self.baseline.clinical_output_digest
                != self.counterfactual.clinical_output_digest
            ):
                raise ValueError(
                    "administrative-only counterfactual keeps clinical output unchanged"
                )
            if (
                self.baseline.administrative_input_digest
                == self.counterfactual.administrative_input_digest
                or self.baseline.administrative_output_digest
                == self.counterfactual.administrative_output_digest
            ):
                raise ValueError(
                    "administrative-only counterfactual changes administrative digests"
                )
            if self.divergence_class is not DivergenceClass.ADMINISTRATIVE_ONLY:
                raise ValueError(
                    "administrative-only counterfactual reports administrative divergence"
                )
            if (
                self.changed_variable.baseline_digest
                != self.baseline.administrative_input_digest
                or self.changed_variable.counterfactual_digest
                != self.counterfactual.administrative_input_digest
            ):
                raise ValueError(
                    "changed variable digests equal the two administrative inputs"
                )
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("impact-observation provenance references remain unique")
        return self


class ProvenanceFormation(StrEnum):
    SOURCE_EXACT = "source_exact"
    DETERMINISTIC_TRANSFORM = "deterministic_transform"
    ONTOLOGY_RESOLVED = "ontology_resolved"
    LLM_EXTRACTED = "llm_extracted"
    LLM_LINKED = "llm_linked"
    GENERATED = "generated"
    HUMAN_CURATED = "human_curated"


class ProvenanceStanding(StrEnum):
    SOURCE_REPORTED = "source_reported"
    ARTIFACT_VERIFIED = "artifact_verified"
    CONSTELLATION_DERIVED = "constellation_derived"
    ACCOUNTABLY_REVIEWED = "accountably_reviewed"


class ProvenanceResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    UNRESOLVED_FLAGGED = "unresolved_flagged"


class SourceFieldCoordinate(ContractModel):
    source_observation_ref: Identifier
    record: ReleaseScopedIdentifier
    field_path: NonEmptyText

    @model_validator(mode="after")
    def record_uses_coordinate_observation(self) -> "SourceFieldCoordinate":
        if self.record.source_observation_ref != self.source_observation_ref:
            raise ValueError("source field record retains the source observation")
        return self


class ProvenanceAssertion(ContractModel):
    assertion_version: Literal["1.0.0"] = "1.0.0"
    assertion_id: Identifier
    subject_refs: tuple[Identifier, ...] = Field(min_length=1)
    formation: ProvenanceFormation
    standing: ProvenanceStanding
    resolution_status: ProvenanceResolutionStatus
    claim: NonEmptyText
    source_coordinate: SourceFieldCoordinate | None = None
    method: MethodCoordinate | None = None
    derived_from_assertion_refs: tuple[Identifier, ...] = Field(default_factory=tuple)
    evidence_digest: Sha256Digest
    review: AccountableReview | None = None

    @model_validator(mode="after")
    def formation_coordinates_remain_sufficient(self) -> "ProvenanceAssertion":
        if len(self.subject_refs) != len(set(self.subject_refs)):
            raise ValueError("provenance subjects remain unique")
        if len(self.derived_from_assertion_refs) != len(
            set(self.derived_from_assertion_refs)
        ):
            raise ValueError("provenance parent references remain unique")
        if self.assertion_id in self.derived_from_assertion_refs:
            raise ValueError("provenance assertion does not derive from itself")
        method_kind_by_formation = {
            ProvenanceFormation.DETERMINISTIC_TRANSFORM: MethodKind.DETERMINISTIC_TRANSFORM,
            ProvenanceFormation.ONTOLOGY_RESOLVED: MethodKind.ONTOLOGY_RESOLUTION,
            ProvenanceFormation.LLM_EXTRACTED: MethodKind.LLM_PROPOSAL,
            ProvenanceFormation.LLM_LINKED: MethodKind.LLM_PROPOSAL,
            ProvenanceFormation.GENERATED: MethodKind.GENERATED_FIXTURE,
            ProvenanceFormation.HUMAN_CURATED: MethodKind.HUMAN_CURATED,
        }
        if self.formation is ProvenanceFormation.SOURCE_EXACT:
            if self.source_coordinate is None or self.derived_from_assertion_refs:
                raise ValueError(
                    "source-exact provenance names a source field and no derived parents"
                )
            if self.method is not None:
                raise ValueError("source-exact provenance carries no local method")
        elif self.source_coordinate is not None:
            raise ValueError("derived provenance reaches source fields through parent assertions")
        else:
            expected_kind = method_kind_by_formation[self.formation]
            if self.method is None or self.method.kind is not expected_kind:
                raise ValueError(
                    "provenance formation carries its matching method kind"
                )
        transform_kinds = {
            ProvenanceFormation.DETERMINISTIC_TRANSFORM,
            ProvenanceFormation.ONTOLOGY_RESOLVED,
            ProvenanceFormation.LLM_EXTRACTED,
            ProvenanceFormation.LLM_LINKED,
        }
        if self.formation in transform_kinds:
            if self.method is None or not self.derived_from_assertion_refs:
                raise ValueError("derived provenance names its method and parent assertions")
        if self.formation is ProvenanceFormation.HUMAN_CURATED:
            if self.review is None:
                raise ValueError("human-curated provenance carries accountable review")
        if self.formation is ProvenanceFormation.SOURCE_EXACT:
            if self.standing not in {
                ProvenanceStanding.SOURCE_REPORTED,
                ProvenanceStanding.ARTIFACT_VERIFIED,
            }:
                raise ValueError(
                    "source-exact provenance retains source-reported or artifact-verified standing"
                )
        elif self.standing in {
            ProvenanceStanding.SOURCE_REPORTED,
            ProvenanceStanding.ARTIFACT_VERIFIED,
        }:
            raise ValueError(
                "derived provenance retains constellation-derived or accountably-reviewed standing"
            )
        if self.standing is ProvenanceStanding.ACCOUNTABLY_REVIEWED:
            if self.review is None or self.review.disposition not in {
                ReviewDisposition.ACCEPT,
                ReviewDisposition.REVISE,
            }:
                raise ValueError(
                    "accountably reviewed provenance carries a non-declining review"
                )
            if self.resolution_status is not ProvenanceResolutionStatus.RESOLVED:
                raise ValueError(
                    "accountably reviewed provenance carries resolved status"
                )
        return self


PublicObjectName = Literal[
    "AdministrativeAdapterContract",
    "AdministrativeContext",
    "InsuranceClassification",
    "CoverageEnrollment",
    "PolicyRuleSet",
    "AdministrativeDecision",
    "DecisionImpactObservation",
    "PopulationScenario",
    "ProvenanceAssertion",
]


class PublicObjectDescriptor(ContractModel):
    object_name: PublicObjectName
    semantic_owner: Identifier
    receiving_job: NonEmptyText


class SchemaProjectionRef(ContractModel):
    schema_name: RepositoryPath
    schema_id: Identifier
    root_object: Literal[
        "AdministrativeAdapterContract",
        "ExternalAdministrativeContractSet",
    ]
    projection_mode: Literal["validation_input"] = "validation_input"
    dependency_closure: Literal["self_contained"] = "self_contained"


class ExampleResourceRef(ContractModel):
    example_id: Identifier
    path: RepositoryPath
    root_object: Literal[
        "AdministrativeAdapterContract",
        "ExternalAdministrativeContractSet",
        "DecisionImpactObservation",
    ]
    purpose: NonEmptyText


class CompatibilityContract(ContractModel):
    core_object_model: Literal["closed"] = "closed"
    open_vocabulary_behavior: Literal["identified_terms_preserved"] = (
        "identified_terms_preserved"
    )
    additive_rule: NonEmptyText
    changed_meaning_rule: NonEmptyText
    breaking_change_rule: NonEmptyText


class InvalidationTrigger(ContractModel):
    trigger_id: Identifier
    condition: NonEmptyText
    response: NonEmptyText


class AdoptionState(StrEnum):
    PENDING_REVIEWED_MERGE = "pending_reviewed_merge"
    RELEASED = "released"
    RETIRED = "retired"


class AdoptionEvent(ContractModel):
    event_id: Identifier
    state: AdoptionState
    requirement: NonEmptyText
    receiving_repositories: tuple[Identifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def receivers_remain_unique(self) -> "AdoptionEvent":
        if len(self.receiving_repositories) != len(set(self.receiving_repositories)):
            raise ValueError("adoption-event receivers remain unique")
        return self


def build_policy_input_digest_material(
    decision: AdministrativeDecision,
    policy: PolicyRuleSet,
    classifications: dict[str, InsuranceClassification],
    enrollments: dict[str, CoverageEnrollment],
) -> PolicyInputDigestMaterial:
    selected_classifications = sorted(
        (classifications[reference] for reference in decision.classification_refs),
        key=lambda item: item.classification_id,
    )
    selected_enrollments = sorted(
        (enrollments[reference] for reference in decision.enrollment_refs),
        key=lambda item: item.enrollment_id,
    )
    if any(
        item.disposition
        not in {
            ClassificationDisposition.ACCEPTED,
            ClassificationDisposition.REVISED,
        }
        for item in selected_classifications
    ):
        raise ValueError(
            "policy inputs use accepted or reviewed-revised classifications"
        )

    def sources_for(
        items: list[object], id_name: str, version_name: str
    ) -> tuple[PolicyInputSource, ...]:
        return tuple(
            PolicyInputSource(
                record_ref=getattr(item, id_name),
                record_version=getattr(item, version_name),
            )
            for item in items
        )

    classification_sources = sources_for(
        selected_classifications,
        "classification_id",
        "classification_version",
    )
    enrollment_sources = sources_for(
        selected_enrollments,
        "enrollment_id",
        "enrollment_version",
    )

    inputs: list[NamedPolicyInput] = []
    for requirement in policy.input_requirements:
        if requirement.input_id == "classification_state":
            sources = classification_sources
            values = tuple(
                PolicyInputValue(
                    source_ref=item.classification_id,
                    match_value=item.state.value,
                )
                for item in selected_classifications
            )
        elif requirement.input_id == "classification_term_ids":
            sources = classification_sources
            values = tuple(
                sorted(
                    (
                        PolicyInputValue(
                            source_ref=item.classification_id,
                            match_value=term.term_id,
                            vocabulary_id=term.vocabulary_id,
                            vocabulary_version=term.vocabulary_version,
                        )
                        for item in selected_classifications
                        for term in item.assigned_terms
                    ),
                    key=lambda value: (
                        value.source_ref,
                        value.vocabulary_id or "",
                        value.vocabulary_version or "",
                        value.match_value,
                    ),
                )
            )
        elif requirement.input_id == "enrollment_state":
            sources = enrollment_sources
            values = tuple(
                PolicyInputValue(
                    source_ref=item.enrollment_id,
                    match_value=item.state.value,
                )
                for item in selected_enrollments
            )
        else:
            raise ValueError(
                "policy input digest profile does not define input "
                f"{requirement.input_id!r}"
            )
        inputs.append(
            NamedPolicyInput(
                input_id=requirement.input_id,
                availability=(
                    PolicyInputAvailability.PRESENT
                    if sources
                    else PolicyInputAvailability.MISSING
                ),
                sources=sources,
                values=values,
            )
        )
    return PolicyInputDigestMaterial(
        context_ref=decision.context_ref,
        inputs=tuple(inputs),
    )


def _policy_predicate_matches(
    predicate: PolicyPredicate,
    material_by_input: dict[str, NamedPolicyInput],
) -> bool:
    material = material_by_input[predicate.input_id]
    if material.availability is PolicyInputAvailability.MISSING:
        return False
    observed = {value.match_value for value in material.values}
    expected = set(predicate.values)
    if predicate.operator is PredicateOperator.EQUALS:
        return observed == expected
    if predicate.operator is PredicateOperator.CONTAINS_ANY:
        return bool(observed & expected)
    if predicate.operator is PredicateOperator.CONTAINS_ALL:
        return expected.issubset(observed)
    return predicate.operator is PredicateOperator.PRESENT


class ExternalAdministrativeContractSet(ContractModel):
    """Dependency-closed v1 validation bundle for the administrative family."""

    contract_set_version: Literal["1.0.0"] = "1.0.0"
    contract_set_id: Identifier
    public_objects: tuple[PublicObjectDescriptor, ...] = Field(min_length=9)
    schema_roots: tuple[SchemaProjectionRef, ...] = Field(min_length=2)
    examples: tuple[ExampleResourceRef, ...] = Field(min_length=3)
    compatibility: CompatibilityContract
    invalidation_triggers: tuple[InvalidationTrigger, ...] = Field(min_length=1)
    adoption_event: AdoptionEvent
    source_observations: tuple[SourceObservation, ...] = Field(default_factory=tuple)
    adapter_contracts: tuple[AdministrativeAdapterContract, ...] = Field(min_length=1)
    population_scenarios: tuple[PopulationScenario, ...] = Field(min_length=1)
    administrative_contexts: tuple[AdministrativeContext, ...] = Field(min_length=1)
    insurance_classifications: tuple[InsuranceClassification, ...] = Field(min_length=1)
    coverage_enrollments: tuple[CoverageEnrollment, ...] = Field(min_length=1)
    policy_rule_sets: tuple[PolicyRuleSet, ...] = Field(min_length=1)
    administrative_decisions: tuple[AdministrativeDecision, ...] = Field(min_length=1)
    impact_observations: tuple[DecisionImpactObservation, ...] = Field(min_length=1)
    provenance_assertions: tuple[ProvenanceAssertion, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def references_form_one_acyclic_contract_graph(
        self,
    ) -> "ExternalAdministrativeContractSet":
        object_names = [item.object_name for item in self.public_objects]
        expected_object_names = {
            "AdministrativeAdapterContract",
            "AdministrativeContext",
            "InsuranceClassification",
            "CoverageEnrollment",
            "PolicyRuleSet",
            "AdministrativeDecision",
            "DecisionImpactObservation",
            "PopulationScenario",
            "ProvenanceAssertion",
        }
        if len(object_names) != len(set(object_names)) or set(object_names) != (
            expected_object_names
        ):
            raise ValueError("public object index names all nine contracts exactly once")
        schema_names = [item.schema_name for item in self.schema_roots]
        schema_ids = [item.schema_id for item in self.schema_roots]
        if len(schema_names) != len(set(schema_names)) or len(schema_ids) != len(
            set(schema_ids)
        ):
            raise ValueError("schema-root names and identities remain unique")
        schema_index = {
            item.schema_name: (item.schema_id, item.root_object)
            for item in self.schema_roots
        }
        if schema_index != {
            "administrative-adapter-contract.v1.schema.json": (
                "urn:driftframe:lims-eln:administrative-adapter-contract:1.0.0",
                "AdministrativeAdapterContract",
            ),
            "external-administrative-contract-set.v1.schema.json": (
                "urn:driftframe:lims-eln:external-administrative-contract-set:1.0.0",
                "ExternalAdministrativeContractSet",
            ),
        }:
            raise ValueError(
                "schema-root index binds each released filename to its canonical "
                "identity and root object"
            )
        example_paths = [item.path for item in self.examples]
        example_ids = [item.example_id for item in self.examples]
        if len(example_paths) != len(set(example_paths)) or len(example_ids) != len(
            set(example_ids)
        ):
            raise ValueError("example resource paths and identities remain unique")
        example_index = {
            item.path: (item.example_id, item.root_object) for item in self.examples
        }
        if example_index != {
            "administrative/insurance-administrative-adapter.v1.json": (
                "EXAMPLE-INSURANCE-ADMINISTRATIVE-ADAPTER",
                "AdministrativeAdapterContract",
            ),
            "administrative/independent-multilabel-policy.v1.json": (
                "EXAMPLE-INDEPENDENT-MULTILABEL-POLICY",
                "ExternalAdministrativeContractSet",
            ),
            "administrative/administrative-counterfactual.v1.json": (
                "EXAMPLE-ADMINISTRATIVE-COUNTERFACTUAL",
                "DecisionImpactObservation",
            ),
        }:
            raise ValueError(
                "example index binds each released path to its canonical identity "
                "and root object"
            )
        trigger_ids = [item.trigger_id for item in self.invalidation_triggers]
        if len(trigger_ids) != len(set(trigger_ids)):
            raise ValueError("invalidation-trigger identifiers remain unique")

        collections = {
            "source observation": {
                item.observation_id: item for item in self.source_observations
            },
            "adapter contract": {
                item.adapter_id: item for item in self.adapter_contracts
            },
            "population scenario": {
                item.scenario_id: item for item in self.population_scenarios
            },
            "administrative context": {
                item.context_id: item for item in self.administrative_contexts
            },
            "insurance classification": {
                item.classification_id: item
                for item in self.insurance_classifications
            },
            "coverage enrollment": {
                item.enrollment_id: item for item in self.coverage_enrollments
            },
            "policy rule set": {
                item.policy_id: item for item in self.policy_rule_sets
            },
            "administrative decision": {
                item.decision_id: item for item in self.administrative_decisions
            },
            "impact observation": {
                item.observation_id: item for item in self.impact_observations
            },
            "provenance assertion": {
                item.assertion_id: item for item in self.provenance_assertions
            },
        }
        for label, mapping in collections.items():
            expected = {
                "source observation": len(self.source_observations),
                "adapter contract": len(self.adapter_contracts),
                "population scenario": len(self.population_scenarios),
                "administrative context": len(self.administrative_contexts),
                "insurance classification": len(self.insurance_classifications),
                "coverage enrollment": len(self.coverage_enrollments),
                "policy rule set": len(self.policy_rule_sets),
                "administrative decision": len(self.administrative_decisions),
                "impact observation": len(self.impact_observations),
                "provenance assertion": len(self.provenance_assertions),
            }[label]
            if len(mapping) != expected:
                raise ValueError(f"{label} identifiers remain unique")

        all_ids: list[str] = []
        for mapping in collections.values():
            all_ids.extend(mapping)
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("contract record identifiers remain unique across the set")

        source_observations = collections["source observation"]
        scenarios = collections["population scenario"]
        contexts = collections["administrative context"]
        classifications = collections["insurance classification"]
        enrollments = collections["coverage enrollment"]
        policies = collections["policy rule set"]
        decisions = collections["administrative decision"]
        provenance = collections["provenance assertion"]

        def require(reference: str, mapping: dict[str, object], label: str) -> None:
            if reference not in mapping:
                raise ValueError(f"{label} reference {reference!r} resolves in the contract set")

        def require_provenance(references: tuple[str, ...], owner: str) -> None:
            for reference in references:
                require(reference, provenance, f"{owner} provenance")

        def require_subject_provenance(
            references: tuple[str, ...], subject_id: str
        ) -> None:
            require_provenance(references, subject_id)
            for reference in references:
                if subject_id not in provenance[reference].subject_refs:
                    raise ValueError(
                        "object provenance assertion names the referenced object "
                        "as a subject"
                    )

        for adapter in self.adapter_contracts:
            require_subject_provenance(adapter.provenance_refs, adapter.adapter_id)

        for scenario in self.population_scenarios:
            require_subject_provenance(
                scenario.provenance_refs, scenario.scenario_id
            )
            for reference in scenario.calibration_source_refs:
                require(reference, source_observations, "population calibration source")
                if (
                    SourceObservationClaim.POPULATION_CALIBRATION
                    not in source_observations[reference].supported_claims
                ):
                    raise ValueError(
                        "population calibration source observation supports the calibration claim"
                    )
            require_provenance(
                scenario.calibration_evidence_refs,
                f"{scenario.scenario_id} calibration evidence",
            )
            for reference in scenario.calibration_evidence_refs:
                if scenario.scenario_id not in provenance[reference].subject_refs:
                    raise ValueError(
                        "population calibration evidence names the population scenario as a subject"
                    )

        for context in self.administrative_contexts:
            require(context.population_scenario_ref, scenarios, "population scenario")
            require_subject_provenance(context.provenance_refs, context.context_id)
            for scoped in (context.subject, context.episode):
                if scoped.source_observation_ref is not None:
                    require(
                        scoped.source_observation_ref,
                        source_observations,
                        "context source observation",
                    )
                    observation = source_observations[scoped.source_observation_ref]
                    if (
                        SourceObservationClaim.ADMINISTRATIVE_CONTEXT
                        not in observation.supported_claims
                    ):
                        raise ValueError(
                            "context source observation supports an administrative-context claim"
                        )
                    if (
                        scoped.namespace_id != observation.source_id
                        or scoped.release_id != observation.source_version
                    ):
                        raise ValueError(
                            "external context records retain observed source identity and version"
                        )
                    if (
                        context.evidence_standing
                        is ContextEvidenceStanding.ARTIFACT_VERIFIED
                        and observation.integrity_standing
                        is not SourceIntegrityStanding.LOCALLY_COMPUTED_DIGEST
                    ):
                        raise ValueError(
                            "artifact-verified context requires a locally computed digest"
                        )

        for classification in self.insurance_classifications:
            require(classification.context_ref, contexts, "classification context")
            require_subject_provenance(
                classification.provenance_refs, classification.classification_id
            )
            if classification.review is not None:
                require_provenance(
                    classification.review.evidence_refs,
                    f"{classification.classification_id} review",
                )

        for enrollment in self.coverage_enrollments:
            require(enrollment.context_ref, contexts, "enrollment context")
            require_subject_provenance(
                enrollment.provenance_refs, enrollment.enrollment_id
            )

        for policy in self.policy_rule_sets:
            require_subject_provenance(policy.provenance_refs, policy.policy_id)

        for decision in self.administrative_decisions:
            require(decision.context_ref, contexts, "decision context")
            context = contexts[decision.context_ref]
            if decision.effect is DecisionEffect.AUTHORIZED_ADMINISTRATIVE and (
                context.source_class
                is not AdministrativeSourceClass.AUTHORIZED_OPERATIONAL
                or context.evidence_standing
                is not ContextEvidenceStanding.OPERATIONALLY_OBSERVED
            ):
                raise ValueError(
                    "authorized administrative effect requires an authorized "
                    "operational context with operationally observed evidence"
                )
            for reference in decision.classification_refs:
                require(reference, classifications, "decision classification")
                if classifications[reference].context_ref != decision.context_ref:
                    raise ValueError(
                        "decision and referenced classification retain one context"
                    )
            for reference in decision.enrollment_refs:
                require(reference, enrollments, "decision enrollment")
                if enrollments[reference].context_ref != decision.context_ref:
                    raise ValueError(
                        "decision and referenced enrollment retain one context"
                    )
            require(
                decision.policy_evaluation.policy_rule_set_ref,
                policies,
                "decision policy",
            )
            policy = policies[decision.policy_evaluation.policy_rule_set_ref]
            evaluation = decision.policy_evaluation
            if evaluation.policy_digest != policy.policy_digest:
                raise ValueError("policy evaluation retains the released policy digest")
            input_material = build_policy_input_digest_material(
                decision,
                policy,
                classifications,
                enrollments,
            )
            if evaluation.input_material != input_material:
                raise ValueError(
                    "policy evaluation material equals its cited normalized inputs"
                )
            if evaluation.input_digest != input_material.calculated_digest():
                raise ValueError(
                    "policy evaluation input digest binds its cited normalized inputs"
                )
            inputs_by_id = {
                item.input_id: item for item in input_material.inputs
            }
            expected_missing_inputs = tuple(
                requirement.input_id
                for requirement in policy.input_requirements
                if requirement.required
                and inputs_by_id[requirement.input_id].availability
                is PolicyInputAvailability.MISSING
            )
            if evaluation.missing_input_ids != expected_missing_inputs:
                raise ValueError(
                    "policy evaluation missing inputs equal absent required inputs"
                )
            rules_by_id = {rule.rule_id: rule for rule in policy.rules}
            rule_ids = set(rules_by_id)
            for reference in (
                *evaluation.matched_rule_refs,
                *evaluation.conflicting_rule_refs,
            ):
                if reference not in rule_ids:
                    raise ValueError("policy evaluation rule references resolve")
            expected_matches = tuple(
                rule.rule_id
                for rule in policy.rules
                if all(
                    _policy_predicate_matches(predicate, inputs_by_id)
                    for predicate in rule.when_all
                )
            )
            if evaluation.matched_rule_refs != expected_matches:
                raise ValueError(
                    "policy evaluation matched rules equal the declared predicates"
                )
            expected_conflicts = (
                expected_matches if len(expected_matches) > 1 else ()
            )
            if evaluation.conflicting_rule_refs != expected_conflicts:
                raise ValueError(
                    "policy evaluation conflicts equal overlapping matched rules"
                )
            evaluation_date = _utc_instant(evaluation.evaluated_at).date().isoformat()
            if evaluation_date < policy.effective_interval.starts_on or (
                policy.effective_interval.ends_on is not None
                and evaluation_date > policy.effective_interval.ends_on
            ):
                raise ValueError(
                    "policy evaluation occurs within the policy effective interval"
                )
            if expected_missing_inputs:
                expected_missing_state = {
                    MissingInputBehavior.ABSTAIN: PolicyEvaluationState.ABSTAINED,
                    MissingInputBehavior.REQUIRE_REVIEW: PolicyEvaluationState.REVIEW_REQUIRED,
                }[policy.missing_input_behavior]
                if evaluation.state is not expected_missing_state:
                    raise ValueError(
                        "policy evaluation applies the declared missing-input behavior"
                    )
            elif expected_conflicts:
                expected_conflict_state = {
                    ConflictBehavior.ABSTAIN: PolicyEvaluationState.ABSTAINED,
                    ConflictBehavior.REQUIRE_REVIEW: PolicyEvaluationState.REVIEW_REQUIRED,
                    ConflictBehavior.HIGHEST_PRECEDENCE: PolicyEvaluationState.ASSIGNED,
                }[policy.conflict_behavior]
                if evaluation.state is not expected_conflict_state:
                    raise ValueError(
                        "policy evaluation applies the declared conflict behavior"
                    )
                if policy.conflict_behavior is ConflictBehavior.HIGHEST_PRECEDENCE:
                    highest = min(
                        evaluation.conflicting_rule_refs,
                        key=policy.precedence.index,
                    )
                    if evaluation.selected_rule_ref != highest:
                        raise ValueError(
                            "policy conflict selects the highest-precedence matched rule"
                        )
            elif len(expected_matches) == 1:
                if (
                    evaluation.state is not PolicyEvaluationState.ASSIGNED
                    or evaluation.selected_rule_ref != expected_matches[0]
                ):
                    raise ValueError(
                        "single matching policy rule supplies the assigned evaluation"
                    )
            elif evaluation.state is not PolicyEvaluationState.ABSTAINED:
                raise ValueError(
                    "an evaluation without a matching rule retains abstained state"
                )
            if evaluation.selected_rule_ref is not None:
                selected_outcome = rules_by_id[evaluation.selected_rule_ref].outcome
                if evaluation.outcome != selected_outcome:
                    raise ValueError(
                        "policy evaluation outcome equals its selected rule outcome"
                    )
                review_revises_outcome = (
                    decision.review is not None
                    and decision.review.disposition is ReviewDisposition.REVISE
                )
                if review_revises_outcome and decision.outcome == evaluation.outcome:
                    raise ValueError(
                        "reviewed decision revision changes the policy evaluation proposal"
                    )
                if not review_revises_outcome and decision.outcome != evaluation.outcome:
                    raise ValueError(
                        "accepted administrative decision outcome equals its policy evaluation outcome"
                    )
            require_subject_provenance(decision.evidence_refs, decision.decision_id)
            if decision.review is not None:
                require_provenance(
                    decision.review.evidence_refs, f"{decision.decision_id} review"
                )

        for observation in self.impact_observations:
            require(
                observation.population_scenario_ref,
                scenarios,
                "impact population scenario",
            )
            require_subject_provenance(
                observation.provenance_refs, observation.observation_id
            )
            arm_contexts: list[AdministrativeContext] = []
            for arm in (observation.baseline, observation.counterfactual):
                require(arm.context_ref, contexts, "impact context")
                require(arm.decision_ref, decisions, "impact decision")
                context = contexts[arm.context_ref]
                decision = decisions[arm.decision_ref]
                arm_contexts.append(context)
                if decision.context_ref != arm.context_ref:
                    raise ValueError("impact arm decision retains the arm context")
                if context.population_scenario_ref != observation.population_scenario_ref:
                    raise ValueError("impact arm retains the observation population scenario")
                if context.clinical_evidence_digest != arm.clinical_evidence_digest:
                    raise ValueError(
                        "impact arm clinical evidence equals its context evidence"
                    )
                if (
                    arm.administrative_input_digest
                    != decision.policy_evaluation.input_digest
                ):
                    raise ValueError(
                        "impact arm administrative input equals its policy input digest"
                    )
                if arm.administrative_output_digest != canonical_sha256(decision):
                    raise ValueError(
                        "impact arm administrative output equals its canonical decision digest"
                    )
            if arm_contexts[0].subject != arm_contexts[1].subject:
                raise ValueError("counterfactual arms retain one release-scoped subject")
            if arm_contexts[0].episode != arm_contexts[1].episode:
                raise ValueError("counterfactual arms retain one release-scoped episode")

        public_subject_ids = set(all_ids)
        for assertion in self.provenance_assertions:
            for reference in assertion.subject_refs:
                if reference not in public_subject_ids:
                    raise ValueError("provenance subject references resolve")
            for reference in assertion.derived_from_assertion_refs:
                require(reference, provenance, "provenance parent")
            if assertion.source_coordinate is not None:
                source_ref = assertion.source_coordinate.source_observation_ref
                require(source_ref, source_observations, "provenance source observation")
                observation = source_observations[source_ref]
                if (
                    SourceObservationClaim.SOURCE_FIELD_PROVENANCE
                    not in observation.supported_claims
                ):
                    raise ValueError(
                        "provenance source observation supports a source-field claim"
                    )
                record = assertion.source_coordinate.record
                if (
                    record.namespace_id != observation.source_id
                    or record.release_id != observation.source_version
                ):
                    raise ValueError(
                        "provenance source record retains observed source identity and version"
                    )
                if (
                    assertion.standing is ProvenanceStanding.ARTIFACT_VERIFIED
                    and observation.integrity_standing
                    is not SourceIntegrityStanding.LOCALLY_COMPUTED_DIGEST
                ):
                    raise ValueError(
                        "artifact-verified provenance requires a locally computed digest"
                    )
            if assertion.review is not None:
                require_provenance(
                    assertion.review.evidence_refs,
                    f"{assertion.assertion_id} review",
                )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(assertion_id: str) -> None:
            if assertion_id in visiting:
                raise ValueError("provenance assertion graph remains acyclic")
            if assertion_id in visited:
                return
            visiting.add(assertion_id)
            assertion = provenance[assertion_id]
            for parent in assertion.derived_from_assertion_refs:
                visit(parent)
            visiting.remove(assertion_id)
            visited.add(assertion_id)

        for assertion_id in provenance:
            visit(assertion_id)

        source_lineage_cache: dict[str, frozenset[str]] = {}

        def source_lineage(assertion_id: str) -> frozenset[str]:
            if assertion_id in source_lineage_cache:
                return source_lineage_cache[assertion_id]
            assertion = provenance[assertion_id]
            observed_sources: set[str] = set()
            if assertion.source_coordinate is not None:
                observed_sources.add(
                    assertion.source_coordinate.source_observation_ref
                )
            for parent in assertion.derived_from_assertion_refs:
                observed_sources.update(source_lineage(parent))
            result = frozenset(observed_sources)
            source_lineage_cache[assertion_id] = result
            return result

        for scenario in self.population_scenarios:
            if (
                scenario.calibration_standing
                is PopulationCalibrationStanding.NOT_CALIBRATED
            ):
                continue
            evidence_sources: set[str] = set()
            for reference in scenario.calibration_evidence_refs:
                evidence_sources.update(source_lineage(reference))
            if evidence_sources != set(scenario.calibration_source_refs):
                raise ValueError(
                    "population calibration evidence traces exactly to its declared source observations"
                )
        return self


ADMINISTRATIVE_ADAPTER_CONTRACT_SCHEMA_ID = (
    "urn:driftframe:lims-eln:administrative-adapter-contract:1.0.0"
)
EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_SCHEMA_ID = (
    "urn:driftframe:lims-eln:external-administrative-contract-set:1.0.0"
)
ADMINISTRATIVE_ADAPTER_CONTRACT_SEMANTIC_INVARIANTS = (
    "representative records retain unique local identities and unique field names",
    "adapter stages form one contiguous extract, validate, normalize, classify, contract-map, and emit chain",
    "replay identity uses record_id and input_version; duplicate input converges without an additional effect",
)
EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_SEMANTIC_INVARIANTS = (
    "all contract record identifiers are unique and every cross-record reference resolves",
    "the administrative adapter remains source-neutral and binds only repository-owned representative records",
    "population calibration standing determines whether source and evidence references are absent or jointly present; calibration observations declare support and scenario-bound evidence traces exactly to them",
    "final classifications and final administrative decisions carry accountable, authorizing review",
    "decision proposal, review, and final transitions bind their declared actor identities; evaluation precedes proposal and review stays within its review interval",
    "policy evaluations occur during policy effectivity; a named profile binds cited normalized inputs, declared predicates derive match and conflict sets, selected-rule and evaluation outcomes agree, and only an authorizing revise review may change the final decision outcome",
    "provenance formation binds its method kind; source evidence standing binds its observation; resolution remains distinct and parent assertions form an acyclic graph",
    "administrative-only counterfactual arms use distinct contexts and decisions, bind named administrative input and output digest profiles to those records, retain equal clinical evidence and output digests, and differ in administrative input and output digests",
)


def external_administrative_schema_documents() -> dict[str, dict]:
    """Return the external projections from the single schema-artifact owner."""

    # The local import keeps model definition independent from artifact registration;
    # schema_artifacts owns document assembly and imports these models only after this
    # module has finished loading.
    from .schema_artifacts import SCHEMA_ARTIFACTS

    external_filenames = {
        "administrative-adapter-contract.v1.schema.json",
        "external-administrative-contract-set.v1.schema.json",
    }
    return {
        artifact.filename: artifact.document()
        for artifact in SCHEMA_ARTIFACTS
        if artifact.filename in external_filenames
    }

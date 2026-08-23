"""Evidence vocabulary shared by producers, comparators, and workbench views."""

from __future__ import annotations

from enum import StrEnum
import re

from pydantic import Field, model_validator

from .primitives import (
    ContractModel,
    Identifier,
    NonEmptyText,
    Sha256Digest,
)


class EvidenceMode(StrEnum):
    PLANNED = "planned"
    SIMULATED = "simulated"
    OBSERVED = "observed"


class AssuranceStage(StrEnum):
    SPECIFIED = "specified"
    VERIFIED = "verified"
    QUALIFIED = "qualified"
    VALIDATED = "validated"
    ACCEPTED = "accepted"

    def reaches(self, stage: "AssuranceStage") -> bool:
        sequence = tuple(AssuranceStage)
        return sequence.index(self) >= sequence.index(stage)


class ApprovalDomain(StrEnum):
    ENGINEERING = "engineering"
    OPERATIONS = "operations"
    QUALITY = "quality"
    REGULATORY = "regulatory"
    SCIENTIFIC = "scientific"
    SECURITY = "security"


class ApprovalDecision(StrEnum):
    ACCEPT = "accept"
    REVISE = "revise"
    ESCALATE = "escalate"


class ObservationDataClass(StrEnum):
    APPROVED_SYNTHETIC_EXEMPLAR = "approved-synthetic-exemplar"
    APPROVED_SYNTHETIC_QUALIFICATION = "approved-synthetic-qualification"
    REDACTED_CONFIDENTIAL_MANIFEST = "redacted-confidential-manifest"
    REDACTED_REGULATED_MANIFEST = "redacted-regulated-manifest"
    SYNTHETIC = "synthetic"


class RedactionStatus(StrEnum):
    GENERATED_IDENTITIES = "generated-identities"
    REVIEWED_REDACTED_MANIFEST = "reviewed-redacted-manifest"


class EvidenceSource(ContractModel):
    environment_id: Identifier = Field(
        description="Environment whose execution produced this observation."
    )
    implementation_commit: NonEmptyText = Field(
        description=(
            "Exact commit for observed evidence or released source coordinate for a simulation."
        )
    )
    configuration_digest: Sha256Digest


class EvidenceProvenance(ContractModel):
    raw_artifact_digest: Sha256Digest
    governed_locator: NonEmptyText = Field(
        description="Governed evidence reference; protected values stay in their approved store."
    )
    performed_by: Identifier
    reviewed_by: Identifier

    @model_validator(mode="after")
    def reviewer_identity_remains_independent(self) -> "EvidenceProvenance":
        if self.performed_by == self.reviewed_by:
            raise ValueError(
                "performed_by and reviewed_by require distinct identities; "
                "route the artifact to an independent reviewer"
            )
        if re.fullmatch(r"[a-z][a-z0-9+.-]*://[^?#]+", self.governed_locator) is None:
            raise ValueError(
                "governed_locator uses an absolute governed URI without query or fragment data"
            )
        return self


class ObservationApproval(ContractModel):
    domain: ApprovalDomain
    decision: ApprovalDecision
    approver: Identifier


class ObservationClassification(ContractModel):
    data_class: ObservationDataClass
    redaction_status: RedactionStatus

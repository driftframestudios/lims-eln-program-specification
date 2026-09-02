"""Shared observation envelope for actual and simulated evidence producers."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from .canonical import canonical_sha256
from .evidence import (
    AssuranceStage,
    EvidenceMode,
    EvidenceProvenance,
    EvidenceSource,
    ObservationApproval,
    ObservationClassification,
    RedactionStatus,
)
from .primitives import ContractModel, UpperIdentifier


class ObservationEnvelope(ContractModel):
    envelope_version: Literal["1.0.0"] = "1.0.0"
    observation_id: UpperIdentifier
    evidence_mode: EvidenceMode
    assurance_stage: AssuranceStage
    scenario_id: UpperIdentifier
    source: EvidenceSource
    result: dict[str, JsonValue]
    provenance: EvidenceProvenance
    approvals: tuple[ObservationApproval, ...] = Field(default_factory=tuple, max_length=24)
    classification: ObservationClassification

    @model_validator(mode="after")
    def evidence_posture_remains_inspectable(self) -> "ObservationEnvelope":
        if self.evidence_mode is EvidenceMode.OBSERVED:
            if re.fullmatch(
                r"(?:[a-f0-9]{40}|[a-f0-9]{64})",
                self.source.implementation_commit,
            ) is None:
                raise ValueError(
                    "observed evidence names an exact 40- or 64-character commit; "
                    "supply the commit that produced the artifact"
                )
            if re.fullmatch(
                r"(?:evidence-vault|s3)://[^/?#]+/[^?#%]+",
                self.provenance.governed_locator,
            ) is None:
                raise ValueError(
                    "observed evidence stays in evidence-vault or s3 storage; "
                    "supply its governed object locator"
                )
            if (
                self.classification.redaction_status
                is not RedactionStatus.REVIEWED_REDACTED_MANIFEST
            ):
                raise ValueError(
                    "observed evidence uses a reviewed-redacted manifest; "
                    "supply that approved projection while protected values stay in "
                    "governed storage"
                )
        if self.assurance_stage is AssuranceStage.ACCEPTED and not self.approvals:
            raise ValueError(
                "accepted evidence carries at least one accountable approval; "
                "record the domain decision that advances this stage"
            )
        return self

    def canonical_digest(self) -> str:
        return canonical_sha256(self)

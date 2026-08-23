"""Strict specimen commands for shared scenario and service boundaries."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, JsonValue, NonNegativeInt, model_validator

from .canonical import canonical_sha256
from .primitives import (
    ContractModel,
    Identifier,
    NonEmptyText,
    SemanticVersion,
    UtcTimestamp,
)


class SpecimenCommandAction(StrEnum):
    REGISTER = "register"
    ACCESSION = "accession"
    START_PROCESSING = "start_processing"
    SUBMIT_REVIEW = "submit_review"
    RELEASE = "release"
    CORRECT = "correct"
    VOID = "void"


class SpecimenCommand(ContractModel):
    schema_version: SemanticVersion = "1.0.0"
    command_id: Identifier
    tenant_id: Identifier
    specimen_id: Identifier
    actor_id: Identifier
    action: SpecimenCommandAction
    expected_version: NonNegativeInt
    occurred_at: UtcTimestamp
    payload: dict[str, JsonValue] = Field(default_factory=dict)
    reason_code: NonEmptyText | None = None

    @model_validator(mode="after")
    def command_carries_transition_evidence(self) -> "SpecimenCommand":
        if self.action is SpecimenCommandAction.REGISTER and self.expected_version != 0:
            raise ValueError("register begins at expected_version 0")
        if self.action in {SpecimenCommandAction.CORRECT, SpecimenCommandAction.VOID}:
            if self.reason_code is None:
                raise ValueError(
                    f"{self.action.value} carries a reason_code; "
                    "supply the attributable correction or void rationale"
                )
        return self

    def canonical_digest(self) -> str:
        return canonical_sha256(self)


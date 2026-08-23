"""Executable scenario boundary for the shared golden-specimen journey."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, JsonValue, PositiveInt, model_validator

from .primitives import (
    ContractModel,
    Identifier,
    NonEmptyText,
    SemanticVersion,
    UpperIdentifier,
    UtcTimestamp,
)
from .specimen import SpecimenCommand, SpecimenCommandAction


class FixtureClass(StrEnum):
    SYNTHETIC = "synthetic"


class InstrumentDisposition(StrEnum):
    ACCEPTED = "accepted"
    QUARANTINED = "quarantined"


class QualityFlag(StrEnum):
    PASS = "pass"
    REVIEW = "review"


class SpecimenFixture(ContractModel):
    tenant_id: Identifier
    specimen_id: Identifier
    specimen_type: NonEmptyText
    initial_location: NonEmptyText


class ScientificResult(ContractModel):
    analyte: NonEmptyText
    value: float
    unit: NonEmptyText
    quality_flag: QualityFlag


class InstrumentMessage(ContractModel):
    message_id: Identifier
    tenant_id: Identifier
    specimen_id: Identifier
    instrument_id: Identifier
    captured_at: UtcTimestamp
    media_type: Literal["application/json"]
    raw_document: dict[str, JsonValue]


class ExpectedSpecimenState(ContractModel):
    lifecycle_state: Literal["released"]
    aggregate_version: PositiveInt
    custody_location: NonEmptyText
    instrument_disposition: InstrumentDisposition
    result: ScientificResult
    outbox_topics: tuple[NonEmptyText, ...] = Field(min_length=1)


class RecoveryRoute(ContractModel):
    trigger: NonEmptyText
    replacement_state: NonEmptyText
    owner_role: Identifier


class ScenarioContract(ContractModel):
    scenario_version: SemanticVersion
    scenario_id: UpperIdentifier
    title: NonEmptyText
    source_scenario_ids: tuple[UpperIdentifier, ...] = Field(min_length=1)
    fixture_class: FixtureClass
    clock: UtcTimestamp
    specimen: SpecimenFixture
    commands: tuple[SpecimenCommand, ...] = Field(min_length=2)
    instrument_message: InstrumentMessage
    expected_state: ExpectedSpecimenState
    recovery_route: RecoveryRoute

    @model_validator(mode="after")
    def journey_remains_coherent(self) -> "ScenarioContract":
        if len(self.source_scenario_ids) != len(set(self.source_scenario_ids)):
            raise ValueError("source scenario identifiers remain unique")
        command_ids = [command.command_id for command in self.commands]
        if len(command_ids) != len(set(command_ids)):
            raise ValueError("scenario command identifiers remain unique")
        if self.commands[0].action is not SpecimenCommandAction.REGISTER:
            raise ValueError("the golden journey begins with register")
        if self.commands[-1].action is not SpecimenCommandAction.RELEASE:
            raise ValueError("the golden journey reaches release as its final lifecycle command")
        expected_versions = tuple(range(len(self.commands)))
        observed_versions = tuple(command.expected_version for command in self.commands)
        if observed_versions != expected_versions:
            raise ValueError(
                "scenario command versions form one contiguous sequence starting at zero"
            )
        if self.expected_state.aggregate_version != len(self.commands):
            raise ValueError("expected aggregate_version equals the completed command count")
        for command in self.commands:
            if (
                command.tenant_id != self.specimen.tenant_id
                or command.specimen_id != self.specimen.specimen_id
            ):
                raise ValueError(
                    "every scenario command retains the fixture tenant and specimen identity"
                )
        if (
            self.instrument_message.tenant_id != self.specimen.tenant_id
            or self.instrument_message.specimen_id != self.specimen.specimen_id
        ):
            raise ValueError(
                "instrument message retains the fixture tenant and specimen identity"
            )
        instants = [
            datetime.fromisoformat(command.occurred_at.removesuffix("Z") + "+00:00")
            for command in self.commands
        ]
        if instants != sorted(instants):
            raise ValueError("scenario command instants progress in chronological order")
        expected_result = self.expected_state.result.model_dump(mode="json")
        if self.instrument_message.raw_document.get("result") != expected_result:
            raise ValueError(
                "instrument result and expected scientific result remain identical"
            )
        if len(self.expected_state.outbox_topics) != len(
            set(self.expected_state.outbox_topics)
        ):
            raise ValueError("expected outbox topics remain unique")
        return self


"""Typed comparison projection for the shared Golden Specimen result."""

from __future__ import annotations

from datetime import datetime
from typing import Final, Literal

from pydantic import Field, JsonValue, PositiveInt, model_validator

from .canonical import canonical_sha256
from .observation import ObservationEnvelope
from .primitives import ContractModel, Identifier, NonEmptyText, UtcTimestamp
from .scenario import QualityFlag, ScientificResult


GOLDEN_SPECIMEN_SCENARIO_ID: Final = "SCN-GOLDEN-SPECIMEN-001"
GOLDEN_SPECIMEN_RESULT_PROJECTION_ID: Final = (
    "urn:driftframe:lims-eln:golden-specimen-result"
)
GOLDEN_SPECIMEN_RESULT_PROJECTION_VERSION: Final = "1.0.0"
GOLDEN_SPECIMEN_RESULT_COMPATIBILITY: Final = "exact-version"


class GoldenSpecimenLifecycleResult(ContractModel):
    state: Literal["released"]
    aggregate_version: PositiveInt


class GoldenSpecimenCustodyResult(ContractModel):
    current_location: NonEmptyText


class GoldenSpecimenMeasurementResult(ScientificResult):
    quality_flag: QualityFlag


class GoldenSpecimenReviewResolution(ContractModel):
    review_id: Identifier
    decision: Literal["accepted"]
    resolved_at: UtcTimestamp


class GoldenSpecimenReleaseResult(ContractModel):
    approval_receipt_id: Identifier
    released_at: UtcTimestamp


class GoldenSpecimenResultProjection(ContractModel):
    """Decision-relevant result shared by implementation and simulation."""

    projection_id: Literal["urn:driftframe:lims-eln:golden-specimen-result"]
    projection_version: Literal["1.0.0"]
    comparison_compatibility: Literal["exact-version"]
    tenant_id: Identifier
    specimen_id: Identifier
    lifecycle: GoldenSpecimenLifecycleResult
    custody: GoldenSpecimenCustodyResult
    measurement: GoldenSpecimenMeasurementResult
    review_resolution: GoldenSpecimenReviewResolution
    release: GoldenSpecimenReleaseResult

    @model_validator(mode="after")
    def review_precedes_release(self) -> "GoldenSpecimenResultProjection":
        review_instant = _utc_instant(self.review_resolution.resolved_at)
        release_instant = _utc_instant(self.release.released_at)
        if review_instant > release_instant:
            raise ValueError(
                "review resolution precedes release; supply the accepted review "
                "instant that authorized this release"
            )
        return self

    def canonical_digest(self) -> str:
        return canonical_sha256(self)


class GoldenSpecimenObservationResult(ContractModel):
    """Shared fields plus producer-owned detail retained outside comparison."""

    projection: GoldenSpecimenResultProjection
    producer_detail: dict[str, JsonValue] = Field(default_factory=dict)


class GoldenSpecimenObservation(ObservationEnvelope):
    """Observation envelope for the Golden Specimen comparison boundary."""

    scenario_id: Literal["SCN-GOLDEN-SPECIMEN-001"]
    result: GoldenSpecimenObservationResult


def _utc_instant(value: str) -> datetime:
    return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")

"""Deterministic JSON Schema artifacts for shared external boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import json

from pydantic import BaseModel

from .bounded_call import BoundedCallReceipt, BoundedCallRequest, OperationCatalog
from .external_administrative import (
    EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_SCHEMA_ID,
    EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_SEMANTIC_INVARIANTS,
    EXTERNAL_SOURCE_MANIFEST_SCHEMA_ID,
    EXTERNAL_SOURCE_MANIFEST_SEMANTIC_INVARIANTS,
    ExternalAdministrativeContractSet,
    ExternalSourceManifest,
)
from .golden_specimen import GoldenSpecimenResultProjection
from .observation import ObservationEnvelope
from .scenario import ScenarioContract
from .specimen import SpecimenCommand


@dataclass(frozen=True, slots=True)
class SchemaArtifact:
    filename: str
    schema_id: str
    model: type[BaseModel]
    semantic_invariants: tuple[str, ...] = ()

    def document(self) -> dict:
        generated = self.model.model_json_schema(by_alias=True, mode="validation")
        document = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": self.schema_id,
            **generated,
        }
        if self.semantic_invariants:
            document["x-semantic-invariants"] = list(self.semantic_invariants)
        return document

    def rendered_bytes(self) -> bytes:
        return (
            json.dumps(
                self.document(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")


SCHEMA_ARTIFACTS = (
    SchemaArtifact(
        "bounded-call-receipt.v1.schema.json",
        "urn:driftframe:lims-eln:bounded-call-receipt:1.0.0",
        BoundedCallReceipt,
    ),
    SchemaArtifact(
        "bounded-call-request.v1.schema.json",
        "urn:driftframe:lims-eln:bounded-call-request:1.0.0",
        BoundedCallRequest,
    ),
    SchemaArtifact(
        "external-administrative-contract-set.v1.schema.json",
        EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_SCHEMA_ID,
        ExternalAdministrativeContractSet,
        EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_SEMANTIC_INVARIANTS,
    ),
    SchemaArtifact(
        "external-source-manifest.v1.schema.json",
        EXTERNAL_SOURCE_MANIFEST_SCHEMA_ID,
        ExternalSourceManifest,
        EXTERNAL_SOURCE_MANIFEST_SEMANTIC_INVARIANTS,
    ),
    SchemaArtifact(
        "golden-specimen-result-projection.v1.schema.json",
        "urn:driftframe:lims-eln:golden-specimen-result:1.0.0",
        GoldenSpecimenResultProjection,
        (
            "review_resolution.resolved_at occurs at or before release.released_at",
        ),
    ),
    SchemaArtifact(
        "observation-envelope.v1.schema.json",
        "urn:driftframe:lims-eln:observation-envelope:1.0.0",
        ObservationEnvelope,
    ),
    SchemaArtifact(
        "operation-catalog.v1.schema.json",
        "urn:driftframe:lims-eln:operation-catalog:1.0.0",
        OperationCatalog,
    ),
    SchemaArtifact(
        "scenario.v1.schema.json",
        "urn:driftframe:lims-eln:scenario:1.0.0",
        ScenarioContract,
    ),
    SchemaArtifact(
        "specimen-command.v1.schema.json",
        "urn:driftframe:lims-eln:specimen-command:1.0.0",
        SpecimenCommand,
    ),
)


def rendered_schema_artifacts() -> dict[str, bytes]:
    return {artifact.filename: artifact.rendered_bytes() for artifact in SCHEMA_ARTIFACTS}

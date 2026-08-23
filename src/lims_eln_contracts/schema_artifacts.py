"""Deterministic JSON Schema artifacts for shared external boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import json

from pydantic import BaseModel

from .bounded_call import BoundedCallReceipt, BoundedCallRequest, OperationCatalog
from .observation import ObservationEnvelope
from .scenario import ScenarioContract
from .specimen import SpecimenCommand


@dataclass(frozen=True, slots=True)
class SchemaArtifact:
    filename: str
    schema_id: str
    model: type[BaseModel]

    def document(self) -> dict:
        generated = self.model.model_json_schema(by_alias=True, mode="validation")
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": self.schema_id,
            **generated,
        }

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


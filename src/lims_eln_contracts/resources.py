"""Released package resources and typed loaders for the contract nucleus."""

from __future__ import annotations

from importlib import resources
from typing import Final, Literal

from .bounded_call import OperationCatalog
from .canonical import model_from_strict_json, strict_json_loads
from .external_administrative import (
    DecisionImpactObservation,
    ExternalAdministrativeContractSet,
    ExternalSourceManifest,
)
from .golden_specimen import GoldenSpecimenObservation
from .scenario import ScenarioContract


OPERATION_CATALOG_RESOURCE: Final = "operations.v1.json"
GOLDEN_SCENARIO_RESOURCE: Final = "scenarios/golden-specimen.v1.json"
GOLDEN_OBSERVATION_EXAMPLE_RESOURCES: Final = {
    "implementation": "observations/golden-specimen.implementation.v1.json",
    "simulation": "observations/golden-specimen.simulation.v1.json",
}
EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_RESOURCE: Final = (
    "external-administrative-contracts.v1.json"
)
EXTERNAL_SOURCE_MANIFEST_EXAMPLE_RESOURCE: Final = (
    "administrative/synthetic-hospital-v1.3.v1.json"
)
INDEPENDENT_MULTILABEL_POLICY_EXAMPLE_RESOURCE: Final = (
    "administrative/independent-multilabel-policy.v1.json"
)
ADMINISTRATIVE_COUNTERFACTUAL_EXAMPLE_RESOURCE: Final = (
    "administrative/administrative-counterfactual.v1.json"
)
SCHEMA_RESOURCE_NAMES: Final = (
    "bounded-call-receipt.v1.schema.json",
    "bounded-call-request.v1.schema.json",
    "external-administrative-contract-set.v1.schema.json",
    "external-source-manifest.v1.schema.json",
    "golden-specimen-result-projection.v1.schema.json",
    "observation-envelope.v1.schema.json",
    "operation-catalog.v1.schema.json",
    "scenario.v1.schema.json",
    "specimen-command.v1.schema.json",
)


def _resource_bytes(relative_path: str) -> bytes:
    target = resources.files("lims_eln_contracts").joinpath("resources")
    for part in relative_path.split("/"):
        target = target.joinpath(part)
    return target.read_bytes()


def load_operation_catalog() -> OperationCatalog:
    return model_from_strict_json(
        OperationCatalog,
        _resource_bytes(OPERATION_CATALOG_RESOURCE),
    )


def load_golden_specimen_scenario() -> ScenarioContract:
    return model_from_strict_json(
        ScenarioContract,
        _resource_bytes(GOLDEN_SCENARIO_RESOURCE),
    )


def load_golden_specimen_observation_example(
    producer: Literal["implementation", "simulation"],
) -> GoldenSpecimenObservation:
    try:
        resource_name = GOLDEN_OBSERVATION_EXAMPLE_RESOURCES[producer]
    except KeyError as error:
        raise ValueError(
            "producer names one released example: implementation or simulation"
        ) from error
    return model_from_strict_json(
        GoldenSpecimenObservation,
        _resource_bytes(resource_name),
    )


def load_external_administrative_contract_set(
) -> ExternalAdministrativeContractSet:
    return model_from_strict_json(
        ExternalAdministrativeContractSet,
        _resource_bytes(EXTERNAL_ADMINISTRATIVE_CONTRACT_SET_RESOURCE),
    )


def load_external_source_manifest_example() -> ExternalSourceManifest:
    return model_from_strict_json(
        ExternalSourceManifest,
        _resource_bytes(EXTERNAL_SOURCE_MANIFEST_EXAMPLE_RESOURCE),
    )


def load_independent_multilabel_policy_example(
) -> ExternalAdministrativeContractSet:
    return model_from_strict_json(
        ExternalAdministrativeContractSet,
        _resource_bytes(INDEPENDENT_MULTILABEL_POLICY_EXAMPLE_RESOURCE),
    )


def load_administrative_counterfactual_example(
) -> DecisionImpactObservation:
    return model_from_strict_json(
        DecisionImpactObservation,
        _resource_bytes(ADMINISTRATIVE_COUNTERFACTUAL_EXAMPLE_RESOURCE),
    )


def load_generated_schema(schema_name: str) -> dict:
    if schema_name not in SCHEMA_RESOURCE_NAMES:
        raise ValueError(
            "schema_name uses the released schema inventory; choose one of "
            + ", ".join(SCHEMA_RESOURCE_NAMES)
        )
    document = strict_json_loads(_resource_bytes(f"schemas/{schema_name}"))
    if not isinstance(document, dict):
        raise ValueError("generated schema resource carries one JSON object")
    return document


def generated_schema_bytes(schema_name: str) -> bytes:
    if schema_name not in SCHEMA_RESOURCE_NAMES:
        raise ValueError(
            "schema_name uses the released schema inventory; choose one of "
            + ", ".join(SCHEMA_RESOURCE_NAMES)
        )
    return _resource_bytes(f"schemas/{schema_name}")

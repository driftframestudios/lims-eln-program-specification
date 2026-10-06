"""Exercise every released resource family through its public typed loader."""
import json
from importlib.metadata import version
from pathlib import Path

from container_runtime import run
from lims_eln_contracts import (
    SCHEMA_RESOURCE_NAMES,
    load_administrative_adapter_contract_example,
    load_administrative_counterfactual_example,
    load_external_administrative_contract_set,
    load_generated_schema,
    load_golden_specimen_observation_example,
    load_golden_specimen_scenario,
    load_independent_multilabel_policy_example,
    load_operation_catalog,
)


def produce(output: Path) -> None:
    schemas = {name: load_generated_schema(name) for name in SCHEMA_RESOURCE_NAMES}
    contract_set = load_external_administrative_contract_set()
    if not schemas or contract_set.contract_set_version != "1.0.0":
        raise ValueError("package-resource-contract")
    documents = {
        "operationCatalog": load_operation_catalog(),
        "goldenScenario": load_golden_specimen_scenario(),
        "implementationObservation": load_golden_specimen_observation_example("implementation"),
        "simulationObservation": load_golden_specimen_observation_example("simulation"),
        "externalAdministrativeContractSet": contract_set,
        "administrativeAdapter": load_administrative_adapter_contract_example(),
        "independentMultilabelPolicy": load_independent_multilabel_policy_example(),
        "administrativeCounterfactual": load_administrative_counterfactual_example(),
    }
    result = {
        "packageVersion": version("lims-eln-program-specification"),
        "schemas": schemas,
        "resources": {name: model.model_dump(mode="json") for name, model in documents.items()},
    }
    (output / "resources.json").write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    run(produce)

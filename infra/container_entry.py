"""Exercise the installed package's complete schema/resource family."""
import json
from importlib.metadata import version
from container_runtime import run
from lims_eln_contracts import SCHEMA_RESOURCE_NAMES, load_generated_schema, load_external_administrative_contract_set


def produce(output):
    resources={name:load_generated_schema(name) for name in SCHEMA_RESOURCE_NAMES}
    assert resources and all(isinstance(value,dict) for value in resources.values())
    contract=load_external_administrative_contract_set()
    assert contract.contract_set_version=="1.0.0"
    (output/"resources.json").write_text(json.dumps({"packageVersion":version("lims-eln-program-specification"),"schemas":resources},sort_keys=True,indent=2)+"\n")

if __name__=="__main__": run(produce)

# Start using the LIMS/ELN constellation

Choose the result that would help the current question. Each repository can be
explored on its own; the shared contracts connect the results when a study needs
more than one part of the constellation.

## Choose a first result

| Starting question | First useful result | Entry route |
| --- | --- | --- |
| How do the two laboratory models differ? | A readable comparison with matching JSON | [Golden Specimen report](https://cometspectrum.io/reports/golden-specimen/comparison.html) and [comparison source](https://github.com/driftframestudios/lims-eln-comparative-evidence) |
| What would a selected future workflow produce? | A repeatable scenario result and observation artifacts | [Simulation: run a scenario](https://github.com/driftframestudios/lims-eln-simulated-final-state#run-it) |
| How does the application behave during use? | An interactive workbench with visible laboratory state | [Enterprise workbench guide](https://github.com/driftframestudios/lims-eln-enterprise-implementation/blob/develop/docs/README.md) |
| How can insurance and administrative context be represented? | Typed records and a controlled comparison example | [Try the administrative contract kit](#try-the-administrative-contract-kit) |
| What evidence supports accepting a result? | Inspectable evidence, decision, and review records | [Governance schema guide](https://github.com/driftframestudios/site-reading-governance/blob/main/schemas/README.md) |

For example, begin by reading one difference in the comparison report. Follow
its source into Simulation to understand the selected future behavior, or into
Enterprise to examine the application mechanism. Program defines the shared
meanings; Governance makes the evidence and decision authority inspectable.

The [workbench capability guide](WORKBENCH_CAPABILITIES.md) explains how to
identify the active adapter, package compatibility, and current HTTP operations.
The [execution and skill map](WORKBENCH_EXECUTION_MAP.md) connects the database,
interface, study, comparison, and public-carrier work to their owning Issues.

## Prepare only the environment the task needs

Reading the report, schemas, and examples works directly in the browser. To run
the administrative example below, use an authorized Program checkout and `uv`.
The command creates an isolated Python 3.12 environment for the checked-out
package. The first run may download the managed interpreter and package
dependencies; later offline use depends on the prepared cache.

The [researcher environment guide](RESEARCHER_ENVIRONMENTS.md) owns the runtime
matrix, exact package coordinates, installed-resource checks, and native or
container choices. The [finite container job](../infra/README.container-job.md) is another
entry for a bounded repository check. Enterprise's persistent workbench has its
own startup, secret, and recovery procedure.

## Try the administrative contract kit

From the Program repository root:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with . -- python -I - <<'PY'
from lims_eln_contracts import (
    load_administrative_adapter_contract_example,
    load_administrative_counterfactual_example,
    load_external_administrative_contract_set,
)

family = load_external_administrative_contract_set()
adapter = load_administrative_adapter_contract_example()
comparison = load_administrative_counterfactual_example()

print("Contract family:", family.contract_set_version)
print("Public record types:", len(family.public_objects))
print("Adapter standing:", adapter.execution_standing)
print("Example difference:", comparison.divergence_class)
PY
```

The bundled example prints:

```text
Contract family: 1.0.0
Public record types: 9
Adapter standing: design_only
Example difference: administrative_only
```

This exercise loads and validates three packaged resources as typed Python
objects. It establishes a usable representation and validation route. The
adapter example describes six stages; `design_only` identifies the example's
execution standing. The counterfactual records an administrative difference
while its scientific-input and result digests stay fixed. Those values are
authored fixtures for examining the contract.

The [package guide](../src/lims_eln_contracts/README.md) describes the public
loaders and models. The [administrative family reference](EXTERNAL_ADMINISTRATIVE_CONTRACTS.md)
owns record meanings, schema roots, raw-label preservation, provenance, and
review. For incoming bytes, the [bounded admission guide](ADMINISTRATIVE_ADMISSION.md)
adds explicit size, depth, graph, and output budgets.

## Build an insurance question in layers

Consider: "With the same scientific evidence, does changing an administrative
field change a workflow's routing, evidence requests, or result?"

The contract kit provides separate records for administrative context,
classification, enrollment, policy rules, decisions, and observed differences.
It also carries population purpose and provenance. A raw insurance label,
candidate classification, reviewed decision, and authorized effect each retain
their own meaning. Code reportability, eligibility, coverage, authorization,
claim disposition, and payment each need the corresponding evidence.

Begin with the bundled counterfactual to inspect that separation. Executing a
paired study across the constellation follows these implementation owners:

| Facet | Available starting point | Next implementation owner |
| --- | --- | --- |
| Shared records and validation | Program models, two schema roots, three examples, and bounded admission | [Administrative family reference](EXTERNAL_ADMINISTRATIVE_CONTRACTS.md) |
| Connected adapter stages | An adapter design contract and Enterprise's accepted package/resource handoff | [Enterprise #36](https://github.com/driftframestudios/lims-eln-enterprise-implementation/issues/36) |
| Insurance classification and assignment | Explicit classification, uncertainty, policy, and review records | [Enterprise #37](https://github.com/driftframestudios/lims-eln-enterprise-implementation/issues/37) |
| Replayable administrative scenarios | Program's authored contract examples | [Simulation #38](https://github.com/driftframestudios/lims-eln-simulated-final-state/issues/38) |
| Paired outcome evaluation | A controlled administrative-difference example | [Comparison #41](https://github.com/driftframestudios/lims-eln-comparative-evidence/issues/41) |
| Administrative assurance | Existing Governance evidence and decision grammar | [Governance #38](https://github.com/driftframestudios/site-reading-governance/issues/38) |

The kit supports contract exploration now. A running insurance classifier,
connected administrative pipeline, and evaluated scenario portfolio belong to
the linked implementation work. Real-payer applicability and population claims
receive their own source, calibration, and accountable review.

## Carry a useful result to the next repository

Keep the input fixture, contract version, source revision, configuration, and
output together. Describe whether the result comes from an authored example,
simulation, or a configured execution. A digest establishes content identity;
the receiving repository's checks establish the behavior relevant to its task.

Program's [current package coordinate](../release/contract-package-coordinate.json)
and each consumer's dependency declaration have separate roles. Enterprise's
reviewed `contracts` profile consumes Program `0.6.1`; this example uses the
package in the current Program checkout. Coordinate updates travel through the consumer's
reviewed adoption route.

Continue with the [environment guide](RESEARCHER_ENVIRONMENTS.md),
[schema catalog](../schemas/README.md), or [Program overview](../README.md).

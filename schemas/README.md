# Program schema index

This index routes readers to each Program-owned JSON Schema surface and to the
source that owns its meaning. A schema establishes a machine-readable
structural boundary. Repository validators and typed models continue to own
cross-record and semantic invariants.

## Begin with an example

The [administrative contract example](../docs/README.md#try-the-administrative-contract-kit)
shows how records and schema-backed meanings fit together. Use the catalog
below when choosing the exact contract for a receiving artifact.

## Release and promotion records

| Schema | Stable identity | Behavior authority |
| --- | --- | --- |
| [`program-release-observation.v1.schema.json`](program-release-observation.v1.schema.json) | `https://schemas.driftframestudios.org/lims-eln-program-specification/v0.3.1/program-release-observation.v1.schema.json` | [`scripts/verify_program_release_observation.py`](../scripts/verify_program_release_observation.py) validates the pending and observed lifecycle shapes |
| [`promotion-receipt.schema.json`](promotion-receipt.schema.json) | `https://schemas.driftframestudios.org/lims-eln-program-specification/v0.3.1/promotion-receipt.schema.json` | [`scripts/validate_program.py`](../scripts/validate_program.py) validates promotion state with the complete release carriers |

The release observation can name a signed tag while its living post-tag
observation remains pending. A released Program coordinate is established only
when the complete promotion carriers and their verification agree.

## Shared package projections

The generated package schemas live under
[`src/lims_eln_contracts/resources/schemas/`](../src/lims_eln_contracts/resources/schemas/).
[`src/lims_eln_contracts/schema_artifacts.py`](../src/lims_eln_contracts/schema_artifacts.py)
owns their bytes and the typed model named beside each projection.

| Projection | Identity | Typed source |
| --- | --- | --- |
| [`bounded-call-receipt.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/bounded-call-receipt.v1.schema.json) | `urn:driftframe:lims-eln:bounded-call-receipt:1.0.0` | `BoundedCallReceipt` |
| [`bounded-call-request.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/bounded-call-request.v1.schema.json) | `urn:driftframe:lims-eln:bounded-call-request:1.0.0` | `BoundedCallRequest` |
| [`golden-specimen-result-projection.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/golden-specimen-result-projection.v1.schema.json) | `urn:driftframe:lims-eln:golden-specimen-result:1.0.0` | `GoldenSpecimenResultProjection` |
| [`observation-envelope.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/observation-envelope.v1.schema.json) | `urn:driftframe:lims-eln:observation-envelope:1.0.0` | `ObservationEnvelope` |
| [`operation-catalog.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/operation-catalog.v1.schema.json) | `urn:driftframe:lims-eln:operation-catalog:1.0.0` | `OperationCatalog` |
| [`scenario.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/scenario.v1.schema.json) | `urn:driftframe:lims-eln:scenario:1.0.0` | `ScenarioContract` |
| [`specimen-command.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/specimen-command.v1.schema.json) | `urn:driftframe:lims-eln:specimen-command:1.0.0` | `SpecimenCommand` |

The Golden Specimen projection declares the temporal invariant that review
resolution occurs at or before release. JSON Schema communicates the invariant;
the typed loader enforces it. Other consumers apply that rule beside structural
validation.

## Verify generated equality

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_contract_schemas.py --check
```

The command establishes that every committed package schema matches the current
typed source. It does not establish a receiving service's runtime behavior.
Use the [`package adoption guide`](../src/lims_eln_contracts/README.md) for
installation and consumer-conformance checks.

## Administrative family

The [synthetic study guide](../docs/ADMINISTRATIVE_STUDIES.md) introduces the
additive `administrative-study.v1.schema.json` and
`administrative-study-comparison.v1.schema.json` package projections. The
former preserves plans and observations; the latter carries derived counts and
output-identity findings. Both remain discoverable through the package inventory.

The external benchmark and administrative-context family begins with:

| Schema | Canonical identity | Use |
| --- | --- | --- |
| [`administrative-adapter-contract.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/administrative-adapter-contract.v1.schema.json) | `urn:driftframe:lims-eln:administrative-adapter-contract:1.0.0` | Validate a source-neutral administrative adapter and its replay-safe stage design independently. |
| [`external-administrative-contract-set.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/external-administrative-contract-set.v1.schema.json) | `urn:driftframe:lims-eln:external-administrative-contract-set:1.0.0` | Validate the dependency-closed family; Python enforces declared referential and temporal invariants. |

The
[`external-administrative-contracts.v1.json`](../src/lims_eln_contracts/resources/external-administrative-contracts.v1.json)
canonical bundle names every object, example, compatibility rule, invalidation
event, owner, and adoption condition and carries the dependency-closed fixture
graph. `scripts/generate_administrative_examples.py --check` verifies its
reader-specific projections. The design and evidence boundary are in
[`docs/EXTERNAL_ADMINISTRATIVE_CONTRACTS.md`](../docs/EXTERNAL_ADMINISTRATIVE_CONTRACTS.md).

The remaining generated package schemas continue to be discoverable through
`lims_eln_contracts.SCHEMA_RESOURCE_NAMES`. A package consumer should use that
inventory so a successor schema cannot disappear silently from its conformance
check.

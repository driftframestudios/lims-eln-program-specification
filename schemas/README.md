# Program schema index

This index routes readers to each Program-owned JSON Schema surface and to the
source that owns its meaning. A schema establishes a machine-readable
structural boundary. Repository validators and typed models continue to own
cross-record and semantic invariants.

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

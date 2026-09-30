# Shared LIMS/ELN contract package

`lims_eln_contracts` is the small Python and JSON contract nucleus shared by the
Program's implementation, simulation, and comparison repositories. Use this
directory when adopting or revising wire meaning. The Program repository owns
the contract; each consumer continues to own authentication, authorization,
domain behavior, persistence, observed evidence, and accountable decisions.

## What the package carries

- strict specimen commands;
- bounded operation definitions, requests, effect summaries, and receipts;
- evidence-mode and assurance-stage vocabulary;
- comparative observation envelopes;
- the executable Golden Specimen scenario;
- implementation- and simulation-shaped example observations; and
- generated JSON Schema projections for non-Python consumers.

The package distribution is `lims-eln-program-specification`; its import name is
`lims_eln_contracts`. The current package version is `0.3.1`, and the shared
contract version exposed by the package is `1.0.0`.
This source-local adoption guide is outside the built distribution and the
package source digest; the machine coordinate names that narrow exclusion so
documentation can improve without changing accepted runtime bytes.

## Quickest local proof

From the repository root:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python -m unittest \
  tests.test_contract_resources tests.test_contract_models -v
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_contract_schemas.py --check
```

These checks establish typed resource loading, semantic invariants, and equality
between generated schemas and committed projections. They do not establish a
consumer's configured runtime behavior or production acceptance.

## Adopt the reviewed package source

[`release/contract-package-coordinate.json`](../../release/contract-package-coordinate.json)
is the machine-readable source for package version, reviewed commit, scoped
digest, transport, authentication posture, and consumer-conformance checks.
The reviewed `0.3.1` source coordinate is currently:

```text
4d06eeb7f96910311fbcb7f51547c978b6a07290
```

An authenticated PEP 508 installation uses that full commit:

```sh
python3 -m pip install \
  "lims-eln-program-specification @ git+https://github.com/driftframestudios/lims-eln-program-specification.git@4d06eeb7f96910311fbcb7f51547c978b6a07290"
```

HTTPS is the canonical private-distribution transport. Git obtains credentials
from a configured credential helper or short-lived GitHub App token; committed
requirement text stays free of credentials. A team that already manages deploy
keys and host verification can use SSH to resolve the same full commit.

For active work in this repository:

```sh
python3 -m pip install -e .
```

For a sibling checkout during local development:

```sh
python3 -m pip install -e ../lims-eln-program-specification
```

The editable route is convenient for development. Release conformance uses a
reviewed immutable commit and the scoped package digest.

## Verify a receiving installation

A receiving repository checks the installed distribution's PEP 610
`direct_url.json` and confirms:

- `vcs_info.commit_id` equals the reviewed full commit;
- distribution and import versions are `0.3.1`;
- the package reports contract version `1.0.0`;
- the scoped package-source digest matches the reviewed binding;
- the operation catalog and Golden Specimen scenario load;
- both shaped example observations load; and
- every schema named by `SCHEMA_RESOURCE_NAMES` loads as a JSON object.

The reviewed coordinate may move to a later commit at the same package version
only when its scoped package digest is identical. A package-content change
advances both version and digest, and each consumer adopts either replacement
through review.

## Load released resources

```python
from lims_eln_contracts import (
    load_golden_specimen_observation_example,
    load_golden_specimen_scenario,
    load_operation_catalog,
)

catalog = load_operation_catalog()
scenario = load_golden_specimen_scenario()
implementation_example = load_golden_specimen_observation_example("implementation")
simulation_example = load_golden_specimen_observation_example("simulation")
```

The Golden Specimen result keeps common comparison fields in
`result.projection` and producer-owned detail in `result.producer_detail`.
Its stable identity is `urn:driftframe:lims-eln:golden-specimen-result`, its
version is `1.0.0`, and its comparison rule is `exact-version`. A comparator
verifies identity, version, and rule before comparing canonical projection
bytes.

The two shipped example observations retain distinct evidence modes and local
provenance while sharing one decision-relevant projection. Their shared
projection digest is
`sha256:cead042eaf3ca8f72b9c30c41d9acb0bd9255027448f3b28e3451305bed1aef1`.
They establish exchange shape; producer execution and governed evidence
establish an environment-specific result and assurance stage.

## Generated schemas

[`schema_artifacts.py`](schema_artifacts.py) owns the generated bytes under
[`resources/schemas/`](resources/schemas/). Routine validation checks equality:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_contract_schemas.py --check
```

After an accepted model revision, generate the projections once:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_contract_schemas.py
```

JSON Schema supplies the structural boundary. Pydantic loaders also enforce
declared semantic invariants, strict field types, finite numbers, duplicate-key
rejection, and immutable model instances. A non-Python consumer applies the
same semantic invariants alongside schema validation.

See the repository [`schema index`](../../schemas/README.md) for the root
release schemas and the complete generated package inventory.

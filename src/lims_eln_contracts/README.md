# Shared LIMS/ELN contract package

The 0.7.1 candidate reuses each referenced decision's canonical digest within
one administrative graph admission. Its wire schemas and canonical examples
retain their bytes. The package coordinate remains pending review; consumers
retain their accepted 0.7.0 source until a focused adoption review selects the
successor. Each admission prepares fresh digests for its own immutable values.

`lims_eln_contracts` is the small Python and JSON contract nucleus shared by the
Program's implementation, simulation, and comparison repositories. Use this
directory when adopting or revising wire meaning. The Program repository owns
the contract; each consumer continues to own authentication, authorization,
domain behavior, persistence, observed evidence, and accountable decisions.

## Try the package first

The [synthetic study example](../../docs/ADMINISTRATIVE_STUDIES.md) preserves
paired plans, actual outputs, incomplete runs and expected outcomes separately.
It is the package 0.5.0 entry for administrative-context experiments.

The [administrative example](../../docs/README.md#try-the-administrative-contract-kit)
loads typed resources from the current checkout in an isolated Python
environment. The [current package coordinate](../../release/contract-package-coordinate.json)
identifies the reviewed source. The 0.4.0 installation below preserves
Enterprise's accepted consumer handoff; later package adoption belongs to that
consumer's review route.

## What the package carries

- strict specimen commands;
- bounded operation definitions, requests, effect summaries, and receipts;
- evidence-mode and assurance-stage vocabulary;
- comparative observation envelopes;
- the executable Golden Specimen scenario;
- implementation- and simulation-shaped example observations; and
- generated JSON Schema projections for non-Python consumers; and
- the optional database lifecycle admission API with two exact authored schemas.

The package distribution is `lims-eln-program-specification`; its import name is
`lims_eln_contracts`. The machine coordinate declares the current package version;
the shared contract version exposed by the package is `1.0.0`.
The reviewed `0.4.0` installed source below preserves Enterprise's accepted
consumer handoff. Each receiver selects and verifies its own accepted coordinate.
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

[The accepted `0.4.0` binding](https://github.com/driftframestudios/lims-eln-program-specification/blob/a307f422596e5098ac5efca29968212b5e24da0b/release/contract-package-coordinate.json)
owns the reviewed commit, scoped digest, transport, authentication posture,
and consumer-conformance checks for the installation below.
[The current package coordinate](../../release/contract-package-coordinate.json)
tracks the successor's own version and review standing. Adopt that successor
through its exact reviewed source and the receiving repository's checks.
The retained reviewed `0.4.0` source coordinate is:

```text
d8f41d0ce98a75120c99f0a23d00796ae8a8b913
```

An authenticated PEP 508 installation uses that full commit:

```sh
python3 -m pip install \
  "lims-eln-program-specification @ git+https://github.com/driftframestudios/lims-eln-program-specification.git@d8f41d0ce98a75120c99f0a23d00796ae8a8b913"
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
- distribution and import versions are `0.4.0` for that reviewed source;
- the package reports contract version `1.0.0`;
- the scoped package-source digest matches the reviewed binding;
- the operation catalog and Golden Specimen scenario load;
- both shaped example observations load;
- the canonical administrative bundle and its three examples load; and
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

## Administrative family and receiving environments

[The family reference](../../docs/EXTERNAL_ADMINISTRATIVE_CONTRACTS.md) owns
source-neutral adapter, classification, policy, population, review, and
provenance meaning. Its canonical bundle produces three byte-checked examples.
Run `python scripts/generate_administrative_examples.py --check` in the prepared
environment after a related source change.

[Researcher environments](../../docs/RESEARCHER_ENVIRONMENTS.md) distinguishes
installed and editable use, complete-profile interpreter requirements, and
configured native/container evidence. [The handoff runbook](../../.agents/runbooks/constellation-contract-release-handoff.v0.1.md)
keeps each consumer's acknowledgement and recovery with its receiving Issue.

## Comparison interpretation companion

The 0.6.0 package adds `StudyAnalysisProfile`, `StudyInterpretation`, and the
pure `interpret_administrative_study` projection. Existing study and comparison
contracts keep their meanings. The [study guide](../../docs/ADMINISTRATIVE_STUDIES.md)
shows declared control coverage and explicit eligibility profiles; the
[migration route](../../docs/migrations/0.5.0-to-contract-package-0.6.0.md)
describes the exact-source receiving handoff. Package preparation remains
separate from tagged publication.

## Receive the database lifecycle companion

Package 0.7.0 adds `lims_eln_contracts.database_lifecycle`. Install the `lifecycle`
extra in the receiver's dedicated proof environment and select the exact commit
from the [package coordinate](../../release/contract-package-coordinate.json).
The [migration guide](../../docs/migrations/0.6.1-to-contract-package-0.7.0.md)
explains schema identity, provenance, independent expectations and recovery.
`AUTHORED_SCHEMA_RESOURCE_NAMES` and `authored_schema_bytes(name)` expose the
source-authored companions separately from generated model projections.

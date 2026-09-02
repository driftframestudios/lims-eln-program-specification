# LIMS/ELN Program Specification

This repository defines the shared requirements and acceptance route for a
five-repository LIMS/ELN program. Start here to understand what the suite is
meant to prove, find which repository owns a behavior, and compare the active
implementation with the simulated final state against the same contract.

Repository authorship and maintenance provenance is recorded in
[`AUTHORS`](AUTHORS). Git history and reviewed pull requests preserve change
chronology and contribution credit.

## Start here

1. Read [`release/repository-role.json`](release/repository-role.json) for this
   repository's role and current release state, then use
   [`STATUS.yaml`](STATUS.yaml) for the compact status.
2. Use [`constellation.json`](constellation.json) and the table below to find
   the repository that can establish the behavior you need. Use
   [`constellation.lock.json`](constellation.lock.json) when an exact release
   tag, commit, or digest affects the decision.
3. Use Python 3.12, run `python3 -m pip install -e .`, and begin with
   `python3 scripts/validate_program.py`. The complete candidate proof is in
   [Validation](#validation).
4. Start changes from `develop` using the branch forms in
   [`BRANCHING.md`](BRANCHING.md), follow the contribution contract in
   [`CONTRIBUTING.md`](CONTRIBUTING.md), and keep tests beside the behavior they
   establish.
5. Use the repository-local
   [`source-authority-mapping`](.agents/skills/source-authority-mapping/SKILL.md)
   skill when a requirement, schema, implementation result, simulated result,
   comparison report, release coordinate, or public page crosses repository
   roles.

[`coordination-horizon.json`](coordination-horizon.json) records current and
queued work. [`first-receipt.json`](first-receipt.json) provides a compact
re-entry record with the current evidence status and next verified move.

The current planned program release is `spec-v0.3.1`. It consumes the accepted
governance release `governance-v2.1.0`, Control Plane Profile 0.3.0, and schema
release `2.1.0`. The Governance coordinate in
[`constellation.lock.json`](constellation.lock.json) binds the annotated tag
object, accepted commit, Git tree, and reproducible Git archive as distinct
identities. The Program release coordinate remains open until its reviewed
promotion supplies the corresponding commit and tree.

The repository describes what collaborators can verify. The simulation supplies
an executable future reality whose assumptions, synthetic decisions, and
evidence mode remain visible and revisable. A complete simulated closure can
therefore stand as a first-class result while a separately represented observed
closure remains available for future running-system evidence.

## Constellation

| Repository | Authority |
|---|---|
| [`lims-eln-program-specification`](https://github.com/driftframestudios/lims-eln-program-specification) | Intent, examples, risks, forecasts, and acceptance criteria |
| [`lims-eln-enterprise-implementation`](https://github.com/driftframestudios/lims-eln-enterprise-implementation) | Active code, infrastructure, migrations, and observed execution manifests |
| [`lims-eln-simulated-final-state`](https://github.com/driftframestudios/lims-eln-simulated-final-state) | Executable counterfactual and simulated phase artifacts |
| [`lims-eln-comparative-evidence`](https://github.com/driftframestudios/lims-eln-comparative-evidence) | Paired execution, normalization, adjudication, and redacted evidence |
| [`site-reading-governance`](https://github.com/driftframestudios/site-reading-governance) | Shared schemas, language posture, workflows, templates, and rulesets |

The merged
[`prototype-exemplars` LIMS/ELN pack](https://github.com/driftframestudios/prototype-exemplars/pull/3)
is the provenance-bearing seed. New releases preserve its source commit,
merge commit, and content lineage.

## Working model

1. A specification release freezes rules, scenarios, forecasts, and fixtures.
2. The simulated final state resolves each open design question through an
   assumption-bearing decision record.
3. The active implementation evolves independently against the same contract.
4. The comparator pins exact releases and emits an adjudicated difference
   report.
5. Collaborators classify each difference as convergence, beneficial
   divergence, an implementation gap, a simulation correction, a context
   change, or an evidence question.
6. New evidence creates a new forecast release while the earlier forecast
   remains available for calibration.

## Coordination Horizon

[`coordination-horizon.json`](coordination-horizon.json) is the flexible
coordination surface for active, queued, and exploratory work. It records
entry evidence, exit evidence, dependencies, and re-entry instructions. Its
authority is coordination-only; released contracts, runtime policy, and
accountable domain roles continue to govern effects and acceptance.

[`machine-node.json`](machine-node.json),
[`first-receipt.json`](first-receipt.json), and the Coordination Horizon are
strict projections of governance schema release `2.1.0`. This release keeps the
stable `/v2.0/` schema identifier family while adding compatible contract
capabilities. Contract references carry SHA-256 digests that the program
validator recalculates. The Machine Node orients; the first receipt supplies
safe re-entry; runtime services and accountable roles continue to own effects
and decisions.

## Practitioner Probes

[`probes/catalog.json`](probes/catalog.json) contains ten LIMS/ELN Practitioner
Probes. Each probe progresses through:

1. observable surface;
2. mechanism;
3. realistic scientific use;
4. edges and maintenance;
5. review, repair, evidence, and accountable handoff.

Each probe declares a technical-veracity status and links requirements, rules,
scenarios, and receipts. This makes principal-level claims inspectable rather
than relying on prose confidence alone.

## Shared Python contract nucleus

[`src/lims_eln_contracts`](src/lims_eln_contracts) publishes the small runtime
contract shared by implementation, simulation, and comparison work. It gives
each repository the same vocabulary for:

- evidence mode and assurance stage;
- strict specimen commands;
- bounded operations, requests, effect summaries, and receipts;
- comparative observation envelopes; and
- the executable golden-specimen journey.

The package owns wire meaning and canonical digests. Each consuming service
continues to own authenticated identity, authorization, domain behavior,
persistence, and accountable decisions. This keeps agency calibrated to the
role that can exercise it.

The released resources travel inside the package:

- [`operations.v1.json`](src/lims_eln_contracts/resources/operations.v1.json)
  carries the three versioned operation definitions;
- [`golden-specimen.v1.json`](src/lims_eln_contracts/resources/scenarios/golden-specimen.v1.json)
  carries one synthetic, executable specimen journey; and
- [`resources/schemas`](src/lims_eln_contracts/resources/schemas) carries the
  generated JSON Schema projections for non-Python consumers.

### Shared Golden Specimen result

The Golden Specimen observation places its common comparison fields in
`result.projection` and keeps producer-specific detail in
`result.producer_detail`. The surrounding observation continues to state its
evidence mode, assurance stage, source, provenance, approvals, and data class.
Implementation and simulation can therefore report the same decision-relevant
result while retaining the detail each repository owns.

The surrounding observation binds that result to the released source scenario
with its identifier, semantic version, and canonical scenario digest. A
comparator verifies this three-part coordinate before it compares projection
bytes, so a revised command, instrument message, expected state, or recovery
route receives a new source identity even when its scenario identifier remains
familiar.

The projection carries the tenant and specimen identities, released lifecycle
revision, current custody location, scientific measurement, accepted review
resolution, and approval receipt with the release timestamp. Its stable
identity is `urn:driftframe:lims-eln:golden-specimen-result`, its current
version is `1.0.0`, and its comparison rule is `exact-version`. A comparator
verifies all three values before comparing canonical projection bytes. A later
projection version can receive an explicit adapter when its meaning is settled.

The package includes an
[`implementation`-shaped example](src/lims_eln_contracts/resources/observations/golden-specimen.implementation.v1.json)
and a
[`simulation`-shaped example](src/lims_eln_contracts/resources/observations/golden-specimen.simulation.v1.json).
Their shared projection has canonical digest
`sha256:cead042eaf3ca8f72b9c30c41d9acb0bd9255027448f3b28e3451305bed1aef1`.
These resources establish the exchange shape. Producer execution and governed
evidence establish the environment-specific result and its assurance stage.
Each example binds its local configuration and complete result to the SHA-256
digests carried in the observation.
The generated
[`golden-specimen-result-projection.v1.schema.json`](src/lims_eln_contracts/resources/schemas/golden-specimen-result-projection.v1.schema.json)
provides the closed structural boundary and declares the temporal invariant for
non-Python consumers. The typed loader enforces that review resolves at or
before release; another consumer applies the same declared invariant alongside
JSON Schema validation.

Pydantic strengthens these external boundaries through strict types, declared
fields, finite numbers, and immutable model instances. The JSON parser also
rejects duplicate keys and non-finite numeric tokens; callers can proceed by
supplying one value per key and a finite measurement or explicit textual state.

### Install the shared contract package

The Python distribution is `lims-eln-program-specification`; its import package
is `lims_eln_contracts`, and the current package version is `0.3.1`.
[`release/contract-package-coordinate.json`](release/contract-package-coordinate.json)
records the installation and replacement contract. Program repository owners
publish the reviewed source coordinate. The final protected `main` commit may
replace the reviewed integration commit at version `0.3.1` when their scoped
package digests are identical. A package-content change advances both version
and digest. Each consumer adopts either kind of replacement through review.
The same record binds `pyproject.toml` and `src/lims_eln_contracts` through a
path-delimited SHA-256 digest, so consumers can verify package content
independently of the repository coordinate. The coordinate defines the framing:
each regular file is ordered by the UTF-8 bytes of its POSIX relative path, then
contributes its unsigned eight-byte big-endian path length, path bytes, content
length, and content bytes. Runtime cache files are outside the selection, and
symlinks make the scoped digest invalid. This makes the custom digest
reproducible without requiring the Program validator as an implementation.

This branch leaves the source commit open because its reviewed merge commit
becomes the immutable package coordinate. After that merge, an authenticated
PEP 508 installation uses the full 40-character commit:

```sh
python3 -m pip install \
  "lims-eln-program-specification @ git+https://github.com/driftframestudios/lims-eln-program-specification.git@<FULL_40_HEX_COMMIT>"
```

HTTPS is the canonical transport for this private distribution because the
same requirement works for developer machines, CI, and service accounts. Git
receives authentication from a configured credential helper or a short-lived
GitHub App token, while the committed requirement remains free of credentials.
SSH remains a receiving-environment option for teams that already manage deploy
keys and host verification; both routes resolve the same full commit.

Inside this repository, install the active source directly:

```sh
python3 -m pip install -e .
```

A receiving repository can use an adjacent editable checkout during local
development:

```sh
python3 -m pip install -e ../lims-eln-program-specification
```

A receiving repository's release-conformance check later reads the installed
distribution's PEP 610 `direct_url.json`, confirms that `vcs_info.commit_id`
matches its reviewed binding, and verifies the scoped package-source digest,
distribution and import versions, contract version `1.0.0`, operation catalog,
Golden Specimen scenario, implementation- and simulation-shaped observations,
and every schema named by `SCHEMA_RESOURCE_NAMES`. The editable route remains
the direct path for active local development. The first recorded receiving
repository is `lims-eln-enterprise-implementation`, using a clean Python 3.12
environment for the release-conformance observation.

```python
from lims_eln_contracts import (
    load_golden_specimen_scenario,
    load_operation_catalog,
)

catalog = load_operation_catalog()
scenario = load_golden_specimen_scenario()
```

Load either shaped observation through the same typed boundary:

```python
from lims_eln_contracts import load_golden_specimen_observation_example

implementation_example = load_golden_specimen_observation_example("implementation")
simulation_example = load_golden_specimen_observation_example("simulation")
```

The generated schemas remain a byte-identical projection of the Python models.
After a deliberate model revision, render them once; routine validation checks
that the committed projection remains current.

```sh
PYTHONPATH=src python3 scripts/generate_contract_schemas.py
PYTHONPATH=src python3 scripts/generate_contract_schemas.py --check
```

## Bounded callers

[`specifications/bounded-caller.json`](specifications/bounded-caller.json)
defines one service-owned contract for humans, workloads, workflows, and
task-scoped AI callers. The service derives identity from authenticated
context, validates strict inputs, enforces tenant and resource scope, applies
budgets, rechecks effect preconditions, and emits an attributable receipt.

The specification-by-example suite covers:

- one authorized read;
- one narrow idempotent metadata correction;
- one approval-gated migration cutover.

An AI caller selects released operations through an allowlist. It gains no
independent Scientific, Quality, Regulatory, Security, Operations, or business
authority. Consequential approvals bind operation version, canonical request
digest, tenant, effect ceiling, intended use, expiry, and recovery coordinates.
The outer request and released payload carry one approval receipt identity,
keeping the reviewed payload and execution grant joined at the service boundary.

## Database modernization contracts

[`database/primitive-findings.json`](database/primitive-findings.json) records
32 critical or high cross-repository findings with stable identities,
source locations, material effects, affirmative target states, and correction
bindings. [`plans/database-modernization-plans.json`](plans/database-modernization-plans.json)
compares five routes against one declared probability event and synthesizes a
seven-stage chain with a recalibration interstitial after every stage. The
reference and implementation probability tables are bounded local derivatives;
the canonical program estimates remain the cross-route comparison surface.

[`database/constellation-finding-index.json`](database/constellation-finding-index.json)
binds all 115 intentionally overlapping program, reference, and implementation
finding records to immutable source commits, raw ledger digests, record identities,
counts, and each exact probability event's relationship to the canonical event.

[`specifications/data-primitives.json`](specifications/data-primitives.json)
defines canonical temporal, identifier, digest, measurement, unit, vocabulary,
JSON, nullability, tenancy, event, idempotency, evidence, and access-path
semantics. [`specifications/database-migration.json`](specifications/database-migration.json)
defines a tool-neutral PostgreSQL schema-migration capability contract, the
selected Flyway Community 13.0.0 profile, four ownership boundaries, nine
reconciliation dimensions, seven release gates, and a retained-test
verification matrix. Flyway owns ordering, checksummed history, coordination,
and status. Program SQL owns PostgreSQL domain semantics; vendor-supported
lifecycle paths, cross-vendor reconciliation, and accountable release evidence
retain their separate owners.

[`receipts/database-open-receipts.json`](receipts/database-open-receipts.json)
preserves eight future-observed proof obligations. The digest-bound
[`release/database-release-manifest.json`](release/database-release-manifest.json)
joins those obligations to the contract artifacts and specification-by-example
suite while implementation coordinates remain explicitly pending. See
[`docs/DATABASE_MODERNIZATION.md`](docs/DATABASE_MODERNIZATION.md) for the
probability posture, evidence boundaries, synthesized chain, and interstitials.
The [`database constellation ledger`](docs/DATABASE_CONSTELLATION_LEDGER.md)
interprets that machine index and connects it to the governance, reference,
implementation, simulation, and comparison proof surfaces.

## Evidence ladder

`specified → simulated → locally_verified → configured_environment_qualified
→ representative_rehearsal_completed → intended_use_validated
→ accountably_accepted`

Each stage states its own evidence mode. A simulated future reality may
exercise and close the full shape of any stage with synthetic environments,
measurements, and role-bound decisions. That result remains
`evidence_mode: simulated`. The program design carries
`authority: advisory_design_only`; an executed canonical closure can be
definitive inside its named selected future reality while retaining
`production_authorization_effect: none`. Its separately tracked observed
successor begins open and can advance later through environment-bound evidence
and accountable human decisions.

## Simulated closure of the four substantive receipt classes

[`simulations/future-reality-closure-v0.3.json`](simulations/future-reality-closure-v0.3.json)
is the advisory program design for a coherent 2028 future and fully specifies:

- configured Sapio, Benchling, and LabKey environments;
- representative migration, rollback, clean restore, continuity, and data exit;
- production-bound security, privacy, AWS configuration and secret lifecycle,
  observability, support, and incident operation;
- distinct Scientific, Quality, and Regulatory acceptance.

All nine underlying receipt records point to one of these four class-level
closures. Every record preserves both `closed_in_future_reality` for the
simulated branch and `open` for its future observed branch.

[`simulations/simulated-receipt-closure.v2.json`](simulations/simulated-receipt-closure.v2.json)
is the exact canonical closure emitted by the executable simulation under its
historical governance 2.0.0 record schema and validated by governance 2.0.1.
Its identity is `FUTURE-REALITY-LIMS-2028-001`, and its canonical
JSON digest is
`sha256:c402e7a72d9066424d5b83c8fda51ca2fad43c025d017a5f5535126239c96ffb`.
It contains exactly four receipt families, declares `closed_in_simulation`,
preserves the environment-observed branch as `separate_unasserted_state`, and
grants zero production-authorization effect. The advisory design uses the
distinct identity `FUTURE-REALITY-DESIGN-LIMS-2028-001`; one identity therefore
denotes one modeled reality and authority posture.

[`simulations/future-reality-2028-06-30-v1.json`](simulations/future-reality-2028-06-30-v1.json)
is the byte-identical canonical bundle shared with the simulation and
comparison surfaces. It binds reference result digest
`sha256:9d42b972c77764c81ff32fefe8f02367a27406e9ba082a704587cc9b5a9da860`
and aggregate artifact digest
`sha256:2d8e67ec2da8236fc23de7943e7727d2b74e0e6ee2b15afd9c765443b9c52b61`.

[`specifications/receipt-vocabulary-map.v1.json`](specifications/receipt-vocabulary-map.v1.json)
version-controls the mapping from individual governance receipt families to
program proof classes and grouped canonical closure families. It also makes
the `closed_in_future_reality` → `closed_in_simulation` and observed
`open` → `separate_unasserted_state` transitions explicit.

## Validation

```sh
python3 scripts/validate_program.py
python3 scripts/check_language.py
python3 scripts/check_language.py --format sarif
python3 scripts/scan_secret_shapes.py
PYTHONPATH=src python3 scripts/generate_contract_schemas.py --check
python3 -m unittest discover -s tests -v
```

The program validator uses the Python standard library and checks stable identifiers,
cross-file references, bounded operation classes, probe levels and veracity,
forecast coordinates, simulated and observed receipt-state separation,
Coordination Horizon structure, Machine Node posture, receipt ownership, and
required collaboration surfaces. Database validation additionally closes the
finding-to-policy map, plan and interstitial shape, contract references, open
receipt set, and manifest digests. Its JSON boundary requires unique object
keys and finite numbers before identifiers or canonical digests enter
validation. The shared contract tests use Pydantic at the external model
boundary and verify strict parsing, semantic invariants, packaged resources,
and byte-identical JSON Schema regeneration.

Candidate records carry explicit zero coordinates and an open promotion receipt.
Released records carry pinned coordinates and a closed, evidence-bearing
promotion receipt. The validator exercises both lifecycle shapes, so settlement
can advance without weakening the candidate boundary.

## Program Pages candidate

[`pages/program-content.json`](pages/program-content.json) is the source-owned
visitor orientation for the five-repository constellation. The builder combines
that content with the current repository role, release status, constellation,
and exact Git `HEAD`. The resulting static pages describe the 0.3.1 candidate
posture, route readers to each authority, provide local commands, and link every
program source reference through the full producing commit SHA.

A clean checkout can create and validate one local projection outside the
worktree:

```sh
python3 scripts/build_pages.py --output ../program-pages-build
python3 scripts/validate_projection.py ../program-pages-build
```

The aggregate creates two isolated builds, compares every projected byte,
validates their manifests and relative links, and scans generated text for
credential-shaped values:

```sh
python3 scripts/verify_pages.py
```

The default build remains portable and carries no domain claim. A publication
receiver can provide both `--canonical-origin https://docs.example.org` and
`--cname docs.example.org` to create matching HTML canonical links and `CNAME`.
Branch creation, Pages activation, and domain configuration remain separate
publication actions.

Repository skills join the generated catalog when their `SKILL.md` front matter
declares `source_band: public_ready`. The current public-ready set contains the
repository-local source-authority map used to follow one material object through the
five-repository suite. Internal and public-possible sources retain their
collaboration boundaries, and an empty public-ready set produces no catalog.

The released projection manifest contract is `1.0.0`. It records the projection
owner, complete file scope, verified source revision and standing, optional
canonical origin, authoritative program-content digest, public-skill inventory,
and byte length plus SHA-256 for every projected file. Unit tests use an explicit
`fixture` standing; ordinary builds accept only a clean exact `HEAD`.

Release changes and consumer migration notes are recorded in
[`CHANGELOG.md`](CHANGELOG.md) and
[`docs/migrations/0.3.0-to-0.3.1.md`](docs/migrations/0.3.0-to-0.3.1.md).

## Runtime configuration and protected values

AWS Systems Manager Parameter Store carries environment-scoped non-secret
configuration. AWS Secrets Manager carries vendor credentials and other secret
material under the approved KMS key. Workload identities receive the narrow
read actions and resource paths required by their environment. Rotation,
version-stage handling, bounded caches, CloudTrail evidence, and redacted
retrieval telemetry form one testable lifecycle.

Repositories, build artifacts, Terraform state, logs, fixtures, and telemetry
carry governed references or redacted metadata. The open receipt
`RCP-SECR-001` advances after production-bound retrieval, rotation, policy, KMS,
cache, audit, and secret-shape probes complete accountable review.

## Language posture

Guidance names desired states, stable invariants, and verifiable outcomes.
Hard safety and privacy boundaries pair the boundary with the state that
replaces it. Code comments use `TARGET`, `GUARD`, and `CONTRAST` where the
distinction materially assists future collaborators.

[`docs/AUTHOR_FEEDBACK.md`](docs/AUTHOR_FEEDBACK.md) defines the advisory,
structure-aware Vale scope, rule severity, and checksum-verified tool
coordinate. The deterministic program gate retains candidate authority.

That gate projects `language-policy-v1.0.0` across authored Markdown, JSON,
YAML, and Python surfaces. It emits stable text, JSON, or SARIF findings and
qualifies behavior against a versioned golden corpus. Exact exemptions carry
accountable ownership, review/expiry coordinates, and a
rule–path–fingerprint binding. See
[`docs/LANGUAGE_POLICY.md`](docs/LANGUAGE_POLICY.md) for the complete contract
and its bounded authority.

Source guidance:
[Semantic Attractor Design — Negation-Aware Instructions](https://app.notion.com/p/abcb29b960a842ce8f1a409408a29257).

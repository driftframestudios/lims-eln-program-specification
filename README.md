# LIMS/ELN Program Specification

This repository defines the shared requirements and acceptance route for a
five-repository LIMS/ELN program. Start here to understand what the suite is
meant to prove, find which repository owns a behavior, and compare the active
implementation with the simulated final state against the same contract.

Repository authorship and maintenance provenance is recorded in
[`AUTHORS`](AUTHORS). Git history and reviewed pull requests preserve change
chronology and contribution credit.

## Start with a useful result

Use the constellation to explore a laboratory workflow, compare two models, or
carry an evidence-backed result into review. Begin with the part that answers
the current question:

- **See an existing result:** read the [Golden Specimen comparison](https://cometspectrum.io/reports/golden-specimen/comparison.html), then follow a difference to its source.
- **Try a small example:** load the [administrative contract kit](docs/README.md#try-the-administrative-contract-kit) in an isolated Python environment.
- **Use the application:** follow the [constellation starting guide](docs/README.md) to Enterprise's workbench, Simulation, and the evidence routes.

Program supplies the shared meanings, schemas, and acceptance criteria. Its
insurance and administrative layer is usable today as typed records, validation,
and authored examples. Runtime classification and connected scenario execution
have their own [implementation owners](docs/README.md#build-an-insurance-question-in-layers).

Choose a result first; the release coordinates and detailed proof routes below
support the next level of inspection.

## Current state

The signed annotated tag `spec-v0.3.1` exists and resolves to the reviewed
release subject. Current `main` also carries later release-line diagnostics and
Pages repairs. The living release carriers intentionally remain in
`candidate_pending_promotion`: the four-sibling hosted proof and the post-tag
release observation have not yet settled. In this repository, a present tag and
a completed release observation are distinct facts.

[`release/repository-role.json`](release/repository-role.json) and
[`STATUS.yaml`](STATUS.yaml) provide the compact living state.
[`receipts/promotion-observation-spec-v0.3.1.json`](receipts/promotion-observation-spec-v0.3.1.json)
names the open post-tag observation. [`coordination-horizon.json`](coordination-horizon.json)
records current work, and [`first-receipt.json`](first-receipt.json) supplies the
smallest machine-readable re-entry route.

The 0.3.1 constellation consumes accepted Governance 2.1.0, Implementation
0.3.2, Simulation 2028 selected-future, and Comparison 0.3.1 release subjects.
[`constellation.lock.json`](constellation.lock.json) binds their tag objects,
commits, Git trees, reproducible archives, and decision-changing semantic
relations. Governance 2.1.0 remains the current schema authority.

## Choose your route

| Reader job | Begin here | Continue with |
| --- | --- | --- |
| Understand what this repository owns | [`release/repository-role.json`](release/repository-role.json) | [Constellation](#constellation) and [`constellation.json`](constellation.json) |
| Resume current work | [`first-receipt.json`](first-receipt.json) | [`coordination-horizon.json`](coordination-horizon.json), live Issues, and the [skill catalog](.agents/skills/README.md) |
| Adopt the shared Python/JSON contract | [`src/lims_eln_contracts/README.md`](src/lims_eln_contracts/README.md) | [`release/contract-package-coordinate.json`](release/contract-package-coordinate.json) and the [schema index](schemas/README.md) |
| Inspect Program requirements or decision probes | [`specifications/`](specifications/) | [`probes/catalog.json`](probes/catalog.json), [`acceptance/`](acceptance/), and [`decisions/`](decisions/) |
| Compare active and selected-future behavior | [`constellation.json`](constellation.json) | the [accepted public comparison](https://cometspectrum.io/reports/golden-specimen/comparison.html) |
| Build or inspect Program Pages | [`pages/README.md`](pages/README.md) | [`pages/program-content.json`](pages/program-content.json) and [Program Pages](#program-pages-candidate) |
| Select a reproducible researcher environment | [Researcher environments](docs/RESEARCHER_ENVIRONMENTS.md) | Installed/editable profiles, exact receiver pins, native/container entry, and recovery |
| Receive an external benchmark or evolve an administrative contract | [Program runbooks](.agents/runbooks/README.md) | [External benchmark reception](.agents/skills/external-benchmark-reception/SKILL.md) and the named receiving Issue |
| Contribute a reviewed change | [`AGENTS.md`](AGENTS.md) | [`CONTRIBUTING.md`](CONTRIBUTING.md), [`BRANCHING.md`](BRANCHING.md), and [Validation](#validation) |

## Ten-minute proof

With `uv` available, run the repository-owned aggregate in an isolated Python
3.12 environment:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_program.py
```

The result establishes internal contract coherence, release-carrier lifecycle,
skill inventory and lineage, schema and receipt bindings, Program database
contracts, and collaboration surfaces for this checkout. It does not establish
the four-sibling hosted proof, a configured implementation environment, public
delivery, or accountable acceptance. The complete local suite and detached
sibling route are in [Validation](#validation).

## Evidence and authority boundary

This repository owns Program intent, shared contract meaning, examples,
forecasts, and acceptance boundaries. It describes what a collaborator can
verify; it does not turn planned or simulated evidence into an observation of a
running system. The simulation can establish behavior inside its declared
selected future. The enterprise implementation establishes configured runtime
behavior. Comparative evidence establishes the relation between accepted
inputs. Accountable Scientific, Quality, Regulatory, Security, Operations, and
business roles retain their decisions.

Program Pages is a deterministic delivery projection of reviewed source. Its
manifest can establish which bytes were built from which commit. Publication
does not settle a Program release coordinate or a receiving system's behavior.

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

Cross-repository validation reproduces the historical Governance 2.0.1
coordinate as a commit without a release tag, confirms that it belongs to the
accepted Governance 2.1.0 lineage, materializes its exact archive, and runs its
validator against the signed Comparison `machine-node.json` and
`first-receipt.json`. The current Program orientation continues through the
signed Governance 2.1.0 validator.

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

### External benchmark and administrative context

The versioned
[`external-administrative-contracts.v1.json`](src/lims_eln_contracts/resources/external-administrative-contracts.v1.json)
canonical conformance bundle leads to the source-neutral administrative
adapter, administrative context,
raw-preserving insurance classification, coverage enrollment, declared policy,
reviewed decision, impact observation, population scenario, and provenance
contracts. It also records compatibility, invalidation, ownership, examples,
and the event that permits receiving repositories to adopt this family. The
three files under `resources/administrative/` are deterministic, byte-checked
reader projections of this one authored bundle.

The generated
[`administrative-adapter-contract.v1.schema.json`](src/lims_eln_contracts/resources/schemas/administrative-adapter-contract.v1.schema.json)
supports adapter design and replay behavior as a stand-alone boundary. The generated
[`external-administrative-contract-set.v1.schema.json`](src/lims_eln_contracts/resources/schemas/external-administrative-contract-set.v1.schema.json)
provides the dependency-closed family. Open domain vocabularies retain system,
version, code, and display identity; closed workflow states remain explicit.
The [`schema index`](schemas/README.md) places both roots beside the Program's
release and promotion schemas and names each behavior authority.

The repository-owned
[`insurance and administrative adapter`](src/lims_eln_contracts/resources/administrative/insurance-administrative-adapter.v1.json)
example describes representative raw records, six connected ETL stages, and a
convergent replay requirement. It is a design contract rather than an executed
adapter; its local synthetic inputs illustrate mechanics without binding this
family to a particular repository, release, dataset, or runtime. The
independently authored
[`multi-label policy example`](src/lims_eln_contracts/resources/administrative/independent-multilabel-policy.v1.json)
exercises accepted single- and multi-label classifications, unknown and
abstained states, pending enrollment, missing input, precedence-resolved rule
conflict, deterministic evaluation, and a reviewed revision. The
[`administrative counterfactual`](src/lims_eln_contracts/resources/administrative/administrative-counterfactual.v1.json)
keeps clinical evidence and output unchanged while administrative state and
output vary.

[`docs/EXTERNAL_ADMINISTRATIVE_CONTRACTS.md`](docs/EXTERNAL_ADMINISTRATIVE_CONTRACTS.md)
explains ownership, compatibility, invalidation, adoption, and evidence
ceilings. These fixtures establish contract behavior. Population calibration,
live-payer semantics, clinical validity, configured deployment, and accountable
operational acceptance continue through their named evidence routes.

#### Artifact classes and dataset metadata

The Program distributes several machine-readable artifact classes rather than
one undifferentiated dataset. Their current documentation route follows the
meaning they own:

| Artifact class | Examples | Standing and default documentation |
| --- | --- | --- |
| Canonical state | contracts, release coordinates, accepted scenario definitions | Versioned source owns meaning; schema, migration note, and release receipt explain use |
| Synthetic fixtures | administrative examples and Golden Specimen inputs | Independently authored test or demonstration input with its construction and claim ceiling beside it |
| Validation corpora | language-policy and migration cases | Named oracle scope, case inventory, generation or review method, and manifest digest |
| Evidence registries and receipts | open-receipt ledgers, observations, and promotion records | Attributable claims about a named source and environment; they are not training labels or operational ground truth |
| Generated manifests and projections | schemas, reader projections, Pages and release inventories | Derived bytes with one canonical owner, generator, parity check, and replacement event |

This compact classification is the default across the constellation. A JSON
collection earns a package-local dataset card when it becomes an independently
distributed, versioned collection intended for analysis, training,
benchmarking, or reuse outside its owning check. The card then records
motivation, composition, generation or collection, preprocessing and review,
intended and unsuitable uses, population and privacy limits, distribution,
versioning, and maintenance. The Simulation scenario packs are the strongest
near-term candidate when
[Simulation #38](https://github.com/driftframestudios/lims-eln-simulated-final-state/issues/38)
turns them into a shared collection; a solitary executable fixture remains
adequately served by its local README and contract.

[MLCommons Croissant 1.1](https://mlcommons.org/croissant/1.1) becomes useful
only when that collection has stable distributions and record structure worth
machine discovery or loading. At that point its JSON-LD can identify dataset,
`FileObject` or `FileSet`, `RecordSet`, fields, checksums, provenance, and use
conditions. Croissant complements the human-readable dataset card and the
repository's canonical manifests; it does not replace either. The current
Program contracts, Enterprise test fixtures, Comparative receipts, Governance
examples, and Gist Registry teaching fixtures remain below that promotion
threshold. Comparative can reconsider the same route if a versioned
multi-observation calibration or benchmark corpus becomes an independently
published input through
[Comparative #41](https://github.com/driftframestudios/lims-eln-comparative-evidence/issues/41).

Pydantic strengthens these external boundaries through strict types, declared
fields, finite numbers, and immutable model instances. The JSON parser also
rejects duplicate keys and non-finite numeric tokens; callers can proceed by
supplying one value per key and a finite measurement or explicit textual state.

### Install the shared contract package

The package-level [`README`](src/lims_eln_contracts/README.md) owns installation,
reviewed source coordinates, PEP 610 conformance, editable development,
resource-loading examples, replacement rules, and generated-schema checks.
[`release/contract-package-coordinate.json`](release/contract-package-coordinate.json)
remains the machine-readable authority for the reviewed package source and its
scoped digest.

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
suite. Implementation 0.3.2 is pinned; migration-head, catalog, executable,
configured-environment, and accountable-acceptance observations remain open. See
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
is the exact canonical closure emitted by the executable simulation inside the
historical 2.0.1 bundle family and validated by the Program's accepted
Governance 2.1.0 projection.
Its identity is `FUTURE-REALITY-LIMS-2028-001`, and its canonical
JSON digest is
`sha256:33bcc14da24309b7716728b3f0204008e8f7ebf58de75f9e40a5986b421f06b5`.
It contains exactly four receipt families, declares `closed_in_simulation`,
preserves the environment-observed branch as `separate_unasserted_state`, and
grants zero production-authorization effect. The advisory design uses the
distinct identity `FUTURE-REALITY-DESIGN-LIMS-2028-001`; one identity therefore
denotes one modeled reality and authority posture.

[`simulations/future-reality-2028-06-30-v1.json`](simulations/future-reality-2028-06-30-v1.json)
is the byte-identical canonical bundle shared with the simulation and
comparison surfaces. It binds reference result digest
`sha256:5ed067887dc02d2a4c85845d3d25ab6b3fbee857011bed7e5b528e4e58c03861`
and aggregate artifact digest
`sha256:ddbce2fe891bfcd70515005714cdabf34e6430869cc2e2a4daca59016ac6ce3b`.

[`specifications/receipt-vocabulary-map.v1.json`](specifications/receipt-vocabulary-map.v1.json)
version-controls the mapping from individual governance receipt families to
program proof classes and grouped canonical closure families. It also makes
the `closed_in_future_reality` → `closed_in_simulation` and observed
`open` → `separate_unasserted_state` transitions explicit.

## Validation

Focused source checks use an editable package. The complete suite installs the
local package and test profile to exercise installed-wheel provenance as well.

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_program.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/verify_program_release_observation.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_pinned_sources.py --preflight-external
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/check_language.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/check_language.py --format sarif
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/scan_secret_shapes.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_contract_schemas.py --check
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_administrative_examples.py --check
uv run --isolated --no-project --python 3.12 --managed-python \
  --with . --with-requirements requirements-test.txt \
  -- python -m unittest discover -s tests -v
```

The external preflight confirms that every sibling release coordinate is ready
before checkout. Exact cross-repository settlement checks out each sibling at
the commit in `constellation.lock.json`, then runs:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_pinned_sources.py --allow-pending \
  --source simulation=../lims-eln-simulated-final-state \
  --source implementation=../lims-eln-enterprise-implementation \
  --source comparison=../lims-eln-comparative-evidence \
  --source governance=../site-reading-governance
```

The shown paths use the standard sibling layout. The four complete
`ROLE=PATH` bindings can point to another checkout layout.

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
uv run --isolated --no-project --python 3.12 --managed-python \
  -- python scripts/build_pages.py --output ../program-pages-build
uv run --isolated --no-project --python 3.12 --managed-python \
  -- python scripts/validate_projection.py ../program-pages-build
```

The aggregate creates two isolated builds, compares every projected byte,
validates their manifests and relative links, and scans generated text for
credential-shaped values:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  -- python scripts/verify_pages.py
```

The default build remains portable and carries no domain claim. A publication
receiver can provide both `--canonical-origin https://docs.example.org` and
`--cname docs.example.org` to create matching HTML canonical links and `CNAME`.
Branch creation, Pages activation, and domain configuration remain separate
publication actions.

The generated catalog currently selects repository skills whose `SKILL.md`
front matter declares `metadata.source_band: public_ready`. Publication,
version, adaptation, and upstream identities share that standard
`metadata` mapping so standard skill tools and the Program projection read the
same source. Public-possible guidance is also suitable for public use and
refinement; it can join a later catalog when that serves the visitor route. The
current selection keeps the repository-local source-authority map,
constellation-coherence reconciliation, and uv-backed Python execution guide in
the catalog.
The declared band domain is `public_ready` and `public_possible`. A skill with
no band remains outside the projection; a present band uses one of those exact
values so a spelling variation cannot silently change publication standing. An
empty selected set produces no catalog.

The [Agent Skills specification](https://agentskills.io/specification) also
defines optional top-level fields. This repository currently uses the smaller
`name`, `description`, and `metadata` profile. A new optional field joins that
profile when a repository contract defines how Program collaborators and the
public projection should interpret it.

The released projection manifest contract is `1.0.0`. It records the projection
owner, complete file scope, verified source revision and standing, optional
canonical origin, authoritative program-content digest, public-skill inventory,
and byte length plus SHA-256 for every projected file. Unit tests use an explicit
`fixture` standing; ordinary builds accept only a clean exact `HEAD`.

Release changes and consumer migration notes are recorded in
[`CHANGELOG.md`](CHANGELOG.md) and
[`docs/migrations/0.3.1-to-contract-package-0.4.0.md`](docs/migrations/0.3.1-to-contract-package-0.4.0.md).

## Repository map

| Surface | What it owns | Reader route |
| --- | --- | --- |
| [`specifications/`](specifications/) | Program capabilities, invariants, bounded callers, data primitives, migration contracts, and shared vocabulary | Begin with the contract named by the current Issue |
| [`src/lims_eln_contracts/`](src/lims_eln_contracts/) | Typed shared package, released resources, and generated schema source | Use the [package guide](src/lims_eln_contracts/README.md) |
| [`schemas/`](schemas/) | Program release and promotion schemas plus the index for package projections | Use the [schema index](schemas/README.md) |
| [`acceptance/`](acceptance/) and [`probes/`](probes/) | Acceptance roles, proof classes, and question-led evaluation routes | Match the claim to its proof class and accountable role |
| [`simulations/`](simulations/) and [`forecasts/`](forecasts/) | Program-held selected-future and forecast inputs | Retain their declared simulated or planned evidence mode |
| [`database/`](database/) and [`plans/`](plans/) | Cross-repository database findings and modernization plan synthesis | Follow stable record identities into their source contracts |
| [`receipts/`](receipts/) and [`release/`](release/) | Promotion, release, database, package, and repository-role carriers | Read them together before making a release-state claim |
| [`pages/`](pages/) | Source content for the deterministic public orientation projection | Use the [Pages guide](pages/README.md) before building |
| [`.agents/skills/`](.agents/skills/) | Repository-local reusable collaboration methods | Choose from the [skill catalog](.agents/skills/README.md) after current truth is known |
| [`scripts/`](scripts/) and [`tests/`](tests/) | Executable validation, projection, diagnostics, and regression behavior | Prefer the smallest check that answers the active question |

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

## Confined container job

The [finite container entry](infra/README.container-job.md) reuses the constellation's
prepared-input and confined-runtime safeguards. Its source profile, focused
checks, output ownership, and release-evidence boundary remain inspectable.

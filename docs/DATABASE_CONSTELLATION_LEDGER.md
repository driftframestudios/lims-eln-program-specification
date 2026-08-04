# Database constellation ledger

## Purpose and reading posture

This index makes the database-definition review legible across the six-repository
constellation. The machine-readable
[`constellation-finding-index.json`](../database/constellation-finding-index.json)
binds each detailed ledger to its repository, pull request, immutable source
commit, path, raw SHA-256 digest, record identities, and count. The detailed
ledgers remain the source of record for individual evidence, dispositions, and
verification gates.

Repository validation settles source identity, commit shape, immutable retrieval
URL construction, raw digest shape, contiguous record identity, per-source count,
aggregate count, and release-manifest binding. An independent verifier can resolve
each commit-addressed URL and recompute the raw digest. A newer reviewed source
head receives a successor index coordinate, preserving the evidence represented by
this release.

The constellation currently contains **109 finding records**: 32 program-level
discovery findings, 53 reference-pack findings, and 24 active-implementation
findings. These records intentionally overlap. A source defect can appear once
as a discovered contract gap, once as a reference correction, and once as an
implementation proof obligation. The count therefore measures recorded review
perspectives rather than deduplicated defects.

## Coverage register

| Surface | Recorded coverage | Authority and use | Current evidence posture |
|---|---:|---|---|
| [`site-reading-governance`](https://github.com/driftframestudios/site-reading-governance/pull/15) | Six database governance schemas with conforming examples | Defines portable finding, contract, migration-plan, migration-receipt, reconciliation, and release-manifest records. | Schema and validator evidence is repository-observed; environment and accountable acceptance remain separate receipts. |
| This program specification | [32 discovery findings](../database/primitive-findings.json) | Names cross-repository defects and binds each correction to the data or migration contract. | Complete for the reviewed reference trees; successor reviews receive a new ledger version. |
| [`prototype-exemplars`](https://github.com/driftframestudios/prototype-exemplars/pull/4) | 53 reference-pack findings | Preserves the original v0.1 SQL as an explicit legacy baseline and demonstrates a PostgreSQL expand/backfill/validate/cutover/contract path. | Static, clean-install, pre-populated adoption, contract, security, and catalog proofs are release gates; organization-owned representative rehearsal remains receipt-bound. |
| [`lims-eln-enterprise-implementation`](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/10) | 24 implementation findings | Connects primitives to authenticated tenant authority, transactions, migrations, concurrency, recovery, and scientific semantics. | The ledger records corrected, strengthened, partially settled, and receipt-bound findings while preserving their distinct evidence stages. |
| [`lims-eln-simulated-final-state`](https://github.com/driftframestudios/lims-eln-simulated-final-state/pull/14) | One digest-bound database oracle | Supplies the selected-future comparison target: native primitives, phased migration, reconciliation, recovery, and role-bound acceptance. | Simulated evidence is definitive inside the named future reality and carries zero production-authorization effect. |
| [`lims-eln-comparative-evidence`](https://github.com/driftframestudios/lims-eln-comparative-evidence/pull/12) | Typed database-release coordinates and exact JSON comparison | Compares active and simulated database releases without collapsing Boolean and numeric values or mutable input state. | Unit and report-concordance evidence is repository-observed; comparison to a configured release remains receipt-bound. |

## Material finding families

The table below is the constellation-level triage ledger. Each family links an
observed condition to the desired durable state and the evidence that settles
it. Individual file and line coordinates remain in the detailed ledgers.

| Family | Observed condition | Desired durable state | Settlement evidence |
|---|---|---|---|
| Temporal semantics | Instants appeared as text; some aware values retained arbitrary offsets; timestamp types could still admit infinity. | `timestamptz` represents finite instants, `date` represents civil dates, local schedules preserve wall time plus IANA zone, and canonical digests use a released UTC profile. | Catalog assertions, offset-equivalence and daylight-saving fixtures, range queries, retention tests, and migration reconciliation. |
| Identity and tenancy | Unbounded text represented tenant, specimen, actor, and external identities; relationships could cross tenant boundaries. | UUIDs identify internal entities, scoped natural keys retain external meaning, and tenant-owned relationships use tenant-preserving composite keys. | Catalog inspection, cross-tenant foreign-key failures, row-security adversarial tests, and identity reconciliation. |
| Boolean and state semantics | Integer-like flags and independent nullable fields admitted ambiguous state combinations. | Native Booleans express binary facts; constrained enums or state tables express lifecycle state; transition evidence is append-oriented. | Type assertions, exhaustive state-combination tests, transition tests, and historical reconstruction. |
| Exact scientific quantities | Floating or loosely constrained numbers obscured precision, scale, finiteness, qualifiers, analyte meaning, and units. | Exact decimal values retain released precision and scale, UCUM-coded units, source representation, qualifiers, and assay-specific validation. | Boundary vectors, over-scale rejection, unit-conversion qualification, round-trip export, and Scientific and Quality review. |
| JSON and canonicalization | Broad JSON or text envelopes lacked released schemas; language-specific serialization could change digests. | Versioned ingress schemas bound shape and size; canonical byte profiles bind digests; stable domain fields project into typed columns. | Duplicate-key and non-finite rejection, Unicode and decimal vectors, cross-runtime digest parity, and schema-version compatibility tests. |
| Relational integrity | Location, lineage, approval, and evidence relationships were encoded as strings or implicit application conventions. | Referenced hierarchies, composite keys, and explicit evidence nodes preserve domain relationships and tenant scope. | Constraint validation, orphan scans, relationship reconciliation, and representative scientific review. |
| Evidence and audit history | Mutable event, approval, custody, and receipt rows could lose prior meaning or advance independently from current state. | Append-oriented events bind before/after state, actor, authorization, correlation, causation, payload schema, recording time, and supersession. | Mutation-denial tests, state/event atomicity tests, signature verification, reconstruction exercises, and accountable acceptance. |
| Inbox, outbox, and idempotency | Keys could ignore tenant or content; queue state omitted lease and recovery semantics; payload meaning could drift after commit. | Tenant-scoped identities bind canonical request content; immutable messages use exhaustive states, fenced claims, finite leases, attempts, terminal reasons, and transactional domain writes. | Collision tests, duplicate delivery, concurrent claims, expired-lease recovery, crash points, and downstream reconciliation. |
| Migration history and serialization | Bootstrap scripts lacked durable history, checksums, deployment serialization, and supported-baseline declarations. | Immutable forward SQL uses the selected Flyway Community profile for ordered application, checksummed history, database coordination, PostgreSQL transactions, explicit baselining, and status. | Flyway validate/info evidence, clean install, every supported predecessor upgrade, transactional failure, exact replay, zero pending work, and schema-fingerprint parity. |
| Expand/contract and legacy conversion | Direct replacement could round quantities, reorder versions, infer identity, or discard source meaning before acceptance. | Additive columns and tables precede resumable conversion; deterministic mappings, exception ownership, dual compatibility, validation, cutover, and evidence-bound retirement preserve meaning. | Preflight profiling, checkpoint replay, conversion ledgers, exception closure, zero-based ordering fixtures, and post-cutover observation. |
| Ownership, privileges, and row security | Object ownership and broad grants could let runtime identities bypass intended boundaries or mutate immutable content. | A migration owner controls DDL; workload roles use least privilege and `NOBYPASSRLS`; forced row security and database-verified tenant assertions govern access. | ACL and owner inspection, direct-SQL adversarial tests, key-confidentiality tests, assertion expiry/tamper tests, and Security review. |
| Schema fingerprint and runtime semantics | Object-name checks omitted policies, grants, triggers, indexes, function definitions, constraint validation, and engine-major behavior. | A canonical catalog projection covers behavior-bearing objects and runs on every supported PostgreSQL major. | PostgreSQL-major matrix, normalized catalog digest, clean/upgrade convergence, planner-shaped tenant probes, and source/target comparison. |
| Secrets and configuration | Connection strings or verification material could drift into source, fixtures, logs, or broad environment variables. | Parameter Store supplies scoped non-secret configuration; Secrets Manager supplies rotatable secret material; workload identity and KMS policy bound retrieval. | Secret-shape scans, IAM simulation, runtime retrieval and rotation, redacted telemetry, revocation, and incident rehearsal. |
| Simulation fidelity | In-memory doubles could collapse Boolean and numeric identity, retain mutable aliases, or model temporal values as strings. | The selected-future oracle and in-memory doubles preserve exact JSON types, immutable snapshots, canonical aware instants, and native database primitives. | Mutation tests, Boolean-versus-number regression vectors, oracle digest validation, and comparison with the active database release. |
| Release coordinates and accountable acceptance | A passing unit suite alone could appear equivalent to configured migration, recovery, security, or scientific acceptance. | Release records bind commit, migration head, manifest and catalog digests, environment identity, reconciliation, recovery, residual risk, and bounded role decisions. | Configured vendor environments; representative migration and restore rehearsals; production security and observability; separate Scientific, Quality, and Regulatory acceptance. |

## Source-of-record map

1. **Discovery and intended correction:**
   [`database/primitive-findings.json`](../database/primitive-findings.json),
   [`specifications/data-primitives.json`](../specifications/data-primitives.json),
   and
   [`specifications/database-migration.json`](../specifications/database-migration.json).
2. **Reference implementation and legacy comparison:** the reference pack's
   `database/data-primitive-ledger.json`, immutable legacy v0.1 baseline,
   canonical migrations, upgrade phases, contract checks, and rehearsal
   receipts. Its custom runner is transition input rather than the target
   program architecture.
3. **Active implementation disposition:** the implementation repository's
   `docs/data-primitive-corrective-ledger.md`, reviewed versioned SQL,
   PostgreSQL adversarial suite, retained end-to-end and parameterized tests,
   Flyway transition evidence, and hosted proof receipt.
4. **Selected-future target:** the simulation repository's
   `database/final-state-database-oracle-v1.json` and executable oracle model.
5. **Difference adjudication:** the comparative repository's typed
   database-release coordinate, observation envelope, comparison profile, and
   generated report.
6. **Portable governance:** the governance repository's Draft 2020-12 schemas,
   examples, and conformance tests.

The detailed reference baseline now lives under `database/legacy/v0.1`. That
location makes its evidentiary role explicit: it is input to the supported
upgrade path, while the versioned migration chain defines the current database
state.

## Explicit cross-repository decisions

The ledgers also expose deliberate differences which require settlement before
constellation promotion:

| Decision | Current representations | Required settlement |
|---|---|---|
| Migration mechanism | Earlier program and selected-future records named Alembic while the implementation and reference pack demonstrated bespoke SQL runners with distinct history tables. | The program now states tool-neutral capabilities and selects Flyway Community 13.0.0 for implementation. Flyway owns ordering, checksummed history, database coordination, PostgreSQL transactional execution, explicit baselining, and status; the release coordinate records the resolved executable digest and catalog evidence. |
| Canonical internal identity | The program contract and reference pack use UUID identities with scoped external natural keys. The active implementation retains bounded text identities in its first vertical slice. | `DP-013` settles the implementation identity inventory and migration; any retained text key receives explicit external-identity semantics and tenant-scoped uniqueness. |
| Digest and JSON profile | The program and reference pack name binary SHA-256 and versioned canonicalization. The active implementation still contains application-governed JSON and text-encoded digest boundaries. | `DATA-CANON-001`, `DATA-JSON-001`, and `DP-015` bind one cross-runtime byte profile, schema corpus, typed projection decision, and forward migration. |
| Baseline entry | A reconstructed synthetic v0.1 fixture and an already-populated v0.1 database represent different evidence events. | Flyway keeps `baselineOnMigrate=false`. Populated adoption begins with schema and data attestation, an explicit reviewed baseline coordinate, and forward migrations; clean installation runs the complete versioned SQL history. |
| Ownership boundary | A single migration label previously combined program schema evolution, vendor upgrades, cross-vendor data movement, and release acceptance. | Flyway executes program-owned PostgreSQL evolution; vendor-supported lifecycle paths govern Sapio, Benchling, and LabKey; adapters, exports/imports, DMS options, and reconciliation govern cross-vendor movement; release workflows bind accountable evidence. |
| Migration evidence | Repository-hosted synthetic proofs exercise structure and adversarial behavior. Configured records, workload shape, lock budgets, restore topology, and accountable review remain environment-specific. | The four substantive receipt classes close through configured vendors, representative migration/restore, production security/observability, and separate Scientific, Quality, and Regulatory decisions. |

These differences are visible design coordinates rather than silent
equivalences. A local passing suite advances its named evidence stage; promotion
also requires contract concordance or an explicitly accepted successor
decision.

## Probability frame and selected route

All five program route estimates answer one conditional event:

> Given a capable hybrid team, two implementation increments, the stated
> gates, and a representative PostgreSQL rehearsal, the route yields a
> reviewable enterprise-grade database release candidate that preserves
> qualified scientific semantics, tenant isolation, audit reconstruction, and
> recoverability and passes independent principal-engineer, database,
> security, operations, and scientific review with follow-up limited to
> accepted non-critical items.

The machine-readable plan set records the team, horizon, gate stability,
representative rehearsal, and independent-review conditions as separate
assumptions. Each reevaluation interstitial either retains those conditions or
recalibrates the estimates before the next stage.

The reference-pack and active-implementation tables are conditional derivatives,
rather than additional estimates of this same event. The reference table narrows
the horizon to one promotion-ready artifact tranche; the implementation table
narrows it to one active release cycle and vertical slice. They support local
sequencing. Cross-route comparison uses the canonical program estimates unless a
future release publishes an explicit calibration transform between events. The
machine-readable constellation index records each exact estimated event and its
relationship to the canonical event beside each source coordinate.

The five program plans range from 0.54 to 0.89. The selected synthesis is 0.88
with a 0.79–0.94 credible range. It combines a canonical relational core,
selective append-oriented event semantics, dual-run reconciliation, and the
selected-future comparison oracle. The implementation and reference pack use
the migration-first route as their execution spine. These values are
judgmental planning estimates; each interstitial recalibrates them with
executable evidence.

`FLYWAY-TRANSITION-EQUIVALENCE-001` is a separate conditional derivative. It
estimates a **0.91** probability with a **0.84–0.96** credible range that one
corrective tranche replaces bespoke orchestration with Flyway Community 13.0.0
while the retained clean, predecessor, failure, replay, zero-pending-work,
convergence, and end-to-end domain scenarios preserve their critical contract
outcomes. The first Flyway-driven rehearsal recalibrates this estimate.

## Chain of action and reevaluation interstitials

1. **Settle semantic ownership.** Bind intended use, systems of record,
   primitive meaning, tenant boundaries, and accountable roles.
   **Interstitial:** profile source values and reopen any primitive whose
   observed distribution changes its meaning.
2. **Adopt the Flyway profile.** Preserve legacy bytes, map reviewed SQL into
   immutable Flyway versions, attest populated predecessors through explicit
   baselines, and reuse the existing end-to-end and parameterized suites.
   **Interstitial:** compare Flyway validate/info state, supported baselines,
   retained test results, and runtime catalog before data movement.
3. **Expand and convert.** Add canonical structures, use deterministic and
   checkpointed transformations, and retain owned exceptions.
   **Interstitial:** compare identities, relationships, quantities, temporal
   meaning, artifacts, and audit evidence before cutover.
4. **Validate authority and behavior.** Exercise tenant isolation, privileges,
   immutable history, idempotency, concurrency, queue recovery, and catalog
   parity across supported PostgreSQL majors.
   **Interstitial:** route every failure to the owning contract, migration,
   threat model, or operating assumption.
5. **Rehearse cutover and recovery.** Use representative volume and shape,
   measure locks and lag, restore cleanly, and compare semantic digests.
   **Interstitial:** update recovery budgets, exception ownership, and route
   probability from the observed rehearsal.
6. **Settle bounded acceptance.** Engineering, Security, Operations,
   Scientific, Quality, and Regulatory reviewers receive the same immutable
   evidence packet while retaining their distinct decision authority.
   **Interstitial:** record limitations, residual risks, and requalification
   triggers with each decision.
7. **Promote and observe.** Bind the protected coordinate, migration head,
   catalog digest, receipts, gates, and monitoring window.
   **Interstitial:** new engine, schema, source distribution, threat, intended
   use, or role decision reopens the dependent evidence branch.

## Evidence basis

- PostgreSQL defines native temporal, exact numeric, UUID, JSON, constraint,
  row-security, and lock behavior in its current manuals:
  <https://www.postgresql.org/docs/current/datatype-datetime.html>,
  <https://www.postgresql.org/docs/current/datatype-numeric.html>,
  <https://www.postgresql.org/docs/current/datatype-uuid.html>,
  <https://www.postgresql.org/docs/current/datatype-json.html>,
  <https://www.postgresql.org/docs/current/ddl-constraints.html>,
  <https://www.postgresql.org/docs/current/ddl-rowsecurity.html>, and
  <https://www.postgresql.org/docs/current/explicit-locking.html>.
- Flyway documents immutable versioned migrations and schema-history evidence:
  <https://documentation.red-gate.com/fd/versioned-migrations-273973333.html>
  and
  <https://documentation.red-gate.com/flyway/flyway-concepts/migrations/flyway-schema-history-table>.
- Flyway documents checksum validation, JSON command output, and the safety
  posture of explicit baselining:
  <https://documentation.red-gate.com/flyway/reference/commands/validate>,
  <https://documentation.red-gate.com/flyway/reference/command-line-parameters/output-type-parameter>,
  and
  <https://documentation.red-gate.com/flyway/reference/configuration/flyway-namespace/flyway-baseline-on-migrate-setting>.
- AWS DMS Schema Conversion automates compatible schema conversion while
  surfacing objects that require human action:
  <https://docs.aws.amazon.com/dms/latest/userguide/schema-conversion.html>.
- Strong Migrations provides field-tested examples of separating hazardous
  changes into safer multi-step transitions:
  <https://github.com/ankane/strong_migrations>.
- The Npgsql timestamp migration discussion and the Prefect PostgreSQL upgrade
  incident illustrate how temporal and migration assumptions surface in real
  libraries and operating systems:
  <https://github.com/npgsql/efcore.pg/pull/1214> and
  <https://github.com/PrefectHQ/prefect/issues/18263>.
- FDA data-integrity and laboratory-control guidance anchors attributable,
  contemporaneous, original, accurate, complete, consistent, enduring, and
  available evidence in regulated laboratory work:
  <https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers>
  and
  <https://www.fda.gov/drugs/guidances-drugs/questions-and-answers-current-good-manufacturing-practice-requirements-laboratory-controls>.

These sources establish engine behavior and durable field lessons. Intended
use, representative distributions, qualified engine majors, operating budgets,
and accountable acceptance remain explicit program evidence.

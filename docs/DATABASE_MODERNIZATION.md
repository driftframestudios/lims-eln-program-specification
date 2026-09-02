# Database modernization program

This program turns the cross-repository database review into a versioned,
machine-checkable collaboration surface. It establishes the desired data
semantics before implementation code selects concrete migrations, then keeps
implementation, rehearsal, recovery, and release evidence connected through
stable identifiers and digests.

The program specification has design authority. The implementation repository
owns executable PostgreSQL release artifacts. The program contract states
tool-neutral migration capabilities, and the implementation profile selects
Flyway Community 13.0.0. This settles a deliberate ownership boundary: Flyway
supplies migration ordering, history, checksums, database coordination,
transactional execution, baselining, and status; repository SQL supplies the
domain schema and data transition semantics. Configured environments and
representative rehearsals supply observed evidence. Scientific, Quality,
Regulatory, Security, Operations, data, platform, and business roles retain
their bounded acceptance authority.

## Ownership boundaries

| Concern | Owner | Durable result |
|---|---|---|
| Program-owned PostgreSQL schema evolution | Implementation database release | Reviewed versioned SQL, Flyway state, catalog convergence, and retained integration evidence |
| Sapio, Benchling, and LabKey lifecycle | Vendor-supported platform operations | Version-pinned vendor upgrades, APIs or SDKs, configuration, conformance, and support evidence |
| Cross-vendor data movement | Data migration program | Vendor adapters, exports/imports, optional AWS DMS or DMS Schema Conversion, checkpointed transformations, reconciliation, and owned exceptions |
| Database release and acceptance | Release governance and bounded accountable roles | Recovery, security, observability, Scientific, Quality, Regulatory, and release decisions bound to one immutable coordinate |

Flyway evolves program-owned PostgreSQL objects. It remains outside the vendor
product upgrade lifecycle, scientific mapping decisions, cross-vendor semantic
reconciliation, restore ownership, and accountable acceptance. That separation
concentrates custom code on the LIMS/ELN opportunity rather than on a general
database migration engine.

## Finding ledger

[`database/primitive-findings.json`](../database/primitive-findings.json)
records 32 critical or high findings from the two reviewed reference trees.
Each finding carries:

- a stable `DBF-*` identifier;
- repository, path, and line evidence;
- the observed representation and its material effect;
- an affirmative target state and correction;
- bindings into the data or migration contract.

The ledger covers temporal semantics, identifiers, digests, decimal
measurements and units, controlled vocabularies, JSON boundaries, nullability,
relational integrity, evidence immutability, tenant row security, indexing,
idempotency, migration lifecycle, reconciliation, validation, and reference
fork convergence. Its sources include current PostgreSQL documentation for
[date and time types](https://www.postgresql.org/docs/current/datatype-datetime.html),
[constraints](https://www.postgresql.org/docs/current/ddl-constraints.html),
[row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html),
[JSON types](https://www.postgresql.org/docs/current/datatype-json.html),
[numeric types](https://www.postgresql.org/docs/current/datatype-numeric.html),
and [partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html),
plus Flyway's official references for
[versioned migrations](https://documentation.red-gate.com/fd/versioned-migrations-273973333.html),
[schema history](https://documentation.red-gate.com/flyway/flyway-concepts/migrations/flyway-schema-history-table),
[validation](https://documentation.red-gate.com/flyway/reference/commands/validate),
[JSON command output](https://documentation.red-gate.com/flyway/reference/command-line-parameters/output-type-parameter),
and
[explicit baselining](https://documentation.red-gate.com/flyway/reference/configuration/flyway-namespace/flyway-baseline-on-migrate-setting).
AWS documents the role and limits of
[DMS Schema Conversion](https://docs.aws.amazon.com/dms/latest/userguide/schema-conversion.html)
for cross-engine conversion; program reconciliation remains responsible for
scientific meaning and owned exceptions.

These sources establish engine behavior. Intended-use semantics, qualified
engine majors, representative distributions, lock budgets, and acceptance
decisions remain program- and environment-specific evidence.

[`database/constellation-finding-index.json`](../database/constellation-finding-index.json)
adds the cross-repository evidence coordinate. It binds the program, reference,
and active-implementation ledgers to immutable source commits, raw file digests,
record identities, and counts. Its aggregate retains intentional overlap between
discovery, reference correction, and implementation proof obligations.

## Comparative plans and probability event

[`plans/database-modernization-plans.json`](../plans/database-modernization-plans.json)
defines one probability event:

> Given a capable hybrid team, two implementation increments, the stated
> gates, and a representative PostgreSQL rehearsal, the route yields a
> reviewable enterprise-grade database release candidate that preserves
> qualified scientific semantics, tenant isolation, audit reconstruction, and
> recoverability and passes independent principal-engineer, database,
> security, operations, and scientific review with follow-up limited to
> accepted non-critical items.

| Route | Estimate | Credible range | Most useful contribution |
|---|---:|---:|---|
| Constrained primitive retrofit | 0.54 | 0.39–0.67 | Quickly corrects high-risk illustrative primitives |
| Canonical relational model with migration spine | 0.83 | 0.73–0.90 | Establishes the durable system of record |
| Event-led evidence core | 0.71 | 0.57–0.82 | Preserves consequential history and approval meaning |
| Dual-run migration and reconciliation program | 0.89 | 0.80–0.95 | Produces encounter-based migration confidence |
| Simulated final-state database twin | 0.78 | 0.66–0.87 | Supplies an explicit comparison target |

These are conditional planning estimates rather than frequencies observed
from a shared trial population. The plan set separates five conditioning
assumptions: named multidisciplinary ownership; a two-increment horizon with
review and remediation capacity; stable gates or prompt recalibration;
representative PostgreSQL and data access; and shared criteria with owned
non-critical follow-up. Their intervals communicate uncertainty and
recalibrate when schema inventory, data profiling, representative rehearsal,
concurrency, recovery, or acceptance evidence changes the fit.

The reference-pack and active-implementation probability tables answer narrower
local events. They are declared conditional derivatives for artifact-level and
release-cycle sequencing and remain outside direct numerical comparison with the
canonical program routes. Recalibration can promote a local event into a future
program event through an explicit versioned plan-set update.

`DB-SYNTHESIS-001` combines the canonical relational core, selective event
semantics, dual-run reconciliation, and simulated comparison target. It uses
the constrained retrofit to close unsafe examples early. Its estimated
probability is 0.88 with a 0.79–0.94 credible range under the declared
assumptions.

### Corrective Flyway transition estimate

`FLYWAY-TRANSITION-EQUIVALENCE-001` asks this narrower question:

> Given the reviewed versioned PostgreSQL SQL, existing end-to-end integration
> suite, parameterized migration scenarios, Flyway Community 13.0.0, and one
> corrective tranche, the implementation replaces bespoke migration
> orchestration while preserving clean installation, populated predecessor
> upgrade, failure atomicity, replay, zero-pending-work, and clean-versus-upgrade
> convergence evidence without a critical domain-contract regression.

The estimate is **0.91**, with a **0.84–0.96** credible range. It is a
conditional derivative used to sequence the corrective transition and remains
numerically separate from the five canonical route estimates. The first
Flyway-driven rehearsal recalibrates it against actual retained-test coverage,
explicit baseline fit, and catalog convergence.

## Canonical data contract

[`specifications/data-primitives.json`](../specifications/data-primitives.json)
binds every finding assigned to storage semantics into 13 policies:

- timezone-aware instants, explicit local-date and duration semantics;
- canonical UUID identity and scoped natural-key uniqueness;
- algorithm-qualified binary digests over canonical bytes;
- exact decimal measurements with explicit units and qualified precision;
- controlled vocabularies with forward-compatible unknown-value handling;
- validated `jsonb` envelopes with schema version and canonicalization rules;
- explicit required, optional, unknown, pending, and not-applicable states;
- tenant ownership, composite integrity, row security, and least-privilege roles;
- append-only domain events, corrections, and approval evidence;
- transactional inbox, outbox, idempotency, and artifact identity;
- immutable evidence coordinates and workload-shaped access paths.

Entity bindings state which policies apply to tenants, specimens, samples,
measurements, artifacts, approvals, events, inbox/outbox records, and migration
evidence. Requirements, invariants, scenarios, and future-observed receipts
make the contract executable as specification by example.

## Migration and reconciliation contract

[`specifications/database-migration.json`](../specifications/database-migration.json)
defines tool-neutral PostgreSQL schema-migration requirements and selects
Flyway Community 13.0.0 as the corrective implementation profile. The contract
retains five domain phases:

1. inventory and profile the source at a stable snapshot;
2. introduce additive canonical structures and dual-compatible reads;
3. backfill with resumable checkpoints and evidence-bound transformations;
4. dual-run, reconcile, and repair classified exceptions;
5. cut over, observe, exercise recovery, and retire superseded structures under
   an approved successor migration.

Every implementation migration receives one immutable version, predecessor,
checksum, owner, lock posture, transaction posture, forward plan, recovery
plan, and affected-contract inventory. Flyway owns ordered application,
checksummed history, database coordination, validation, status, and explicit
baseline adoption. The implementation records `validate`, `info`, and `migrate`
JSON rather than treating Flyway's internal history relation as a custom API.

Release checks exercise schema
convergence, rows and keys, field-level scientific semantics, measurements and
units, custody and event order, artifacts, approvals and signatures, tenant
isolation, and representative distributions. Thresholds and owned exception
registers remain explicit.

The release gates bind static contract review, migration rehearsal, semantic
reconciliation, concurrent idempotency and event behavior, tenant security,
restore and rollback, and accountable release acceptance. The program
represents database rollback as a rehearsed recovery strategy; forward
remediation remains the ordinary evolution path after dependent writes exist.
The selected Community profile uses only Community commands and capabilities;
Teams- and Enterprise-tier undo, drift, dry-run, diff, and generation features
remain outside this release contract.

### Test-preserving transition

The migration engine changes while the domain oracle stays stable. The existing
end-to-end PostgreSQL integration suite retains its schema, tenancy, event,
measurement, custody, outbox, and evidence assertions. The parameterized
migration suite retains clean installation, populated predecessor upgrade,
incompatible-preflight rejection, transactional failure, replay,
zero-pending-work, and clean-versus-upgrade convergence scenarios. Flyway
becomes the migration executor for those tests. Tests that only reproduce
ordering, history, checksum, or coordination behavior move to assertions over
Flyway `validate` and `info` output or retire when they duplicate the selected
product contract.

## Release manifest and open receipts

[`release/database-release-manifest.json`](../release/database-release-manifest.json)
binds the ledger, plan set, contracts, requirements, invariants, and scenarios
by path, version, and SHA-256 digest. Its implementation migration head,
catalog digest, and exact Flyway executable artifact digest remain pending
until the implementation repository publishes an immutable candidate
coordinate. The profile selects version 13.0.0 while the environment-specific
multi-platform artifact digest remains observed release evidence.

[`receipts/database-open-receipts.json`](../receipts/database-open-receipts.json)
tracks eight future-observed receipts for data semantics, tenant isolation,
event history, concurrency and idempotency, migration execution,
reconciliation, recovery, and release acceptance. Each receipt names its
success event, accountable roles, required evidence, and requalification
triggers. A simulated future can exercise the complete shape while preserving
the independently open environment-observed branch.

## Chain of action and interstitials

The synthesized route has seven stages. Every stage ends with an interstitial
that compares observed signals with assumptions and routes a bounded response.

1. **Settle semantics and ownership.** Confirm intended use, systems of record,
   primitive policies, tenant boundaries, event meaning, and accountable roles.
2. **Adopt the Flyway profile.** Inventory every database object, map reviewed
   SQL into immutable Flyway versions, preserve explicit predecessor baselines,
   and reuse the existing end-to-end and parameterized test scenarios.
3. **Build the canonical model.** Implement constraints, indexes, row security,
   transactional event/inbox/outbox behavior, and representative database
   contract tests.
4. **Backfill and reconcile.** Run checkpointed transformations and compare all
   nine dimensions against approved thresholds and owned exceptions.
5. **Exercise concurrency and recovery.** Rehearse retries, duplicate delivery,
   restore, rollback, neutral-reader export, and operating objectives.
6. **Settle accountable acceptance.** Present evidence packets to each bounded
   domain and operational role and record current decisions.
7. **Promote and monitor.** Bind the protected implementation coordinate,
   migration head, catalog, receipts, gates, residual risks, and requalification
   triggers into the observed release manifest.

Interstitials ask whether evidence changes primitive semantics, representative
fit, risk ownership, lock and recovery budgets, or the probability estimate.
The response updates the owning contract or implementation artifact, records
the change, reruns affected scenarios, and preserves prior evidence for
comparison.

## Verification

The program validator enforces stable finding identities, complete finding-to-
contract coverage, one canonical probability event, one bounded Flyway
transition event, five plans, a seven-stage chain
with seven interstitials, contract reference closure, eight open receipts,
manifest digest integrity, Coordination Horizon bindings, and orientation
surface concordance. The unit suite includes mutation cases for omitted
findings, stale digests, and unresolved program references.

The release candidate advances after the program validator, language policy,
secret-shape scan, pinned-source preflight, and unit suite all pass. Observed
database promotion additionally requires implementation, rehearsal, recovery,
and accountable acceptance evidence identified by the open receipts.

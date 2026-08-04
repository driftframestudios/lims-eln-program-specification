# Database modernization program

This program turns the cross-repository database review into a versioned,
machine-checkable collaboration surface. It establishes the desired data
semantics before implementation code selects concrete migrations, then keeps
implementation, rehearsal, recovery, and release evidence connected through
stable identifiers and digests.

The program specification has design authority. The implementation repository
owns executable PostgreSQL and Alembic artifacts. Configured environments and
representative rehearsals supply observed evidence. Scientific, Quality,
Regulatory, Security, Operations, data, platform, and business roles retain
their bounded acceptance authority.

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
plus the official [Alembic migration guide](https://alembic.sqlalchemy.org/en/latest/)
and [Flyway schema-history reference](https://documentation.red-gate.com/fd/flyway-schema-history-table-273973417.html).

These sources establish engine behavior. Intended-use semantics, qualified
engine majors, representative distributions, lock budgets, and acceptance
decisions remain program- and environment-specific evidence.

## Comparative plans and probability event

[`plans/database-modernization-plans.json`](../plans/database-modernization-plans.json)
defines one probability event: the probability that a route produces a
reviewable enterprise-grade database release candidate within two
implementation increments while preserving qualified scientific semantics,
tenant isolation, audit reconstruction, and recoverability.

| Route | Estimate | Credible range | Most useful contribution |
|---|---:|---:|---|
| Constrained primitive retrofit | 0.54 | 0.39–0.67 | Quickly corrects high-risk illustrative primitives |
| Canonical relational model with migration spine | 0.83 | 0.73–0.90 | Establishes the durable system of record |
| Event-led evidence core | 0.71 | 0.57–0.82 | Preserves consequential history and approval meaning |
| Dual-run migration and reconciliation program | 0.89 | 0.80–0.95 | Produces encounter-based migration confidence |
| Simulated final-state database twin | 0.78 | 0.66–0.87 | Supplies an explicit comparison target |

These are conditional planning estimates rather than frequencies observed
from a shared trial population. Their intervals communicate uncertainty and
recalibrate when schema inventory, data profiling, representative rehearsal,
concurrency, recovery, or acceptance evidence changes the fit.

`DB-SYNTHESIS-001` combines the canonical relational core, selective event
semantics, dual-run reconciliation, and simulated comparison target. It uses
the constrained retrofit to close unsafe examples early. Its estimated
probability is 0.88 with a 0.79–0.94 credible range under the declared
assumptions.

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
defines a PostgreSQL and Alembic migration spine with five phases:

1. inventory and profile the source at a stable snapshot;
2. introduce additive canonical structures and dual-compatible reads;
3. backfill with resumable checkpoints and evidence-bound transformations;
4. dual-run, reconcile, and repair classified exceptions;
5. cut over, observe, exercise recovery, and retire superseded structures under
   an approved successor migration.

Every implementation migration receives one immutable revision, predecessor,
checksum, owner, lock posture, transaction posture, forward plan, recovery
plan, and affected-contract inventory. Release checks exercise schema
convergence, rows and keys, field-level scientific semantics, measurements and
units, custody and event order, artifacts, approvals and signatures, tenant
isolation, and representative distributions. Thresholds and owned exception
registers remain explicit.

The release gates bind static contract review, migration rehearsal, semantic
reconciliation, concurrent idempotency and event behavior, tenant security,
restore and rollback, and accountable release acceptance. The program
represents database rollback as a rehearsed recovery strategy; forward
remediation remains the ordinary evolution path after dependent writes exist.

## Release manifest and open receipts

[`release/database-release-manifest.json`](../release/database-release-manifest.json)
binds the ledger, plan set, contracts, requirements, invariants, and scenarios
by path, version, and SHA-256 digest. Its implementation migration head and
catalog digest remain pending until the implementation repository publishes
an immutable candidate coordinate.

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
2. **Publish the migration catalog.** Inventory every database object and bind
   each Alembic revision to checksum, dependency, lock, recovery, and contract
   effects.
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
contract coverage, one named probability event, five plans, a seven-stage chain
with seven interstitials, contract reference closure, eight open receipts,
manifest digest integrity, Coordination Horizon bindings, and orientation
surface concordance. The unit suite includes mutation cases for omitted
findings, stale digests, and unresolved program references.

The release candidate advances after the program validator, language policy,
secret-shape scan, pinned-source preflight, and unit suite all pass. Observed
database promotion additionally requires implementation, rehearsal, recovery,
and accountable acceptance evidence identified by the open receipts.

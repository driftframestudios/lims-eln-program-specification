# LIMS/ELN Program Specification

This repository owns the questions, data semantics, and representative scenarios
used to evaluate LIMS and ELN products and the surrounding integration architecture.
Runtime services remain with implementation frameworks; organizational workflows
retain product selection, Quality, Regulatory, security, and release decisions; Git
and artifact registries provide release identity.

The primary audience is a hybrid human–AI team comparing vendor capabilities,
implementation fit, migration risk, and the material effects on scientists,
laboratory operations, technical teams, and evaluators.

## Start here

| Surface | Purpose |
|---|---|
| [`specifications/capabilities.json`](specifications/capabilities.json) | Material capabilities shared across product candidates |
| [`specifications/invariants.json`](specifications/invariants.json) | Stable behavior that implementations and vendor adapters preserve |
| [`specifications/data-primitives.json`](specifications/data-primitives.json) | Canonical temporal, identity, measurement, unit, tenant, event, and provenance semantics |
| [`specifications/data-contract-concordance.json`](specifications/data-contract-concordance.json) | Questions and evidence levels for comparing vendor representations |
| [`specifications/database-migration.json`](specifications/database-migration.json) | Flyway delivery, expand-and-contract, reconciliation, and transactional outbox requirements |
| [`examples/scenarios.json`](examples/scenarios.json) | Specification-by-example fixtures for configured environments |
| [`probes/catalog.json`](probes/catalog.json) | Principal-level Practitioner Probes for technical and evaluative conversations |
| [`machine-node.json`](machine-node.json) | Documentary navigation and hydration for future collaborators |

## Evaluation posture

Evidence remains legible through four descriptive levels:

1. `documented` — official documentation or a supported API contract describes
   the behavior;
2. `configured` — the behavior is visible in a named evaluation environment;
3. `exercised` — a repeatable test demonstrates the behavior with representative
   synthetic data;
4. `observed` — a production-representative run supplies measurements and a
   governed raw-evidence locator.

These levels describe evidence quality. The organization’s Quality, Regulatory,
security, procurement, and scientific processes retain their established decision
responsibilities.

## Database delivery

The program uses Flyway Community for program-owned PostgreSQL migrations. The
contract selects:

- UTC timestamp versions such as `V20260804164600__add_specimen_status.sql`;
- `outOfOrder=true` for late-merging parallel work;
- `validateMigrationNaming=true` and immutable applied versioned migrations;
- clean-install and populated-predecessor tests in ephemeral PostgreSQL;
- expand–transition–contract changes across independently deployable application
  releases;
- repeatable migrations for replaceable views and functions;
- Flyway `validate`, `info`, `migrate`, and pipeline-mediated `repair` through the
  product’s supported interfaces.

Vendor-managed products retain their documented upgrade and configuration
mechanisms. Flyway applies only to the program-owned PostgreSQL model.

## Event delivery

Cross-service domain events use a transactional outbox when the aggregate change
and integration intent must commit together. The application owns event meaning,
schema version, stable identity, and idempotent consumption. The
[Debezium Outbox Event Router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)
owns change-data capture and routing. The selected broker, consumer framework, and
observability platform supply replay, idempotency, failure handling, and operational
visibility.

## Vendor comparison

The scenarios are designed for Sapio, Benchling, LabKey, and additional candidates.
They examine:

- specimen lifecycle and correction semantics;
- custody under concurrency;
- instrument ingress and raw-artifact fidelity;
- supported APIs, SDKs, webhooks, batch operations, and readback;
- scientific numeric and unit fidelity;
- migration, restore, data exit, and representative reconciliation;
- tenant isolation, configuration, secret lifecycle, and observability;
- transactional event delivery and duplicate handling.

The comparative-evidence repository consumes caller-supplied records and produces
normalized factual differences for the organization’s established decision
processes.

## Validation

Active validation uses JSON Schema and ordinary unit tests:

```sh
python3 -m pip install --editable ".[validation]"
python3 -m unittest discover -s tests -v
```

The test suite validates the active specification schemas, cross-references, Flyway
configuration, outbox framework boundary, and Machine Node navigation. Repository
branch policy belongs in GitHub Rulesets. Secret scanning and push protection belong
in GitHub’s repository security configuration.

## Historical quarantine

[`quarantine/legacy-control-plane/`](quarantine/legacy-control-plane/) preserves
the earlier bounded-caller, acceptance, simulated-closure, Coordination Horizon,
receipt, digest-binding, custom validator, and branch-policy artifacts for historical
study. CI and active specifications load the top-level specification, schema,
scenario, probe, and documentary paths listed in this README.

The bounded-caller material may later hydrate a small Visitor-pattern example that
maps framework-native request contexts into common read/write operations. That reuse
requires a concrete implementation need and keeps identity, policy, workflow, and
approval behavior in the selected frameworks.

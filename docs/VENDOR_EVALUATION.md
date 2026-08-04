# Vendor-evaluation field guide

## Comparison unit

Compare one named product version in one named configuration against one released
scenario. Record the observation time, official documentation, configured behavior,
result values, known limitations, and governed source locator.

The comparison keeps four evidence levels distinct: documented, configured,
exercised, and observed. A missing result remains visibly unmeasured.

## Minimum product tranche

For each candidate, examine:

1. specimen, aliquot, container, plate, assay, result, and artifact identity;
2. lifecycle, correction, signature, audit, and export semantics;
3. precision, unit, qualifier, interval, detection-limit, and vocabulary support;
4. API, SDK, webhook, batch, rate-limit, retry, idempotency, and readback behavior;
5. tenant isolation, workload identity, secret lifecycle, and diagnostic privacy;
6. instrument ingress, raw artifact retention, parser versioning, and replay;
7. migration, restore, rollback, data exit, and neutral-reader access;
8. event integration, including transactional outbox fit and supported CDC or broker
   connectors;
9. operational measures, support lifecycle, upgrade path, and total ownership cost.

## Configured-environment method

Use a bounded synthetic corpus with representative relationships, measurements,
artifacts, corrections, duplicate messages, late messages, and malformed inputs.
Run the same scenario through the supported vendor interface and read the result
back independently. Preserve raw outputs in governed evidence storage and publish a
redacted comparison record.

The method emphasizes supported product behavior. Adapter hypotheses remain marked
as hypotheses until a configured environment exercises them.

## Data migration

Program-owned PostgreSQL schema changes use Flyway. Vendor products use their
supported lifecycle mechanisms. Cross-vendor movement uses supported exports,
imports, APIs, SDKs, and fit-for-purpose managed data movement tools.

Reconcile identity, structure, scientific meaning, relationships, distributions,
artifacts, audit history, and tenant scope. A source snapshot or watermark, versioned
mapping, restartable checkpoint, and explicit exception set make each run repeatable.

## Event delivery

Use the transactional outbox only for cross-service domain events that require
atomicity with aggregate state. Debezium owns change-data capture and outbox routing.
The application owns stable event identity, payload schema, idempotent consumption,
and publication-lag telemetry.

## Reading the result

The comparative-evidence repository normalizes caller-supplied records and reports
matches, advantages, gaps, and missing measurements. It preserves source identity
and emits factual comparisons; downstream organizational processes determine which
tradeoffs are acceptable for the intended use.

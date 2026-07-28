# Security and Privacy

Synthetic fixtures and redacted manifests belong in this repository.
Credentials stay in protected runtime environments. Patient records,
configured-tenant payloads, private evidence URLs, and raw security findings
stay in approved evidence systems.

AWS Systems Manager Parameter Store holds environment-scoped non-secret
configuration. AWS Secrets Manager holds secret material under the approved KMS
key. Runtime workloads use environment-scoped identity, bounded caches,
version-stage-aware rotation, CloudTrail evidence, and redacted telemetry.

The dependency-free secret-shape scan reports file, line, rule, and redacted
length. Protected values remain absent from scanner output.

Human, workflow, service, and AI callers use released operations with strict
schemas. The service derives identity and tenant from authenticated context,
applies operation and field allowlists, bounds record count retries time depth
and egress, and records an attributable effect receipt. Retrieved text, vendor
content, issue text, files, and tool descriptions enter the boundary as
untrusted data. URL-shaped inputs resolve through approved destination classes
and network policy.

Evidence projections assess direct, metadata, structural, temporal, and
correlational leakage. Public-safe artifacts carry synthetic identifiers,
approved aggregation, small-cell treatment where applicable, redacted
locators, and a declared limitation record.

Security reports use the repository owner's private reporting channel. The
report identifies the affected specification, potential material effect,
available evidence, and the safe coordination route.

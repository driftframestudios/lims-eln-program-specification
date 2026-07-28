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

Security reports use the repository owner's private reporting channel. The
report identifies the affected specification, potential material effect,
available evidence, and the safe coordination route.

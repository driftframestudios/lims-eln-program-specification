# Security and privacy

Repository examples use synthetic or approved de-identified data. Raw vendor
exports, configured-tenant payloads, patient records, credentials, private evidence
URLs, and detailed security findings stay in the organization’s governed systems.

Runtime implementations resolve environment-scoped non-secret configuration from
AWS Systems Manager Parameter Store and secret material from AWS Secrets Manager.
Workload identities receive the minimum required paths and actions; applications log
references and version metadata with protected values redacted.

GitHub secret scanning and push protection inspect repository changes. GitHub
Rulesets and required reviews protect release branches. Security reports use the
repository owner’s private reporting channel and identify the affected specification,
material effect, and available reproduction evidence.

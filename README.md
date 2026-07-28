# LIMS/ELN Program Specification

This repository is the intent and comparison control plane for the LIMS/ELN
open-receipt collaboration. It publishes versioned requirements, executable
examples, decision forecasts, acceptance contracts, and the lock coordinates
used to compare the active implementation with the simulated final state.

The current planned program release is `spec-v0.2.0`. It consumes governance
schema `1.0.0`; its release and governance commit coordinates receive observed
commit and tree identities during promotion.

The repository describes what collaborators can verify. Running-system truth
comes from the active implementation and observed receipt manifests. The
simulation supplies an executable counterfactual whose assumptions remain
visible and revisable.

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

## Evidence ladder

`specified → simulated → locally_verified → configured_environment_qualified
→ representative_rehearsal_completed → intended_use_validated
→ accountably_accepted`

Each stage states its own evidence. Configured environments, representative
rehearsals, production controls, and accountable acceptance advance through
observed receipts.

## Validation

```sh
python3 scripts/validate_program.py
python3 scripts/scan_secret_shapes.py
python3 -m unittest discover -s tests -v
```

The validator uses the Python standard library and checks stable identifiers,
cross-file references, forecast coordinates, receipt ownership, and required
collaboration surfaces.

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

Source guidance:
[Semantic Attractor Design — Negation-Aware Instructions](https://app.notion.com/p/abcb29b960a842ce8f1a409408a29257).

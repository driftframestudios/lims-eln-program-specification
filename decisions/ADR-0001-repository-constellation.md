# ADR-0001 — Four Domain Repositories and Shared Governance

**Status:** accepted for simulation and initial delivery  
**Date:** 2026-07-28

## Decision

Use separate program, actual implementation, simulated final state, and
comparative evidence repositories. A fifth governance repository releases
shared schemas, workflows, templates, and rulesets.

## Expected effects

- Authority boundaries remain legible to technical and evaluative readers.
- Simulation artifacts retain their generative completeness and their
  simulated evidence identity.
- Observed receipts receive tighter access and review controls.
- The comparator remains independent of both implementations.

## Alternatives considered

- one monorepository with directory boundaries;
- paired actual and simulated repositories;
- a three-repository program/actual/simulation constellation;
- one repository for each regulatory and vendor simulation profile.

## Falsifiers

- cross-repository drift exceeds one sprint for two consecutive release trains;
- maintenance consumes more than twenty percent of delivery capacity without
  advancing a material decision;
- evidence access patterns require a dedicated external ledger service.


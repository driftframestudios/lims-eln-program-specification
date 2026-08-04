# Legacy control-plane quarantine

This directory preserves historical collaboration artifacts that exceeded the
active purpose of the program-specification repository. The active build, tests,
Machine Node, and documentation load only the top-level paths listed in the root
README.

The retained material includes:

- bounded-caller contracts and examples;
- modeled acceptance roles, proof classes, receipts, and promotion records;
- selected-future closure and simulated receipt artifacts;
- runtime Coordination Horizon and first-receipt projections;
- release-role, cross-repository coordinate, and digest-binding artifacts;
- custom repository, pinned-source, language, secret-shape, and branch-flow
  validators with their tests and workflow;
- superseded migration notes and control-plane ADRs.

The files remain available solely as historical hydration material. Their declared
state is inactive with `runtime_effect: none`.

## Reuse boundary

Reuse begins with a concrete product requirement and selects a mature framework
first. A future bounded-operation example may reuse the earlier operation maps as
Visitor inputs while delegating authentication, authorization, workflow, policy,
and observability to selected frameworks. The example remains absent from the
active program until an implementation consumer requires it.

Cross-repository traceability uses released semantic versions and explicit source
links. Git and artifact registries provide commit identity and immutable release
coordinates.

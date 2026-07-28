# GitFlow-Like Branching

## Long-lived branches

- `main` carries reviewed specification releases.
- `develop` integrates the next specification release.

## Supporting branches

- `feature/SPEC-####-short-name` begins from `develop` and returns to `develop`.
- `release/vX.Y.Z` begins from `develop`, receives release-only stabilization,
  lands in `main`, and merges forward into `develop`.
- `hotfix/SPEC-####-short-name` begins from `main`, lands in `main`, and merges
  forward into `develop`.
- `forecast/YYYY-QN-rN` freezes a preregistered forecast from `develop`; its
  release tag remains immutable.
- `evidence/RCP-####-short-name` carries redacted receipt-link changes toward
  `develop`.

## Review contract

Every pull request states:

- its specification, scenario, decision, and receipt identifiers;
- the evidence mode and assurance stage it affects;
- the predicted scientific, operational, and evaluative effect;
- the fixtures and comparison coordinates that reproduce the claim;
- the recovery or forward-merge path;
- the accountable review roles.

Release and hotfix branches preserve semantic-version compatibility and
generate a new constellation lock coordinate.


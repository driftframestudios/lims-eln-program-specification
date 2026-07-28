# GitFlow-Like Branching

## Long-lived branches

- `main` carries reviewed specification releases.
- `develop` integrates the next specification release.

## Supporting branches

- `feature/<stable-claim-or-receipt>` begins from `develop` and returns to
  `develop`.
- `fix/<stable-claim-or-receipt>` carries a behavior repair toward `develop`.
- `chore/<stable-claim-or-receipt>` carries maintenance with stable external
  behavior.
- `release/<semver>` begins from `develop`, receives release-only stabilization,
  lands in `main`, and merges forward into `develop`.
- `hotfix/<stable-claim-or-receipt>` begins from `main`, lands in `main`, and merges
  forward into `develop`.
- `forecast/YYYY-qN-rN` freezes a preregistered forecast from `develop`; its
  release tag remains immutable.
- `evidence/rcp-####-short-name` carries redacted receipt-link changes toward
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

## Automated dependency maintenance

Dependabot monitors the repository's immutable GitHub Action references.
Minor and patch updates may share one bounded pull request; major updates retain
separate review and rollback coordinates. An automation change is identified by
a complete branch grammar, exact pull-request author, and governed target
together:

- Dependabot uses `dependabot/github_actions/<dependency-update>` with
  `dependabot[bot]`.
- Renovate uses `renovate/<dependency-update>` with `renovate[bot]`.
- Either automation flow targets `main` or `develop`.

The read-only branch-policy workflow checks out the exact pull-request base
commit into `.branch-policy-base` and executes that reviewed checker.
Pull-request head content remains in ordinary validation; the policy gate
receives its branch name and author as quoted event data. The gate begins
governing subsequent proposals after the workflow reaches the default branch
and the checker reaches each protected target branch.

GitHub security updates may target the default branch. These pull requests run
the complete validation suite and receive human review before promotion. A
change accepted on `main` is reconciled into `develop` so the next
specification release retains the repair.

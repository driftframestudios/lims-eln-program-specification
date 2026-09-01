# GitFlow-Like Branching

## Long-lived branches

- `main` carries reviewed specification releases.
- `develop` integrates the next specification release.

`main` carries the active protected-delivery ruleset. `develop` remains the
lean integration branch for reviewed candidate work.

## Supporting branches

- `feature/<stable-claim-or-receipt>` begins from `develop` and returns to
  `develop`.
- `fix/<stable-claim-or-receipt>` carries a behavior repair toward `develop`.
- `chore/<stable-claim-or-receipt>` carries maintenance with stable external
  behavior.
- `release/<semver>` begins from `develop`, receives release-only stabilization,
  lands in `main`, merges forward into `develop`, and closes after that forward
  merge settles.
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

## Local proof and bounded hosted maintenance

Local program validation and unit tests remain the complete source-owned proof
path. The repository has a monthly **100–300 runner-minute** allocation for one
small pull-request proof. Pull requests targeting `develop` or `main` run the
program aggregate, language and secret-shape checks, generated-schema equality,
and repository regression suite on Python 3.12. One standard runner, read-only
permissions, cancellation of superseded runs, and a ten-minute ceiling keep
that observation bounded.

The manual `Validate program specification` workflow retains the broader
Python matrix, candidate and release coordinate paths, advisory author
feedback, and cross-repository proof. A named receiver sets
`ENABLE_GITHUB_ACTIONS=true`, selects `confirm_run`, and dispatches it when that
additional evidence is material.

Monthly dependency updates live in `.github/dependabot.yml`, target `develop`,
group minor and patch updates, and keep at most two update pull requests open.
An automation change is identified by a complete branch grammar, exact
pull-request author, and governed target together:

- Dependabot uses `dependabot/github_actions/<dependency-update>` with
  `dependabot[bot]`.
- Renovate uses `renovate/<dependency-update>` with `renovate[bot]`.
- Either automation flow targets `main` or `develop`.

The repository-local branch checker remains available to reviewers and local
validation. Pull requests carry their branch and author coordinates for human
review. Setting `ENABLE_GITHUB_ACTIONS=false` rests the manual proof; repository
settings can rest all hosted execution, and a reviewed return to
`.github/dependabot.manual.yml` rests dependency scheduling.

An activated security update may target the default branch. Its standing proof
is the complete local validation suite plus human review before promotion. A
change accepted on `main` is reconciled into `develop` so the next specification
release retains the repair.

## Program Pages source and publication

`pages/` and the standard-library projection scripts are program source.
Feature work begins from `develop`, returns through review, and keeps generated
Pages bytes outside the source worktree. A clean exact `HEAD` can therefore
produce a manifest that truthfully identifies the complete source state.

The local Pages aggregate creates two isolated builds, validates both complete
inventories, and scans their text for credential-shaped values. A later,
separately authorized publication action can place reviewed bytes on a `docs`
branch, activate repository Pages settings, and attach an HTTPS origin plus its
matching CNAME. Each action keeps the accepted projection manifest as its
recovery coordinate.

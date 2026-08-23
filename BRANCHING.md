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

## Local proof and optional dependency maintenance

Local program validation and unit tests are the standing proof path. GitHub
Actions rests disabled in repository settings at a **$0** budget. The manual
`Validate program specification` workflow becomes available only when a named
human enables Actions, sets `ENABLE_GITHUB_ACTIONS=true`, selects
`confirm_run`, and dispatches the proof. After the proof is read, set
`ENABLE_GITHUB_ACTIONS=false` and disable Actions in repository settings to
restore the resting state.

Dependency scheduling rests in `.github/dependabot.manual.yml`. Reviewing that
template and renaming it to `.github/dependabot.yml` activates its schedule; the
manual filename is the return state. When dependency automation is active, an
automation change is identified by a complete branch grammar, exact
pull-request author, and governed target together:

- Dependabot uses `dependabot/github_actions/<dependency-update>` with
  `dependabot[bot]`.
- Renovate uses `renovate/<dependency-update>` with `renovate[bot]`.
- Either automation flow targets `main` or `develop`.

The repository-local branch checker remains available to reviewers and local
validation. Pull requests carry their branch and author coordinates for human
review; no automatic branch-policy workflow runs in the resting state.

An activated security update may target the default branch. Its standing proof
is the complete local validation suite plus human review before promotion. A
change accepted on `main` is reconciled into `develop` so the next specification
release retains the repair.

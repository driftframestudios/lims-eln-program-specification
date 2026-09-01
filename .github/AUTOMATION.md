# Bounded automation

## Monthly allocation and pull-request proof

This repository has an approved allocation of **100–300 GitHub Actions runner
minutes per month**. Pull requests targeting `develop` or `main` receive one
read-only `ubuntu-24.04` job on Python 3.12. Superseded runs cancel, and each
run has a ten-minute ceiling. The job runs the program aggregate, language and
secret-shape checks, byte-current generated schemas, and the repository-owned
regression suite. Its parsed controls must match the source-owned
`automation_controls` projection in `release/repository-role.json`.

The pull-request path receives repository contents and proposed source through
read-only permissions. Credentials and cross-repository coordinates stay with
their dedicated proof paths. Monthly Dependabot updates target `develop`, group
minor and patch updates, and keep at most two update pull requests open.

## Deliberate full proof

The manual **Validate program specification** workflow retains the broader
Python matrix, advisory author feedback, candidate or accepted coordinate
checks, cross-repository checkouts, and aggregate result. A named receiver sets
`ENABLE_GITHUB_ACTIONS=true`, selects `confirm_run`, and dispatches that proof
when a release, compatibility question, or external-coordinate change calls
for the wider observation.

## Recovery

Local validation remains the complete source-owned proof path. Setting
`ENABLE_GITHUB_ACTIONS=false` rests the manual proof. Disabling Actions in
repository settings rests all hosted execution while local commands continue
to serve review. A reviewed rename from `.github/dependabot.yml` to
`.github/dependabot.manual.yml` returns dependency scheduling to a dormant
source state. The next receiver can restore either path from the same reviewed
workflow and configuration.

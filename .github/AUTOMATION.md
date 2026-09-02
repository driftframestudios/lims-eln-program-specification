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
read-only permissions. Its checkout retains complete repository history so a
reviewed package-source commit can be reproduced from its Git tree while
credential persistence remains disabled. Cross-repository coordinates stay
with their dedicated proof paths. Monthly Dependabot updates target `develop`,
group minor and patch updates, and keep at most two update pull requests open.

## Deliberate full proof

The manual **Validate program specification** workflow retains the broader
Python matrix, advisory author feedback, candidate or accepted coordinate
checks, cross-repository checkouts, and aggregate result. A named receiver sets
`ENABLE_GITHUB_ACTIONS=true`, selects `confirm_run`, and dispatches that proof
when a release, compatibility question, or external-coordinate change calls
for the wider observation. The Program matrix installs the repository package
before it validates the Pydantic contract boundary. Before any private sibling
checkout, the cross-repository path authenticates `CONSTELLATION_READ_TOKEN`
and confirms Contents read access to each exact repository and commit selected
by the lock. The check reports only the coordinate that can be read. Its
status-only result separates successful credential authentication from a
private-resource request that GitHub reports as forbidden or unavailable.
Those statuses narrow the recovery checks while preserving GitHub's deliberate
ambiguity among repository selection, Contents permission, policy, rate state,
and coordinate availability. Response bodies, headers, account names, and the
credential value stay in the ephemeral runner boundary. A dispatch from a
later carrier can set `release_tag` to the Program release
named by `constellation.lock.json`; a direct dispatch from that tag selects the
same subject automatically. The proof requires an annotated tag, verifies its
repository-trusted signature, and confirms that its peeled commit belongs to
the current carrier's ancestry. The workflow success summary reports the
validated tag and Git commit identifiers; `git verify-tag` supplies the trusted
public-signature principal and key-fingerprint result before the
external-coordinate proof continues. After promotion, run
`python scripts/verify_program_release_observation.py --require-observed` from
the later observation carrier. The verifier reproduces the tag, tree, archive,
signature, accepted-main ancestry, and exact carrier bytes, then reports the
carrier commit for its receiving lock.

## Recovery

Local validation remains the complete source-owned proof path. Setting
`ENABLE_GITHUB_ACTIONS=false` rests the manual proof. Disabling Actions in
repository settings rests all hosted execution while local commands continue
to serve review. A reviewed rename from `.github/dependabot.yml` to
`.github/dependabot.manual.yml` returns dependency scheduling to a dormant
source state. The next receiver can restore either path from the same reviewed
workflow and configuration.

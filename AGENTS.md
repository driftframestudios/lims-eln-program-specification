# Program repository collaboration ground

This repository defines the shared requirements and acceptance route for a
five-repository LIMS/ELN program. Make changes here when the desired behavior,
shared contract, comparison input, or acceptance boundary needs to change.

## Begin with current source

- Run `git status --short --branch` and read the latest local and remote history.
- Read [`README.md`](README.md), [`release/repository-role.json`](release/repository-role.json),
  and [`STATUS.yaml`](STATUS.yaml) before changing a program contract.
- Use [`constellation.json`](constellation.json) to identify which repository can
  establish the behavior in question. Use
  [`constellation.lock.json`](constellation.lock.json) when exact tags, commits,
  and digests affect the decision.
- Use [`coordination-horizon.json`](coordination-horizon.json) for current work
  and re-entry. Released contracts and runnable source continue to define
  behavior.
- Preserve unrelated work already present in the worktree.

Use [`repository-reentry`](.agents/skills/repository-reentry/SKILL.md) when
branch, release, constellation, current coordination records, and public
projection need one reliable starting point.

## Keep repository roles clear

- This repository owns program intent, shared examples, decisions, forecasts,
  and acceptance boundaries.
- `site-reading-governance` owns shared schemas, language rules, workflows, and
  templates.
- `lims-eln-enterprise-implementation` owns active code and evidence observed in
  a configured environment.
- `lims-eln-simulated-final-state` owns the executable selected future and its
  declared assumptions.
- `lims-eln-comparative-evidence` owns paired execution, normalization,
  difference classification, and redacted reports.

Use
[`source-authority-mapping`](.agents/skills/source-authority-mapping/SKILL.md)
when a claim, contract, generated artifact, release coordinate, or public page
crosses these roles. The map identifies the source that establishes meaning or
evidence, then ends at the receiver that can make the next decision.

Use
[`constellation-coherence-reconciliation`](.agents/skills/constellation-coherence-reconciliation/SKILL.md)
before a coordinated release becomes pinned. It checks exact signed release
subjects, copied semantic artifacts, schema-era bindings, and hub summaries as
one receiving state.

Use
[`external-benchmark-reception`](.agents/skills/external-benchmark-reception/SKILL.md)
when a synthetic system, dataset, paper, interface, or evaluation method may
enter the constellation. It binds the external subject and its claim ceiling,
then selects a reference, adapter-probe, derived-scenario, or held-review route
before a receiving repository adopts it.

Use
[`proportionate-recovery-routing`](.agents/skills/proportionate-recovery-routing/SKILL.md)
when a failed check, repeated retry, source loss, authority mismatch, stale
handoff, or coordination drift prevents reliable continuation. It preserves
the current contract, selects one smallest adequate move and owning surface,
and returns a decision-bearing receipt with an exact re-entry event.

Use
[`contextual-jargon-scan`](.agents/skills/contextual-jargon-scan/SKILL.md) in
stride when public or cross-repository prose may assume Program-local context.
Keep exact code, schema, scientific, regulatory, version, and evidence terms;
define useful compact language and revise shorthand whose object or
consequence is unclear.

Use
[`uv-backed-python-execution`](.agents/skills/uv-backed-python-execution/SKILL.md)
to run a named Program check with a repository-compatible Python environment
while the operating system's base Python installation and global packages keep
their current state. The skill distinguishes the current lockless local route
from hosted Python 3.12 and 3.13 observations.

Versioned Program procedures live in
[`.agents/runbooks/`](.agents/runbooks/README.md). They order a known route
across current source owners while GitHub Issues retain scope and acceptance
and each receiving repository retains its behavior authority.

Both source bands are suitable for public collaboration. `public_possible`
identifies guidance available for use and refinement; `public_ready` identifies
guidance reviewed for a defined reader and navigation path. A publication
surface can select the subset that serves its current visitor job.
Keep skill-package `name` and `description` at the top level of front matter.
Place Program publication standing, version, adaptation relation, and upstream
identities inside the standard `metadata` mapping so standard skill tools
and the Program projection read one source. The current Program profile accepts
only top-level `name`, `description`, and scalar `metadata`; introduce another
optional skill-package field through a named repository contract before using
it here.

## Use the accepted branch route

- `main` carries reviewed releases; `develop` integrates the next release.
- Begin ordinary work from `develop` on `feature/`, `fix/`, or `chore/` and
  return it to `develop` through review.
- Form `release/<semver>` when a named release candidate is assembled. Form a
  `hotfix/` from `main` for an accepted release repair, then merge that repair
  forward into `develop`.
- Follow [`BRANCHING.md`](BRANCHING.md) for the complete branch and review
  contract.

## Write toward the verifiable state

- Lead instructions with the behavior collaborators can create or verify.
- Pair a hard safety, privacy, or scope boundary with the affirmative behavior
  that keeps the work useful.
- Use ordinary language around exact technical and regulated terms. Define
  program-specific shorthand where it first changes a reader's decision.
- State what each observation establishes before its coverage boundary.
- Keep personal attribution in the repository's approved carriers. Commit,
  Issue, pull-request, and review prose stays focused on the change.

## Validate the material behavior

Use the repository-local uv skill to select Python 3.12 and install the local
package in an isolated environment before running the complete proof:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_program.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/verify_program_release_observation.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_pinned_sources.py --preflight-external
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/check_language.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python -m unittest tests.test_language_policy -v
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/scan_secret_shapes.py
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_contract_schemas.py --check
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/generate_administrative_examples.py --check
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python -m unittest discover -s tests -v
```

The external preflight establishes that every sibling coordinate is complete
before checkout. For exact release settlement, check out each sibling at the
commit recorded in `constellation.lock.json`, then run:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_pinned_sources.py --allow-pending \
  --source simulation=../lims-eln-simulated-final-state \
  --source implementation=../lims-eln-enterprise-implementation \
  --source comparison=../lims-eln-comparative-evidence \
  --source governance=../site-reading-governance
```

The relative paths above describe the standard sibling layout. Supply the same
four role-to-path bindings from another checkout layout when needed.

Run the following aggregate from a clean commit when repository skills or
Program Pages source changes. It builds twice, validates both sites, compares
their bytes, and scans generated text for credential-shaped values.

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  -- python scripts/verify_pages.py
```

## Close with one clear receiver

Return the changed source, the smallest observation that establishes its
behavior, its evidence limit, and the repository or accountable role that can
make the next decision. A release coordinate stays pending until the protected
promotion path supplies its full commit and digest.

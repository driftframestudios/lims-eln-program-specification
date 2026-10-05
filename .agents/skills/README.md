# Program collaboration skills

These repository-local skills turn recurring Program work into explicit,
reviewable routes. They help a human or AI collaborator select a fitting method
after current source, authority, and task scope are known. They do not replace
the active Issue, grant additional authority, or establish evidence that the
named source cannot establish.

## Choose a skill

| Skill | Use it when | Standing |
| --- | --- | --- |
| [`repository-reentry`](repository-reentry/SKILL.md) | Branch, release, constellation, coordination, and public-projection records need one current starting point | Public-possible; exercised across the five-repository orientation workbench |
| [`source-authority-mapping`](source-authority-mapping/SKILL.md) | A claim, contract, artifact, or release coordinate crosses repository roles | Public-ready; selected for Program Pages |
| [`constellation-coherence-reconciliation`](constellation-coherence-reconciliation/SKILL.md) | A coordinated release must align exact source subjects, copied meaning, and schema-era bindings | Public-ready; selected for Program Pages |
| [`uv-backed-python-execution`](uv-backed-python-execution/SKILL.md) | A Program check needs Python 3.12 or 3.13 without changing the host Python installation | Public-ready; selected for Program Pages |
| [`proportionate-recovery-routing`](proportionate-recovery-routing/SKILL.md) | A failed check, source gap, permission boundary, or stale handoff needs the smallest reliable recovery route | Public-possible; exercised against the Program hosted-proof handoff |
| [`contextual-jargon-scan`](contextual-jargon-scan/SKILL.md) | Changed public or cross-repository prose may assume context its reader does not share | Public-possible; exercised in the Program collaboration workbench |

| [`external-benchmark-reception`](external-benchmark-reception/SKILL.md) | An authorized external subject may become a reference, adapter probe, or derived scenario | Public-possible; external-source exercise remains separately authorized |

`public_possible` and `public_ready` describe observed maturity and navigation
standing. Both bands are available for public collaboration. The Pages builder
currently selects the public-ready subset because that set serves the visitor
route defined in [`pages/README.md`](../../pages/README.md).

## A practical order

1. Use `repository-reentry` when the starting state is uncertain.
2. Use `source-authority-mapping` when more than one repository or projection
   participates in the claim.
3. Select the task-specific skill: constellation reconciliation, uv-backed
   execution, recovery routing, or contextual language review.
4. Return the changed or inspected source, the observation and its coverage
   boundary, the active Issue, and one exact continuation event.

One direct source reading remains the better route when it answers the question
without a reusable workflow.

## Source and publication boundaries

Each `SKILL.md` uses the portable Agent Skills envelope: `name` and
`description` remain at the top level, while Program maturity, version, and
lineage fields live in `metadata`. Repository validation checks the complete
seven-skill inventory, required sections, declared standing, and exact upstream
lineage for derivative skills.

The public catalog is a generated projection of selected source files. The
source skill retains authority for its instructions; the Pages manifest records
which exact source revision and bytes were projected. Publication neither
changes the skill's maturity nor grants a new task permission.

## Revise or add a skill

- Begin with a repeated, decision-changing need and name the source that can
  establish the method.
- Prefer revising an existing contract when the new case has the same trigger,
  boundaries, and result.
- Give a distinct method its own directory and `SKILL.md`, then update this
  catalog, `AGENTS.md`, the root [`README.md`](../../README.md), the validator,
  and focused tests together.
- Retain exact upstream repository, path, revision, blob, and SHA-256 lineage
  when adapting a portable skill.
- Advance `public_ready` only through a reviewed reader and navigation decision.

Validate the workbench with:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python -m unittest tests.test_collaboration_workbench -v
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . -- python scripts/validate_program.py
```

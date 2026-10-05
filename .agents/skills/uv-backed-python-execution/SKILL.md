---
name: uv-backed-python-execution
description: Resolves and runs Program Specification Python checks through uv while preserving the host's base Python installation. Applies when Python 3.12 or 3.13, a project without a uv.lock, an isolated dependency environment, or uv storage needs a clear choice before validation.
metadata:
  source_band: public_ready
  skill_version: 0.1.0
  upstream_repository: https://github.com/driftframestudios/human-ai-systems-exemplars.git
  upstream_path: .agents/skills/uv-backed-python-execution/SKILL.md
  upstream_revision: 0ed54696e01babe3020cd7b0e38bc06eeab64e67
  upstream_blob_sha1: b8fb9d34ed16146f22cfbbccad954ae4419a1692
  upstream_sha256: e9d788cae6d2ceb1ed328f8c5ce70c0c34c18d1e0849b4804d89ade6ed42f414
  adaptation_relation: repository_local_derivative
---

# Program Specification uv-backed Python execution

## Contract

- **What:** A repository-local way to select a Program-compatible Python
  interpreter through `uv`, prepare the declared package dependencies, run one
  named check, and report the environment details that affect its result.
- **When:** Program validation runs on a machine whose base Python, existing
  environment, dependency state, or uv storage leaves the interpreter or
  dependency choice unclear.
- **Boundaries:** Current task authority, `pyproject.toml`, hosted workflow
  versions, and the named check govern the run. The host Python installation
  and global packages remain unchanged. Dependency upgrades, lock creation,
  package-metadata edits, and toolchain conversion belong to separately
  authorized work. Environment readiness and a passing Program check remain
  distinct observations.
- **Result:** The named Program check runs through an identified uv and Python
  combination; the resolved dependency versions and files produced locally are
  explicit; and any remaining environment condition has one owner and a clear
  trigger for another attempt.

## Current Program route

At this skill revision, `pyproject.toml` requires Python `>=3.12` and Pydantic
`>=2.13,<3`. Hosted validation observes Python 3.12 and 3.13. The repository has
no `.python-version` or `uv.lock`, so a local run establishes the dependency
versions resolved for that run. Dependency-byte reproducibility begins with a
separately accepted lock policy.

The smallest local check uses an isolated uv-managed Python 3.12 environment:

```sh
uv run --isolated --no-project \
  --python 3.12 \
  --managed-python \
  --with-editable . \
  -- python scripts/validate_program.py
```

Add `--cache-dir <authorized-cache>` when the default uv cache is outside the
current write boundary. Use the same uv prefix for the complete test suite,
language check, secret-shape scan, schema check, release-observation verifier,
Pages verifier, or external sibling preflight named by the current task.
The standard-library Pages builder, projection validator, aggregate, and static
preview need the uv-provided interpreter rather than the local package, so
their commands omit `--with-editable .`.

## Rules

### Rule: Program declarations choose the runtime

Read `pyproject.toml`, any future `.python-version` or `uv.lock`, the relevant
workflow matrix, and the exact validation command before selecting Python. An
available interpreter is useful when it satisfies those sources. A future
disagreement returns to the Program source that owns the changed runtime
contract.

### Rule: uv prepares the environment

### Rule: The selected dependency profile determines its interpreter floor

Choose Python against the intersection of the project and every selected
dependency's requirements. A receiver can retain a Python 3.11 standard-library
core while its optional Program conformance profile requires Python 3.12.
Keep those profiles in separate isolated environments and name the selected
extras with the result. A declared version range describes admission; an
observed check describes the particular interpreter and platform used.

The [researcher environment route](../../../docs/RESEARCHER_ENVIRONMENTS.md)
maps the current receivers and their dependency owners. Exact package source,
resolved dependencies, and a tested environment are separate identities.

### Rule: uv prepares the selected environment

Run Program checks through `uv run`. Let uv prepare dependencies and the
execution environment while the host operating-system Python installation and
global packages remain unchanged. A repository-compatible host or runner
interpreter can execute the check when Program permits it; record whether uv or
the host supplied that interpreter. Use `--managed-python` for the current
macOS route and whenever the task requires a uv-provisioned interpreter.

### Rule: Lockfile presence bounds the evidence claim

The current command uses `--isolated --no-project --with-editable .` so
validation can install the local package while lock creation remains with a
future dependency-policy decision. Record the materially relevant dependency
versions beside the result.

If Program later accepts a current `uv.lock`, prefer a project run that asserts
the lock remains current:

```sh
uv run --project <repository-root> --locked \
  --python <version> \
  -- <named-check>
```

A stale lock produces a finding that identifies the lock as stale. Lock
revision remains with the task that owns dependency policy.

### Rule: Build effects stay visible

Local editable and non-editable package builds can create ignored backend
material such as `src/lims_eln_program_specification.egg-info/` or `build/`.
Tracked-tree cleanliness is the ordinary Program source observation.
`git status --short --ignored` inventories ignored paths, but an existing
ignored directory can retain the same status line while files inside it change.
When the full tree must remain untouched, run from a disposable worktree or
source copy. When byte equality of ignored output matters, prefer the
repository's snapshot tool; otherwise compare records of relative path, byte
length, and SHA-256 sorted by relative path before and after.

### Rule: Writable uv state has named locations

Select an ignored repository cache, an authorized task-temporary cache with
`--cache-dir`, or `--no-cache` when the default cache cannot receive writes.
When uv-managed Python storage also needs an authorized location, set
`UV_PYTHON_INSTALL_DIR=<authorized-path>` for interpreter installation and all
subsequent uv commands that must discover it. Cache, interpreter storage, and
network access remain distinct conditions.

### Rule: Program evidence stays proportionate

Capture the exact uv command, `uv --version`, the executing Python version,
Pydantic version, named check result, and `git status --short` before and after.
Add `--ignored` when the requested result needs an inventory of ignored paths.
Add a scoped digest inventory when unchanged ignored bytes are part of the
claim. State whether the run observed Python 3.12 or 3.13, local macOS or hosted
Linux, the primary validator or full suite, and any external sibling access.

### Rule: Another attempt follows a changed signal

Classify a failed run as interpreter selection, dependency resolution, cache or
filesystem access, network or private source access, or Program behavior. Make
the smallest change owned by the current task, then repeat the same command. An
unchanged failure remains with its named recovery owner while the accepted
Program source stays intact.

## Operating sequence

1. **Reconcile:** Read Program runtime declarations and name the exact check
   plus the decision it can change.
2. **Select:** Choose the current command without a lockfile or a future
   lock-checked project command, the Python version, and whether uv must
   provide the interpreter.
3. **Place:** Give the cache and, when needed, `UV_PYTHON_INSTALL_DIR`
   authorized writable locations.
4. **Execute:** Run the named Program check through uv while dependency policy
   and host Python retain their current state.
5. **Observe:** Record the small set of environment versions and settings that
   affect interpretation and confirm tracked or full-tree state as requested.
6. **Return:** State the result, evidence boundary, and either completion or
   one owned recovery step with its re-entry signal.

## Representative scenarios

### Scenario: The macOS base Python is older than Program requires

- **Given:** macOS supplies Python 3.9 and Program requires Python 3.12 or
  newer.
- **When:** the collaborator selects uv-managed Python 3.12 and runs the
  primary Program validator in the isolated lockless environment.
- **Then:** the result is bound to the uv-provisioned interpreter and observed
  Pydantic version, the macOS Python installation remains unchanged, and
  Python 3.13 plus hosted Linux remain separate observations.

### Scenario: The exact sibling preflight reaches a permission boundary

- **Given:** the local Program environment validates and the named task also
  requires `validate_pinned_sources.py --preflight-external`.
- **When:** uv prepares the local Python environment and the external request
  reaches a repository access response.
- **Then:** the local runtime observation remains valid, the access response
  returns through the Program recovery route, and another external attempt
  follows a credential, policy, rate, or network change.

## Adaptation lineage

This repository-local derivative adapts the portable
`uv-backed-python-execution` contract accepted in
`human-ai-systems-exemplars` at revision
`0ed54696e01babe3020cd7b0e38bc06eeab64e67`. The front matter records the
upstream path, Git blob, and SHA-256 digest. The derivative narrows interpreter
selection, lock evidence, commands, locally produced files, and recovery to the
Program Specification repository's Python 3.12/3.13 validation surface.

## Completion

The skill completes when the named Program check has run through a compatible
uv-backed environment and its runtime versions, repository-state observation,
and evidence boundary are legible, or when one unresolved condition has an
owner and a changed-signal re-entry point. A future accepted Program lockfile
reopens the local command choice; upstream behavior changes reopen adaptation
lineage review.

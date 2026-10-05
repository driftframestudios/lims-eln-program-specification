# Researcher environments and exact consumption

## Choose a source coordinate

Start with a named repository release when the study requires a released
baseline. [The constellation lock](../constellation.lock.json) owns its exact
sibling coordinates; [the role manifest](../release/repository-role.json) owns
Program's release standing. The current lock still carries a pending Program
promotion coordinate. Its accepted sibling entries remain useful inputs for
their stated jobs; complete coordinated-release acceptance stays with Program
#40 and the protected promotion route.

For the current native/container journey, select the reviewed `develop`
candidate through the Enterprise entry guides. Record the full commit before
installation. An exact integration commit establishes a reproducible source
choice while release, site tagging, and publication retain their own decisions.

[Program #54](https://github.com/driftframestudios/lims-eln-program-specification/issues/54)
owns this environment route.
[The handoff runbook](../.agents/runbooks/constellation-contract-release-handoff.v0.1.md)
joins shared contract identity to each receiver's explicit adoption.

## Runtime and dependency choices

The matrix below describes the reviewed source as of 2026-10-05. Each linked
declaration remains the owner of later changes. An interpreter declaration
describes admissible versions; a passing observation names the particular
platform, interpreter, dependencies, and profile actually exercised.

| Receiver and source owner | Effective Python profile | Dependency and installation choice | First evidence route |
| --- | --- | --- | --- |
| [Program](../pyproject.toml) | Python 3.12 or newer | Ranged library dependencies; isolated uv execution. The library retains its current lockless policy. | Program validator and packaged-resource tests; installed consumption through Enterprise's handoff check |
| [Enterprise](https://github.com/driftframestudios/lims-eln-enterprise-implementation/blob/develop/pyproject.toml) | Python 3.12 or newer; maintained local selection is 3.12 | Application `uv.lock`; `contracts`, `postgres`, and `test` extras select distinct needs. `uv sync --locked --no-editable` supplies the installed profile. | Native entry, container entry, protected export, and configured PostgreSQL checks |
| [Simulation](https://github.com/driftframestudios/lims-eln-simulated-final-state/blob/develop/pyproject.toml) | Core: 3.11 or newer. Optional Program conformance: 3.12 or newer. | Standard-library core; optional exact-commit `contract-conformance` extra. Current extra retains the earlier Program package coordinate. | Independent selected-future artifact and resource checks in its README |
| [Comparative](https://github.com/driftframestudios/lims-eln-comparative-evidence/blob/develop/pyproject.toml) | Core/validation: 3.11 or newer. Optional Program conformance: 3.12 or newer. | Standard-library core, separately pinned `validation` extra, optional exact-commit `contract-conformance` extra. | Independent normalization, artifact, and report checks in its README |
| [Governance](https://github.com/driftframestudios/site-reading-governance/blob/develop/README.md) | Source-owned validator: 3.11 or newer | Dependency-free JSON validation; complete projection checks install `requirements-projections.txt` with `--require-hashes` in an isolated environment. | `tools/validate_governance.py` or the named `make check` profile |

Choose the interpreter for the **complete selected profile**. Simulation and
Comparative retain their Python 3.11 core path; adding a Program dependency
raises the effective floor to 3.12. Keep separate environments for distinct
profiles so a previously installed optional package cannot silently broaden a
core-only result.

Enterprise consumes Program package `0.4.0` at the full commit in
[the accepted `0.4.0` binding](https://github.com/driftframestudios/lims-eln-program-specification/blob/a307f422596e5098ac5efca29968212b5e24da0b/release/contract-package-coordinate.json).
[The current package coordinate](../release/contract-package-coordinate.json)
tracks the successor's separate review and adoption standing.
Simulation and Comparative's present conformance extras retain
`4d06eeb7f96910311fbcb7f51547c978b6a07290`. Their receivers adopt a successor
through their own contract and scenario checks. Shared contract version
`1.0.0` alone establishes neither identical package content nor an accepted
receiver upgrade.

## Installed consumption and editable development

The first Program resource check can run independently of a sibling checkout.
From any authorized working directory, use the current reviewed source
requirement:

~~~sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with 'lims-eln-program-specification @ git+https://github.com/driftframestudios/lims-eln-program-specification.git@d8f41d0ce98a75120c99f0a23d00796ae8a8b913' \
  -- python -I -c 'from importlib.metadata import version; import lims_eln_contracts as c; assert version("lims-eln-program-specification") == "0.4.0"; assert c.__version__ == "0.4.0"; assert c.CONTRACT_VERSION == "1.0.0"; assert c.SCHEMA_RESOURCE_NAMES; assert all(isinstance(c.load_generated_schema(name), dict) for name in c.SCHEMA_RESOURCE_NAMES); print("Installed package and schema resources: passed")'
~~~

Python's `-I` mode resolves imports through the selected installed environment
and keeps assertions active independently of the caller's working directory,
`PYTHONPATH`, and `PYTHONOPTIMIZE` settings.

Git credentials stay with the receiving operator's configured credential
helper. Initial interpreter and package acquisition needs authorized network
access. A prepared cache can support repeat execution; offline capability
depends on the actual cached artifacts. This command establishes installed
version and resource availability. Enterprise's
[package handoff guide](https://github.com/driftframestudios/lims-eln-enterprise-implementation/blob/develop/docs/runbooks/program-package-handoff.v0.1.md)
adds PEP 610 commit identity, scoped source digest, and the complete required
resource observations. Its explicit `--program-source` argument supplies a
verification source; ordinary installed application execution resolves its
resources from the installed package.

For Program source work, use the
[uv execution skill](../.agents/skills/uv-backed-python-execution/SKILL.md) and
`--with-editable .`. For a clean local package smoke, use `--with .` in an
isolated environment. Editable development proves source behavior; installed
execution also exercises package discovery and resource inclusion.

Retain library dependency ranges. Enterprise's application lock owns exact
runtime resolutions; Governance's hash-locked parser requirements own that
projection profile. A research experiment that adds dependencies owns its
separate lock or exact resolution record. Updating a lock begins with one
named change and affected-profile checks. Recovery selects the previous
reviewed source and matching lock in a separate environment.

## First native and container journey

Use the existing Enterprise owners in sequence:

1. [Native entry](https://github.com/driftframestudios/lims-eln-enterprise-implementation/blob/develop/docs/runbooks/local-workbench-entry.v0.1.md):
   install the locked profile, select the adapter, and observe readiness.
2. [Container entry](https://github.com/driftframestudios/lims-eln-enterprise-implementation/blob/develop/docs/runbooks/local-container-entry.v0.1.md):
   prepare exact Program/Enterprise artifacts, retain external secrets, and
   start the complete dependency chain.
3. Reuse the exact request for replay. Keep restart, independent experiment,
   contention, and explicitly named reset as separate observations.
4. [Protected export](https://github.com/driftframestudios/lims-eln-enterprise-implementation/blob/develop/docs/runbooks/local-observation-export.v0.1.md):
   complete transfer, validate the typed observation, and preserve exact bytes.
5. Compare the declared Golden Specimen projection under its contract.
   Environment-owned receipt identifiers and timestamps keep their individual
   provenance. A comparison with the selected future additionally needs
   [scientific mapping](https://github.com/driftframestudios/lims-eln-comparative-evidence/issues/44);
   software-environment agreement establishes its narrower behavior.

### Observations already available

| Observed surface | Environment and evidence owner | What the result establishes |
| --- | --- | --- |
| Exact Program package handoff | [Program PR #56](https://github.com/driftframestudios/lims-eln-program-specification/pull/56) and [Enterprise PR #44](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/44) | Reviewed full commit/scoped digest and first installed-resource consumption |
| Native durable workbench | [Enterprise PR #46](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/46), local macOS with Python 3.12 and configured PostgreSQL | Declared Golden Specimen result, explicit adapter/readiness, retained replay and conflict behavior |
| Confined container workbench | [Enterprise PR #47](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/47), Linux arm64 under a local macOS/Colima receiver | Same declared journey contract through pinned application/migration images, retained state and credential recovery |
| Typed export and contention | [Enterprise PR #48](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/48) and [PR #49](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/49) | Exact-byte export, bounded recovery, deterministic serialization-conflict observation, and unchanged accepted replay |
| Reset and recovery instructions | [Enterprise PR #50](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/50) and [PR #51](https://github.com/driftframestudios/lims-eln-enterprise-implementation/pull/51) | Disposable reset with retained workbench intact, protected migration inspection, exact-request reconciliation, and fail-fast shell boundaries |
| Hosted repository checks | Each receiving PR's Ubuntu/Python job | The source checks actually selected by that workflow; optional configured-container methods retain their separate opt-in evidence |

Native and container results satisfy the declared result contract in their
named observations. That is distinct from full-artifact byte equality and
from equivalence of scientific conclusions across different producers.
Additional architectures, Python versions, Windows, remote deployment, and
HPC/Apptainer receive a named environment and their own focused observations.
Keep existing support declarations intact while recording that broader matrix.

## Select one evidence lane

| Lane | Question | Existing owner and stopping point |
| --- | --- | --- |
| Package/resource smoke | Did the installed distribution carry the required resources and identity? | Program resources plus the receiving conformance script; stop after the selected package boundary passes |
| Unit and contract | Does the changed rule preserve independent expectations? | Each repository's existing unittest discovery and contract fixtures |
| Configured integration | Does the chosen implementation work with its actual database/images/services? | Enterprise's explicit integration and transport opt-ins; renew affected cases only |
| Reproducible artifacts | Are the complete selected output sets and their bytes consistent? | Simulation and Comparative source-owned inventory/report validators |
| Measurement | How does equal behavior change with a declared input and environment? | [Comparative #41](https://github.com/driftframestudios/lims-eln-comparative-evidence/issues/41), separate from correctness acceptance |

Keep hosted triggers, budgets, and optional profiles under their existing
owners. A documentation change calls for route/source checks; a changed runtime
boundary calls for its focused behavior check. A new environment claim calls
for its configured observation.

A measurement records input/profile identity, record count, graph shape,
payload/output size, concurrency, cold preparation versus warm execution,
execution order, every trial/failure, and the statistic suited to the sample.
A small exploration informs the next decision; a tail or population claim
needs its own design and evidence. A timing gate begins with an accepted
baseline and a receiver who can act on a change.

## Recovery, handback, and re-entry

Retain the accepted source, lock, credential store, and data while resolving
one changed prerequisite. Interpreter mismatch goes to profile selection;
package/resource mismatch goes to the receiver's conformance owner;
migration or uncertain commit goes to the Enterprise recovery guides;
scientific divergence goes to Comparative's accountable mapping route.
A repeated unchanged result stays with that owner until the source,
environment, input, authority, or diagnostic condition changes.

Use the existing receiving PR for source/lock/interpreter/platform/image/input
identities, normalized check result, evidence scope, and next receiver.
Private paths, raw output, credentials, and payloads stay local. Public skill
packages keep their referenced material available through existing repository
routes; a new hosted projection waits for the accepted immutable site tag and
complete carrier. The [runbook index](../.agents/runbooks/README.md) and
[root README](../README.md) supply return routes.

The environment coordination step completes when a collaborator can choose
the correct profile, reach its first result, and identify the owner of any
remaining evidence. New runtime adoption or a named receiving platform reopens
the relevant matrix row. Program #55 receives bounded graph/lineage work;
administrative receiver Issues retain their own implementation and acceptance.

---
name: source-authority-mapping
description: Traces a LIMS/ELN program claim, contract, artifact, or release coordinate through the five-repository suite. Applies when specification meaning, governance schema, runtime evidence, simulated behavior, comparison output, public projection, or promotion ownership requires clear sources and receivers.
metadata:
  source_band: public_ready
  skill_version: 0.1.0
  upstream_repository: https://github.com/driftframestudios/human-ai-systems-exemplars.git
  upstream_path: .agents/skills/source-authority-mapping/SKILL.md
  upstream_revision: a9ba528946fead335b49da3ae6dfb91c65588046
  upstream_blob_sha1: 112830e9b70540b0bc9a8535ab77c7a04c1a5926
  upstream_sha256: 1420eaee7f6d58805c29eaff23644d4982fdf1f12d2f6ce3cc39c65791939aff
  adaptation_relation: repository_local_derivative
---

# Source authority mapping

## Contract

- **What:** A repository-local method for tracing one material object through
  its defining source, exact revision, projections, evidence producers, and
  receiving decision across the LIMS/ELN suite.
- **When:** A requirement, schema, operation, scenario, result, report, Pages
  artifact, or release coordinate appears in more than one repository or could
  be mistaken for evidence owned elsewhere.
- **Boundaries:** The map records relations supported by current source. Program
  intent, governance schemas, implementation observations, simulated results,
  comparison judgments, publication, and accountable acceptance retain their
  distinct owners. Protected values remain in their approved systems and enter
  a map through governed references or redacted metadata.
- **Result:** A concise map naming the source that defines meaning, the exact
  accepted coordinate, each decision-changing relation, the current receiver,
  and the observation that would require another mapping pass.

## Five repository roles

| Role | Repository | What it can establish |
| --- | --- | --- |
| Program | `lims-eln-program-specification` | Program intent, shared contract content, examples, forecasts, and acceptance boundaries |
| Governance | `site-reading-governance` | Shared schema meaning, language policy, workflows, templates, and governance rules |
| Implementation | `lims-eln-enterprise-implementation` | Active code behavior and evidence observed in a named environment |
| Simulation | `lims-eln-simulated-final-state` | Behavior inside the selected future and the assumptions that make that result possible |
| Comparison | `lims-eln-comparative-evidence` | Pinned paired inputs, normalization, challengeable difference classifications, and redacted reports |

One repository can publish or carry a copy of material owned elsewhere. That
copy keeps its relation to the defining source visible.

## Rules

### Rule: Begin with one material object and decision

Name the exact claim, contract, schema, package, result, or report whose route
changes a decision. A bounded object keeps the map useful and leaves the wider
suite inventory available through `constellation.json`.

### Rule: Read local role records before following links

Use these sources in order when their distinction matters:

1. `release/repository-role.json` states this repository's role, release state,
   contract bindings, and promotion state.
2. `constellation.json` states the five current repository roles.
3. `constellation.lock.json` records release tags, commits, tree digests, source
   bindings, and coordinate status for a coordinated release.
4. `STATUS.yaml` supplies a compact human-readable status.
5. `machine-node.json`, `first-receipt.json`, and
   `coordination-horizon.json` provide orientation and current work. They guide
   re-entry while runnable source and released contracts establish behavior.

### Rule: Keep authority roles independent

Distinguish the roles that affect the current decision:

- meaning and program acceptance;
- schema or shared-rule definition;
- source implementation;
- environment-observed evidence;
- selected-future evidence;
- comparison and adjudication;
- public projection and delivery; and
- accountable promotion or acceptance.

One team may carry several roles. The map still names each role separately so
a delivery route does not become evidence of the behavior it carries.

### Rule: Type every decision-changing relation

Use the smallest literal relation: `defines`, `implements`, `generates`,
`packages`, `simulates`, `observes`, `compares`, `projects`, `publishes`,
`accepts`, or `supersedes`. A generated schema or public page projects source;
the defining source keeps its stated authority.

### Rule: Carry exact coordinates

For every accepted cross-repository input, record the repository, source path
or artifact identity, full commit SHA, release tag when present, content or tree
digest when governed, relation, and coordinate status. Preserve explicit zero
placeholders while a candidate remains pending. The protected promotion path
replaces them with observed commit and digest values.

### Rule: Keep evidence mode beside the claim

State whether the supporting result is specified, simulated, locally verified,
or observed in a named environment. A simulated closure can be definitive
inside its selected future while production behavior remains established by
configured-environment evidence and accountable acceptance.

### Rule: Public projections keep source and delivery visible

Program Pages records its producing Git revision, projected source paths, and
file digests. That manifest establishes the identity and completeness of the
generated site. Source meaning, browser behavior, hosted responses, domain
configuration, and publication approval each retain their fitting observation.

### Rule: End at the next capable receiver

The map ends with a concrete choice: revise the program contract, update the
governance source, change the implementation or simulation, rerun comparison,
publish an accepted projection, promote exact coordinates, or return a question
to the accountable role. Name the smallest evidence or authority event that
would reopen the map.

## Operating sequence

1. **Name the object and decision:** State what is moving and what becomes
   decidable after its route is clear.
2. **Confirm repository state:** Read the current branch, worktree, role record,
   status, and relevant release or coordination source.
3. **Locate meaning:** Identify the source that defines the object's semantics
   and record its exact path and revision.
4. **Trace material relations:** Follow only the implementation, generation,
   simulation, observation, comparison, projection, or publication steps that
   affect the decision.
5. **Inspect the receiver:** State what the destination accepts and which
   identities, digests, evidence modes, and role boundaries must survive.
6. **Select the route:** Name the smallest update, comparison, promotion,
   deferral, or accountable question that creates a legible result.
7. **Preserve re-entry:** Leave the source coordinate, relation, evidence limit,
   next receiver, and reopening event.

## Output shape

```text
Object:
Decision:

Role | repository and source | exact coordinate | relation | established state

Current receiver:
Evidence boundary:
Next action:
Reopen when:
```

## Representative scenario

### Scenario: The Golden Specimen crosses four receiving roles

- Given
  `src/lims_eln_contracts/resources/scenarios/golden-specimen.v1.json` defines the
  released synthetic journey and carries its canonical digest
- And the packaged result schema defines the shared comparison shape
- When implementation and simulation produce their shaped observations and the
  comparison repository evaluates the pinned pair
- Then the map records the Program scenario and schema source, each producer's
  full release coordinate and evidence mode, and the comparator's pinned input
  coordinates
- And implementation retains authority for configured-environment observations,
  simulation retains authority inside the selected future, and comparison retains
  authority for the resulting difference classification
- And any revision to the scenario, schema, producer result, or comparison input
  reopens the map from the changed source coordinate

## Adaptation lineage

This repository-local derivative adapts the upstream
`source-authority-mapping` contract at revision
`a9ba528946fead335b49da3ae6dfb91c65588046`. The front matter records the
upstream path, Git blob, and SHA-256 digest. The derivative narrows the general
method to the five LIMS/ELN repository roles, their candidate and release
coordinates, their evidence modes, and the Program Pages receiver. Future
revisions preserve these source coordinates or record a new upstream relation.

## Completion

The map is ready when another collaborator can identify the source that defines
meaning, verify the current representation against its exact coordinate,
distinguish specified, simulated, observed, compared, and projected states,
name the receiver that can act, and return to the precise event that would
reopen the map.

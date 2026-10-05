---
title: External benchmark intake
version: 0.1.0
status: working
audience: human_and_ai_collaborators
source_band: public_possible
task_type: operational_collaboration
---

# External benchmark intake

## Desired receiving state

A public or authorized external benchmark enters the Program through an exact
source coordinate, a field- and relation-level provenance map, a stated claim
ceiling, and one bounded reception mode. The next capable repository can act
without treating an upstream label, synthetic result, interface claim, or
release carrier as Program acceptance.

Completion is a public-safe intake record containing:

- source kind and its applicable exact carriers: repository revision, dataset
  version and distribution, DOI or publisher record, standard edition, or API
  schema/documentation revision, plus artifacts, reported byte counts and
  digests where available, citation, terms, and observation date;
- the runnable interfaces, tests, data card, open defects, and reproduction
  prerequisites that affect the receiving question;
- supported use, transfer limits, populations represented or omitted, and
  provenance tiers for decision-changing fields;
- `reference_only`, `adapter_probe`, `derived_scenario`, or
  `held_for_review`, scoped to the admitted subject;
- one exact Program contract question and next receiver; and
- the event that would reopen the intake.

The current owner is [Program Issue #51](https://github.com/driftframestudios/lims-eln-program-specification/issues/51).
[Issue #50](https://github.com/driftframestudios/lims-eln-program-specification/issues/50)
owns contract changes exposed by the intake.

## Entry condition and safe non-entry behavior

Enter when the current task names an external benchmark and a Program decision,
and authorizes the network or local observations needed for that decision.
Begin in `observation_only` mode. Record the current Program revision, worktree
state, active Issue, and external subject before retrieving or executing
material.

When the exact release, applicable terms, artifact identity, provenance, or
intended use cannot be established, retain the source as `reference_only` or
`held_for_review`. Return the missing coordinate, its review owner, and the
observable event that permits another pass. Existing Program contracts and
accepted release coordinates remain unchanged.

## Authority map

| Surface | Authority retained |
| --- | --- |
| External repository, release, paper, data card, and terms | Upstream source statements and distributed artifacts at the named coordinate |
| Program Issue #51 and this runbook | Intake procedure and current work owner |
| Program Issue #50 and accepted Program source | Shared receiving meaning and acceptance boundary |
| Governance | Shared schemas, review grammar, and language rules |
| Enterprise | Configured adapter and service behavior |
| Simulation | Behavior inside a named selected future and synthetic scenario |
| Comparative | Pinned-input comparison and adjudication |
| Named human or accountable role | Publication, dependency adoption, deployment, real-data use, regulated acceptance, and upstream contribution decisions retained there |

## Ordered phases

### Phase 1 — Bind the external subject and receiving decision

**Owner:** Program maintainer acting through Issue #51; Issue #50 owns any
resulting shared-contract question.

**Action mode:** `observation_only`.

1. Name one external repository, release, paper, dataset, or interface and one
   Program decision it could change.
2. Record the current task grant, held decisions, intended receiver, and
   requested evidence depth.
3. Confirm Program branch, revision, worktree state, repository role, and
   relevant current Issue state.

**Checkpoint:** The intake has one bounded subject and one receiving decision.
This establishes scope and ownership, not upstream integrity or local fitness.

**Recovery:** Narrow a broad request to the first decision-changing subject.
Keep adjacent sources as unassessed candidates.

**Stop condition:** Stop before external retrieval when network access is not
granted, or when the named decision remains materially ambiguous. Return the
one source or decision choice needed for re-entry.

### Phase 2 — Bind release, artifact, citation, and terms

**Owner:** The upstream publisher defines its release carriers; Program records
their observed identities without changing them.

**Action mode:** `observation_only`; artifact download or execution requires a
separate grant when it changes the environment or incurs material cost.

1. Classify the source as repository/software, dataset/artifact, paper,
   standard/vocabulary, or API/interface.
2. Record its applicable exact carriers: a peeled revision for repository
   source; dataset version and distribution; DOI or publisher version; standard
   identifier and edition; or interface version and stable schema or
   documentation revision. Record the observation date for every kind.
3. Record every applicable decision-changing asset name, reported byte count,
   reported digest, content type, and download location. Mark carriers that do
   not exist for that source kind as `not_applicable`.
4. Locate citation, code license, data terms, terminology obligations, model
   terms, and source-corpus redistribution limits separately.
5. Label each coordinate as source-reported, API-observed, or locally verified.

**Checkpoint:** The record identifies the exact public subject and the source
of each integrity and terms observation. An API-reported digest establishes
release metadata; a locally computed digest additionally establishes the bytes
retrieved in that run.

**Recovery:** Keep metadata-only reception active while a separately named
material class awaits terms or integrity review.

**Stop condition:** Select `held_for_review` for material reuse when its terms,
release revision, or artifact identity remains unresolved. Citation and
metadata analysis can continue within their established boundary.

### Phase 3 — Inspect runnable behavior and reproduction boundary

**Owner:** Upstream source owns its implementation; the Program intake owns the
bounded observation and interpretation for the receiving question.

**Action mode:** `observation_only` for source reading; `implementation_authorized`
only when the current task grants an isolated execution or adapter probe.

1. Read the smallest relevant README, data card, schemas, interface
   advertisement, source implementation, and test configuration.
2. Inventory named resources, tasks, access controls, fixtures, and source data
   excluded from redistribution.
3. Inspect open defects and pull requests that materially affect the intended
   adapter or evaluation surface.
4. State which results can be reproduced from released artifacts and which
   depend on unavailable source material, licensed terminologies, credentials,
   model services, or private infrastructure.

**Checkpoint:** The record establishes the source behavior visible at the
named revision and a bounded reproduction route. Documentation alone
establishes an advertised capability; source or an executed probe establishes
its matching behavior at the scope observed.

**Recovery:** Reduce the observation to source reading or one interface slice.
Carry unavailable dependencies as explicit reproduction limits.

**Stop condition:** Stop execution when secrets, material downloads, licensed
sources, cost, or environment changes exceed the current grant. Preserve the
source-reading result and route the exact remaining observation.

### Phase 4 — Classify provenance, claims, and population reach

**Owner:** Program records the reception map; upstream sources retain their
statements; accountable clinical and population reviewers retain acceptance.

**Action mode:** `observation_only`.

1. Classify decision-changing fields and relations as source-exact,
   deterministic transform, ontology-resolved, LLM-extracted, LLM-linked,
   generated, human-curated, or unresolved and flagged.
2. State the benchmark's construction purpose, included and omitted population
   dimensions, validation design, small-cell posture, and known error classes.
3. Separate interface and workflow utility from population calibration,
   clinical validity, causal inference, payer behavior, deployment fitness,
   and regulated acceptance.
4. Record the claim ceiling beside each proposed local use.

**Checkpoint:** The map establishes how the relevant material formed and which
claims its current evidence can support. It leaves every separately governed
acceptance claim open.

**Recovery:** Mark unclear fields `unresolved/flagged` and retain their source
value. Select a smaller use whose evidence ceiling is established.

**Stop condition:** Stop before deriving a population, clinical, or operational
claim that exceeds the observed construction and validation evidence. Route
that claim to its evidence owner.

### Phase 5 — Select a reception mode and exact Program question

**Owner:** Program Issue #51 owns the intake disposition; Issue #50 owns a
shared-contract change; the named receiving repository owns later execution.

**Action mode:** `observation_only` for classification. A later adapter,
scenario, dependency, or source change uses its own authorized task.

1. Apply the `external-benchmark-reception` skill to select
   `reference_only`, `adapter_probe`, `derived_scenario`, or
   `held_for_review` for the bounded subject.
2. Name semantic matches, missing Program objects, translation needs,
   authority differences, and useful counterexamples.
3. State the smallest contract question the intake makes decidable.
4. Route upstream defects and contribution candidates separately from local
   reception.

**Checkpoint:** One mode and scope explain what can proceed, what remains a
reference, and which Program decision follows. The classification supplies no
execution, contribution, adoption, or publication authority.

**Recovery:** Use a component-level disposition when the whole source is too
broad. For example, keep a release as `reference_only` while one read-only
interface becomes an `adapter_probe`.

**Stop condition:** Select `held_for_review` when a missing term, provenance
fact, authority decision, or integrity result could materially change the
mode.

### Phase 6 — Return one receiver-ready intake

**Owner:** The active Program Issue receives the intake; the next capable
repository or accountable role receives only its bounded continuation.

**Action mode:** `observation_only` for the handback; external mutation follows
its separately granted route.

1. Return the exact source coordinate, observed surfaces, mode, provenance and
   claim map, known gaps, and Program question.
2. State the commands or API observations used, normalized result, and what
   each observation leaves open.
3. Name one next receiver and one exact re-entry event.
4. Keep raw logs, credentials, protected response material, private locators,
   and user-specific paths with their authorized owner.

**Checkpoint:** A cold collaborator can recover the source subject, evidence
boundary, chosen route, current owner, and next action without another private
context source.

**Recovery:** Amend the existing Issue return when one missing fact changes the
decision. Create another artifact only when a materially new receiver needs a
distinct contract.

**Stop condition:** The route stops when the intake has one capable receiver or
a deliberate hold with a named release event.

## Current standing

This route remains `working`. The Program's administrative contract family now
uses a repository-owned, source-neutral adapter fixture, so it supplies no
external-subject exercise for this intake procedure. A future benchmark enters
only when a receiving claim depends on that external identity and the user has
authorized the applicable observations. That future pass will name its own
coordinate, terms, integrity evidence, reception mode, claim ceiling, and next
receiver.

## Handback

Return `pass`, `friction`, or `blocker` to the active Issue:

```text
Disposition:
External subject and exact coordinate:
Selected mode and scope:
Decision-changing findings:
Observation and normalized result:
What the observation establishes:
Coverage and claim boundary:
Terms or integrity review still open:
Current Issue:
Next receiver:
Re-enter when:
```

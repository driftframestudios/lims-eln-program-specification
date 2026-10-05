---
name: external-benchmark-reception
description: Classifies an external synthetic or benchmark system into a coordinate-bound reference, adapter probe, derived scenario, or held review route. Applies when a LIMS/ELN repository may learn from external artifacts, interfaces, labels, or methods while preserving distinct source and acceptance authority.
metadata:
  source_band: public_possible
  skill_version: 0.1.0
  adaptation_relation: repository_local_original
---

# External benchmark reception

## Contract

- **What:** A source- and claim-aware method for deciding how an external
  benchmark can enter the LIMS/ELN constellation.
- **When:** An external synthetic system, dataset, paper, repository, release,
  interface, task, or evaluation method may inform a Program contract or one
  of its receiving repositories.
- **Boundaries:** The current task supplies network, download, execution,
  dependency, contribution, and repository-mutation authority. Upstream terms
  govern upstream material. Reception preserves the distinction among source
  statements, locally observed behavior, derived scenarios, population
  evidence, clinical validity, configured-environment evidence, and
  accountable acceptance.
- **Result:** One bounded reception record identifies the exact external
  subject, provenance and claim ceilings, the smallest useful reception mode,
  its current receiver, the observation that supports it, and the event that
  would reopen the decision.

## Fit and attention

- **Useful when:** A credible external source could become a reference,
  interoperability probe, scenario seed, evaluation input, or implementation
  dependency and those roles could otherwise be conflated.
- **Poor fit when:** The source is already an accepted pinned dependency with a
  current receiving contract, or a short citation supplies the entire need.
- **Smallest useful dose:** Bind one source subject and one receiving decision,
  inspect only the source surfaces that can change that decision, and select
  one mode.
- **Interactions:** `source-authority-mapping` traces accepted meaning and
  evidence through the constellation. `constellation-coherence-reconciliation`
  settles a later coordinated release. The external-benchmark intake runbook
  orders the Program-specific procedure; this skill owns the reusable
  reception decision.
- **Rest or release when:** The selected mode has an exact source coordinate,
  claim ceiling, receiver, evidence boundary, and reopening event, or a named
  review owner holds the unresolved term or artifact question.

## Rules

### Rule: Identity precedes interpretation

Bind the source kind first, then record the stable identity carriers that kind
actually supplies. A missing Git tag is not an integrity gap for a DOI-versioned
paper or publisher-versioned standard.

| Source kind | Exact identity carriers |
| --- | --- |
| Repository or software release | Repository, release or tag when present, full revision, artifact identity, and reported digest and bytes when available |
| Dataset or distributed artifact | Publisher, dataset identity and version, distribution identity, reported digest and bytes, and access date |
| Paper | DOI, arXiv or publisher record and version, publication date, citation carrier, and authoritative full-text location |
| Standard or vocabulary | Publisher, canonical identifier, edition or version, publication date, and authoritative specification location |
| API or hosted interface | Provider, interface identity and version, stable schema or documentation revision, observation date, and the inspected capability surface |

Record citation and applicable code, data, model, terminology, and source-corpus
terms beside those carriers. Distinguish an API-reported digest from a locally
computed digest and a release tag from its peeled commit. Mark a field
`not_applicable` when the source kind has no corresponding carrier; use
`unresolved` only when an applicable identity is expected but unavailable.

### Rule: Source, observation, and derivation retain separate owners

Record what the upstream source states, what the current reception pass
observes, and what the constellation later derives as three relations. An
upstream field name remains a source-exact input; a normalized classification,
adapter projection, or synthetic scenario receives a constellation-owned
identity and version.

### Rule: Provenance is field- and relation-specific

Classify material claims using the smallest supported tier: source-exact,
deterministic transform, ontology-resolved, LLM-extracted, LLM-linked,
generated, human-curated, or unresolved and flagged. A dataset can contain
several tiers. Its repository-level description does not replace field-level
provenance.

### Rule: A benchmark carries a claim ceiling

State the purpose, construction method, populations represented or omitted,
known defects, validation design, and reproduction boundary. Synthetic
plausibility can support interface and workflow experiments while population
calibration, live clinical validity, payer behavior, deployment fitness, and
regulated acceptance remain with their own evidence routes.

### Rule: Reception uses the least-authoritative useful mode

Select one mode for the named subject and decision:

| Mode | Use it when | Material result |
| --- | --- | --- |
| `reference_only` | The source informs design or comparison without local execution or derived behavior | A coordinate-bound source and claim map |
| `adapter_probe` | A small interface slice can test contract fit without adopting the external domain model | A read-only or isolated adapter observation |
| `derived_scenario` | Source material can seed a new, independently identified synthetic scenario | A locally versioned scenario with derivation and claim boundaries |
| `held_for_review` | Terms, provenance, artifact integrity, authority, or intended use is unresolved | A protected current state, review owner, and release event |

Different components can have different modes when each scope is explicit. A
source retained as a reference can expose one interface to an adapter probe.

### Rule: Capability and authority are tested separately

Inspect runnable interfaces, tests, data cards, schemas, open defects, and
reproduction prerequisites for the named use. An advertised interface supplies
a discovery lead. Source behavior and a bounded observation establish
capability; Program and accountable receivers establish local acceptance.

### Rule: Terms follow each material class

Review code, data, terminology, model, and documentation terms independently.
A code license does not settle redistribution of a database, ontology, model
output, or upstream source corpus. Reception can proceed through metadata and
public interfaces while material reuse remains held for its specific review.

### Rule: Known gaps become receiver inputs

Record open upstream defects and absent resource families when they affect the
receiving question. Route a useful upstream contribution candidate separately
from local adoption. A contribution begins only through its own task grant.

### Rule: The next capable repository receives the result

Program owns shared meanings and acceptance boundaries; Governance owns shared
schema and review grammar; Enterprise owns configured implementation behavior;
Simulation owns selected-future scenarios; Comparative owns paired evaluation.
End at the repository that can create the next decision-changing result.

## Operating sequence

1. **Bind the decision:** Name one external subject, receiving question,
   current Issue, granted actions, and held decisions.
2. **Capture the subject:** Record the source-kind identity carriers, artifacts,
   digests, bytes, citation, terms, and retrieval observation that apply, with
   their evidence type.
3. **Inspect material behavior:** Read the smallest runnable interfaces, tests,
   schemas, data card, defects, and reproduction instructions that can answer
   the question.
4. **Map provenance and claims:** Classify decision-changing fields and
   relations, then state supported use, omitted populations, and claim ceiling.
5. **Compare the receiver:** Identify semantic matches, missing objects,
   translation needs, incompatibilities, and ownership differences.
6. **Select the mode:** Choose `reference_only`, `adapter_probe`,
   `derived_scenario`, or `held_for_review` for the bounded subject and state
   the observation that supports the choice.
7. **Return the route:** Give one receiver the coordinate, findings, evidence
   boundary, unresolved review owner, and exact event that reopens reception.

## Output shape

```text
External subject and exact coordinate:
Receiving decision:
Granted actions and held decisions:
Source statements:
Observed behavior:
Provenance tiers and claim ceiling:
Terms and reproduction boundary:
Selected mode and scope:
Current receiver:
Observation and coverage boundary:
Reopen when:
```

## Representative scenario

### Scenario: A generated insurance string enters a Program contract question

- **Given:** A pinned synthetic benchmark release carries an `insurance` field
  produced during LLM profile generation
- **And:** Its value may help exercise normalization and administrative
  workflow without establishing enrollment, coverage, prevalence, or a payer
  decision
- **When:** Reception evaluates the field
- **Then:** The raw string remains source-exact input with generated provenance
- **And:** Any normalization, assignment, policy result, or reviewed decision
  receives its own local identity and version
- **And:** A derived synthetic scenario begins only after the Program contract
  defines those distinctions and the task grants that work

### Scenario: A paper has no Git release

- **Given:** A benchmark method is described by a DOI-versioned paper whose
  publisher record and version of record are stable
- **And:** No source repository or downloadable benchmark artifact is part of
  the receiving decision
- **When:** Reception binds the external subject
- **Then:** The DOI, paper version, publication date, citation, and authoritative
  full text form the exact coordinate
- **And:** Repository, tag, commit, artifact digest, and byte count are recorded
  as not applicable rather than unresolved
- **And:** Any later code implementation receives its own source coordinate and
  observation before it supports a capability claim

## Completion

Reception completes when the exact external subject, material provenance,
claim ceiling, term and reproduction boundaries, selected mode, supporting
observation, current receiver, and reopening event are legible. Another pass
begins when the upstream coordinate, intended use, source behavior, terms,
local contract, or receiving evidence changes.

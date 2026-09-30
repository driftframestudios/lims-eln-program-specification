---
title: Administrative-context contract evolution
version: 0.1.0
status: exercised
audience: human_and_ai_collaborators
source_band: public_possible
task_type: operational_collaboration
---

# Administrative-context contract evolution

## Desired receiving state

A new insurance, coverage, eligibility, authorization, claim, billing, payment,
or patient-responsibility distinction enters the Program as a versioned contract
whose source value, normalized classifications, assignment, policy evaluation,
accepted decision, and impact observation remain independently inspectable.

Completion provides:

- one named receiving decision and authoritative object owner;
- canonical identities and an explicit compatibility direction;
- independent source, subject-effective, policy-effective, observation, review,
  and release times where they affect meaning;
- examples for success, absence, ambiguity, conflict, abstention, override, and
  unchanged clinical evidence under changed administrative context;
- checked schema projections and dependency closure;
- migration notes and exact receiving-Issue handoffs; and
- a separately retained human decision for publication, deployment, real payer
  material, and regulated use.

[Program Issue #50](https://github.com/driftframestudios/lims-eln-program-specification/issues/50)
owns the current contract family. [Issue #51](https://github.com/driftframestudios/lims-eln-program-specification/issues/51)
owns this procedure.

## Entry condition and safe non-entry behavior

Enter when an active Program Issue names the administrative distinction and
the downstream decision its representation must support. Begin with existing
Program vocabulary, schemas, examples, generated projections, and receiving
repository contracts. Use `observation_only` until the task grants source
changes.

When object ownership, evidence standing, compatibility direction, or an
accountable decision path remains unresolved, retain the observation as an
open contract question. Existing object meaning and released schemas continue
unchanged while the owning Issue receives the smallest decision needed to
resume.

## Layer map

| Layer | Contract job | Authority boundary |
| --- | --- | --- |
| Raw source | Preserve the received value and its exact source coordinate | Source supplies the value; reception records provenance |
| Normalized classification | Project one or more controlled terms while retaining ambiguity and abstention | Versioned vocabulary and method own the projection |
| Assignment | Apply a declared synthetic or authorized mapping to a subject and interval | Assignment owner and evidence standing remain explicit |
| Policy evaluation | Evaluate inputs under a versioned rule set and precedence model | Policy owner, jurisdiction, product, and effective time govern the result |
| Accepted decision | Record coverage, authorization, claim, billing, or related state plus recourse | Named accountable actor and review receipt own acceptance |
| Impact observation | Compare controlled clinical and administrative outputs without exceeding the design | Comparative evidence owns the bounded finding |

Clinical evidence, diagnosis, scientific interpretation, and care need remain
available independently from these layers.

## Ordered phases

### Phase 1 — Name the decision, object, and evidence ceiling

**Owner:** Program Issue #50 and the maintainer authorized to change its
contract source.

**Action mode:** `observation_only`, then `implementation_authorized` when the
current task grants the named contract changes.

1. State the downstream decision, actor, subject, episode or specimen scope,
   evidence mode, and assurance stage.
2. Identify the smallest new object or revision needed and every existing
   object whose meaning must remain stable.
3. Name populations, jurisdictions, products, workflows, and omissions
   represented by the scenario.

**Checkpoint:** The proposed change has one receiving decision and an explicit
claim ceiling. This establishes scope, not clinical, payer, or population
validity.

**Recovery:** Split a combined object into independently owned questions. Keep
unresolved terms as open records rather than selecting a convenient meaning.

**Stop condition:** Stop implementation when the accountable decision, object
owner, or evidence ceiling remains ambiguous enough to change schema meaning.

### Phase 2 — Separate source, classification, assignment, policy, and decision

**Owner:** Program defines shared distinctions; Governance receives any shared
schema or review-grammar need.

**Action mode:** `implementation_authorized` for the accepted Program scope.

1. Preserve each raw source value and its source identity.
2. Model normalized terms as a multi-label projection with vocabulary and
   method versions, confidence, ambiguity, `unknown`, and `abstain`.
3. Give assignment a distinct owner, method, interval, and synthetic or
   authorized evidence standing.
4. Give the policy rule set its own owner, jurisdiction, product, version,
   effective interval, precedence, required inputs, missing-input behavior,
   and digest.
5. Give each accepted administrative decision a class, state transition,
   actor or authority, reasons and evidence, policy coordinate, recourse, and
   review receipt.

**Checkpoint:** Each layer can change without silently rewriting another, and
an AI-generated or deterministic proposal remains distinct from accountable
acceptance.

**Recovery:** Retain an unknown, ambiguous, conflicting, or abstained result
with its source value and next review owner. Add a missing layer before adding
an overloaded field.

**Stop condition:** Stop before one field collapses eligibility, enrollment,
coverage interpretation, authorization, coding, claim acceptance, payment, or
patient responsibility into a shared state.

### Phase 3 — Select compatibility and extension behavior

**Owner:** Program owns canonical meaning; Governance owns shared schema rules;
each receiving repository owns adoption of the accepted version.

**Action mode:** `implementation_authorized` for source and migration notes;
receiver adoption remains separately authorized.

1. Select stable canonical JSON Schema identities and dependency closure before
   publication URLs.
2. Use closed enums for genuinely closed state machines. Use identified open
   records and a named extension envelope for evolving payer, plan, policy,
   jurisdiction, and classification vocabularies.
3. Define additive compatibility, meaning-changing revision, deprecation, and
   replacement behavior.
4. Keep vocabulary, policy, prompt, model, code, adapter, and effective-date
   versions independently addressable.

**Checkpoint:** A receiver can distinguish an additive term from a changed
meaning and can reject or preserve unknown extensions according to the declared
contract.

**Recovery:** Introduce a new version and migration when an existing meaning
would change. Preserve the prior version as an accepted historical subject.

**Stop condition:** Stop release preparation when dependency closure,
compatibility direction, or replacement behavior remains unspecified.

### Phase 4 — Exercise representative and boundary examples

**Owner:** Program owns source examples; Simulation later owns selected-future
execution; Comparative later owns paired evaluation.

**Action mode:** `implementation_authorized` for synthetic Program examples.

Create independently identified examples for:

1. one unambiguous source label and accepted classification;
2. one value with multiple valid classifications;
3. absent source evidence and explicit `unknown`;
4. ambiguity that results in `abstain`;
5. conflicting rules with declared precedence or unresolved conflict;
6. a reviewer override that preserves the proposal and rationale;
7. enrollment or eligibility that remains distinct from a payer decision; and
8. unchanged clinical evidence and diagnosis while administrative state varies.

Each example binds source, vocabulary, method, policy, scenario, and contract
versions plus the relevant clocks and evidence ceiling.

**Checkpoint:** The examples establish serialization and intended distinctions,
including absence and conflict. They remain synthetic specification evidence,
not live-payer, clinical-validity, causal, or population evidence.

**Recovery:** Add the smallest counterexample that exposes an overload or
unstated default. Revise source meaning before adapting downstream code.

**Stop condition:** Stop before a successful-path example becomes the sole
evidence for ambiguity, missing inputs, precedence, recourse, or clinical
independence.

### Phase 5 — Generate and check projections

**Owner:** Program source models own canonical meaning; generated schemas are
their named projection; the Program validator owns repository consistency.

**Action mode:** `implementation_authorized`.

1. Generate schema projections through the repository-owned command.
2. Check canonical examples, negative cases, dependency closure, identifiers,
   and digests.
3. Run the smallest focused tests, schema check, Program validator, language
   check, secret-shape scan, and complete suite required by the current change.
4. Record exact commands, normalized results, and environment details that
   affect interpretation.

**Checkpoint:** Passing generation and validation establish source-to-schema
agreement and exercised repository invariants at the inspected revision. They
leave configured-environment, population, clinical, payer, and accountable
acceptance claims open.

**Recovery:** Correct canonical source first, regenerate once, and repeat the
same check. Route an environment failure through
`proportionate-recovery-routing` when source behavior remains unobserved.

**Stop condition:** Stop handoff while committed projections differ from their
source, examples violate the accepted invariants, or a failing check lacks a
bounded owner and release event.

### Phase 6 — Pass the accepted version to the constellation

**Owner:** Program prepares the source handoff. Simulation, Enterprise,
Comparative, and Governance each own their receiving Issue and evidence.

**Action mode:** `observation_only` for handoff preparation; repository changes,
publication, and deployment use their own grants.

1. Bind accepted Program revision, contract version, schema identities and
   digests, examples, migration notes, and known limits.
2. Give each receiver one bounded job and pass condition.
3. Keep public schema hosting, API activation, production hostname, real payer
   material, and accountable acceptance with their named human owner.
4. Continue through the constellation contract release handoff runbook.

**Checkpoint:** Every receiver can verify the same Program source subject and
identify the evidence it alone can create.

**Recovery:** Preserve the last accepted Program version while one receiver
routes a compatibility or authority question back to Issue #50.

**Stop condition:** Stop the affected handoff when coordinates, generated bytes,
migration behavior, or receiver acceptance are incomplete. Unaffected
observation and planning routes can remain active.

## Candidate-fixture exercise — Issue #50 example family

**Exercise date:** 2026-09-29

**Action mode:** `implementation_authorized`

**Source owner:** Program Issue #50

The exercise authored a Program-owned synthetic fixture beside a metadata-only
Synthetic Hospital source manifest. The upstream database was neither
downloaded nor executed, and no upstream `insurance` value enters the Program
fixture. The manifest and fixture therefore exercise separate source and local
meaning paths:

1. `ExternalSourceManifest` binds the upstream release and API-observed asset
   coordinate.
2. `ProvenanceAssertion` records API-observed release metadata separately from
   independently authored fixture formation.
3. `InsuranceClassification` preserves a present raw label, represents absent
   source evidence as `unknown`, and can emit one term, multiple terms,
   ambiguity, or `abstain` under independently versioned vocabulary and method
   coordinates.
4. `CoverageEnrollment` carries a separately declared synthetic enrollment or
   eligibility state and effective interval.
5. `PolicyRuleSet` supplies a versioned synthetic policy, required inputs,
   missing-input behavior, precedence, and its own effective interval.
6. `AdministrativeDecision` records one policy result, actor, reason, recourse,
   and reviewed disposition without becoming clinical evidence.
7. `DecisionImpactObservation` compares unchanged clinical evidence under a
   changed administrative variable.
8. `PopulationScenario` states whether the exercise concerns workflow,
   accessibility, policy mechanics, or population distribution and retains its
   omissions.

The candidate fixtures exercise a single-label acceptance, a multi-label
acceptance, absent source evidence routed to `unknown`, ambiguity routed to
abstention, a missing policy input routed to an abstained evaluation, a
precedence-resolved rule conflict, a pending enrollment, and a reviewed
revision that preserves the engine proposal beside the final outcome. The
downstream handoff remains held until Issue #50 accepts canonical identities,
schemas, dependency closure, examples, and migration notes.

### Exercise observation

The exercise confirmed that layer separation alone is insufficient when time
and evidence standing remain implicit. This runbook therefore requires
independent source, subject-effective, policy-effective, observation, review,
and release times where they change meaning, plus an evidence ceiling on each
example. This route is `exercised`; the separate constellation handoff remains
`working` until the accepted schema family enters it.

## Handback

```text
Contract decision and version:
Changed canonical sources and generated projections:
Compatibility and migration behavior:
Examples and counterexamples exercised:
Exact validation commands and normalized result:
What the evidence establishes:
Claims and acceptances still open:
Current Issue:
Next receiving repository and pass condition:
Re-enter when:
```

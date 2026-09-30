# External benchmark and administrative-context contracts

## Purpose

This contract family lets the LIMS/ELN constellation receive an external
synthetic-care benchmark while source formation, local interpretation,
administrative policy, clinical evidence, and accountable acceptance retain
separate identities. The first exercised source is Synthetic Hospital v1.3.
Its generated `insurance` text supplies useful interface input. Enrollment,
coverage, prevalence, payer behavior, and clinical validity continue to depend
on evidence and authority that this source does not provide.

The family is version `1.0.0`. The Python distribution that carries it is the
`0.4.0` successor candidate. The Program release remains `spec-v0.3.1`; these
version lines advance independently. A reviewed merge commit will replace the
pending package source coordinate after the package bytes are accepted.

## Source and generated carriers

The canonical dependency-closed conformance bundle is
[`external-administrative-contracts.v1.json`](../src/lims_eln_contracts/resources/external-administrative-contracts.v1.json).
It names the objects, schema roots, examples, ownership, compatibility rules,
invalidation events, and receiving release event, then carries the complete
record graph used by the examples.

Two self-contained Draft 2020-12 projections support non-Python consumers:

- [`external-source-manifest.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/external-source-manifest.v1.schema.json)
  validates an intake coordinate without requiring the remaining family.
- [`external-administrative-contract-set.v1.schema.json`](../src/lims_eln_contracts/resources/schemas/external-administrative-contract-set.v1.schema.json)
  exposes the complete family under one dependency-closed root.

The Python models are the schema-generation authority. The generator compares
committed bytes with those models, while the typed aggregate enforces
relationships that JSON Schema expresses only as declared semantic
invariants.

The three files below `resources/administrative/` are reader-specific
projections of that canonical bundle. The source-manifest projection selects
its first manifest, the independent-policy projection removes the external
source and its provenance assertion, and the counterfactual projection selects
its first impact observation. Run
`python3 scripts/generate_administrative_examples.py --check` to establish
byte equality; edit the canonical bundle and regenerate projections when a
fixture changes.

## Exercised examples

- [`synthetic-hospital-v1.3.v1.json`](../src/lims_eln_contracts/resources/administrative/synthetic-hospital-v1.3.v1.json)
  binds the public `v1.3` tag to commit
  `77cc57e9c595ce731bbdde4fabdcbd25a8458ae2` and records the
  `benchmark_v1.3.db` release asset as 92,430,336 bytes with SHA-256
  `8fb8eb114508f272588b6121ca78cff53a6fc2e5f47d7aa01bfbb5bcef4e6ddb`.
  It points to the pinned data card, license, citation file, and upstream FHIR
  limitation without copying the database. The media type remains the GitHub
  API-reported `application/octet-stream`; the `.db` name does not substitute
  for a local download, content inspection, or execution observation.
- [`independent-multilabel-policy.v1.json`](../src/lims_eln_contracts/resources/administrative/independent-multilabel-policy.v1.json)
  is an independently authored synthetic scenario. It preserves one raw label,
  exercises accepted single- and multi-label classifications, represents
  absent source evidence as `unknown`, retains explicit abstention, pending
  enrollment, a missing-input evaluation, a precedence-resolved policy
  conflict, and a reviewed revision that preserves the engine proposal beside
  the final outcome.
- [`administrative-counterfactual.v1.json`](../src/lims_eln_contracts/resources/administrative/administrative-counterfactual.v1.json)
  varies administrative state while clinical evidence and clinical output
  digests remain equal. Each arm binds its administrative input to the cited
  decision's policy-input digest and its administrative output to the
  canonical digest of that complete decision. Its observation classifies that
  result as an administrative-only divergence.

These examples are fixtures for contract behavior. They are independent of the
upstream database and avoid patient, customer, payer, or deployment claims.
The canonical bundle remains their one authored authority. Deterministic,
byte-checked projections give a receiver either the source manifest, the
source-independent conformance set, or the small counterfactual root without
creating parallel record owners.

## Object and authority map

| Object | Meaning it owns | Meaning it leaves with another owner |
| --- | --- | --- |
| `ExternalSourceManifest` | Immutable upstream and asset coordinate, terms, observations, limitations, and local adapter state | Upstream behavior beyond the named observation; local adoption |
| `ProvenanceAssertion` | Formation and resolution of one field or relation | Truth or acceptance beyond the named evidence and review |
| `InsuranceClassification` | Raw-preserving proposal, open terms, ambiguity or abstention, and reviewer disposition | Enrollment, coverage, authorization, billing, or payer decision |
| `CoverageEnrollment` | Declared or synthetic enrollment/eligibility context over an effective interval | A coverage interpretation or final payer action |
| `PolicyRuleSet` | Versioned declared rules, precedence, required inputs, conflict handling, and missing-input behavior | Live payer policy unless separately established |
| `AdministrativeContext` | Administrative state beside a release-scoped subject and episode | Clinical evidence, diagnosis, and accountable decision authority |
| `AdministrativeDecision` | One reviewed coverage, authorization, claim, billing, payment, or related transition with recourse | Other administrative state families and clinical truth |
| `DecisionImpactObservation` | Controlled comparison inputs, outputs, divergence class, and claim ceiling | Causal or population inference beyond the design |
| `PopulationScenario` | Purpose, construction, dimensions, omissions, review participants, small-cell policy, and explicit calibration standing with supporting references when calibration is claimed | Population representation without supporting calibration evidence |

## Deterministic policy and impact digests

`urn:driftframe:lims-eln:policy-input-digest:1.0.0` is the canonical SHA-256
digest of the `PolicyInputDigestMaterial` document carried by each
`PolicyEvaluation`. The material carries the decision context and every
declared policy input in policy order. Each input records `present` or
`missing`, source record identity and version, and ordered match values.
Classification values use state or term identity plus vocabulary identity and
version; enrollment values use state. Raw and display labels stay available
for audit and visitor language while remaining outside deterministic matching.
A present source with no terms differs from a missing source.

The aggregate derives missing inputs, predicate matches, overlaps, precedence,
and the selected outcome from that same material. An evaluation cannot supply
an independent match list or opaque digest. Receivers implementing the profile
serialize the material with the package's canonical JSON rules: UTF-8,
lexicographically sorted object keys, compact separators, finite JSON values,
and SHA-256 with the `sha256:` prefix.
The dependency-closed aggregate schema carries the material and its component
types in `$defs`. Python receivers can import `PolicyInputDigestMaterial` and
`build_policy_input_digest_material` from `lims_eln_contracts`; the aggregate
requires that carried material to equal the builder's derivation from the cited
classification and enrollment records.

`urn:driftframe:lims-eln:administrative-decision-digest:1.0.0` applies the same
canonical JSON and SHA-256 rules to the complete `AdministrativeDecision`
record. A counterfactual arm identifies both profiles and must equal the input
digest and full decision digest of its referenced decision. The two arms also
name distinct contexts and decisions. These bindings make administrative
divergence reproducible from the canonical bundle instead of relying on
uninterpreted digest values.

Program owns these bounded exchange meanings and examples. Simulation owns
designed population and access-friction truth. Enterprise owns configured
adapter, classifier, policy, API, persistence, and runtime behavior.
Comparative owns paired execution and claim-bounded evaluation. Governance owns
generic provenance, population-claim, review, and recourse grammar. A receiver
can adopt the family after a reviewed Program merge supplies the `0.4.0`
package source commit and digest; each receiving Issue still decides its own
implementation or publication action.

## Compatibility

Core records are closed. Domain vocabularies use identified terms with their
own system and version so emerging payer, program, plan, decision, and reason
codes do not become prematurely frozen enums. Closed workflow states remain
enums because a consumer must distinguish each transition deliberately.

- A patch preserves required fields, field meanings, authority invariants,
  digest profiles, and emitted values.
- An additive optional field can share the major version when producers emit it
  only to receivers that declare support. A governed extension reference is
  the preferred path when negotiation is unavailable.
- A new open-vocabulary term is compatible when its system/version identity is
  preserved and the receiver can retain or route an unknown term.
- A changed term meaning receives a new term identity or vocabulary version.
- A new required field, removed field, changed field meaning, new closed-state
  value, changed digest profile, or relaxed authority invariant advances the
  contract major version and provides an explicit adapter.

The migration from package `0.3.1` is recorded in
[`0.3.1-to-contract-package-0.4.0.md`](migrations/0.3.1-to-contract-package-0.4.0.md).

## Invalidation and re-entry

Re-review begins when a source tag, commit, release asset, digest, byte count,
license, data card, citation, known limitation, adapter, vocabulary, model,
prompt, code artifact, policy, population claim, review disposition, or digest
profile changes. A changed upstream coordinate forms a new manifest rather
than silently replacing the observed subject. A changed local meaning forms a
new contract or term version. An unresolved integrity, provenance, or rights
question keeps the affected component in `reference_only` or
`held_for_review` posture.

The Program runbooks in [`.agents/runbooks/`](../.agents/runbooks/README.md)
order intake, contract evolution, and release handoff. The
[`external-benchmark-reception`](../.agents/skills/external-benchmark-reception/SKILL.md)
skill supplies the reusable reception decision.

## Constellation skill cultivation

This change exercises `external-benchmark-reception` against one immutable
release and one bounded receiving decision. That repeated decision is distinct
from the longer Program intake procedure, so it is carried as a repository
skill.

`administrative-authority-contracting` remains a named candidate. It becomes
eligible for a portable contract after both Simulation and Enterprise use this
family and reveal whether raw value, classification, policy evaluation,
accountable review, and recourse separation remains stable in authored and
configured behavior. Simulation-specific scenario-pack authoring,
Enterprise-specific removable-adapter qualification, Comparative-specific
claim-ceiling evaluation, and Governance-specific provenance/recourse review
remain observations within their existing Issues until repeated use shows a
method distinct from their runbooks and source contracts.

## Evidence boundary

The Program validator, administrative-example projection check,
generated-schema check, and unit suite establish the declared structure,
strict parsing, canonical and projected example equality, canonical schema
bytes, source coordinates, cross-record references, policy-output binding,
review authority and chronology, provenance acyclicity, and the counterfactual
digest relation exercised by these fixtures. The read-only source intake
records the GitHub API-reported asset digest, byte count, and media type; it
does not claim that this change downloaded, inspected, or executed the
database. An external context can therefore retain `source_reported` standing;
`artifact_verified` requires a manifest observation that records a locally
hashed download.

Population calibration, epidemiologic representation, live-payer semantics,
clinical validity, configured adapter behavior, deployed API behavior,
security and privacy qualification, regulated use, and accountable operational
acceptance remain open to their named evidence and review routes.

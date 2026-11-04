---
name: contextual-jargon-scan
description: Classifies specialist and collaboration-local wording in a bounded Program Specification corpus and revises replaceable shorthand into ordinary language. Applies in stride when public orientation, contracts, release prose, or cross-repository instructions may assume context the reader does not share.
metadata:
  source_band: public_possible
  skill_version: 0.2.0
  upstream_repository: https://github.com/driftframestudios/human-ai-systems-exemplars.git
  upstream_path: .agents/skills/contextual-jargon-scan/SKILL.md
  upstream_revision: 0c023343e46cd9b1333a63c2d509787352fbad14
  upstream_blob_sha1: 3c3a94db99152385253e0281c8afa8fea8208ac5
  upstream_sha256: da383f99eaff364d7e17c3bff93d8da618ec95894a45ff78a9620d8d7fc81523
  adaptation_relation: repository_local_derivative
---

# Program Specification contextual jargon scan

## Contract

- **What:** A context-aware review that distinguishes exact program and
  evidence language from shorthand a reader must decode.
- **When:** A bounded public, cross-repository, contract, release, Pages, or
  instruction surface is already receiving material prose changes.
- **Boundaries:** Schema keys, identifiers, version coordinates, code,
  quotations, accessibility meaning, established technical and regulated
  terms, and source-owned language retain their fidelity. Search tools produce
  candidates; contextual reading determines whether a revision helps.
- **Result:** A scoped occurrence map, targeted revisions, intentional
  retentions that affect future work, and a verification signal tied to the
  changed prose.

## Rules

### Rule: Scope and reader come first

Name the files already changing, intended readers, exclusions, and candidate
word families. Keep an in-stride scan within the active Program surface.

### Rule: Search results are candidates

Search inflections and nearby forms with enough context to read their role.
Counts locate repeated language; contextual reading establishes whether a
revision helps.

### Rule: Read a count alongside its claim

When an author uses an inventory to support readiness or completion, ask what
changed for this reader. A count can establish coverage of a named set or send
a scientist to specific discrepant measurements. A claim of equivalence asks
for the comparison, methods, and units that support that claim. Keep the
smaller supported result when the evidence establishes coverage alone.

### Rule: Give a reader enough context to decide

Use the optional Program Vale profile on a selected authored Markdown passage.
Read a suggestion with the surrounding paragraph, then read the excerpt a
receiver may see on its own. Identify the actor, actual object or action, and
the decision that would change. Keep literal terms such as a laboratory
instrument, define a useful metaphor near first use, or replace shorthand
with its concrete meaning. A repository with a different vocabulary can give
the same word a different job.

When interpretation changes scientific meaning, preserve the original and
return one specific question to the accountable scientist. An author can
finish after a passage supports its reader's task. One consequential deferred
question can travel with the existing review. Counts of suggestions or
rewrites provide no additional evidence of reader understanding.

### Rule: Classify each material occurrence

Treat an occurrence as ordinary language, exact technical or governed
vocabulary, quoted or source-owned language, useful compact language, or
replaceable shorthand. The same word can receive several classifications.

### Rule: Replacement follows function

For replaceable shorthand, name the concrete contract object, evidence action,
authority relation, source boundary, or consequence it was carrying. Use the
smallest ordinary-language revision that preserves technical depth.

### Rule: Exact program language can stay

Retain terms such as LIMS, ELN, canonical digest, source revision, evidence
mode, assurance stage, selected future, release subject, and acceptance when
they are technically exact. Define a term near first use when the intended
reader otherwise lacks the relationship it names.

### Rule: Fidelity-bearing text keeps its owner

Preserve code, JSON keys, schema vocabulary, release identities, citations,
and accessibility meaning. Route a disputed source-owned term to its authority
for resolution.

### Rule: Verification returns to the reader

Read every changed sentence in its heading, paragraph, table, metadata, or
accessibility context. Run the owning structural, contract, and deterministic
Pages checks after the prose review.

## Operating sequence

1. Bind the corpus, readers, exclusions, and candidate word families.
2. Gather occurrences with surrounding text.
3. Classify each decision-changing occurrence.
4. Retain, define, revise, or defer using the smallest useful action.
5. Re-read nearby headings, links, metadata, and accessibility text.
6. Run the receiving surface's existing checks.
7. Return the scope, changes, meaningful retentions, evidence, and any receiver.

## Completion

The scan completes when a reader can retrieve the program objects, actions,
authority relations, and consequences using the context supplied by the
receiving surface; retained specialist language has an exact or useful role;
and the receiving surface's behavior remains verified.

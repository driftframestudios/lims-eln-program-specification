# ADR-0004 — Desired-State Language Across Prose and Code

**Status:** accepted  
**Date:** 2026-07-28

## Decision

Instructions, comments, identifiers, tests, and review templates name the
desired state and its verification method. Common lexicalized antonyms serve
where a constitutive statement remains awkward. Hard safety and privacy
boundaries preserve precise exclusions and pair them with the replacement
state.

The executable projection binds to `language-policy-v1.0.0`. It parses
Markdown scopes, JSON values and control groups, conservative YAML values, and
Python comments, docstrings, and identifiers before applying stable rules.
Exact, expiring exemptions bind rule, path, and finding fingerprint; expired
and unused entries become integrity findings.

The projection is a candidate-eligibility control. The governance repository
owns the policy release, while accountable roles retain authority over domain
meaning and acceptance. The
[language-policy operating contract](../docs/LANGUAGE_POLICY.md) records scope,
limits, output formats, and exit semantics.

## Source

[Semantic Attractor Design — Negation-Aware Instructions](https://app.notion.com/p/abcb29b960a842ce8f1a409408a29257)

## Examples

- `contextRemainsIntact` names the invariant.
- `reconcileBeforeResubmission` names the recovery sequence.
- `credentials stay in the protected runtime; fixtures use synthetic
  identities` pairs a security boundary with its replacement behavior.

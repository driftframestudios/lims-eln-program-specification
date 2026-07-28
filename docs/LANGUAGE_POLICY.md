# Language Assurance Policy Projection

This repository projects `language-policy-v1.0.0`, whose governance authority
remains with the released site-reading governance surface. The projection is a
deterministic candidate-eligibility control. It evaluates authored language;
it grants no Scientific, Quality, Regulatory, Security, Privacy, Operations,
or production authority.

## Assurance model

The checker parses semantic units before applying rules:

| Format | Evaluated units | Context retained as evidence |
|---|---|---|
| Markdown | headings, paragraphs, continued list text | block quotations, example sections, fenced examples |
| JSON | string values and sibling control-field groups | object keys |
| YAML | conservative scalar values, including literal and folded blocks | keys and comments |
| Python | comments, docstrings, and identifier tokens | executable operators and ordinary string literals |

Inline code, attributed quotations, Markdown quotation blocks, and explicitly
headed example sections remain visible in source while staying outside the
authored-instruction decision path. Python comments and docstrings remain
inside that path. JSON control objects join instruction and target fields into
one unit, which permits a boundary and its replacement behavior to occupy
separate sibling values.

## Released rules

| Rule | Meaning | Severity |
|---|---|---|
| `LANG001_UNPAIRED_PROHIBITION` | A directive exclusion lacks a paired target state or replacement behavior. | error |
| `LANG002_NEGATIVE_IDENTIFIER` | An authored identifier names an exclusion rather than the available capability or target state. | error |
| `LANG003_UNVERIFIABLE_TARGET` | A paired replacement remains qualitative rather than concrete or observable. | error |
| `LANG900_PARSE_FAILURE` | A selected authored surface could not enter the parser boundary. | error |
| `LANG901_EXEMPTION_INVALID` | An exemption is malformed, expired, unused, duplicated, or broader than one occurrence. | error |

`LANG001`–`LANG003` produce exit code 1. `LANG900` and `LANG901` identify
checker, input, or exemption-integrity failures and produce exit code 2. A
clean evaluation produces exit code 0.

The checker recognizes paragraph-level and multi-sentence pairing. An
unlabeled following sentence qualifies only when it shares subject matter with
the exclusion. Explicit replacement labels can carry the relationship across
JSON sibling values. Concrete system locations, schemas, receipts, assertions,
measurements, and other observable outcomes qualify a target. Vague assurances
remain visible as `LANG003`.

## Stable findings

Every finding contains a rule ID, severity, surface kind, repository-relative
path, source range, actionable message, and SHA-256 fingerprint. The
fingerprint binds rule, path, surface kind, and normalized evidence; the policy
release stays outside the fingerprint material. It survives line movement
while content and location remain stable. Text, JSON, and SARIF 2.1.0
renderers expose the same identity.

## Narrow exemptions

[`language-policy/exemptions.json`](../language-policy/exemptions.json) is the
only exemption registry. Each entry binds one rule, one exact relative POSIX
path, and one finding fingerprint. It also carries a stable `LANG-EX-…`
identifier, substantive rationale, accountable owner role, UTC review and
expiry timestamps, and a review window of at most 180 days.

Glob paths and parent traversal stay outside the contract. Expired, unused,
duplicate, or multi-occurrence matches produce `LANG901`; they do not suppress
the underlying finding. Source drift therefore becomes an explicit review
event.

## Qualification corpus

[`language-policy/corpus-v1.json`](../language-policy/corpus-v1.json) freezes
the behavior of the projection in 89 representative cases. It covers
typographic and modal directive forms, descriptive and negative-test prose,
multiline pairing, quotations and examples, JSON control grouping and parser
integrity, YAML scalars/keys/comments, Python comments/docstrings/identifiers,
and current, expired, unused, drifted, and overbroad exemptions. Every expected
finding binds its exact source range and fingerprint.

The corpus is a behavioral specification rather than a repository allowlist.
Newly discovered language classes enter the corpus before a rule changes,
which keeps policy evolution reviewable.

## Commands

```sh
python3 scripts/check_language.py
python3 scripts/check_language.py --format json
python3 scripts/check_language.py --format sarif
python3 -m unittest tests.test_language_policy -v
```

Explicit paths remain bounded to this repository. A missing path, an
out-of-repository resolution, or an unreadable selected surface produces
`LANG900` without reading or reporting external content. Symbolic links,
non-regular files, invalid UTF-8, and exemption-registry I/O failures follow
the same fail-closed posture. Each failure carries a stable reason code and a
repository-relative path or `<outside-root>` placeholder; text, JSON, and
SARIF output excludes host exception text and remains comparable across
checkout locations.

Vale supplies a complementary author-feedback loop through the pinned local
style configuration. It is advisory: the standard-library checker and golden
corpus remain the deterministic candidate gate.

The governance
[Semantic Shadow Review Contract](https://github.com/driftframestudios/site-reading-governance/blob/main/docs/SEMANTIC_SHADOW_REVIEW.md)
defines the bounded path for any future statistical or model-assisted review.
Its current state is `inactive_design_contract`: this repository configures
zero semantic models, prompts, endpoints, dependencies, workflow jobs, or API
calls. Future evaluation first supplies approved inputs, privacy handling,
immutable coordinates, measured qualification evidence, advisory-only
authority, and accountable promotion.

## Known boundary

This checker recognizes structure and bounded lexical relationships; it does
not claim general natural-language understanding. Ambiguous scientific,
Quality, or Regulatory meaning still receives accountable human review.

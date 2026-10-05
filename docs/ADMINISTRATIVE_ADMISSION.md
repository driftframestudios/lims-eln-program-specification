# Bounded administrative admission

## Receiving contract

Use `lims_eln_contracts.administrative_admission.admit_administrative_contract`
when an application or research runner needs an explicit resource envelope for
one administrative contract document. Supply immutable UTF-8 bytes and an
`AdministrativeAdmissionLimits` profile. A successful result contains the
validated frozen model, complete canonical bytes, and stage-specific usage.

Ordinary v1 models and resource loaders retain their existing contract. This
separate entry point supplies the budget guarantee. The caller owns transport,
input acquisition, profile approval, deadlines, persistence, and publication.
Enforce a transport/read limit while acquiring input; the package receives
already-owned bytes. Retain the prior accepted artifact until the complete
new result is available.

## Select a receiving profile

The API supplies no implicit workload limits. The following profile belongs to
the repository's bounded review exercise: the canonical fixture, calibrated
chains through 1,200 added assertions, and compact graph counterexamples.
The input/output ceilings bound that local review's material; record and edge
limits leave room for the stated fixture ladder. They establish a receiving
policy, rather than a production capacity estimate.

~~~python
from lims_eln_contracts.administrative_admission import (
    AdministrativeAdmissionLimits,
    admit_administrative_contract,
)

limits = AdministrativeAdmissionLimits(
    max_input_bytes=2 * 1024 * 1024,
    max_json_depth=32,
    max_decoded_values=200_000,
    max_records=2_000,
    max_provenance_edges=8_000,
    max_graph_steps=100_000,
    max_output_bytes=2 * 1024 * 1024,
)
# payload is immutable UTF-8 bytes acquired under the caller's read limit.
admitted = admit_administrative_contract(payload, limits=limits)
# Publish admitted.canonical_bytes only through the receiver's existing
# complete-artifact validation and atomic publication route.
~~~

A receiving study selects its own profile using observed payload sizes, record
counts, graph shape, scenario count, output needs, and available resources.
Each setting uses an explicitly supplied integer; booleans and coercible text
remain distinct types. Edge and graph-step budgets can be zero to hold that
work. Other maxima are positive. All profile integers fit a signed 64-bit
range, and JSON nesting selects at most 128 containers, the supported decoder
envelope for this API. Profile changes receive review beside the input and
receiving use they admit.

## Stage and unit map

| Stage | Unit and enforcement point | Meaning of rejection |
| --- | --- | --- |
| Input ownership | Encoded bytes, before UTF-8 decoding | Select a smaller complete batch or a reviewed byte profile; streaming acquisition remains the caller's owner. |
| Lexical depth | Nested JSON containers; root container counts as one, before either JSON parser | Reduce structural nesting or select a supported depth profile. Brackets inside strings remain literal. Flat provenance chains have independent graph depth. |
| Strict JSON | Unique object keys and finite numbers through the existing parser | Repair ambiguous keys or invalid numeric/syntax material in the retained input. |
| Decoded values | Every container, scalar, and object-member name; before model construction | Reduce document breadth or select a reviewed decoded-value profile. |
| Records | Total entries across the ten aggregate record families; before model construction | Partition at a dependency-closed contract boundary or review a larger batch. |
| Provenance edges | Parent-reference occurrences; before model construction | Reduce the admitted graph or review its connectivity budget. |
| Graph work | Conservative `(C + 1) * (V + E) + R`; before model construction | Review total cycle/calibration traversal work, including repeated scenarios. |
| Contract semantics | Existing strict JSON-mode Pydantic models and aggregate invariants | Inspect the retained input using trusted local model diagnostics; preserve the accepted predecessor. |
| Output | Accumulated canonical UTF-8 bytes, checked before every append | Select a fitting output profile before publication; the caller receives a complete result or an exception. |

Here V counts provenance assertions, E their parent references, C calibrated
scenarios, and R their calibration-evidence root references. The graph budget
is deliberately conservative: every calibrated scenario is charged for the
complete graph even when its reachable component is smaller. It measures
structural traversal units, rather than elapsed time or an exact instruction
count. Source sets are collected once per scenario; their size is bounded by
the admitted source records.

`AdministrativeAdmissionError` carries a fixed `code`, plus numeric
`limit` and `observed` values for an exceeded budget. Codes identify
`input_bytes`, `json_depth`, `decoded_values`, `records`,
`provenance_edges`, `graph_steps`, or `output_bytes`. Fixed JSON,
UTF-8, decoder-capacity, contract, and canonical-output codes route other
failures. Messages carry boundary names and counts; raw values, member names,
and full validation payloads stay with the caller's protected input. Local
model diagnostics remain the detailed semantic repair route.

## Cost, purity, and allocation ownership

| Function or stage | Time | Additional space and owner |
| --- | --- | --- |
| Profile validation and `_within` | Fixed field count / O(1) per comparison | O(1), immutable configuration or bounded exception |
| `_json_depth` | O(B) | O(1) beyond the UTF-8 text |
| Strict decode and JSON-mode model construction | Separate input-sized parsing passes plus model/semantic work | Input/document/model allocations bounded by the selected bytes and structural envelope |
| `_decoded_values` | O(N) | O(D) iterator stack, local to the call |
| `_graph_envelope` | O(N) upper bound | O(1) auxiliary counters; input collections remain unchanged |
| `require_acyclic` | O(V + E) | O(V + E), local standard-library graph state |
| `reachable_sources` | O(R + V + E) per calibrated scenario | O(R + V + S) local scheduling/source sets; no per-assertion ancestor closures |
| Policy source membership | O(S + M), beside existing sorting | One local source-ID set; ordered-source/value checks retain their own sorting cost |
| Conflict precedence selection | O(P + M) | One local matched-rule set; declaration order remains authoritative |
| `_canonical_output` | O(O) encoding after model projection | O(O) accumulated bytes plus model projection and one encoder chunk |
| `admit_administrative_contract` | Sum of its stages and existing semantic checks | Owns decoded text/document, model, and complete result; performs no publication |

B is input size, N decoded values, D JSON container depth, S source count,
M matching/input values as named by the row, P precedence length, and O encoded
output size. Provenance path depth no longer consumes recursive Python frames.
Existing policy predicates and cross-record semantic passes keep their
individual costs; this graph analysis establishes neither a linear bound for
the whole validator nor a CPU/RSS ceiling.

The output budget governs accumulated bytes. Model projection and a single
encoder chunk have input-bounded allocations, and the final immutable byte
copy briefly coexists with the mutable accumulator. Process isolation and
hard memory/time controls remain the receiving runner's responsibility; Program
#33 owns the separately gated process-boundary experiment.

Cycle detection reuses
[Python 3.12 graphlib](https://docs.python.org/3.12/library/graphlib.html).
Reference resolution occurs first because the standard-library sorter admits
undeclared predecessors as graph nodes. The aggregate preserves its own
missing-parent and acyclic-domain errors, then collects each scenario's
reachable sources without mutating input records.

## Evidence and compatibility

The focused suite preserves exact schema and canonical-output equality,
strict JSON behavior, duplicate/dangling/cycle and calibration semantics,
deep-chain results, shared-source deduplication, multi-scenario accounting,
exact/one-over limits, safe rejection messages, and retained accepted output.
Deterministic visit counts establish the helper's shared-ancestor behavior.
A separate bounded scale observation records its actual environment, input,
result, elapsed time, and traced Python allocation; it supplies one observation.

[The 0.4.1 migration](migrations/0.4.0-to-contract-package-0.4.1.md) separates
the implementation successor from v1 schemas, accepted consumer pins, Program
release, and hosted publication. [The family reference](EXTERNAL_ADMINISTRATIVE_CONTRACTS.md)
owns domain meaning. [Program #55](https://github.com/driftframestudios/lims-eln-program-specification/issues/55)
owns admission acceptance and the next receiving decision.

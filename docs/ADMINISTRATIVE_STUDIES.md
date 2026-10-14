# Observe a synthetic administrative study

Package 0.5.0 adds a bounded study document for paired synthetic experiments.
It preserves the question, factors, expected behavior and actual outcomes as
separate records. A scientific-output change can therefore be admitted and
inspected even when the study expected that output to remain invariant.

## Read the first example

```python
from lims_eln_contracts import compare_administrative_study
from lims_eln_contracts.resources import load_administrative_study_example

study = load_administrative_study_example()
report = compare_administrative_study(study)
print(report.model_dump_json(indent=2, by_alias=True))
```

The example contains a deliberately changed scientific output and a legitimate
unchanged result. Its expected outcomes are authored separately. The comparison
reports output-text identity, expected-invariant violations and oracle agreement.
Substantive scoring, uncertainty and population interpretation belong to the
receiving study and Comparative Evidence.

## Carry the complete denominator

Every planned pair contains arms `a` and `b`. Missing observations remain pending.
Attempts preserve execution order, actual provider/model/configuration and time.
The final attempt determines a run's status; earlier attempts remain available.
Completed, abstained, failed, cancelled, excluded and pending counts partition
the planned runs. The attempted count overlaps those outcome categories.

A completed run carries both complete output families. Unsuccessful runs may
retain partial output. Controlled-input or execution differences produce an
explicit comparability finding; expected-output differences remain observations.

## Admit data at the owned boundary

`admit_administrative_study` accepts UTF-8 bytes through the existing strict JSON,
depth and decoded-value guards. Its offline profile permits at most 512 planned
runs, eight attempts per run, 32 factors, depth 32 and 100,000 decoded values.
Default input/output byte budgets are 2/4 MiB; explicit budgets are bounded by
32 MiB. These are resource limits for this reference profile, rather than
performance or statistical-sample recommendations.

Models own immutable tuples and strict scalar values. Raw text survives round
trip; canonical digests bind the specification, each run and each output. Safe
admission errors name a boundary while the caller retains source input locally.

Synthetic provenance is an assertion whose truth comes from artifact review,
generator lineage and the receiving allowlist. A marker alone provides a routing
hint. Real-person records remain outside this repository's intake.

## Source and receiving route

[`administrative_study.py`](../src/lims_eln_contracts/administrative_study.py)
owns meaning. The existing schema generator projects structural constraints and
lists semantic invariants for other consumers. Generated schema acceptance and
Python semantic acceptance retain their distinct checks.

[Program #71](https://github.com/driftframestudios/lims-eln-program-specification/issues/71)
owns this addition. Enterprise #37/#36 receive the offline execution path;
Simulation owns independent scenario truth, Comparative owns measurement, and
Governance owns claim and correction mapping. The
[migration guide](migrations/0.4.2-to-contract-package-0.5.0.md) describes adoption.

Publication, release tags and external model execution retain their held state.

# Finite container jobs: evidence and design boundaries

## Receiving decision

The four finite jobs preserve each repository's native behavior while sharing a small prepared-context and publication boundary. Enterprise retains its service-oriented database and secret lifecycle. Program owns `container_job.py` and `container_runtime.py`; each receiving repository binds both copies by digest and owns its entry, fixture selection, and native validator.

The working frame is an operator-owned, quiescent source tree, reviewed wheels, trusted finite producers, and a fresh private output directory. Concurrent hostile filesystem writers, arbitrary uploaded workloads, service credentials, and power-loss durability require their own admission and recovery designs. The current profiles keep those capabilities with their existing owners.

## Evidence-to-design bridge

| Evidence | Classification and transfer boundary | Implementation consequence | Material observation |
| --- | --- | --- | --- |
| [Python 3.12 filesystem APIs](https://docs.python.org/3.12/library/os.html#os.mkdir) and [BuildKit PR 6828](https://github.com/moby/buildkit/pull/6828) | Documented mode/umask behavior; the upstream fix is corroborating implementation evidence, rather than proof about a local builder version. | Set every staged directory to 0755 and copied file to 0644 within an outer 0700 context. Preserve the invoking process's umask. | Prepare under umask 077, inspect nested permissions, then execute as the configured non-root identity. |
| [Python directory traversal](https://docs.python.org/3.12/library/os.html#os.walk) | Documented traversal errors are ignored by default. | Supply an error callback that aborts the inventory. | A failure after one readable file produces no completed receipt and preserves prior runs. |
| [pip secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/) | Hash checking requires the full pinned dependency closure. Package trust and current vulnerability status remain separate decisions. | Acquire wheels outside the build; admit exact bytes; install with `--no-index`, `--require-hashes`, `--only-binary=:all:`, and disabled build network access. | Alter requirements or wheel bytes, require preparation to hold, then exercise the real installation separately. |
| [Compose service controls](https://docs.docker.com/reference/compose-file/services/) | Declarative controls describe intended behavior; the selected runtime establishes enforcement. | Keep read-only root, non-root owner, dropped capabilities, bounded resources, one explicit output mount, disabled networking, and an init process. | Inspect and execute the actual Compose service, including repeat invocation and cancellation. |
| [Docker build secrets](https://docs.docker.com/build/building/secrets/) and [container-image secret research](https://arxiv.org/abs/2307.03958) | Official secret-delivery guidance and historical empirical evidence of image leakage. The study describes its sampled images, not these repositories or current prevalence. | Copy a positive source allowlist and declared wheels. Host acquisition owns credentials. Public source, container-image publication, and runtime secret delivery retain separate gates. | A fresh canary demonstrates the scanner and stays outside the admitted context; inspect the exact proposed source and resulting image separately. |
| Existing Simulation and Comparison artifact validators | Local behavior authority for the generated artifact families. | Keep `payload/` as the complete native family; store the job receipt alongside it. Run native validation after bounded inventory and before publication. | Native exact-membership validation, strict input counterexamples, unchanged artifact digests across repeated runs. |

## Practitioner Probe application

The connected public Registry's **Working Frame Declaration**, **Data Shape & Structure Selection Ladder**, **Choosing a Decision Shape**, and **Evidence-Bearing Test Design** supplied the review route. Back-End Vanilla probes BV2, BV3, and BV4 supplied the serialization, failure-surface, and acquire/release questions.

[Evidence-Bearing Test Design](https://kindlight.systems/practitioner-probes/evidence-bearing-test-design-behavior-boundary-observable-proof) routes each assertion through behavior, plausible fault, observable distinction, and consequence. [Choosing a Decision Shape](https://kindlight.systems/practitioner-probes/choosing-a-decision-shape-branches-rules-state-transitions) supports simple guards and an explicit producer/validator boundary here. A factory hierarchy or plugin registry would add structure without a current extension requirement.

The transferable rules are concrete: native parsers own domain admission; every emitted member receives inspection; the acquiring invocation owns cleanup; successful publication follows all validators; safe summaries carry bounded status rather than input bodies or private paths. Runtime-specific examples remain examples. An earlier array member's validity leaves later members unspecified, so complete validation stays in the native owner.

## Cost and mutation ownership

For admitted bytes B, paths P, and maximum path length L, preparation costs O(B + P L + P log P), with O(P L + largest file) auxiliary memory. Path syntax, case-folded identity, and directory permission work are bounded by the profile's size and path-length limits. Regexes use anchored character classes rather than nested ambiguous repetition.

Runtime inventory costs O(B + P L); receipt ordering adds O(P log P). The largest file and path records bound memory within the declared output limits. Native artifact validation adds its own bounded pass over the selected family. The preparation helper mutates only a newly acquired destination. The runtime mutates only its newly acquired pending directory and publishes it by rename. Prior output remains an independent artifact.

Checks for source paths and final-file descriptors support the quiescent operator-owned frame. A hostile concurrent filesystem requirement would call for descriptor-relative traversal and a separately tested race model. Successful rename establishes a complete visible invocation at return; storage durability across power loss calls for an explicit synchronization contract.

## Acceptance and re-entry

Run `python -m unittest discover -s tests -p 'test_container_*.py' -v` through the repository's isolated Python route. The focused fixtures establish the exercised boundaries. Real wheel installation, native artifact parity, actual Compose confinement, platform identity, current image findings, and independent review complete the separate configured acceptance.

Receiving PRs retain the current result and remaining gate. Main promotion, source-projection tagging, and public publication follow their named human review decisions. A source or dependency change renews the affected receipt and configured observation before the next release decision.

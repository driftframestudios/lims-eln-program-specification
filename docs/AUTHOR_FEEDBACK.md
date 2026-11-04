# Vale author feedback

Vale 3.15.2 gives an author a location to reread in Markdown prose or a Python
comment. The repository's Python language checker evaluates the released rules
for candidate eligibility. Authors and accountable reviewers decide what a
passage means. A quiet Vale run establishes only that its enabled patterns
returned no alert in the text Vale examined.

## Try one comparison passage

A reviewer can use a field count to check coverage. Deciding whether two
scientific methods agree requires evidence about the analyte, value and unit.
The first sentence claims equivalence from a count. The next paragraph tells
the reader that three fields differ and identifies what to compare. The
example expects a suggestion on line 1.

```pycon
>>> from pathlib import Path
>>> from qualify import qualify
>>> passage = ("We reviewed all 17 fields, establishing measurement equivalence.\n\n"
...            "Three fields differ. Compare their analyte, value and unit.")
>>> qualify(Path(".vale/program.ini"), {
...     "comparison.md": (passage, [(1, "ProgramReview.CountToConclusion", "suggestion")])
... })

```

With Vale 3.15.2 on the path, run the example from the repository root.

```sh
PYTHONPATH=.vale python3 -m doctest docs/AUTHOR_FEEDBACK.md
```

A successful run confirms the expected suggestion and its location. The
scientific reviewer decides what those three differences mean.

## Shared profile

For a changed document or Python file, select its path. To run the shared
profile on the repository's supported files, use the second command.

```sh
vale --config=.vale.ini --no-global docs/README.md
vale --config=.vale.ini --no-global .
```

The default includes both warnings and suggestions. The Markdown parser skips
blockquotes and code, including fenced and inline examples. Python comment
coverage is specific to the rule and Vale parser. The qualification command
below exercises the supported scopes directly.

| Rule | Severity | Author's question |
| --- | --- | --- |
| `SiteReading.TargetState` | warning | Does the surrounding instruction identify the state to preserve and a concrete action? |
| `SiteReading.EvidenceGrounding` | suggestion | What observation supports the claim? |
| `SiteReading.AmbiguousReferent` | suggestion | Which subject would the reader identify here? |
| `SiteReading.SentenceComplexity` | suggestion | Would the decision be easier to follow if the sentence were split? |

The shared rules and their executable qualification come from Site Reading
Governance. Review a shared change there and exercise the accepted files here.

## Optional Program review

Run this profile locally on one authored Markdown file already receiving
review. It examines sentences, list items and table cells. Each of the two
suggestions can be selected independently. The ordinary shared profile
remains available through the commands above.

```sh
vale --config=.vale/program.ini --no-global docs/README.md
```

- **CountToConclusion** highlights selected sentences that connect a numbered
  inventory to completion, readiness, equivalence, validation, or acceptance.
  Ask what the inventory established and which observation supports the decision. An
  exhaustive count can answer a coverage question. The pattern looks for
  digits and a causal link within one sentence. A conclusion in another
  sentence or a count spelled out in words returns to a reader.
- **ContextualWording** highlights “load-bearing” and selected phrases around
  seams, rooms, moves, arrivals, surfaces, and instruments. Read the actual
  phrase in its paragraph. A laboratory instrument measures a sample. A
  literal review room can house laboratory equipment. Keep either word when
  its meaning is clear. Define a useful term at first use, name the actual
  actor or object when it is unclear, or bring one consequential ambiguity
  to its owner. Source-owned names, quotations, and scientific terms retain
  their meaning.

Consider a comparison of 17 observations. Ten agree, four have explained
variation, and three differ on analyte, value, and unit. That count tells a
scientific reviewer which measurements need inspection. If a summary instead
says that inventorying all 17 completed the comparison, ask which stage
“complete” describes and what evidence establishes that stage. A comparison
report can be complete while the scientific dispositions remain open. The
author can name the completed report and the scientist who will evaluate
equivalence.

Try the passage as a paragraph. Record what the reader understands before
showing the alerts, then read the sentence that could travel on its own. A
recipient who sees only “All three differences were resolved” needs the
dispositions, evidence and reviewer. Vale can return silence on that sentence.
Ask what changed in the reader’s decision or explanation after seeing a cue.
A supported retention or an alert that added little is a valid outcome.

A generic cue such as “review room” may be helpful in one passage and literal
in another. When an individual suggestion repeatedly costs attention without
changing an editorial decision, the reviewing maintainer can narrow its
phrases or disable that rule in `.vale/program.ini` and adjust its owned
qualification cases. Review ends when the passage supports the reader's task
or one material question has an owner and a reason to return. Keep a useful
retention or deferral with the existing review when it affects the decision.

## Reproduce or diagnose the feedback

With Vale 3.15.2 on the path, exercise both profiles from the repository root.

```sh
python3 .vale/qualify.py
python3 .vale/qualify_program.py
```

The checks run the pinned binary on synthetic passages and compare emitted
rule IDs, locations, and severities against independent expectations. A
missing binary, wrong version, or unmatched expectation calls for a check of
the tool or rule before interpreting its output. The Program check includes
an inventory with a scientific purpose, a literal term that merits retention,
an isolated claim that needs human review, code, and quotations.

The shared report checker also has a standard-library example. It exercises
the recorded finding types and multiplicities without starting Vale.

```sh
python3 -m doctest .vale/qualify.py
```

When changing qualification code or a Program rule switch, run the focused
pytest cases in a temporary Python 3.12 environment. The commands below use
`uv` to install the pinned test wheels with hash verification. Keep Vale 3.15.2 on the path for the two
Program cases, which each use their own temporary profile. Both start with
one passage that triggers both cues, then retire one rule and check which
suggestion the author receives.

```sh
vale_test_dir="$(mktemp -d)"
uv venv --python 3.12 --managed-python "$vale_test_dir/venv"
uv pip install --python "$vale_test_dir/venv/bin/python" --require-hashes \
  --only-binary=:all: -r .vale/requirements-pytest.txt
PYTHONPATH=.vale "$vale_test_dir/venv/bin/python" -m pytest -q -p no:cacheprovider --doctest-modules \
  --doctest-glob='AUTHOR_FEEDBACK.md' .vale/qualify.py .vale/test_qualify.py \
  .vale/test_program_review.py docs/AUTHOR_FEEDBACK.md
```

Each profile batches its passages into one Vale scan. Qualification reports a
missing or unexpected executable, an engine failure, or a malformed
report separately from an unexpected finding. The Python-only tests exercise
those failures with synthetic inputs. The real profiles establish which
suggestions the pinned engine emits.

The hosted `author-feedback` job runs only through the manual validation
workflow with `ENABLE_GITHUB_ACTIONS=true` and the dispatcher's confirmation.
CI requests `--minAlertLevel=warning` for the shared profile. The job downloads
the Vale 3.15.2 Linux archive and verifies SHA-256
`fc72e64454d6bd7af91905d4faebbf411bae3eec17bb572f4101311212bc0d9e`
before extraction. It exercises the shared synthetic qualification before
scanning the repository. Its advisory result stays outside the stable aggregate.
Automatic pull-request validation runs the Python Program proof. The two
Program-specific prompts run locally on the author's selected file. The repository
maintainer reviews changes to the styles, engine pin, and workflows.

[Manual workflow](../.github/workflows/validate.yml) ·
[Automatic pull-request proof](../.github/workflows/pull-request.yml) ·
[Program jargon-review skill](../.agents/skills/contextual-jargon-scan/SKILL.md) ·
[Deterministic language policy](LANGUAGE_POLICY.md)

# Vale author feedback

Vale provides structure-aware review for active Markdown and Python comments. The
repository pins Vale `3.15.2`, verifies its release archive checksum in CI, and keeps
the active styles under `.vale/styles`.

The active warning asks authors to pair a hard boundary with the safe replacement
behavior. Suggestions identify ambiguous referents, weak evidence language, and
comma-dense sentences. CI applies Vale only to active prose paths; the historical
quarantine remains available as source material under its declared inactive state.

Run the same warning-level review locally:

```sh
vale --config=.vale.ini --no-global --minAlertLevel=warning \
  README.md CONTRIBUTING.md SECURITY.md charter docs
```

JSON Schema and the unit tests remain the executable contract for structured
specifications. Vale assists authors with prose and comments.

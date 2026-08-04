# Contributing

Contributions strengthen an active requirement, invariant, data contract, scenario,
or Practitioner Probe.

Each change:

1. states the vendor-evaluation or implementation question it answers;
2. identifies the material scientific, operational, technical, or evaluative effect;
3. updates API, event, database, migration, export, and vendor mappings when a data
   primitive changes;
4. uses synthetic or approved de-identified examples;
5. names the official product documentation or configured-environment observation
   supporting a vendor claim;
6. adds or updates a specification-by-example scenario for behavior changes;
7. passes JSON Schema and unit-test validation.

Run the active validation locally:

```sh
python3 -m pip install --editable ".[validation]"
python3 -m unittest discover -s tests -v
vale --config=.vale.ini --no-global --minAlertLevel=warning \
  README.md CONTRIBUTING.md SECURITY.md charter docs
```

GitHub Rulesets supply branch and review policy. GitHub secret scanning and push
protection supply repository credential checks.

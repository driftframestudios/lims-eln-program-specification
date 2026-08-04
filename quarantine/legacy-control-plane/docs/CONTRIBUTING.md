# Contributing

Start from `develop` using the branch forms in [BRANCHING.md](BRANCHING.md).

Every contribution:

1. names the desired state and its verification method;
2. links stable `SPEC-`, `RULE-`, `SCN-`, `DEC-`, and `RCP-` identifiers;
3. states evidence mode and assurance-stage effects;
4. preserves earlier forecasts and supersession lineage;
5. uses synthetic or approved deidentified fixtures;
6. records scientific and executive material effects;
7. identifies bounded-caller effect class and approval posture for callable
   operations;
8. preserves distinct simulated and observed receipt states;
9. updates the Coordination Horizon when active dependencies or re-entry
   instructions materially change;
10. passes program, language, pinned-coordinate, secret-shape, and unit-test
    validation.

For an ordinary candidate:

```sh
python3 scripts/validate_program.py
python3 scripts/validate_pinned_sources.py --allow-pending
python3 scripts/check_language.py
python3 -m unittest tests.test_language_policy -v
python3 scripts/scan_secret_shapes.py
python3 -m unittest discover -s tests -v
```

Vale `3.15.2` can provide advisory author feedback with
`vale --config=.vale.ini .`. The deterministic commands above remain the
candidate-eligibility controls.

Release settlement supplies each external `ROLE=PATH` checkout to
`scripts/validate_pinned_sources.py`. The default command requires pinned
coordinates; `--allow-pending` is an explicit candidate-only posture.

Automated maintenance follows the exact branch, bot-identity, and target
contract in `BRANCHING.md` and retains the same validation and review path.

Code comments describe the invariant that holds. A hard safety or privacy
boundary states both the boundary and the replacement behavior.
The exact scope, finding contract, exemption lifecycle, and exit semantics live
in [docs/LANGUAGE_POLICY.md](docs/LANGUAGE_POLICY.md).

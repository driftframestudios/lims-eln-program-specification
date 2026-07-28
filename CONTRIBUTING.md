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
10. passes the local validator and unit tests.

Automated maintenance follows the exact branch, bot-identity, and target
contract in `BRANCHING.md` and retains the same validation and review path.

Code comments describe the invariant that holds. A hard safety or privacy
boundary states both the boundary and the replacement behavior.

# Branching

The repository uses `main` for released specifications and `develop` for the next
integrated version. Feature, release, and hotfix branches follow the team’s
GitFlow-like convention.

GitHub Rulesets enforce permitted branch targets, required reviews, required status
checks, signed-commit policy when enabled, and automation bypasses. Dependabot and
Renovate use their native bot identities and repository-configured ruleset paths.

GitHub supplies the branch-policy implementation. Ruleset configuration is reviewed
and exported through GitHub’s supported administration interfaces when an audit copy
is required.

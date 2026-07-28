# ADR-0003 — GitFlow-Like Delivery

**Status:** accepted  
**Date:** 2026-07-28

## Decision

Each repository maintains `main` for releases and `develop` for integration.
Feature, release, hotfix, forecast, and evidence branches follow the contract in
`BRANCHING.md`.

## Expected effects

- release state and active integration remain easy to distinguish;
- forecast releases freeze before corresponding observations;
- hotfixes preserve forward integration;
- coordinated constellation releases bind exact repository commits.

## Reconsideration trigger

Sustained deployment frequency or repository scale may favor a simpler
trunk-based pattern. A successor ADR will preserve the historical release
coordinates if that transition becomes beneficial.


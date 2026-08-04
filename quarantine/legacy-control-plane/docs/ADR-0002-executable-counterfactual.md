# ADR-0002 — Executable Counterfactual Reference

**Status:** accepted for simulation  
**Date:** 2026-07-28

## Decision

The simulated final state implements a complete, independently runnable
counterfactual. It shares released contracts and fixtures with the actual
implementation while its runtime source remains independent.

## Expected effects

- Assumptions become executable and falsifiable before actual results arrive.
- Actual implementation can corroborate, improve, or correct the reference.
- Forecast releases support longitudinal calibration.

## Evidence boundary

Simulation receipts use `evidence_mode: simulated`. A selected future reality
can fully close configured-environment, representative-rehearsal, production,
and accountable-acceptance stages inside that evidence mode. Synthetic
environments, measures, evidence locators, and role-bound decisions remain
explicit.

Every simulated closure preserves `authority: advisory_only` and a distinct
future observed successor. The observed successor can advance later through
environment-bound evidence and accountable human decisions while the simulated
closure remains a complete executable comparison baseline.

## Falsifiers

- simulation behavior primarily mirrors copied actual code;
- reference defects dominate material comparison findings;
- scenario maintenance crowds out actual receipt closure.
- evidence consumers collapse simulated and observed closure into one state.

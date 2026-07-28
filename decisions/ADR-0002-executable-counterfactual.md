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

Simulation receipts use `evidence_mode: simulated`. Configured-environment,
representative-rehearsal, production, and accountable-acceptance stages advance
through observed evidence.

## Falsifiers

- simulation behavior primarily mirrors copied actual code;
- reference defects dominate material comparison findings;
- scenario maintenance crowds out actual receipt closure.


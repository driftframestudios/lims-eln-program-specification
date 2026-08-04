# ADR-0006 — Complete Simulated Closure with an Independent Observed Successor

**Status:** accepted for specification  
**Date:** 2026-07-28

## Context

The hybrid team benefits from seeing the complete consequence of its plan
before corresponding operational history exists. A partial mock preserves less
comparative value than a coherent future reality with metrics, exceptions,
evidence artifacts, and decisions.

## Decision

The simulated-final-state repository may close all four substantive receipt
classes inside `evidence_mode: simulated`:

1. configured vendor environments;
2. representative migration and restore;
3. production security and observability;
4. Scientific, Quality, and Regulatory acceptance.

The simulation selects one declared future reality, executes the full chain of
action, and emits deterministic evidence artifacts. Synthetic role actors
record complete decision shapes while `authority: advisory_only` remains
machine-readable.

Each receipt also retains an independent `evidence_mode: observed` successor
whose state begins open. Simulation closure and observed closure are parallel
evidence statements rather than a single maturity flag.

## Expected effects

- collaborators can compare planned, simulated, implemented, and observed
  results over time;
- the complete evidence and acceptance shape is testable before operational
  access is available;
- future observed evidence can confirm, improve, or correct the simulated
  baseline;
- accountable human authority remains explicit.

## Falsifiers

- a simulated receipt omits assumptions, artifact locators, or limitations;
- a synthetic decision appears as legal, regulatory, or production
  authorization;
- one status field collapses simulated and observed state;
- later observed divergence rewrites the immutable simulation rather than
  creating adjudicated successor evidence.

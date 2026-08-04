# ADR-0005 — Service-Owned Operations for Bounded Callers

**Status:** accepted for specification  
**Date:** 2026-07-28

## Context

Humans, services, workflows, and AI systems can all submit plausible requests
at different speeds and scales. A fluent or authenticated caller still needs a
service boundary that determines the operation, identity, authority, scope,
budget, effect, evidence, and recovery.

## Decision

The program publishes versioned service-owned operations. Each operation
declares:

- strict input and output contracts;
- caller classes and identity source;
- read, narrow idempotent write, or approval-gated broad-write effect class;
- tenant, field, resource, record-count, retry, time, and depth ceilings;
- idempotency and ambiguous-result reconciliation;
- approval binding and expiry where applicable;
- attributable audit and recovery.

Retrieved text, tool output, files, and model output remain input data. The
service derives authority from authenticated caller context and released
policy.

AI capability begins with released read and narrow-write operations. A broad
migration cutover is callable by a human or released workflow after a
digest-bound human approval. Scientific, Quality, Regulatory, Security,
Operations, and business decisions remain with accountable humans.

## Expected effects

- Every caller receives the same enforceable boundary.
- AI and workflow speed remain inside declared effect and resource ceilings.
- Retry, denial, approval, and recovery evidence share one grammar.
- Optional MCP or agent interfaces can project released operations without
  becoming an authority source.

## Falsifiers

- an implementation accepts an unregistered free-form command;
- caller-provided identity or tenant scope overrides authenticated context;
- a consequential effect exceeds its approved digest or ceiling;
- a model, workflow, or tool output records domain acceptance.

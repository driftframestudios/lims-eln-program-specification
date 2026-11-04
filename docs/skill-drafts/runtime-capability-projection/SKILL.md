---
name: runtime-capability-projection
description: Projects composed runtime capabilities into bounded API and visitor-facing records. Applies when an interface describes adapters, package support, available operations, or persistence whose actual owners differ from readiness and authorization.
---

# Runtime capability projection

## Contract

- **What:** A source-owned projection of the runtime's declared composition into a small machine record and a matching visitor explanation.
- **When:** Runtime modes or optional dependencies make a fixed interface label misleading, or another component needs a stable capability discovery route.
- **Boundaries:** The composition root owns the adapter. Dependency checks own readiness. Per-operation policy owns authorization. Configured journeys own observed success. Deployment owners retain credentials, resource coordinates, lifecycle, and recovery authority.
- **Result:** A bounded contract, a pure projector, matching visible wording, and focused observations that establish the claims each field makes.

This is a draft skill. Its first receiving exercise is the workbench capability
slice described in the [execution map](../../WORKBENCH_EXECUTION_MAP.md).

## Fit and attention

- **Useful when:** one interface serves process-local and persistent adapters, optional packages change available outputs, or planned tools need a truthful discovery surface.
- **Poor fit when:** the actual question is whether a caller can act, whether a database is reachable, or whether a completed run is valid. Use the respective policy, readiness, or execution owner.
- **Smallest useful dose:** name the composition facts that change a visitor's next move, then project those fields and their meaning.
- **May under-attend:** deployment topology, resource retention, package provenance, and service health. Give each an explicit receiving route when the task needs it.
- **Interactions:** schema authoring owns the record; cost and ownership analysis bounds computation and mutation; stateful behavior contracts test visible and machine agreement; supportive writing keeps the action and evidence scope clear.

## Inputs, defaults, and output

Inputs are the trusted adapter declaration, an explicit package-compatibility
observation, and the server-owned operation declarations. Accepted adapter names
form a finite set. A missing or unfamiliar declaration ends composition with a
specific configuration error and a supported-choice message.

The output contains allowlisted primitives and newly owned collections. Each
receiver can serialize or inspect it independently. Credentials, connection
strings, filesystem paths, and request context retain their existing owners.

## Rules

### Rule: Each claim follows its evidence owner

Describe a composed PostgreSQL adapter as database-backed state. Determine
disposable or retained lifetime from the launcher that owns resource creation
and cleanup. Describe package-version compatibility as version compatibility;
use installed-resource checks for provenance and execution checks for behavior.

### Rule: Declared shape precedes presentation

Give the projection a versioned, closed schema and meaningful field names.
Document whether each value is declared, observed, or derived. A new operation
or authority scope follows an explicit contract revision. Treat discovery as
navigation input while each operation evaluates its own authority context.

### Rule: Project explicitly and preserve ownership

Select declared fields rather than copying configuration objects wholesale.
Use immutable source declarations and fresh output containers. An output edit
must leave the next projection and source declaration intact. Keep domain
transformation pure; the composition root supplies I/O observations.

### Rule: Bound work to the declared surface

A fixed operation catalog permits constant-size projection. An extensible
catalog needs explicit entry and string limits, an O(n) construction bound,
and a documented lookup strategy. Keep health checks and database traversal
outside the projection path. A capability request should have a predictable
cost independent of study size or stored records.

### Rule: One projection serves both readers

Use the same projected record for machine output and initial server-rendered
wording. Preserve ordinary HTML readability with JavaScript disabled. Dynamic
enhancements may refresh values while retaining the record's scope and current
selection. Explain where readiness, review, and recovery can be observed.

## Operating sequence

1. **Map:** Name each visible claim and its source owner.
2. **Declare:** Choose the smallest closed schema and version policy.
3. **Project:** Admit known inputs and construct detached, allowlisted outputs.
4. **Connect:** Supply the record to the API and authored template from the same composition boundary.
5. **Observe:** With execution authority, use parameterized adapter/package fixtures, route correspondence, output-mutation counterexamples, and one affected visitor check.
6. **Return:** State the implemented claims, the evidence actually observed, and the next owner for persistence or authorization work.

## Consequential scenarios

### Scenario: A database-backed application uses a process-local label

- **Given:** the server has composed a database adapter and the template carries fixed process-local wording.
- **When:** the template receives the source-owned capability record.
- **Then:** the visible state describes the database adapter, and the readiness link remains a separate observation.

### Scenario: Package compatibility changes between deployments

- **Given:** a prepared deployment has a declared package coordinate and another deployment uses the lightweight profile.
- **When:** each application projects its local version observation.
- **Then:** each record states its own compatibility result; resource provenance and successful execution continue to require their named checks.

### Scenario: A receiver edits its copy

- **Given:** a consumer changes a nested operation path in one projected record.
- **When:** the next record is constructed.
- **Then:** its path still comes from the immutable declaration. The mutation fixture exercises alias isolation rather than equality alone.

## Recovery and re-entry

An unknown adapter returns to the composition owner with the supported choices.
A dependency failure returns through the readiness route. A schema mismatch
returns to the contract/receiver pair with the exact failing field. Preserve the
existing working adapter and caller authority while repairing the owned boundary.

## Completion

The first exercise settles when the contract and visible projection agree under
their focused observations and the implementation names its evidence limits.
Activate or revise the skill after reviewing that exercise. A new adapter,
remote authority mode, or catalog-size change reopens the relevant rule.

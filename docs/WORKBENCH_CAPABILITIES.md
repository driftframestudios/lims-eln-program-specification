# Choose a workbench by its actual capabilities

The workbench composition contract lets a visitor or receiving tool distinguish
process-local state from PostgreSQL-backed state, find the implemented HTTP
operations, and locate the dependency-readiness observation. Enterprise owns
the running application; Program owns this portable response shape.

## First useful result

Use Enterprise's documented local launcher, then request
`GET /api/workbench/capabilities`. The response follows
[`workbench-capabilities.v1.schema.json`](../schemas/workbench-capabilities.v1.schema.json).
The [process-local example](../examples/workbench-capabilities/process-local.json)
and [PostgreSQL example](../examples/workbench-capabilities/postgresql.json)
are authored contract examples. A live response identifies the composition
selected for that process; `/health/ready` observes its dependencies separately.

| Field | What the value establishes | Further evidence owner |
| --- | --- | --- |
| `runtime.state_adapter` | The composed adapter is `process_local` or `postgresql`. | Enterprise's composition root and adapter tests. |
| `runtime.state_lifetime` | State belongs to the process or the configured database. | The launcher owns database retention, backup, and deletion decisions. |
| `runtime.access_scope` | This version describes a local reference application. | Remote use needs the receiving deployment's authenticated authority boundary. |
| `shared_contracts` | Expected package and contract versions, and the local version-compatibility observation. | Installed-resource checks establish package provenance and behavior. |
| `operations` | The five HTTP operations and their explicit tenant-context inputs. | Each operation enforces its own admission, authorization, and transaction rules. |
| `administrative_interface` | Administrative study execution enters through the Python library. | The administrative guide owns that offline journey; an HTTP interface receives a later contract. |
| `readiness_path` | A route to the current dependency observation. | A successful study or recovery has its own execution evidence. |

The response carries declared capability fields. Connection coordinates,
credentials, secret-file locations, and tenant records stay with their existing
configuration and authority owners. Both capability and readiness responses use
`Cache-Control: no-store` so a receiver obtains a fresh observation on request.

## Ownership and versioning

The schema is a standalone Program contract, separate from the packaged
administrative schema inventory. The Python package keeps its existing version
and resource list. A receiver vendors the schema with its Program source commit
and file digest, then checks actual responses against that exact contract.

The operation map is closed in version 1.0.0. A new operation, deployment scope,
or field receives an explicit successor contract and receiver update. A package
version update can remain compatible with this shape when its version strings
retain the declared release form. Capability discovery supports navigation;
operation authorization remains server-owned for every request.

## Three database profiles to implement next

| Profile | Useful result | Ownership that must be explicit |
| --- | --- | --- |
| Disposable PostgreSQL | A complete temporary journey against real PostgreSQL and Flyway migrations. | The launcher owns a fresh database and removes only that owned resource. |
| Retained PostgreSQL | Resume and recovery across application restarts. | An operator selects the retained project, migrations, backup, and recovery point. |
| External PostgreSQL | A receiving team supplies its database and infrastructure. | The team owns credentials, TLS, least-privilege roles, availability, and recovery. |

`postgresql` alone identifies none of these retention choices. The next launcher
and database-profile contracts will carry the corresponding ownership evidence.
[Program #76](https://github.com/driftframestudios/lims-eln-program-specification/issues/76)
and [Enterprise #60](https://github.com/driftframestudios/lims-eln-enterprise-implementation/issues/60)
retain the remaining migration, persistence, recovery, and configured-execution
acceptance. The [execution and skill map](WORKBENCH_EXECUTION_MAP.md) routes the
subsequent interface work.

Return to [getting started](README.md) or the [schema index](../schemas/README.md).

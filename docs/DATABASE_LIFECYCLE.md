# Choose, launch, inspect, recover, and stop a database profile

Choose who owns one database and what should happen to it when a journey ends.
The [standalone lifecycle schema](../schemas/database-lifecycle-profile.v1.schema.json)
and [source admission](../scripts/database_lifecycle.py) carry that choice,
declared authority, and an ordered operation record. Enterprise owns launch and
execution; Governance owns claim review and accountable acceptance.

## Choose a profile

| Profile and example | Useful result | Creation and destructive authority |
| --- | --- | --- |
| [Disposable](../examples/database-lifecycle/disposable.json) | Create, migrate, and remove a fresh database within one invocation. | The invocation owner creates the named database. Cleanup requires a recorded successful create in that same invocation and explicit destructive authority. |
| [Retained](../examples/database-lifecycle/retained.json) | Inspect an existing database, restore it, and retain it across application stops. | The creation owner and resource owner are named separately. Restore and deletion require an explicit resource-owner decision. |
| [External](../examples/database-lifecycle/external.json) | Inspect a supplied database while its team keeps lifecycle control. | The external owner performs creation, migration, restoration, retention, and deletion. Launcher cleanup is rejected. |

Every example is wholly synthetic. Its source revision of forty `1` characters
is a fixture trust anchor, not an existing Program commit. Engine major `16`
and `ref:synthetic-migrations-v-one` are example requirements, not a supported
engine matrix or an observed migration result.

One record covers one database. A reference names exactly that resource; it
does not authorize deletion of a cluster, shared project, container, volume,
directory, or neighboring database. A runtime manages any additional resources
through its own individually owned registry. Disposable records retain their
whole invocation history starting at `absent`; resuming cleanup carries that
history and the original invocation identity forward.

## Launch through the owning runtime

Select the profile, engine requirement, migration-set reference, credential
receiver class, permitted actions, and recovery reference before launch. Resolve
those semantic references through the authorized runtime configuration. Keep
credentials, account names, connection strings, network coordinates, and absolute
local paths there. Shared records use bounded `ref:` labels, exact schema
identities, revisions, and content digests.

Use the current Enterprise launcher documented by its owner. Lifecycle launcher
integration is a receiving task in
[Enterprise #68](https://github.com/driftframestudios/lims-eln-enterprise-implementation/issues/68)
and [#60](https://github.com/driftframestudios/lims-eln-enterprise-implementation/issues/60).
This Program companion supplies source validation; it starts no database.

Before any effect, the runtime resolves the named decision, authenticates its
actor, checks the live resource identity and current owner, and binds the grant
to this action, resource, and invocation. A syntactically valid decision reference
is a documentary claim, not a credential or executable permission. The runtime
also verifies current engine/migration compatibility and the restore recovery
point. Program admission checks the declared bindings; runtime evidence proves
them. Accountable acceptance travels through Governance's own review record.

## Inspect each evidence layer

| Field owner | What the field establishes | Observation or decision owner |
| --- | --- | --- |
| `schema_ref`, `schema_version`, `source` | Selected contract identity/version and claimed source revision. | Program owns schema meaning; the receiver supplies its independently accepted source and exact schema digest. |
| `profile_ref`, `requested_profile` | Intended disposition, engine major, migration set, credential receiver, permitted actions, cleanup policy, and recovery route. | The selecting operator owns intent; Enterprise resolves safe references and checks runtime compatibility. |
| `invocation` | The invocation identity and its responsible actor. | The launcher owns invocation identity and prevents replay or reassignment. |
| `resource` | Declared creation owner, current owner, creation invocation, initial state, and current state. | The runtime resource registry proves identity and ownership. A planned creator becomes established through a successful creation observation. |
| `composition` | A reference and raw-byte digest for an optional capability v1 response. | Enterprise's composition root supplies the separately admitted response. An observed process-local adapter conflicts with this PostgreSQL profile. |
| `readiness` | A separately named dependency observation, or `not_observed`. | Enterprise's readiness observer establishes dependency availability at its observation time. |
| `operations[].authority` | Owner, actor, decision reference, authority basis, and explicit destructive authorization for this event. | The authenticated decision and runtime owners establish actual authority. |
| `operations[].compatibility` | An event-specific compatibility observation, distinct from the requested engine and migration set. | The migration/engine owner supplies evidence; successful migrate/restore records require a matching `compatible` observation. |
| `operations` | Requested actions or recorded outcomes, ordered state transitions, evidence references, and typed failure codes. | The executor owns observed operation results. `requested` preserves current state and carries no execution evidence. |
| `unresolved_resource_refs` | The named resource still needs resolution. | The resource owner inspects or recovers it; admission preserves the unresolved state. |
| `evidence_class` | Authored example or caller-supplied observation. | Governance verifies provenance and reviews a claim within its evidence class. Admission supplies no accountable acceptance field. |

Composition can be absent while a launcher manages a database. A ready
dependency can coexist with zero executed actions, failed cleanup, or unresolved
resources. Readiness snapshots say nothing about the earlier success of an
operation; a capability response says nothing about retention or restore.
`shared_contracts.version_compatible` keeps capability v1's existing meaning.

## Retain, recover, and stop

| Action | Admitted starting state | Successful result |
| --- | --- | --- |
| `create` | `absent` | `present`, with this invocation as creator |
| `migrate` | `present` | `present`, with matching compatibility evidence |
| `restore` | `present`, `retained`, `unresolved` | `present`, with explicit destructive authority and matching compatibility evidence |
| `retain` | `present` | `retained`; available to retained/external owners |
| `cleanup` | `present`, `retained`, `unresolved` | `removed`, within the disposition's authority boundary |
| `inspect` | Any state | Same known state; an unresolved resource can become `absent` or `present`, or `removed` after a recorded cleanup attempt |
| `stop` | Any state | Same resource state; application stop leaves database disposition intact |

A requested action preserves state. A failed or unresolved action conservatively
leaves resource state `unresolved`, except `stop`, which preserves database state.
Every executed event carries an evidence reference. Failed events carry their
action-specific failure code; unresolved events carry `resource_unresolved`.
Stopping cannot erase a cleanup failure or its unresolved resource.

The [failed cleanup example](../examples/database-lifecycle/cleanup-failed.json)
keeps the successful creation and unsuccessful deletion together. The
[unresolved example](../examples/database-lifecycle/unresolved.json) preserves
an uncertain creation and inspection. Automatic disposal waits for proved
ownership; uncertain creation alone earns no cleanup authority. Retain the
record and use `recovery_ref` with its resource owner. Preserve failed events
when appending a resolved observation or an authorized retry.

Admission reports fixed codes and keeps raw diagnostics with the caller:

| Finding | Next useful move |
| --- | --- |
| `stale_source`, `stale_schema`, `unsupported_version` | Select the exact reviewed source/schema pair with the receiver; version negotiation uses exact `1.0.0` and rejects silent fallback. |
| `composition_unresolved`, `composition_digest`, `composition_contract`, `composition_mismatch` | Supply the referenced capability bytes and resolve adapter/schema differences through their producer. |
| `wrong_owner`, `ownership_profile`, `owner_decision_required`, `destructive_authority_required` | Reconcile the declared resource/creation owner and obtain the action-specific owner decision. |
| `external_cleanup_forbidden`, `external_owner_action_required`, `unowned_cleanup` | Hand the resource to its owner; disposable cleanup follows a successful create by the same invocation. |
| `invalid_transition`, `operation_evidence`, `unresolved_resources` | Preserve history and reconcile the result with the executor's observation. |
| `compatibility_required`, `compatibility_mismatch` | Obtain engine/migration evidence for the intended profile before claiming successful migrate/restore. |
| `action_not_permitted`, `duplicate_operation` | Reconcile the selected action set or event identity with the invocation owner. |
| `input_bytes`, `utf8`, `json_duplicate_key`, `json_number`, `json_syntax`, `json_structure`, `contract_shape`, `source_binding`, `input_unavailable` | Retain the input locally and supply the bounded complete record or receiver-selected source binding. |

## Run the source proof

From the Program repository root, use the local uv profile:

```sh
uv run --isolated --no-project --python 3.12 --managed-python \
  --with-editable . --with-requirements requirements-test.txt \
  -- python -m unittest tests.test_database_lifecycle tests.test_workbench_capabilities -v
```

The tests exercise all three profiles, failure preservation, source/schema/version
admission, explicit ownership, transitions, and independent capability inputs.
They establish the source contract. PostgreSQL execution, Flyway behavior,
durability, backup/restore, authentication, and acceptance remain receiving
observations. `scripts/database_lifecycle.py --help` exposes a local single-record
entry. Supply `--source-ref`, `--source-revision`, and `--schema-digest` from
the receiver's reviewed binding, plus `--capabilities` when composition is observed.
Deriving those trusted arguments from the incoming record would establish only
self-consistency. A successful admission may still report unresolved resources.

## Version and receiving handoff

The closed version `1.0.0` uses Draft 2020-12 with only local `$defs` references.
JSON Schema owns structural admission; `admit_lifecycle_profile` adds exact
source/schema, ownership, composition, compatibility, and transition semantics.
Validation performs no coercion, default insertion, property removal, or network
schema retrieval. New fields, states, actions, and versions require an explicit
successor and receiving update. The byte boundary is 128 KiB per input and the
record carries at most 64 events; its semantic pass is linear in those events.
Parsing, schema validation, and canonical encoding remain their existing owners.

Capability v1 stays byte-identical. Package `0.6.1` and its twelve packaged
schemas retain their existing inventory; no installed consumer needs this
companion yet. The root schema and source script are source-only artifacts.

[Program #79](https://github.com/driftframestudios/lims-eln-program-specification/issues/79)
is prepared as a stack on [PR #78](https://github.com/driftframestudios/lims-eln-program-specification/pull/78).
After the earlier handoffs and parent-arranged independent review, Enterprise
#68/#60 and [Governance #49](https://github.com/driftframestudios/site-reading-governance/issues/49)
receive the reviewed full commit, exact schema bytes/SHA-256, admission source,
examples, and focused evidence. Each receiver authors its own counterexamples
and confirms semantic agreement beside byte equality. The earlier Governance
assurance map retains its separate composition/claim boundaries. This preparation
leaves receiver acceptance, all merges, tags, publication, infrastructure, and
external-model execution with their current authorization owners.

Return to the [capability guide](WORKBENCH_CAPABILITIES.md),
[schema index](../schemas/README.md), or [getting started](README.md).

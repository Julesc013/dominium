Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Schema And Protocol Guidelines

Use these guidelines when adding or changing durable schemas, registries, protocols, manifests, command/result formats, evidence packets, provider descriptors, app/module descriptors, save/replay formats, and package/profile formats.

## Add A Schema

Create or update the schema under the owning contract root and define a schema policy with:

- semantic `schema_id`
- `version`
- `owner`
- `stability`
- compatibility range
- unknown-field behavior
- required-field behavior
- default behavior
- canonical serialization policy
- migration/refusal behavior
- fixtures and proof for stable promotion

Do not use the file path or filename as the ID.

## Add Fields Safely

For provisional schemas, record the behavior in the policy. For stable schemas, adding a required field requires migration or refusal policy. Optional fields still need unknown-field and default behavior so old readers and new readers make deterministic decisions.

Do not add silent defaults. Use `explicit_default_only`, `schema_defined_default`, or `migration_defined_default` and document the source of the value.

## Remove Or Rename Fields

Do not silently remove a stable field. Deprecate first, add migration/refusal behavior, and preserve enough evidence for compatibility review. Renames are remove-plus-add unless a migration says otherwise.

## Add A Protocol

Declare:

- semantic `protocol_id`
- version and owner
- message kinds
- transport if relevant
- unknown-message behavior
- unknown-field behavior
- required-field behavior
- ordering policy
- canonical encoding
- migration/refusal behavior

Protocols must not depend on UI presentation, thread scheduling, hash-table order, pointer order, or private implementation paths.

## Add A Registry

Declare registry ID, version, owner, stability, entry ID policy, lifecycle policy, duplicate policy, unknown-entry policy, and compatibility policy. Do not reuse retired IDs for new meaning.

## Migration

Use explicit migration when data must change. Compatible read is allowed only when it does not mutate source artifacts. If no migration exists, refuse with diagnostic evidence.

Durable user artifacts should record migration provenance and have rollback or backup expectations before mutation.

## Fixtures

Every stable schema/protocol needs positive and negative fixtures. Fixtures under `tests/contract/schema_protocol` are examples for the validator and are not product compatibility promises.

## Examples

Valid schema policy IDs:

- `dominium.artifact.manifest.v1`
- `dominium.command.result.v1`
- `domino.replay.log.v1`

Invalid IDs:

- `contracts/schema/foo.schema.json`
- `foo.schema.json`
- `runtime\\private\\packet`

Valid default policy:

- `schema_defined_default` with a documented value.

Invalid default policy:

- a missing field filled by reader convenience with no schema or migration declaration.

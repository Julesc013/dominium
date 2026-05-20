Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Schema And Protocol Evolution Law

SCHEMA-PROTOCOL-LAW-01 defines the rule set for durable Dominium and Domino data contracts. It applies to schemas, registries, protocols, manifests, command/result formats, diagnostics, evidence packets, provider descriptors, app/module descriptors, pack/profile/save/replay formats, and later compatibility corpora.

The core rule is simple: no silent schema changes, no silent protocol changes, no silent defaults, no unversioned stable contract, and no best-effort migration without policy.

## Authority

The machine-readable law lives in:

- `contracts/schema/schema_evolution.contract.toml`
- `contracts/protocol/protocol_evolution.contract.toml`
- `contracts/registry/registry_evolution.contract.toml`
- `contracts/serialization/canonical_serialization.contract.toml`
- `contracts/migration/migration_policy.contract.toml`

The validator is:

- `tools/validators/contracts/check_schema_protocol_evolution.py`

Existing schemas and registries are inventoried by this task. They are not silently promoted to stable compatibility promises.

## Schema Identity

Every durable schema policy must declare:

- `schema_id`
- `owner`
- `version`
- `stability`
- `compatibility_range`
- `unknown_field_policy`
- `required_field_policy`
- `default_policy`
- `canonical_serialization`
- `migration_policy`
- `refusal_policy`
- fixtures, negative fixtures, and proof before stable promotion

Schema IDs are semantic dotted names. A path, filename, directory, or implementation detail is not schema identity.

## Protocol Identity

Every durable protocol policy must declare:

- `protocol_id`
- `owner`
- `version`
- `stability`
- message kinds
- compatibility range
- unknown-message and unknown-field policy
- required-field policy
- ordering policy
- canonical encoding
- migration and refusal policy

Protocols used for replay, networking, providers, commands, or cross-process surfaces must make ordering and encoding explicit. They must not depend on hash-map iteration, thread completion order, pointer order, or UI behavior.

## Registries

Registries are data contracts. A registry must declare an owner, version, stability, entry ID policy, duplicate policy, unknown-entry policy, entry lifecycle policy, and compatibility policy.

Duplicate stable entry IDs are forbidden. Retired IDs must not be reused as new meanings.

## Unknown Fields

Unknown fields must follow one of the declared policies:

- `reject`
- `ignore_with_diagnostic`
- `preserve_roundtrip`
- `allow_if_extension_declared`

Silent discard is forbidden for governed schemas. Stable schemas must document the chosen behavior.

## Required Fields And Defaults

Required fields may use only declared policy:

- `must_exist`
- `default_if_missing`
- `migrate_if_missing`
- `refuse_if_missing`

Defaults may be:

- `explicit_default_only`
- `no_default`
- `schema_defined_default`
- `migration_defined_default`

Silent defaults are forbidden. If a missing value is filled, the schema or migration policy must say so.

## Canonical Serialization

Canonical serialization is the link between schema law and artifact identity. Stable hashed JSON should use UTF-8, sorted keys, normalized line endings, and no path-dependent output unless a stronger artifact policy explicitly says otherwise.

Binary canonical encoding is deferred and must later declare byte order, alignment behavior, and padding. Raw struct serialization remains forbidden.

## Migration And Refusal

Migration must be explicit. Compatible read must not mutate source artifacts. Incompatible input must refuse deterministically with diagnostic/refusal metadata.

The migration policy records source schema/protocol, target schema/protocol, tool/provenance, and rollback or backup expectations for durable user artifacts.

## Diagnostics And Evidence

Schema/protocol failures should cite stable diagnostics such as:

- `DOM-SCHEMA-MISSING-ID`
- `DOM-SCHEMA-UNKNOWN-FIELD`
- `DOM-SCHEMA-REQUIRED-FIELD-MISSING`
- `DOM-SCHEMA-SILENT-DEFAULT-FORBIDDEN`
- `DOM-PROTOCOL-UNSUPPORTED-VERSION`
- `DOM-MIGRATION-MISSING`
- `DOM-REGISTRY-DUPLICATE-ID`

Evidence packets may reference schema/protocol validation outputs, migration decisions, fixtures, and compatibility proof. Evidence is proof output, not source authority.

## Public Surface And Artifact Relationship

Public surface registry entries say which schemas, protocols, and registries are exposed. Artifact identity law says durable artifacts must carry schema ID and version. Schema/protocol evolution law says how those IDs and versions may change.

Compatibility corpus work is future work. This task creates the law and validator path that later compatibility fixtures must follow.

Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# SCHEMA-PROTOCOL-LAW-01 Audit

Result: PASS_WITH_WARNINGS, pending final commit and post-commit checks.

## Why

Dominium needs explicit schema, registry, protocol, serialization, migration,
and refusal evolution law before more product behavior depends on durable data
contracts. This prevents silent schema changes, silent defaults, unversioned
stable contracts, path-as-identity, and best-effort migrations.

## Added

- `contracts/schema/schema_evolution.contract.toml`
- `contracts/protocol/protocol_evolution.contract.toml`
- `contracts/registry/registry_evolution.contract.toml`
- `contracts/serialization/canonical_serialization.contract.toml`
- `contracts/migration/migration_policy.contract.toml`
- `contracts/schema/schema_policy.schema.json`
- `contracts/protocol/protocol_policy.schema.json`
- `contracts/registry/registry_policy.schema.json`
- `contracts/schema/schema_stability.registry.json`
- `contracts/schema/field_policy.registry.json`
- `contracts/protocol/protocol_stability.registry.json`
- `tools/validators/contracts/check_schema_protocol_evolution.py`
- `tests/contract/schema_protocol/**`
- `docs/architecture/schema_protocol_evolution.md`
- `docs/development/schema_protocol_guidelines.md`

## Inventory

The initial descriptive inventory scanned 17,808 tracked files and classified
2,489 schema/protocol-like files:

- 90 manifest-backed candidates.
- 1,386 likely public schemas.
- 463 registries.
- 7 protocol-like files.
- 27 fixtures.
- 503 deferred data/contract files.

The inventory records scope only. Existing schemas, protocols, registries,
manifests, packs, and fixtures are not migrated by this task.

## Proof

- Schema/protocol validator strict mode passes.
- Schema/protocol fixture mode passes.
- Diagnostics registry validates with 33 codes.
- Public surface registry validates with 67 surfaces.
- Fast strict passes: 32/32 commands in 331.344 seconds.

## Known Limitations

- Law is provisional.
- Compatibility corpus is not populated.
- Runtime schema/protocol migration and dispatch are not implemented.
- Existing dependency-direction debt remains visible.
- Full CTest is not run; it remains T4 full/release proof.

Next task: `CAPABILITY-REFUSAL-LAW-01`.

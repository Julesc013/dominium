# SCHEMA-PROTOCOL-LAW-01 Initial Schema/Protocol Inventory

Starting commit: `2635c7d2475b4b015cf2fb3f01b75866f6976343`

Inventory command:

`python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --inventory`

## Summary

- Files scanned: 17,808 tracked files.
- Schema/protocol-like files: 2,489.
- Inventory status: warning, descriptive only.
- Missing ID-like field count: 1,803.
- Missing version-like field count: 983.

## Categories

- Manifest-backed schema candidates: 90.
- Likely public schemas: 1,386.
- Internal schema/policy files: 13.
- Generated schema files: 0.
- Fixture schema/policy files: 27.
- Historical schema files: 0.
- Registries: 463.
- Protocol-like files: 7.
- Deferred data/contract files: 503.

## Examples

Manifest-backed:

- `content/packs/core/org.dominium.base.body.earth_macro/pack_manifest.json`
- `content/packs/core/org.dominium.base.rules/pack_manifest.json`
- `content/packs/core/org.dominium.base.scenarios.minimal/pack_manifest.json`

Likely public schema:

- `contracts/schema/SCHEMA_MIGRATION_REGISTRY.json`
- `contracts/schema/accessibility_preset.schema`
- `contracts/schema/action_family.schema.json`

Registry:

- `contracts/artifact/artifact_kind.registry.json`
- `contracts/diagnostics/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`

Protocol-like:

- `contracts/registry/protocol_registry.json`
- `contracts/schema/protocol_range.schema.json`
- `contracts/schema/server_protocol.schema`

## Disposition

The inventory is intentionally descriptive. SCHEMA-PROTOCOL-LAW-01 creates the
evolution law and validator; it does not migrate existing schemas, protocols,
registries, manifests, packs, or fixtures.

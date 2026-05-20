# ARTIFACT-IDENTITY-LAW-01 Initial Artifact Inventory

Starting HEAD: `de5b38964a74e56d658bddac791f14b236dd65c0`

## Inventory Summary

The artifact inventory is descriptive only. This task does not migrate existing
artifacts.

- tracked files scanned: 17,782
- artifact-like files found: 1,890
- manifest-backed candidates: 244
- schema or registry files: 1,437
- historical/archive artifact-like files: 103
- generated evidence files: 1
- deferred artifact-like files: 105

## Categories

| Category | Count | Examples | Current Identity Mechanism | Risk | Future Task |
| --- | ---: | --- | --- | --- | --- |
| Manifest-backed candidates | 244 | `content/packs/core/org.dominium.base.rules/pack_manifest.json`, `content/packs/blueprint/blueprints.default.m1/pack.json` | Existing pack/profile/package manifests | May not yet follow universal artifact manifest law | MOD-PACK-TRUST-MODEL-01 / SCHEMA-PROTOCOL-LAW-01 |
| Schema or registry files | 1,437 | `contracts/diagnostics/diagnostic_category.registry.json`, `contracts/command/command.schema.json` | Contract/schema filenames plus registry IDs | Stable schema evolution remains future law | SCHEMA-PROTOCOL-LAW-01 |
| Historical/archive | 103 | `archive/generated/aide/**` schemas | Archive retention and provenance | Must not become active source identity | VERSION-DEPRECATION-LAW-01 |
| Generated evidence | 1 | `.aide/reports/file-quality-ledger.schema.json` | Generated/tracked evidence policy | Evidence is not source truth | ARTIFACT-IDENTITY-LAW follow-up if needed |
| Deferred | 105 | `.aide/install/*.schema.json` and similar AIDE surfaces | Tool-local schemas | Needs later AIDE/tool artifact classification | FOUNDATION-CLOSEOUT-01 |

## Explicit Non-Migration

No pack, profile, save, replay, release, archive, generated report, or AIDE
evidence artifact was rewritten by this task. The new validator validates the
artifact identity law and fixtures, then inventories existing surfaces for later
bounded migration.

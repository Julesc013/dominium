Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# SAVE_MANIFEST_BASELINE

## Purpose

LIB-3 defines `SaveManifest` as the deterministic identity and compatibility contract for portable saves. A save pins:

- `save_id`
- `save_format_version`
- `universe_identity_hash`
- `universe_contract_bundle_hash`
- `generator_version_id`
- `realism_profile_id`
- `pack_lock_hash`
- `overlay_manifest_hash`
- `mod_policy_id`
- `created_by_build_id`
- `migration_chain`
- `allow_read_only_open`
- `deterministic_fingerprint`

## Manifest Fields

Required canonical fields:

- contract and pack identity: `universe_contract_bundle_hash`, `pack_lock_hash`, `overlay_manifest_hash`
- creation identity: `generator_version_id`, `realism_profile_id`, `created_by_build_id`, `mod_policy_id`
- compatibility lineage: `save_format_version`, `migration_chain`, `allow_read_only_open`

Optional adapter fields:

- `semantic_contract_registry_hash`
- `contract_bundle_ref`
- `state_snapshots_ref`
- `patches_ref`
- `proofs_ref`

## Open Policy Decision Tree

When opening a selected save:

1. validate `save.manifest.json`
2. load the pinned contract bundle sidecar and verify its canonical hash
3. compare `pack_lock_hash` against the selected runtime pack lock
4. compare any pinned semantic contract registry hash against the selected install/pack metadata
5. compare `created_by_build_id` against the selected install build set
6. if `save_format_version` is older/newer than the current save contract:
   - explicit migration may be invoked
   - otherwise only `inspect-only` read-only fallback is allowed when `allow_read_only_open` and the launcher flow permit it
7. otherwise continue in full runtime mode

No silent migration or silent read-only downgrade is permitted.

## Migration And Read-Only Rules

- Explicit migrations append deterministic `migration_event` records.
- `migration_chain` is append-only and terminal `to_version` must match `save_format_version`.
- Read-only fallback is lawful only when the save opts in through `allow_read_only_open`.
- Missing or invalid contract bundle sidecars remain refusal outcomes.

## Readiness For LIB-4

LIB-3 is ready for profile/blueprint/resource manifest work because:

- save identity is now separate from instance identity
- save portability is hash-pinned to contracts and pack locks
- explicit migration lineage exists for future manifest/resource conversions
- launcher preflight can negotiate save compatibility without mutating simulation behavior

## Enforced Invariants

- `INV-SAVE-MANIFEST-REQUIRED`
- `INV-SAVE-PINS-CONTRACTS`
- `INV-NO-SILENT-MIGRATION`

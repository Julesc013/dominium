Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Save Model (SAVE2 / LIB-3)

Status: binding.
Scope: portable save manifests, pinned contract bundles, migration lineage, and read-only fallback.

## Authoritative Contracts

Save identity is carried by:

- `schema/save.manifest.schema` for the legacy/runtime-compatible save manifest adapter.
- `schema/lib/save_manifest.schema` for the LIB-3 canonical save descriptor.
- `schema/lib/migration_event.schema` for explicit save migration lineage records.

## Required LIB-3 Identity

Every LIB-3 save must declare:

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

## Save Ownership Rules

- Saves do not belong to instances.
- Instances may reference saves through `save_refs`, but save truth remains portable across installs, forks, and instances.
- Save identity is pinned by hashes and ids, never by host path.

## Open Policy

When a launcher/runtime opens a save it must:

- load `save.manifest.json`
- verify the pinned contract bundle sidecar is present and matches `universe_contract_bundle_hash`
- verify `pack_lock_hash` is available and compatible with the selected instance/install
- compare any pinned semantic contract registry hash against the selected install and pack lock metadata
- refuse mutable runtime if build/contract/pack identity mismatches cannot be reconciled

If `allow_read_only_open` is true and the selected flow is safe for read-only fallback, the launcher may degrade to `inspect-only`. No silent degrade is permitted.

## Migration Rules

- Save format upgrades are explicit invoke-only.
- Any migration must append a `migration_event` to `migration_chain`.
- `save_format_version` must match the terminal migration target.
- Silent save upgrades are forbidden.

## Data Location Adapters

Optional relative locators may point at:

- `contract_bundle_ref`
- `state_snapshots_ref`
- `patches_ref`
- `proofs_ref`

These are adapters only. Identity and compatibility remain hash-pinned.

## Enforced Invariants

- `INV-SAVE-MANIFEST-REQUIRED`
- `INV-SAVE-PINS-CONTRACTS`
- `INV-NO-SILENT-MIGRATION`

## Related Contracts

- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `docs/architecture/SAVE_PIPELINE.md`
- `docs/architecture/SAVE_FORMAT.md`
- `docs/distribution/LAUNCHER_GUIDE.md`
- `docs/audit/SAVE_MANIFEST_BASELINE.md`

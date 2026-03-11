Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# Instance Model (OPS0 / LIB-0)

Status: binding.
Scope: instance manifests, linked vs portable topology, and artifact resolution.

## Authoritative Contracts

Instance manifests are defined by:

- `schema/instance.manifest.schema` for legacy/runtime-compatible fields.
- `schema/lib/instance_manifest.schema` for LIB-0 CAS topology fields.

## Required LIB-0 Identity

Every LIB-0 instance must declare:

- `instance_id`
- `mode` (`linked` or `portable`)
- `install_ref`
- `pack_lock_hash`
- `profile_bundle_hash`
- `mod_policy_id`
- `overlay_conflict_policy_id`
- `instance_settings`
- `deterministic_fingerprint`

## Linked Topology

- Reusable artifacts resolve through `store_root` plus artifact hashes.
- Cloning a linked instance must not duplicate store artifacts.
- Relative store locators are allowed as adapters, but hashes remain authoritative.

## Portable Topology

- Required reusable artifacts are materialized under `embedded_artifacts/`.
- Portable instances must remain valid after directory copy without a shared store.
- Exported portable instances must be self-contained and offline-usable.

## Compatibility Rules

- Legacy `capability_lockfile` remains a compatibility file path only.
- `active_profiles`, `active_modpacks`, and `data_root` remain available for current launcher/ops flows.
- Instance topology must not change authoritative gameplay/runtime behavior; it is storage-only.

## Related Contracts

- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/LOCKFILES.md`
- `docs/distribution/LAUNCHER_GUIDE.md`

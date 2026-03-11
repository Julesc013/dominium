Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# Instance Model (OPS0 / LIB-2)

Status: binding.
Scope: runnable instance manifests, install/build selection, save associations, and linked vs portable topology.

## Authoritative Contracts

Instance manifests are defined by:

- `schema/instance.manifest.schema` for legacy/runtime-compatible fields.
- `schema/lib/instance_manifest.schema` for the LIB-2 canonical instance contract.
- `schema/lib/instance_settings.schema` for deterministic instance settings.

## Required LIB-2 Identity

Every LIB-2 instance must declare:

- `instance_id`
- `instance_kind`
- `mode` (`linked` or `portable`)
- `install_ref`
- `pack_lock_hash`
- `profile_bundle_hash`
- `mod_policy_id`
- `overlay_conflict_policy_id`
- `default_session_template_id`
- `seed_policy`
- `instance_settings`
- `save_refs`
- `deterministic_fingerprint`

Instances may also declare:

- `resolution_policy_id`
- `provides_resolutions`

## Instance Kinds

Supported kinds:

- `instance.client`
- `instance.server`
- `instance.tooling`

`instance_kind` constrains launcher run-mode negotiation only. It does not alter authoritative simulation behavior.

## Save Associations

- Instances do not own saves.
- `save_refs` is a deterministic list of associated `save_id` values.
- The last opened save may be recorded in `extensions["instance.last_opened_save_id"]`.
- Saves must never be embedded under the instance root as authoritative payload.

## Linked Topology

- Reusable artifacts resolve through `store_root` plus artifact hashes.
- Cloning a linked instance must not duplicate store artifacts.
- Install selection may switch between compatible installs as long as build/range negotiation succeeds.
- Relative locators are allowed as adapters, but hashes and IDs remain authoritative.

## Portable Topology

- Required reusable artifacts are materialized under `embedded_artifacts/`.
- Optional embedded binaries are described through `embedded_builds`.
- Portable instances must remain valid after directory copy without a shared store.
- Exported portable instances must be self-contained and offline-usable.

## Build Selection And Degrade

- Launcher start/preflight must verify `pack_lock_hash` and `profile_bundle_hash` before runtime.
- `required_product_builds` and `required_contract_ranges` may pin launcher selection without changing runtime law.
- Required provides surfaces from the bound pack lock must resolve through `resolution_policy_id` plus `provides_resolutions` or an equivalent deterministic pack-lock record.
- Instance-level provider selections must match the bound lock record or the launcher must refuse.
- CAP-NEG may degrade to read-only / inspect-only only when explicitly allowed and logged.
- No silent degrade is permitted.

## Compatibility Rules

- Legacy `capability_lockfile` remains a compatibility file path only.
- Legacy `install_id`, `data_root`, `active_profiles`, and `active_modpacks` remain adapter fields for current launcher/setup flows.
- Instance topology and install switching must not change authoritative gameplay/runtime behavior; they are storage/selection concerns only.

## Enforced Invariants

- `INV-INSTANCE-USES-PACK-LOCK`
- `INV-INSTANCE-USES-PROFILE-BUNDLE`
- `INV-SAVES-NOT-EMBEDDED-IN-INSTANCE`

## Related Contracts

- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/SAVE_MODEL.md`
- `docs/architecture/LOCKFILES.md`
- `docs/distribution/LAUNCHER_GUIDE.md`
- `docs/audit/INSTANCE_MANIFEST_BASELINE.md`

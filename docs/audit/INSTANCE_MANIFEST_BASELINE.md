Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# INSTANCE_MANIFEST_BASELINE

## Purpose

LIB-2 defines `InstanceManifest` as the deterministic runnable configuration for Dominium instances. An instance binds:

- `instance_id`
- `instance_kind`
- `mode`
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

## Instance Types

Supported kinds:

- `instance.client`
- `instance.server`
- `instance.tooling`

Kind selection constrains launcher negotiation only. It does not change authoritative simulation behavior.

## Linked And Portable Behavior

Linked instances:

- resolve reusable artifacts through `store_root`
- keep `install_ref` as the active build selector
- do not duplicate pack/profile artifacts on clone

Portable instances:

- embed required lock/profile/pack artifacts under `embedded_artifacts/`
- may carry optional `embedded_builds`
- remain shareable and offline-usable after directory copy or bundle export

## Save Associations

- Instances reference saves by `save_refs`.
- Instances may record `instance.last_opened_save_id` in `extensions`.
- Instances do not own saves and must not embed save payloads.

## Launcher Selection Rules

- Launcher preflight/start must validate `pack_lock_hash` and `profile_bundle_hash`.
- Launcher preflight/start must compare `required_product_builds` and `required_contract_ranges` against the selected install.
- CAP-NEG degrade ladders may fall back to read-only / inspect-only only when explicitly allowed and logged.
- No silent degrade is permitted.

## Readiness For LIB-3

LIB-2 is ready for `SaveManifest` portability because:

- instances no longer imply save ownership
- save associations are explicit and portable
- instance export/import preserves save references without copying save truth
- linked and portable instance flows already separate reusable content from save state

## Enforced Invariants

- `INV-INSTANCE-USES-PACK-LOCK`
- `INV-INSTANCE-USES-PROFILE-BUNDLE`
- `INV-SAVES-NOT-EMBEDDED-IN-INSTANCE`

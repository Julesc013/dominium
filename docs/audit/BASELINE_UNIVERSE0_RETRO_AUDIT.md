# Baseline Universe 0 Retro Audit

## Scope

- Objective: freeze one canonical MVP reference universe derived from the Ω-1 baseline seed.
- Source seed: `DOMINIUM_MVP_BASELINE_SEED_0`
- WORLDGEN-LOCK dependency: `worldgen_lock.v0_0_0`

## Instance Manifest Structure

- Artifact: `data/baselines/universe/baseline_instance.manifest.json`
- Canonical fields present:
  - `instance_id`
  - `pack_lock_hash`
  - `profile_bundle_hash`
  - `mod_policy_id`
  - `save_refs`
  - `instance_settings.active_modpacks`
  - `instance_settings.active_profiles`
  - `extensions.official.*`
  - `universal_identity_block`
- Frozen values:
  - `instance_id = instance.baseline_universe_0`
  - `pack_lock_hash = 60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
  - `profile_bundle_hash = f94ca4c75cc5ccb7a27a6fcab2a086be85d95dd8804fc180418200e8612a3239`
  - effective `mod_policy_id = mod_policy.lab`
  - requested baseline policy recorded as `extensions.official.requested_mod_policy_id = mod_policy.strict`

## Save Artifact Structure

- Artifact: `data/baselines/universe/baseline_save_0.save`
- Loader surface: `save_file`
- Observed stable metadata:
  - `format_version = 2.0.0`
  - `engine_version_created = 0.0.0+build.bfa086e1ece381b1`
  - deterministic save hash `6717f843285193a0b261aadd424b963502f41fce66755fb18deab2f64c1011dc`
- No separate `save.manifest` artifact is emitted by the current MVP save pipeline; Ω-2 freezes the canonical save file plus loader metadata instead.

## Proof Anchor Mechanism

- Authority anchor builder: `src/time/epoch_anchor_engine.py::build_epoch_anchor_record`
- Proof anchors bind:
  - simulation tick
  - truth hash
  - contract bundle hash
  - pack lock hash
  - overlay manifest hash
  - anchor reason
- Ω-2 snapshot also carries derived-view hash payloads so terrain/refinement surfaces are pinned even when the persisted save schema omits transient refinement caches.

## Epoch Anchor Behavior

- Time anchor policy: `time.anchor.mvp_default`
- Declared checkpoint interval: `10000` ticks
- Frozen checkpoints:
  - `T0` initialization at tick `0`
  - `T1` post-refinement at tick `0`
  - `T2` after first terrain edit at tick `1`
  - `T3` after save-reload cycle at tick `1`

## Default Pack Lock And Profile Bundle

- Pack lock:
  - `pack_lock_id = pack_lock.mvp_default`
  - `pack_lock_hash = 60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
  - packs:
    - `pack.base.procedural`
    - `pack.sol.pin_minimal`
    - `pack.earth.procedural`
- Profile bundle:
  - `profile_bundle_id = profile.bundle.mvp_default`
  - `profile_bundle_hash = f94ca4c75cc5ccb7a27a6fcab2a086be85d95dd8804fc180418200e8612a3239`
  - active truth-critical profiles:
    - `physics.default_realistic`
    - `realism.realistic_default_milkyway_stub`
    - `geo.topology.r3_infinite`
    - `geo.metric.euclidean`
    - `geo.partition.grid_zd`
    - `geo.projection.perspective_3d`

## Install Profile Composition

- Install profile resolved: `install.profile.full`
- Baseline instance composition resolves to:
  - `active_modpacks = [pack.base.procedural, pack.earth.procedural, pack.sol.pin_minimal]`
  - `active_profiles = [geo.metric.euclidean, geo.partition.grid_zd, geo.projection.perspective_3d, geo.topology.r3_infinite, physics.default_realistic, realism.realistic_default_milkyway_stub]`

## Required Pack Presence

- Verified present:
  - `packs/base/pack.base.procedural`
  - `packs/official/pack.sol.pin_minimal`
  - `packs/official/pack.earth.procedural`
- Result: pass

## Provisional Stub Review

- Existing frozen inputs still include previously declared stub-labelled identities:
  - `gen.v0_stub`
  - `realism.realistic_default_milkyway_stub`
- Ω-2 introduces no new provisional or stub-only truth-critical surfaces.
- The baseline-universe freeze is pinned to the already accepted Ω-1 worldgen lock rather than expanding or replacing those frozen identities.

## Findings

- Effective mod policy remains `mod_policy.lab` because `pack_lock.mvp_default` is frozen by Ω-1 and changing it would drift the worldgen lock and universe identity.
- Ω-2 records `requested_mod_policy_id = mod_policy.strict` as the policy target while preserving the frozen effective pack lock for determinism.

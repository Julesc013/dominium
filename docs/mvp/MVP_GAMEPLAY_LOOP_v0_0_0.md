# MVP Gameplay Loop v0.0.0

## 1. Baseline Seed

- Baseline seed: `DOMINIUM_MVP_BASELINE_SEED_0`
- Seed hash: `1a6131adcc7512c23a7aac166dece3944adcc4abf97e907fe53558fba9388281`
- Must match `WORLDGEN-LOCK-0` and `BASELINE-UNIVERSE-0`.

## 2. Contract Bundle

- `semantic_contract_registry_hash = 55bef1f0337c3a311cc5a30c8880715bffbf93d93eb64c24cc2f1d7f86b1df94`
- `worldgen_lock_id = worldgen_lock.v0_0_0`
- `universe_contract_bundle_hash = 377d193b1c4353dbacec453ba321dae2658e3d1e72cb8ff6696c289d7f513338`

## 3. Pack Lock

- `pack_lock_id = pack_lock.mvp_default`
- Included packs:
  - `pack.base.procedural`
  - `pack.sol.pin_minimal`
  - `pack.earth.procedural`

## 4. Instance Configuration

- `install_profile = install.profile.full`
- requested baseline `mod_policy = mod_policy.strict`
- effective frozen `mod_policy = mod_policy.lab`
- `trust_policy = trust.default_mock`
- `physics_profile = physics.default_realistic`

## 5. Proof Anchor Schedule

- Checkpoint interval: `10000`
- Checkpoints are recorded before simulation tick advancement.
- Frozen anchor hashes:
  - `T0`: truth `ae20b5c462fd0b5d95931eb6ce70c882619d347d5201b9f2345df901e92b2593`, derived `f846026503696c711ef98e72d36f7674ac7d84a9e08e7281ce5e96f8fffd32ca`
  - `T1`: truth `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`, derived `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`
  - `T2`: truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`, derived `3f30b070620a6ee1cf28e78afda5c03fbade60832058ad4345ff421fba26a36f`
  - `T3`: truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`, derived `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

## 6. Canonical Loop

### STEP 1 - Launch

- Command:
  - `python tools/mvp/runtime_entry.py client --repo-root . --seed "DOMINIUM_MVP_BASELINE_SEED_0" --profile_bundle data/baselines/universe/baseline_profile_bundle.json --pack_lock data/baselines/universe/baseline_pack_lock.json --ui cli`
- Expected result:
  - deterministic CLI bootstrap opens the baseline universe context
- Expected proof anchor:
  - `T0` truth `ae20b5c462fd0b5d95931eb6ce70c882619d347d5201b9f2345df901e92b2593`
- Expected derived hash:
  - `f846026503696c711ef98e72d36f7674ac7d84a9e08e7281ce5e96f8fffd32ca`

### STEP 2 - Teleport

- Commands:
  - `tool tp /tp sol`
  - `tool tp /tp earth`
  - `tool tp /tp chart.surface.8d9723595c7f.north:0,0,0`
- Expected result:
  - deterministic teleport planning for Sol, Earth, and the frozen baseline coordinate
- Expected proof anchor:
  - `T1` truth `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`
- Expected derived hash:
  - `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`

### STEP 3 - Inspect

- Command:
  - `tool scan`
- Expected result:
  - tile inspection returns the frozen readout for the baseline tile
- Expected readout:
  - elevation proxy `2158`
  - temperature `226`
  - daylight `32`
  - tide height proxy `31`
  - biome `biome.stub.polar`
  - material `material.stone_basic`
- Expected proof anchor:
  - `T1` truth `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`
- Expected derived hash:
  - `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`

### STEP 4 - Modify Terrain

- Command:
  - `tool mine`
- Expected result:
  - one baseline tile is mined deterministically through `process.geometry_remove`
- Frozen target:
  - `chart.surface.8d9723595c7f.north:0,0,0`
- Expected proof anchor:
  - `T2` truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Expected derived hash:
  - `3f30b070620a6ee1cf28e78afda5c03fbade60832058ad4345ff421fba26a36f`

### STEP 5 - Logic Interaction

- Commands:
  - `tool probe`
  - `process.logic_compile_request`
  - `tool trace`
- Expected result:
  - the canonical logic smoke network completes with deterministic L1 and compiled L2 outputs
- Expected hashes:
  - compiled model `c44de1dac0c41cd1903286964fe89d4aedf434c5b1505e25e61bfea25ff2c9eb`
  - toggle off final signal `c47a57a151d39af3b381c8ad59110b789c4cc2f7410f44796c115535329c7cd5`
  - toggle on final signal `53048e95ebda517d4c2e1d1432bd70d7a86a2fdbfb01071398380e9577d22ff9`
- Expected proof anchor:
  - unchanged from `T2` truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`

### STEP 6 - Save

- Command:
  - `save_snapshot`
- Expected result:
  - gameplay loop save hash matches the frozen baseline save
- Expected save hash:
  - `6717f843285193a0b261aadd424b963502f41fce66755fb18deab2f64c1011dc`
- Expected proof anchor:
  - unchanged from `T2` truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`

### STEP 7 - Reload

- Command:
  - `load_versioned_artifact`
- Expected result:
  - reload reproduces the frozen post-edit state
- Expected proof anchor:
  - `T3` truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Expected derived hash:
  - `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

### STEP 8 - Replay

- Command:
  - `python tools/mvp/tool_verify_gameplay_loop.py --repo-root . --seed-text "DOMINIUM_MVP_BASELINE_SEED_0" --snapshot-path data/baselines/gameplay/gameplay_loop_snapshot.json`
- Expected result:
  - replay from seed reproduces the same final anchor as reload and the frozen baseline universe
- Expected proof anchor:
  - `T3` truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Expected derived hash:
  - `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

## 7. Determinism Guarantees

- Replay from seed reproduces identical proof anchors.
- Save-reload reproduces the same frozen post-edit state.
- No wall-clock dependency is permitted.
- No thread-count dependency is permitted.
- The loop must remain callable through CLI/TUI without GUI-only state.

## 8. Stability Marker

- `gameplay_loop_version = 0`
- `stability_class = stable`

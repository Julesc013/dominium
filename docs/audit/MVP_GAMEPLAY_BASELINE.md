# MVP Gameplay Baseline

- Seed: `DOMINIUM_MVP_BASELINE_SEED_0`
- Pack Lock: `pack_lock.mvp_default` (`60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`)
- Profile Bundle: `profile.bundle.mvp_default` (`f94ca4c75cc5ccb7a27a6fcab2a086be85d95dd8804fc180418200e8612a3239`)
- Save Hash: `6717f843285193a0b261aadd424b963502f41fce66755fb18deab2f64c1011dc`
- Replay Confirmation: `True`
- Verification: `PASS`

## Steps

- `STEP_1` Launch
- `STEP_2` Teleport
- `STEP_3` Inspect
- `STEP_4` Modify Terrain
- `STEP_5` Logic Interaction
- `STEP_6` Save
- `STEP_7` Reload
- `STEP_8` Replay

## Commands

- Launch: `python tools/mvp/runtime_entry.py client --repo-root . --seed "DOMINIUM_MVP_BASELINE_SEED_0" --profile_bundle data/baselines/universe/baseline_profile_bundle.json --pack_lock data/baselines/universe/baseline_pack_lock.json --ui cli`
- Teleport: `tool tp /tp sol`
- Teleport: `tool tp /tp earth`
- Teleport: `tool tp /tp chart.surface.8d9723595c7f.north:0,0,0`
- Inspect: `tool scan`
- Modify Terrain: `tool mine`
- Logic Interaction: `tool probe`
- Logic Interaction: `process.logic_compile_request`
- Logic Interaction: `tool trace`
- Save: `save_snapshot`
- Reload: `load_versioned_artifact`
- Replay: `python tools/mvp/tool_verify_gameplay_loop.py --repo-root . --seed-text "DOMINIUM_MVP_BASELINE_SEED_0" --snapshot-path data/baselines/gameplay/gameplay_loop_snapshot.json`

## Proof Anchors

- `T0`: truth `ae20b5c462fd0b5d95931eb6ce70c882619d347d5201b9f2345df901e92b2593`, derived `f846026503696c711ef98e72d36f7674ac7d84a9e08e7281ce5e96f8fffd32ca`
- `T1`: truth `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`, derived `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`
- `T2`: truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`, derived `3f30b070620a6ee1cf28e78afda5c03fbade60832058ad4345ff421fba26a36f`
- `T3`: truth `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`, derived `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

## Logic Hashes

- Compiled Model: `c44de1dac0c41cd1903286964fe89d4aedf434c5b1505e25e61bfea25ff2c9eb`
- Toggle Off Final Signal: `c47a57a151d39af3b381c8ad59110b789c4cc2f7410f44796c115535329c7cd5`
- Toggle On Final Signal: `53048e95ebda517d4c2e1d1432bd70d7a86a2fdbfb01071398380e9577d22ff9`

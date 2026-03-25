# MVP Gameplay Loop Run

- Result: `PASS`
- Seed: `DOMINIUM_MVP_BASELINE_SEED_0`
- Snapshot Fingerprint: `86d64e4c8937301d037aeaf3d38200192216b70a2e7f10785d548a614e245fef`
- Launch Fingerprint: `27fc1e89dcbf5783d0d34cd5b852e631558d84d4dd9a23a10d098873c8c8c964`
- Save Hash: `6717f843285193a0b261aadd424b963502f41fce66755fb18deab2f64c1011dc`
- Replay Final Anchor: `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`

## Steps

### Launch
- Command: `python tools/mvp/runtime_entry.py client --repo-root . --seed "DOMINIUM_MVP_BASELINE_SEED_0" --profile_bundle data/baselines/universe/baseline_profile_bundle.json --pack_lock data/baselines/universe/baseline_pack_lock.json --ui cli`
- Expected Result: `deterministic CLI bootstrap opens the baseline universe context`
- Proof Anchor: `ae20b5c462fd0b5d95931eb6ce70c882619d347d5201b9f2345df901e92b2593`
- Derived View Hash: `f846026503696c711ef98e72d36f7674ac7d84a9e08e7281ce5e96f8fffd32ca`

### Teleport
- Command: `tool tp /tp sol`
- Command: `tool tp /tp earth`
- Command: `tool tp /tp chart.surface.8d9723595c7f.north:0,0,0`
- Expected Result: `teleport planning remains deterministic for sol, earth, and the baseline surface coordinate`
- Proof Anchor: `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`
- Derived View Hash: `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`

### Inspect
- Command: `tool scan`
- Expected Result: `scanner surfaces elevation and climate proxies for the baseline tile without GUI-only state`
- Proof Anchor: `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`
- Derived View Hash: `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`

### Modify Terrain
- Command: `tool mine`
- Expected Result: `one baseline surface tile selection is mined deterministically through process.geometry_remove`
- Proof Anchor: `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Derived View Hash: `3f30b070620a6ee1cf28e78afda5c03fbade60832058ad4345ff421fba26a36f`

### Logic Interaction
- Command: `tool probe`
- Command: `process.logic_compile_request`
- Command: `tool trace`
- Expected Result: `L1 and compiled L2 logic outputs remain deterministic for the canonical smoke network`

### Save
- Command: `save_snapshot`
- Expected Result: `the gameplay loop emits the same save hash as the frozen baseline universe save`
- Proof Anchor: `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Derived View Hash: `3f30b070620a6ee1cf28e78afda5c03fbade60832058ad4345ff421fba26a36f`

### Reload
- Command: `load_versioned_artifact`
- Expected Result: `reloading the saved universe reproduces the same post-edit proof anchor`
- Proof Anchor: `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Derived View Hash: `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

### Replay
- Command: `python tools/mvp/tool_verify_gameplay_loop.py --repo-root . --seed-text "DOMINIUM_MVP_BASELINE_SEED_0" --snapshot-path data/baselines/gameplay/gameplay_loop_snapshot.json`
- Expected Result: `replaying from the baseline seed reproduces the same final anchor as reload`
- Proof Anchor: `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- Derived View Hash: `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

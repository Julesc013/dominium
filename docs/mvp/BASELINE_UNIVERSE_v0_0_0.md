# Baseline Universe v0.0.0

## 1. Baseline Seed

- Baseline seed: `DOMINIUM_MVP_BASELINE_SEED_0`
- Seed hash: `1a6131adcc7512c23a7aac166dece3944adcc4abf97e907fe53558fba9388281`
- Must match `WORLDGEN-LOCK-0`.

## 2. Contract Bundle

- `semantic_contract_registry_hash = 55bef1f0337c3a311cc5a30c8880715bffbf93d93eb64c24cc2f1d7f86b1df94`
- `universe_contract_bundle_hash = 377d193b1c4353dbacec453ba321dae2658e3d1e72cb8ff6696c289d7f513338`
- `worldgen_lock_id = worldgen_lock.v0_0_0`
- `worldgen_lock_version = 0`

## 3. Pack Lock

- `pack_lock_id = pack_lock.mvp_default`
- `pack_lock_hash = 60bdee0f775bcb05eafa3922e8eabf9fc0a64ebc332c26d3ddf3c5b993b65687`
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

Freeze note:
`pack_lock.mvp_default` is inherited from Ω-1 and already contributes to the frozen worldgen identity. Ω-2 records the strict policy target but does not mutate the effective pack lock, because doing so would silently change the locked universe provenance.

## 5. Proof Anchor Schedule

- Time anchor policy: `time.anchor.mvp_default`
- Checkpoint interval: `10000`
- Checkpoints are recorded before simulation tick advancement.

### T0 Initialization

- tick `0`
- truth hash `ae20b5c462fd0b5d95931eb6ce70c882619d347d5201b9f2345df901e92b2593`
- derived-view hash `f846026503696c711ef98e72d36f7674ac7d84a9e08e7281ce5e96f8fffd32ca`

### T1 Post-Refinement

- tick `0`
- truth hash `cdb35b438d558fbd7c46d37ceca142c71a50704e63102e1e1db4a534adff4d24`
- derived-view hash `745952851cfe572c8a0769eab29314e71031cf9ca2881e91d2324d0c2f135d4b`

### T2 After First Terrain Edit

- tick `1`
- truth hash `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- derived-view hash `3f30b070620a6ee1cf28e78afda5c03fbade60832058ad4345ff421fba26a36f`

### T3 After Save-Reload Cycle

- tick `1`
- truth hash `9a4b50a04ec64978167f32b19741821bb6b5cd673e3e33e7c4a7fa024434900d`
- derived-view hash `365a2060075cf547fa703d134d204356ed6a772752693b51d7daeabf9eb0f7c0`

## 6. Determinism Guarantees

- Reconstructing from seed + worldgen lock + contract bundle + pack lock reproduces the committed snapshot.
- Baseline proof anchors reproduce across repeated runs.
- Save reload reproduces the frozen T2 persisted-state anchor.
- No wall-clock dependence is permitted.
- No thread-count dependence is permitted.

## 7. Stability Marker

- `baseline_universe_version = 0`
- `stability_class = stable`

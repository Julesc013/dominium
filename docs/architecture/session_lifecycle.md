Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: `docs/architecture/session_lifecycle.md` v1.0.0 (2026-02-14)
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon/glossary v1.0.0, `schemas/session_spec.schema.json` v1.0.0, `schemas/srz_shard.schema.json` v1.0.0, and `schemas/intent_envelope.schema.json` v1.0.0.

# Session Lifecycle v1

## Purpose
Define deterministic session lifecycle flow for lab bootstrap and scripted execution:
1. create SessionSpec
2. validate contracts
3. ensure lockfile/registries
4. boot
5. schedule intents through SRZ phases
6. emit run-meta with hash anchors
7. shutdown

## Lifecycle Steps
1. **Bundle selection**
   - Read `bundles/<bundle_id>/bundle.json`.
   - Validate with `schemas/bundle_profile.schema.json`.
2. **Session creation**
   - `tools/xstack/session_create --save-id <id> --bundle bundle.base.lab`
   - Emits canonical JSON:
     - `saves/<save_id>/session_spec.json`
     - `saves/<save_id>/universe_identity.json`
     - `saves/<save_id>/universe_state.json`
3. **Setup/packaging (optional but required for reproducible dist launch)**
   - `tools/setup/build --bundle bundle.base.lab --out dist`
   - Emits deterministic dist artifacts:
     - `dist/manifest.json`
     - `dist/lockfile.json`
     - `dist/registries/*.json`
4. **Compile lock + registries**
   - `tools/xstack/lockfile_build --bundle bundle.base.lab --out build/lockfile.json`
   - Registry hashes must match lockfile.
5. **Boot**
   - `tools/xstack/session_boot saves/<save_id>/session_spec.json`
   - Validates SessionSpec, identity/state payloads, lockfile, and registry hashes.
6. **Scripted execution (SRZ scheduler)**
   - `tools/xstack/session_script_run <session_spec> <script> [--workers N] [--logical-shards N]`
   - Input flow:
     - Input script row -> Intent Envelope -> Scheduler (`read -> propose -> resolve -> commit`) -> Process runtime.
   - Process mutations are commit-phase only.
7. **SRZ status inspection**
   - `tools/xstack/srz_status saves/<save_id>/session_spec.json`
   - Reports shard ownership counts and last hash anchor.
8. **Run-meta**
   - `saves/<save_id>/run_meta/<run_id>.json`
   - Includes:
     - `pack_lock_hash`
     - registry hashes
     - `session_spec_hash`
     - per-step `state_hash_anchors`
     - per-tick `tick_hash_anchors`
     - `checkpoint_hashes`
     - final `composite_hash`
9. **Shutdown**
   - v1 remains bounded/headless; no unbounded simulation loop.

## Scheduler Phase Semantics
1. `read`: snapshot only
2. `propose`: derive proposal rows from validated envelopes
3. `resolve`: canonical ordering and conflict rule (`first_wins`)
4. `commit`: apply accepted process mutations and produce hash anchors

## Determinism Rules
- Canonical JSON for all saved/run-meta artifacts.
- No wall-clock or scheduler interleaving in authoritative decisions.
- Identical inputs must produce identical:
  - SessionSpec hash
  - `pack_lock_hash`
  - registry hashes
  - per-tick hash anchors
  - checkpoint hashes
  - final composite hash
  - final state hash
- Timestamps are run-meta only and excluded from deterministic hash formulas.

## Refusal Rules
Create/boot/script execution must refuse deterministically on:
- invalid SessionSpec schema
- invalid or mismatched lockfile/registries
- UniverseIdentity mutation detection (`identity_hash` mismatch)
- invalid intent envelope
- invalid shard target (`SHARD_TARGET_INVALID`)

Refusal payload shape:
- `docs/contracts/refusal_contract.md`

## Example Commands
```text
tools/xstack/session_create --save-id save.lab.bootstrap --bundle bundle.base.lab --rng-seed-string seed.lab.bootstrap
tools/setup/build --bundle bundle.base.lab --out dist
tools/xstack/session_boot saves/save.lab.bootstrap/session_spec.json --bundle bundle.base.lab
tools/launcher/launch run --dist dist --session saves/save.lab.bootstrap/session_spec.json
tools/xstack/session_script_run saves/save.lab.bootstrap/session_spec.json tools/xstack/testdata/session/script.camera_nav.fixture.json --workers 1 --logical-shards 1
tools/xstack/srz_status saves/save.lab.bootstrap/session_spec.json
```

## TODO
- Add explicit cross-shard ownership-transfer lifecycle once multi-shard runtime lands.
- Add replay import/export format for external deterministic audit tooling.

## Cross-References
- `docs/contracts/session_spec.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/refusal_contract.md`
- `docs/architecture/setup_and_launcher.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/architecture/srz_contract.md`
- `docs/architecture/deterministic_parallelism.md`
- `docs/architecture/hash_anchors.md`

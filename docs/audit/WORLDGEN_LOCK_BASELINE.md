Status: DERIVED
Last Reviewed: 2026-03-24
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: Ω-1 canonical world genesis freeze for v0.0.0-mock.
Stability: provisional
Future Series: OMEGA
Replacement Target: Ω-9 toolchain matrix verification and Ω-11 mock release archive

# Worldgen Lock Baseline

## Governing Invariants

- `docs/canon/constitution_v1.md` A1 determinism is primary
- `docs/canon/constitution_v1.md` A4 no runtime mode flags
- `docs/canon/constitution_v1.md` E2-E7 deterministic ordering, reduction, replay, and partition-hash equivalence
- `docs/canon/constitution_v1.md` C1-C4 schema, migration, and CompatX obligations
- `AGENTS.md` Sections 2-5: profile-only behavior, process-only mutation, pack-driven integration, and FAST-minimum verification

## Canonical Inputs

- worldgen_lock_id: `worldgen_lock.v0_0_0`
- worldgen_lock_version: `0`
- baseline_seed: `DOMINIUM_MVP_BASELINE_SEED_0`
- baseline_seed_hash: `1a6131adcc7512c23a7aac166dece3944adcc4abf97e907fe53558fba9388281`
- seed_hash_algorithm: `canonical_sha256({"seed_text": <seed_string>})`
- worldgen_lock_registry_fingerprint: `b0a67499bc36ca58f0a98408230085fc470f3d46226d6a9fe9e93872bd28fa87`
- baseline_snapshot_fingerprint: `608157d9bc07e76d9ee12546e76f255464c8dcc998a899d272cc848be649640e`
- verify_report_fingerprint: `ee914103cb78684cb539de9f5b3fed9c167403760d76be31c3e30bc88162b7aa`

## Locked Identity Anchors

- sol_system_id: `7ca5f639b2245843839918025d66f78ae69ff49adfff73b3d1ab2131a7c4b7c6`
- earth_planet_id: `8d9723595c7f08e73be158cf1e4e6e24842b6e3ceefb62a2a6e6f8cf27f4c411`
- snapshot captures:
  - first `12` galaxy node ids
  - first `8` earth tile hashes
  - first `8` elevation field hashes
  - first `8` initial climate proxy hashes

## RNG Stream Registry

- `rng.worldgen.galaxy`
- `rng.worldgen.galaxy_objects`
- `rng.worldgen.system`
- `rng.worldgen.system.primary_star`
- `rng.worldgen.system.planet_count`
- `rng.worldgen.system.planet.{planet_index}`
- `rng.worldgen.planet`
- `rng.worldgen.surface`
- `rng.worldgen.surface.tile`
- `rng.worldgen.surface.generator`
- `rng.worldgen.surface.elevation`
- `rng.worldgen.surface.earth.elevation`

## Refinement Pipeline

- `L0.galaxy_coarse_structure` -> `367b602fb918081a40bc0594b74347250bb6bcf179c7c9dd286e6465f689a7c3`
- `L1.star_distribution` -> `74903d4d509d3bc993df9553e4286c967f11654be58f7730c08db93265b0eadc`
- `L2.sol_system_derivation` -> `1b9cb72fdd82264f4e05d8d0666ea1558331ba88b90960b48ed76c0efab27cee`
- `L3.earth_terrain_projection` -> `50538ba8573b50dddc8b1011b2aae68a341945046ba0183c774664ede0020ccf`

## Contract And Schema Impact

- Runtime worldgen semantics are unchanged; Ω-1 freezes and verifies the existing deterministic pipeline.
- Added and locked governance artifacts:
  - `docs/worldgen/WORLDGEN_LOCK_v0_0_0.md`
  - `data/registries/worldgen_lock_registry.json`
  - `data/baselines/worldgen/baseline_seed.txt`
  - `data/baselines/worldgen/baseline_worldgen_snapshot.json`
  - `docs/audit/WORLDGEN_LOCK_VERIFY.md`
  - `data/audit/worldgen_lock_verify.json`
- AppShell tool-surface artifacts were regenerated so the governed `dom worldgen generate-worldgen-baseline` and `dom worldgen verify-worldgen-lock` commands are registry-backed rather than orphan entrypoints.
- `docs/audit/TOPOLOGY_MAP.json` and `docs/audit/TOPOLOGY_MAP.md` were regenerated so `omega_artifact_registry` and `worldgen_lock_registry` are declared.
- No schema major version bumps, contract registry rewrites, or semantic compatibility range changes were introduced.

## Gate Execution Snapshot (2026-03-24)

1. Worldgen verify PASS
   - `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
   - result: `matches_snapshot=true`, `mismatch_count=0`
2. TestX PASS
   - `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset test_worldgen_baseline_matches_snapshot,test_rng_streams_registered,test_worldgen_lock_registry_schema_valid,test_cross_run_worldgen_deterministic`
   - result: `status=pass`, `selected_tests=4`
3. Ω registry invariant PASS
   - `python tests/invariant/omega_series_tests.py --repo-root . --case artifact_registry_complete`
   - result: `test_omega_artifact_registry_complete=ok`
4. RepoX STRICT PASS
   - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, `findings=17` warn-level only
5. AuditX STRICT PASS
   - `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, `findings=2449`, `promoted_blockers=0`
6. strict build PASS
   - `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.omega1 --cache on --format json`
   - result: `result=complete`, `canonical_content_hash=b0c95ddcd6ea30b3d812af3168123b0566761ebf538ce9bc266c0350bb23ed2d`

## Determinism Confirmation

- Same committed seed regenerates the same galaxy node IDs, sol system ID, earth planet ID, earth tile hashes, elevation hashes, climate proxy hashes, and stage hashes.
- Repeated snapshot construction matched byte-for-byte in `test_cross_run_worldgen_deterministic`.
- ARCH-AUDIT worldgen enforcement is active for unnamed RNG usage, float truth-path usage, registry presence, and baseline drift detection.

## Stop Conditions

- snapshot mismatch: `not triggered`
- unnamed RNG detected: `not triggered`
- nondeterminism introduced: `not triggered`
- canon conflict: `not triggered`

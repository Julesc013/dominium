Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: Prompt 20 Phase 3 determinism envelope verification
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Determinism Envelope Report

## Envelope Definition

Canonical envelope inputs:

1. `SessionSpec` canonical content (including selected seed and policy ids).
2. `pack_lock_hash` from lockfile.
3. Registry hash map from lockfile/runtime.
4. Deterministic RNG roots from SessionSpec.

Determinism invariants:

1. Identical envelope inputs produce identical final `composite_hash_anchor`.
2. Registry hashes remain stable across repeated end-to-end runs.
3. Worldgen/real-data derived anchors remain stable:
   - `worldgen_constraints_registry_hash`
   - `ephemeris_registry_hash`
   - `terrain_tile_registry_hash`
4. Run-meta timing fields are informational only and excluded from canonical comparisons.

## Verification Commands

1. Strict envelope meta-test:
   - `python tools/xstack/testx_all.py --repo-root . --profile STRICT --cache off --subset test_determinism_envelope_full_stack`
2. Strict pipeline run (includes packaging + lab validation):
   - `python tools/xstack/run.py strict --repo-root . --cache on`

## Evidence Summary

1. `test_determinism_envelope_full_stack`: `pass`.
2. Strict xstack profile: `pass`.
3. Repeated dist-build/lab-launch composite anchor stability confirmed by packaging validation path and determinism envelope meta-test.

## Exclusions

Excluded from determinism envelope comparisons:

1. Wall-clock timings (`duration_ms`) in reports.
2. Informational run timestamps in run-meta artifacts.
3. Non-canonical formatting metadata not used by canonical hash functions.

## Cross-References

- `docs/architecture/hash_anchors.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/audit/DEVELOPER_ACCELERATION_BASELINE.md`
- `tools/xstack/testx/tests/test_determinism_envelope_full_stack.py`

Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# ARCH Audit Baseline

## Checks

- `truth_purity_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `renderer_truth_access_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `duplicate_semantics_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `determinism_scan` -> `known_exception` (blocking=`0`, known_exceptions=`12`)
- `stability_marker_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `contract_pin_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `pack_compat_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)

## Known Provisional Exceptions

- `src/fields/field_engine.py`:649 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/geo/index/geo_index_engine.py`:208 Unreviewed floating-point usage in a truth-side path; review under ARCH-AUDIT-1.
- `src/geo/index/geo_index_engine.py`:228 Unreviewed floating-point usage in a truth-side path; review under ARCH-AUDIT-1.
- `src/geo/index/geo_index_engine.py`:244 Unreviewed floating-point usage in a truth-side path; review under ARCH-AUDIT-1.
- `src/geo/index/geo_index_engine.py`:245 Unreviewed floating-point usage in a truth-side path; review under ARCH-AUDIT-1.
- `src/geo/profile_binding.py`:111 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/logic/compile/logic_proof_engine.py`:148 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/logic/eval/common.py`:264 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/logic/eval/compute_engine.py`:285 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/logic/eval/sense_engine.py`:276 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/logic/fault/fault_engine.py`:206 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.
- `src/worldgen/refinement/refinement_cache.py`:155 Suspicious unordered container iteration in a truth-side path; review under ARCH-AUDIT-1.

## Readiness

- ARCH-AUDIT-1: `ready`
- EARTH-10 / SOL-1 / GAL stubs: `ready`

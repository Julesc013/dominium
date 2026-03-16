Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Canon-aligned documentation set tracked by ARCH-AUDIT and REPO-REVIEW-3.

# ARCH Audit Baseline

## Checks

- `truth_purity_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `renderer_truth_access_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `duplicate_semantics_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `determinism_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `float_in_truth_scan` -> `known_exception` (blocking=`0`, known_exceptions=`9`)
- `noncanonical_serialization_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `compiler_flag_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `parallel_truth_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `parallel_output_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `truth_atomic_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `stability_marker_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `contract_pin_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `pack_compat_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `dist_bundle_composition_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `update_model_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `trust_bypass_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `target_matrix_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)
- `archive_determinism_scan` -> `pass` (blocking=`0`, known_exceptions=`0`)

## Known Provisional Exceptions

- `src/geo/kernel/geo_kernel.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/geo/metric/metric_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/logic/compile/logic_proof_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/logic/eval/common.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/logic/fault/fault_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/meta/instrumentation/instrumentation_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/mobility/geometry/geometry_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/mobility/micro/constrained_motion_solver.py`:1 reviewed numeric bridge: deterministic quantization bridge
- `src/process/qc/qc_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge

## Readiness

- ARCH-AUDIT-1: `ready`
- EARTH-10 / SOL-1 / GAL stubs: `ready`

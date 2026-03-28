Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Numeric discipline baseline and release-pinned numeric policy docs.

# Numeric Scan Report

- report_id: `numeric.discipline.scan.v1`
- source_report_id: `arch.audit.v1`
- result: `complete`
- release_status: `pass`
- blocking_finding_count: `0`
- known_exception_count: `9`
- deterministic_fingerprint: `f047f98761d55282802b82025a6dafdf16dfed8ef40ae67531399c923990baa4`

## Numeric Checks

### float_in_truth_scan
- result: `known_exception`
- blocking_finding_count: `0`
- known_exception_count: `9`
- deterministic_fingerprint: `dc8f7ffda9a8fc357cee77403dd0e954442a42f01fcf721d539c312aa720a253`
- known exceptions:
  - `geo/kernel/geo_kernel.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `geo/metric/metric_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `logic/compile/logic_proof_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `logic/eval/common.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `logic/fault/fault_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `meta/instrumentation/instrumentation_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `mobility/geometry/geometry_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `mobility/micro/constrained_motion_solver.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `process/qc/qc_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge

### noncanonical_serialization_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `d234cf3d22b0f7b9c93e838e23671708707c7e218c20dfb77411566a9b0769c0`

### compiler_flag_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `9cf40fb86be290eddcd762ee4ba9c4125ee4a4cf9e18ca38360dd9916b5b1364`

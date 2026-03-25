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
- deterministic_fingerprint: `f09b1cd3abe7f3dc99c061224bdc3410a93f887171800efba7fde3960aac8400`

## Numeric Checks

### float_in_truth_scan
- result: `known_exception`
- blocking_finding_count: `0`
- known_exception_count: `9`
- deterministic_fingerprint: `527c0f8c27dd6e861a629ec4e1d3dc7dddac037f71fe3c73b43484add093e48a`
- known exceptions:
  - `src/geo/kernel/geo_kernel.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/geo/metric/metric_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/logic/compile/logic_proof_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/logic/eval/common.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/logic/fault/fault_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/meta/instrumentation/instrumentation_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/mobility/geometry/geometry_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/mobility/micro/constrained_motion_solver.py`:1 reviewed numeric bridge: deterministic quantization bridge
  - `src/process/qc/qc_engine.py`:1 reviewed numeric bridge: deterministic quantization bridge

### noncanonical_serialization_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `87741016f4606271b91047a40b336bc257d71879f565ef6cca168b9ec7a2d19d`

### compiler_flag_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `f1635a71df9a65a6a8f1c907c09c54d9220f01c064730d2887e03111f857be67`

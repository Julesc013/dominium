Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Canon-aligned documentation set tracked by ARCH-AUDIT and REPO-REVIEW-3.

# ARCH Audit Report

- report_id: `arch.audit.v1`
- result: `complete`
- release_status: `pass`
- blocking_finding_count: `0`
- known_exception_count: `9`
- deterministic_fingerprint: `6f64ed2cd508ffd2730e13cea445bada9692b25eac1a19a32c50125b37a1da29`

## Checks

### truth_purity_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `d9955ba99c9b2c78cf763af8552faa9300e92e0e7c409d9a328256fe25564c36`

### renderer_truth_access_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `988bab154d3c9918567835737b8597983a00cc95fc5790a31b072cc48f93573d`

### duplicate_semantics_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `3fb7717bc4126a41b744a693d92416226436c0337454fb9bce7c16415ba15f22`

### determinism_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `f6108ee1304de2d6d76f9d8bb6dec6bce8670e952d2b8133b965e0ab33a71f3d`

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
- deterministic_fingerprint: `f3c96e99f71c95043373ef0a43f21ca1d308305e34bb4104f1afb26376d8dd87`

### parallel_truth_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `c82d32f624e432b63da9236786dfcee9c64718f1440beeeb158aa7b962ac91f6`

### parallel_output_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `d93a6696ec19ca4bd9b91246b988d6deeb6f66aaca49b24bb42a10d05a204e1a`

### truth_atomic_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `7af13f74d24a495e1846ca565cc17d88377987e080f79332e6022b81cac87196`

### stability_marker_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `1e501d20cbfb0622d48211ee9a01debb8e674f9eed2dd6b7fd0a15b9b274575a`

### contract_pin_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `a7c536eb1111df1e8cdf915046b2f17f02fff8d6f89e7198abda93ef2e54a9c3`

### pack_compat_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `bbefa5521bb743d8c6c47618803c3fc2fce4c745b0ec5ee064a0c6b25b91af65`

### dist_bundle_composition_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `1646c02e8ce4b9fcd0b67cbc1f912d8112195756d9e21d20f70d4c058da83a2d`

### update_model_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `5648849dd09ffe6efc8b88ac3185ec215091c242985546335740961e22625768`

### trust_bypass_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `67e77c691770441af5e92931a1d5bab649bd70c32bc3dee0d82f22da5c6ef70b`

### target_matrix_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `c41773a75675b689c709cf6b069e7c582d16afd11ad05ef0106f4a59a7ac8a97`

### archive_determinism_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `786b3dece0792f7cc81d4cac9da7a7645ee673eeb2ee9fde7165c12e8ac8b620`

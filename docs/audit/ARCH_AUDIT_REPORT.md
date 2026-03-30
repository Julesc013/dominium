Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Canon-aligned documentation set tracked by ARCH-AUDIT and REPO-REVIEW-3.

# ARCH Audit Report

- report_id: `arch.audit.v1`
- result: `complete`
- release_status: `pass`
- blocking_finding_count: `0`
- known_exception_count: `9`
- deterministic_fingerprint: `6e00e1c3f3084103703b16e65ad5eb99fd8992ff0c77cd1fdfa779cd64c09172`

## Checks

### truth_purity_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `2b14a64ebdc3e1ecd7e1396ae5ed119b500059a1418ea351ccb37f44d5e4eb40`

### renderer_truth_access_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `53517c67595d900023b19f60ad6e2b4a51fb0e1363205896a9d2b7c62e45af9b`

### duplicate_semantics_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `265470d3f7b38e9e356d56049dcceb4faa9ff60e10fe8f125d654c0d460872ef`

### determinism_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `f0930a345be7b80c2cdecc76bdb70fdd21a89d723e3e1efff237dd2f43158b7b`

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

### worldgen_lock_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `a997aef6bc642704c80382c06446d252f0d92fd0d69593de8d973830b2f8b115`

### baseline_universe_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `2d9eaed0a3eed22ce2ce6c5d6963df790bb42d0f7ae1a0077b9ca0f7651d3a05`

### gameplay_loop_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `2260f31f266206435145932b03e0c043c03ddadc34f461b51b39df666563d8c4`

### disaster_suite_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `5dcdade89acc202c9c9524de8581d141b8003f12a0de56b06ba7b458e7a7f3d7`

### ecosystem_verify_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `c3bf1445a317f264223dae9c6fcd8fc636847e7b41c41a5e908f1470fe357301`

### update_sim_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `27b043f9e59a8538e57c8cba0ba0b33aaed806aa5c2e590f2e33d66d177ada45`

### trust_strict_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `26d08917f2a0e723350f32891b19db03b396d55586f95b087fdc4acaaaa30337`

### offline_archive_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `9c21727d7571134a8d565874c1440907123b157110a5366fb41e7aad7c04be99`

### toolchain_matrix_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `ed2d3d51957f44ffb3136290f1311c663c3638b7621fdb3433d67f546d70ef00`

### dist_final_plan_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `5185f468b362074e9dd12806c2e0557756d820ee965a782e86b0dc48b38a0a70`

### noncanonical_serialization_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `d234cf3d22b0f7b9c93e838e23671708707c7e218c20dfb77411566a9b0769c0`

### compiler_flag_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `77e74002e733bd59d601f118f569318cdff0f6b76dd99d013c3711be17ba0a17`

### parallel_truth_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `0fe26164bd7fecb7711c38e05aafdb5930d5cac456705905633c58e8363683c6`

### parallel_output_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `079a16e4b94ae1ebc6d3f4e3bed9f128c01fa61e0992d12f08a9d180d049ebe5`

### truth_atomic_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `8517da365406599b2a5c1d7a6be3cac10d7227cf82dbef65b7507f001cfab76f`

### stability_marker_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `8840751109571c243e3791c4a415c9d3fd19ff4668f59c258fcaf4bfb5b0fe2f`

### contract_pin_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `2cb1da670c5dbee45932c5d7bbc22b6975cefaa82d72c5bcc967baea3e58b78b`

### pack_compat_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `dc40f51647fb2ac2ff4fe9994a07d52ad10b5e4255a9a050f8d1e09acaa447b1`

### dist_bundle_composition_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `1646c02e8ce4b9fcd0b67cbc1f912d8112195756d9e21d20f70d4c058da83a2d`

### update_model_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `5ee8a20f6c7a21bf2c68be84a7bce24fedb6d477c22f115ebad5de6e9668af69`

### trust_bypass_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `969d9249ae289c459be56cf51715933daa45203d142b40d2696b25e34de811c5`

### target_matrix_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `613106507a4bd90f802385a2bc9b54da52f5f0fcab79ed2e82f3bcc3801d8847`

### archive_determinism_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `007657a8b474f032efc1c42ac3fb2edcfdc31c145a57862519526b7f8a8da28a`

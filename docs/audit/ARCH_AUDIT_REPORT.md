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
- deterministic_fingerprint: `0361a57da5f8e5e929ce4b6a528b4bff1442f8e436dd6d0b3c2ed2610713811b`

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
- deterministic_fingerprint: `d2e828cb789392e4cae9044822b164fc3a814a25311e4c5bc98fd6b8c5cd1247`

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

### worldgen_lock_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `907a5f66f846b736b6f187f5a3edc981b0d48fe6e8ba148605c0cb9010d34bb6`

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
- deterministic_fingerprint: `8324082700520c3acb7a168d1f3bd175eff42a56d6e2f35d64c9f4d889e1c176`

### update_sim_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `059b2be6a3277b588a28645833f4eab66148268a047e0429e43d602310a4c267`

### trust_strict_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `da19a9f1f375cbf1e30f89371b01d9e61282c372b95f7e9a998b45a043cf70f8`

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
- deterministic_fingerprint: `181c41d2978b084ed0091c554a11467038d28673d00f48ca2ed23d7afc20ce4d`

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

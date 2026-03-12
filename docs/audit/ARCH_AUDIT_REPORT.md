# ARCH Audit Report

- report_id: `arch.audit.v1`
- result: `complete`
- release_status: `pass`
- blocking_finding_count: `0`
- known_exception_count: `12`
- deterministic_fingerprint: `f857f4fa98b395e3508adb8b9d481e1d1cd2ffc2f3c53a536475f7f9c0b2d429`

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
- deterministic_fingerprint: `f5db984c0d2fc4d8d85c99bef8e61fdf1398fdff612997d8506fa6ecdb93736b`

### determinism_scan
- result: `known_exception`
- blocking_finding_count: `0`
- known_exception_count: `12`
- deterministic_fingerprint: `6e1d8704b2627acba0f1daa0c046904341e6b287f871bfed2a3f932d573c7596`
- known exceptions:
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

### stability_marker_scan
- result: `pass`
- blocking_finding_count: `0`
- known_exception_count: `0`
- deterministic_fingerprint: `e232abdce81b77e8f4d85ac03b3095e03eee9d764596427c8a9bcda290912b15`

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

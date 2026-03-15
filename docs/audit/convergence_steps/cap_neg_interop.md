Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for cap_neg_interop

# Convergence Step - CAP-NEG-4 interop stress

- step_no: `5`
- step_id: `cap_neg_interop`
- result: `complete`
- rule_id: `INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `e7533572d237391ab9508e03eccf7cc9f0dbf74de190ee43254fa5a8e69b65d8`
- observed_refusal_count: `2`
- observed_degrade_count: `0`

## Key Hashes

- baseline_fingerprint: `00cd5f6e84587559e7b7678c21d1cc3ae1b476fd2d70bf9e2ef6fd07ee55ec40`
- matrix_fingerprint: `64f7385dd55163a7ca8dd3a15a2ad5da5b799b6ab3168adab33434c140ed85ec`
- replay_fingerprint: `e3bf42ba50975ea8afe03d91da7d5bf4c19e016654b3560848a73ae1e344d31c`
- stress_report_fingerprint: `e7533572d237391ab9508e03eccf7cc9f0dbf74de190ee43254fa5a8e69b65d8`

## Notes

- baseline_match=True
- mode_counts_hash=631f854f1b566828907887852b015336233389ea7ce03fccfb0463fb856a02e5

## Source Paths

- `build/cap_neg/interop_matrix.json`
- `build/cap_neg/interop_stress.json`
- `data/regression/cap_neg_full_baseline.json`

## Remediation

- module=`tools/compat/tool_run_interop_stress.py` rule=`INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/compat/tool_run_interop_stress.py --repo-root .`

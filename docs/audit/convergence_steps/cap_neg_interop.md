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
- source_fingerprint: `4adc0e3471b8c69206bbb5907c0adf3c54561531e0efccc90eb4c16da41b8a3f`
- observed_refusal_count: `2`
- observed_degrade_count: `0`

## Key Hashes

- baseline_fingerprint: `00cd5f6e84587559e7b7678c21d1cc3ae1b476fd2d70bf9e2ef6fd07ee55ec40`
- matrix_fingerprint: `64f7385dd55163a7ca8dd3a15a2ad5da5b799b6ab3168adab33434c140ed85ec`
- replay_fingerprint: `e052030d97348c7de07df51b35ad6920a9ec3064da19d3e5b24ef5bf64563346`
- stress_report_fingerprint: `4adc0e3471b8c69206bbb5907c0adf3c54561531e0efccc90eb4c16da41b8a3f`

## Notes

- baseline_match=True
- mode_counts_hash=631f854f1b566828907887852b015336233389ea7ce03fccfb0463fb856a02e5

## Source Paths

- `build/cap_neg/interop_matrix.json`
- `build/cap_neg/interop_stress.json`
- `data/regression/cap_neg_full_baseline.json`

## Remediation

- module=`tools/compat/tool_run_interop_stress.py` rule=`INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/compat/tool_run_interop_stress.py --repo-root .`

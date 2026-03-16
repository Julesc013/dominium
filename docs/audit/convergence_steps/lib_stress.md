Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for lib_stress

# Convergence Step - LIB-7 stress

- step_no: `7`
- step_id: `lib_stress`
- result: `complete`
- rule_id: `INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `4f0a0d8617a9e689f4bc37a9160adc1c15f8885f85a7f40afbfe7d883ab5d9cf`
- observed_refusal_count: `6`
- observed_degrade_count: `0`

## Key Hashes

- baseline_fingerprint: `07a1dc392b0139d09175f27ec5eb0bdc903020519b77cadbe1b8d9dae89c54ae`
- bundle_hashes: `8631db495ca297fdb48bb0af00d7c9d04d753e0c1b3a616a4384aa252562f4ec`
- lib_stress_fingerprint: `4f0a0d8617a9e689f4bc37a9160adc1c15f8885f85a7f40afbfe7d883ab5d9cf`

## Notes

- baseline_match=True
- stable_across_repeated_runs=True

## Source Paths

- `build/lib/lib_stress_report.json`
- `data/regression/lib_full_baseline.json`

## Remediation

- module=`tools/lib/tool_run_lib_stress.py` rule=`INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/lib/tool_run_lib_stress.py --repo-root . --out-root build/tmp/convergence/lib_stress_workspace`

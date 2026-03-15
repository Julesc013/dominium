Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for pack_compat_stress

# Convergence Step - PACK-COMPAT verification stress

- step_no: `6`
- step_id: `pack_compat_stress`
- result: `complete`
- rule_id: `INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `1492bb902ea2d6c88716b83b6b88d9e536e13a1ac3fdda132a4cba9f194c4503`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- pack_compat_report_fingerprint: `1492bb902ea2d6c88716b83b6b88d9e536e13a1ac3fdda132a4cba9f194c4503`
- pack_lock_hashes: `e1aaac94ce7b106cbbcec74ecb1b8b1d5ba7260490f2155acd4208e38c149ad0`

## Notes

- all_sets_valid=True
- all_sets_stable=True

## Source Paths

- none

## Remediation

- module=`tools/mvp/tool_run_all_stress.py` rule=`INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/mvp/tool_run_all_stress.py --repo-root .`

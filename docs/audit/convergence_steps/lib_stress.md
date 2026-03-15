Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for lib_stress

# Convergence Step - LIB-7 stress

- step_no: `7`
- step_id: `lib_stress`
- result: `complete`
- rule_id: `INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `a5dc843fd94ff231f8e1ed6a324f276b5dfc064b9c6bf54dadb332a8291aa570`
- observed_refusal_count: `6`
- observed_degrade_count: `0`

## Key Hashes

- baseline_fingerprint: `d8570a43396899349e55016ebd50c8ce63915bf48c7aa6ee06c4da3e1aef73a4`
- bundle_hashes: `14203ec813af61b20bed522a18ad8d4377236ce5841261d875803c870cf51ff5`
- lib_stress_fingerprint: `a5dc843fd94ff231f8e1ed6a324f276b5dfc064b9c6bf54dadb332a8291aa570`

## Notes

- baseline_match=True
- stable_across_repeated_runs=True

## Source Paths

- `build/lib/lib_stress_report.json`
- `data/regression/lib_full_baseline.json`

## Remediation

- module=`tools/lib/tool_run_lib_stress.py` rule=`INV-CONVERGENCE-GATE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/lib/tool_run_lib_stress.py --repo-root . --out-root build/tmp/convergence/lib_stress_workspace`

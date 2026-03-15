Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for mvp_stress

# Convergence Step - MVP-GATE-1 stress suite

- step_no: `12`
- step_id: `mvp_stress`
- result: `complete`
- rule_id: `INV-MVP-STRESS-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `695e55a7d76ba81153c168a7cf3dc46667c3d2bc55a088a75f4335c3f3a28f2e`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- contract_bundle_hash: ``
- proof_anchor_hashes: `c4384fc73e6d04c913b9b319e146533e3920711ec2b7f6c3f7e3193f66498fc0`
- stress_proof_fingerprint: `373015c9f79018b7ed233f58a676df22bd7f112ede8aa72b28540c6e571bd2cc`
- stress_report_fingerprint: `695e55a7d76ba81153c168a7cf3dc46667c3d2bc55a088a75f4335c3f3a28f2e`

## Notes

- baseline_match=True
- proof_result=complete

## Source Paths

- `build/mvp/mvp_stress_proof_report.json`
- `build/mvp/mvp_stress_report.json`
- `data/regression/mvp_stress_baseline.json`
- `docs/audit/MVP_STRESS_FINAL.md`

## Remediation

- module=`tools/mvp/tool_run_all_stress.py` rule=`INV-MVP-STRESS-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/mvp/tool_run_all_stress.py --repo-root .`

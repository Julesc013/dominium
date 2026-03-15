Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for mvp_smoke

# Convergence Step - MVP-GATE-0 smoke suite

- step_no: `11`
- step_id: `mvp_smoke`
- result: `complete`
- rule_id: `INV-MVP-SMOKE-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `bfb1b59e3417eef6b763f9c8cce56037ee97d8c0fdf691e00ed592474b3b8f43`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- contract_bundle_hash: ``
- negotiation_record_hash: `43f466bfbc5904a4280d6c6da867cc53a2dd56f92f233e042df360f4548c438b`
- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- proof_anchor_hash: `b8ef9a775383fd80c6d594348bc99c7354ac2663df6fdc8af1aa2e4d5c0e55da`
- repro_bundle_hash: `a58f261dc8d58b6200e004a509f26f6a16c460689323dbab96598efcdb4c010f`

## Notes

- baseline_match=True
- expected_hashes_match=True

## Source Paths

- `build/mvp/mvp_smoke_report.json`
- `data/regression/mvp_smoke_baseline.json`
- `docs/audit/MVP_SMOKE_FINAL.md`

## Remediation

- module=`tools/mvp/tool_run_mvp_smoke.py` rule=`INV-MVP-SMOKE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/mvp/tool_run_mvp_smoke.py --repo-root .`

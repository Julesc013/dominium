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
- source_fingerprint: `4731aca275640e24cc9e9a5403bfb4068ab403469517395993d6a344b2926758`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- contract_bundle_hash: ``
- negotiation_record_hash: `6cf409c5e07fe4fac5e2d30e3df91bca589e718d8838e00f00e4508143dd53f7`
- pack_lock_hash: `45bf16251b647cca6133e3ad4c88f62b4984ed01fed858491b798bcc4dfc4208`
- proof_anchor_hash: `b8ef9a775383fd80c6d594348bc99c7354ac2663df6fdc8af1aa2e4d5c0e55da`
- repro_bundle_hash: `d4482ad0925532635dadde0a7e2cb87e3588e4def8a0eee1363860e8150cb8dc`

## Notes

- baseline_match=True
- expected_hashes_match=True

## Source Paths

- `build/mvp/mvp_smoke_report.json`
- `data/regression/mvp_smoke_baseline.json`
- `docs/audit/MVP_SMOKE_FINAL.md`

## Remediation

- module=`tools/mvp/tool_run_mvp_smoke.py` rule=`INV-MVP-SMOKE-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/mvp/tool_run_mvp_smoke.py --repo-root .`

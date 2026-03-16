Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for time_anchor

# Convergence Step - TIME-ANCHOR verifier

- step_no: `3`
- step_id: `time_anchor`
- result: `complete`
- rule_id: `INV-TICK-TYPE-64BIT-ENFORCED`
- source_fingerprint: `bd9ee2ea4ebd3aad16ac4077718cdf14e89549ec13d90bd9490a1df0a8c6ba01`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- compaction_report_fingerprint: `24e2fe1ff585d4a3f0347fe7904165dbf83ed4309e09668d404ce2736d5cf70b`
- cross_platform_anchor_hash: `65ce8e65bc3567c2539b259086e5fac9e1f19fc4473e308aa51755deccd095d3`
- interval_anchor_hash: `169f57450be93f1ca91813a3a075d0f370bdea8fc6325fe03585385e7185fda7`
- verify_report_fingerprint: `2caa56dff92ab340a288111a94c30ec18178a32c04fddcd9a939224fe2eef153`

## Notes

- verify_result=complete
- compaction_result=complete

## Source Paths

- `build/time/time_anchor_compaction_report.json`
- `build/time/time_anchor_verify_report.json`

## Remediation

- module=`tools/time/tool_verify_longrun_ticks.py` rule=`INV-TICK-TYPE-64BIT-ENFORCED` refusal=`none` command=`python tools/time/tool_verify_longrun_ticks.py --repo-root .`

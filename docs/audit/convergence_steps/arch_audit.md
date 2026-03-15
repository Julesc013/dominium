Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for arch_audit

# Convergence Step - ARCH-AUDIT tool

- step_no: `4`
- step_id: `arch_audit`
- result: `complete`
- rule_id: `INV-ARCH-AUDIT-MUST-PASS-BEFORE-RELEASE`
- source_fingerprint: `6f64ed2cd508ffd2730e13cea445bada9692b25eac1a19a32c50125b37a1da29`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- arch_audit2_fingerprint: `53c7714c995fc1d04033b35d811fb8e7e0b6a08103fabb5051f75280a63aa43d`
- arch_audit_fingerprint: `6f64ed2cd508ffd2730e13cea445bada9692b25eac1a19a32c50125b37a1da29`
- blocking_findings_hash: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

## Notes

- blocking_finding_count=0
- known_exception_count=9
- arch_audit2_blocking_finding_count=0

## Source Paths

- `data/audit/arch_audit2_report.json`
- `data/audit/arch_audit_report.json`
- `docs/audit/ARCH_AUDIT2_FINAL.md`
- `docs/audit/ARCH_AUDIT2_REPORT.md`
- `docs/audit/ARCH_AUDIT_REPORT.md`

## Remediation

- module=`tools/audit/tool_run_arch_audit.py` rule=`INV-ARCH-AUDIT-MUST-PASS-BEFORE-RELEASE` refusal=`none` command=`python tools/audit/tool_run_arch_audit.py --repo-root . --report-path docs/audit/ARCH_AUDIT_REPORT.md --json-path data/audit/arch_audit_report.json`

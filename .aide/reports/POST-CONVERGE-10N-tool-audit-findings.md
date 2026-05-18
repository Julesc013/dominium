# POST-CONVERGE-10N Tool/Audit Findings

Status: DERIVED
Last Reviewed: 2026-05-17

## Summary

POST-CONVERGE-10N checked 8 tool/audit related RepoX findings: 3 hard failures and 5 warnings.

| Finding | Classification | Disposition |
| --- | --- | --- |
| `INV-TOOL-VERSION-MISMATCH` for `tools/xstack/compatx/compatx.py` and `tools/xstack/securex/securex.py` | `stale_tool_hash_safe_refresh` | Fixed by regenerating `docs/audit/security/INTEGRITY_MANIFEST.json` with SecureX. |
| `INV-IDENTITY-FINGERPRINT` | `stale_audit_manifest_safe_refresh` | Fixed by regenerating `docs/audit/identity_fingerprint.json`. |
| RepoX group cache stale evidence reuse | `rule_false_positive` | Fixed by adding explicit docs/audit evidence dependencies to affected RepoX groups. |
| `INV-AUDITX-OUTPUT-STALE` | `unknown` | Deferred; broad AuditX refresh is out of scope. |
| Four `WARN-GLOSSARY-TERM-CANON` warnings in audit/remediation evidence | `generated_tracked_output_stale` | Deferred; historical/generated evidence was preserved. |

## Safe Fixes

- `docs/audit/identity_fingerprint.json`: refreshed with `python tools/ci/tool_identity_fingerprint.py --repo-root . --output docs/audit/identity_fingerprint.json`.
- `docs/audit/security/INTEGRITY_MANIFEST.json`: refreshed with `python tools/xstack/securex/securex.py integrity-manifest --repo-root . --output docs/audit/security/INTEGRITY_MANIFEST.json`.
- `scripts/ci/check_repox_rules.py`: added direct evidence dependencies for `docs/audit/**` artifacts read by cached groups.

## Deferred

- AuditX output freshness remains a warning because the tracked findings artifact is 199 commits behind HEAD.
- Generated audit/remediation markdown warnings remain because hand rewriting generated or historical evidence is not a safe 10N fix.

# Dominium AIDE Capability Matrix

Status: PARTIAL_BASELINE_NEEDS_REPAIR

See detailed matrix: `.aide/queue/DOMINIUM-AIDE-OPERATING-BASELINE-01/evidence/capability-matrix.md`

Summary:

- Core AIDE commands: doctor/validate/test/selftest PASS under Python 3.14.
- Repo/quality/root/tool/install/repair/upgrade/rollback/uninstall planning commands: PASS.
- XStack integration commands: `xstack status`, `xstack wrap-plan`, and `xstack validate` PASS with legacy execution disabled.
- Git policy and commit checking: PASS.
- Git commit write: BLOCKED by sandbox `.git/index.lock` permission.
- Full eval: deferred timeout warning.
- Unsupported: default Python 3.8 path for current AIDE write helpers.

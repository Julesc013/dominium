# Latest Warning Disposition

## Accepted Warnings

- POST-CONVERGE-10G is PARTIAL because focused tuple `inv_repox_rules` still fails with 1769 failures and 5 warnings.
- Canonical `ctest --preset verify -N` still discovers 0 tests; tuple verify remains the effective focused CTest lane.
- Full CTest wall-time remains unproven while focused RepoX still fails.
- The remaining RepoX warning set is unchanged: one stale AuditX output warning and four glossary-term warnings in historical audit/remediation evidence.
- Move planning and move application remain unauthorized.

## Cleared Warnings / Reduced Blockers

- RepoX no longer uses stale root-level `appshell/` source paths for current AppShell checks.
- RepoX top-level root checks now consume the root allowlist and active layout exceptions instead of only the legacy intent document.
- RepoX group cache now invalidates when `scripts/ci/check_repox_rules.py` changes.
- `INV-REPOX-STRUCTURE` is no longer present in the direct after-run failure counts.
- `INV-OFFLINE-BOOT-OK` is no longer present in the direct after-run failure counts.

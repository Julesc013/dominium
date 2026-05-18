Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Post-Restructure Repair Semantic Lints

## Status

Result: PASS_WITH_WARNINGS.

The remaining semantic lint CTest blockers from RESTRUCTURE-REPAIR-00 and TEST-PERF-01 now pass:

- `slice0_hardcoded_ids`
- `slice1_hardcoded_constants`

## Scope

This task addressed only hardcoded identifier and hardcoded constant disposition. It did not move files, retire root exceptions, implement features, alter product/runtime/game behavior, or run release generation.

## Reproduction

Both tests were reproduced before repair:

- `slice0_hardcoded_ids`: failed with 1,059 hardcoded identifier findings.
- `slice1_hardcoded_constants`: failed with 45 hardcoded constant/vocabulary findings.

Total findings captured: 1,104.

## Disposition

| Disposition | Count |
| --- | ---: |
| `preserve_doctrine_constant` | 213 |
| `preserve_fixture_literal` | 582 |
| `preserve_protocol_literal` | 264 |
| `preserve_schema_literal` | 45 |

No findings remain unknown or unclassified.

## Fixes Applied

- Added `tests/app/semantic_lint_common.py` for exact-match allowlist loading.
- Updated `tests/app/slice0_hardcoded_ids.py` and `tests/app/slice1_hardcoded_constants.py` to honor exact allowlist entries only.
- Added `contracts/repo/semantic_lint_allowlist.json`.
- Added `contracts/repo/semantic_lint_allowlist.schema.json`.
- Added semantic lint disposition docs and AIDE evidence reports.

No source product behavior changed.

## Allowlist Policy

The allowlist is intentionally narrow. It matches:

- `test_name`
- `file`
- `line`
- `validator_message`
- source-line `context_sha256`

No wildcard path, directory-wide, docs-wide, or message-wide suppressions were added.

## Validation Summary

Focused semantic lint validation:

```powershell
ctest --preset verify -R "slice0_hardcoded_ids|slice1_hardcoded_constants" --output-on-failure --timeout 300
```

Result: PASS in 11.01 seconds.

Broader validation is recorded in `.aide/reports/SEMANTIC-LINTS-validation.md`.

## Remaining Blockers

No semantic lint blockers remain.

Root cleanup, exception closure, and full post-restructure proof remain separate tasks.

## Next Readiness

Next task:

`MOVE-SCRIPT-00 - Generate Deterministic Bad-Root Router and Dry-Run Move Plan`

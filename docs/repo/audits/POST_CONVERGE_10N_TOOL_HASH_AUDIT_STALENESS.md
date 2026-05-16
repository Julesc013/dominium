Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# POST-CONVERGE-10N Tool Hash and Audit Staleness Remediation

## Status

- Task ID: POST-CONVERGE-10N
- Result: PARTIAL
- Branch: `main`
- HEAD: `fab604957d04af223a24a353c0bd3c509668010d`
- origin/main: `1def409fc17acfe4061fc3039517d892a4f0afec`
- Worktree before: clean
- Worktree after: scoped RepoX rule/evidence/status changes pending commit

## Scope

This was focused tool hash and audit evidence staleness remediation. It applied no root moves, no file moves, no deletes, no renames, no path aliases, no layout exception retirement, no product proof, no portable projection proof, no package proof, no release generation, and no product/runtime source behavior changes.

## Prior State

POST-CONVERGE-10M left focused RepoX at 23 failures and 5 warnings. The remaining targetable 10N failures were:

- `INV-IDENTITY-FINGERPRINT`: stale `docs/audit/identity_fingerprint.json`.
- `INV-TOOL-VERSION-MISMATCH`: stale SecureX integrity manifest hashes for `tools/compatx/compatx.py` and `tools/securex/securex.py`.
- `INV-AUDITX-OUTPUT-STALE`: warning that AuditX findings lag HEAD by 199 commits.
- four glossary warnings in generated or historical audit evidence.

## Reproduction

| Command | Result | Failures | Warnings | Notes |
| --- | --- | ---: | ---: | --- |
| `ctest --preset verify -N` | PASS | 0 | 0 | Canonical verify discovery reports 493 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` before | FAIL_EXPECTED | 23 | 5 | Baseline from POST-CONVERGE-10M. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` after | FAIL_EXPECTED | 20 | 5 | Identity and tool-hash failures fixed. |
| `python scripts/ci/check_repox_rules.py --repo-root .` | FAIL_EXPECTED | 20 | 5 | Refreshed tracked RepoX proof/profile evidence after the cache dependency fix. |

## Tool/Audit Findings

| Family | Count | Classification | Disposition |
| --- | ---: | --- | --- |
| Stale identity fingerprint | 1 | `stale_audit_manifest_safe_refresh` | Fixed with the canonical identity fingerprint generator. |
| Stale SecureX tool hashes | 2 | `stale_tool_hash_safe_refresh` | Fixed with the canonical SecureX integrity manifest generator. |
| RepoX cache skipped docs/audit evidence dependencies | 0 | `rule_false_positive` | Fixed by adding explicit evidence dependencies for cached groups that read docs/audit artifacts. |
| AuditX output stale warning | 1 warning | `unknown` | Deferred; broad AuditX output regeneration is out of scope. |
| Audit/remediation glossary warnings | 4 warnings | `generated_tracked_output_stale` | Deferred; historical/generated evidence was preserved. |

## Changes Made

- Refreshed `docs/audit/identity_fingerprint.json` with `tools/ci/tool_identity_fingerprint.py`.
- Refreshed `docs/audit/security/INTEGRITY_MANIFEST.json` with `tools/securex/securex.py integrity-manifest`.
- Updated `scripts/ci/check_repox_rules.py` so `repox.docs.canon` and `repox.schema.compat` cache keys explicitly include tracked docs/audit evidence files they read.
- Refreshed tracked RepoX proof/profile evidence after the focused run.
- Added POST-CONVERGE-10N AIDE reports and audit evidence.
- Updated post-converge status docs and latest AIDE packets.

## Before/After

| Metric | Before | After |
| --- | ---: | ---: |
| Focused RepoX failures | 23 | 20 |
| Focused RepoX warnings | 5 | 5 |
| Identity fingerprint failures | 1 | 0 |
| Tool version mismatch failures | 2 | 0 |
| AuditX stale-output warnings | 1 | 1 |
| Audit glossary warnings | 4 | 4 |

## Remaining Blockers

- Distribution/product proof blockers: 12 failures.
- Current `game.domains.embodiment` lazy import blocker: 2 failures.
- Ruleset mapping gaps: 2 failures.
- Canon superseded doc, extension registry gap, worldgen retry-loop policy, and shadow-bound policy failures: 4 failures.
- AuditX stale-output warning plus four glossary warnings in generated/historical audit evidence.

## POST-CONVERGE-11 Readiness

POST-CONVERGE-11 is not ready. Product/projection proof failures should not circularly block POST-CONVERGE-11 on their own, but focused RepoX still contains real non-proof governance and source-policy failures.

## Validation

- `ctest --preset verify -N`: PASS, 493 tests discovered.
- `ctest --preset verify -R inv_repox_rules --output-on-failure`: FAIL_EXPECTED, 20 failures / 5 warnings after safe fixes.
- `python tools/ci/tool_identity_fingerprint.py --repo-root . --check`: PASS.
- `python tools/securex/securex.py integrity-manifest --repo-root . --output .dominium.local/securex-integrity-10n-after.json` plus `git diff --no-index`: PASS.
- `py -3 .aide/scripts/aide_lite.py commit check --latest` after initial 10N commit `e80dc704c`: FAIL due changelog category prefix formatting; recorded without amend in a follow-up evidence commit.
- Final command details are recorded in `.aide/reports/POST-CONVERGE-10N-validation.md`.

## POST-CONVERGE-10O Follow-up

POST-CONVERGE-10O reproduced focused RepoX at 20 failures / 5 warnings and classified the closeout gate as `real_governance_blocker`. POST-CONVERGE-11 remains blocked because non-proof governance/source-policy failures remain after the 10N tool/audit evidence fixes.

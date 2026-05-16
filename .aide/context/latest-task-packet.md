# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10G - RepoX Rule and Canonical Evidence Drift Remediation

## GOAL

Reduce or classify the remaining focused `inv_repox_rules` blocker without weakening RepoX or starting product proof.

## WHY

POST-CONVERGE-10F fixed `invariant_units_present` but left RepoX as the focused semantic blocker. POST-CONVERGE-10G reduces safe stale-path and cache-dependency drift, then records the remaining RepoX families honestly.

## CURRENT RESULT

PARTIAL. RepoX was reduced from 1844 failures and 5 warnings to 1769 failures and 5 warnings. POST-CONVERGE-11 remains blocked.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/reports/POST-CONVERGE-10F-repox-findings.json`
- `.aide/reports/POST-CONVERGE-10G-repox-failure-families.json`
- `docs/repo/audits/POST_CONVERGE_10G_REPOX_DRIFT_REMEDIATION.md`

## ALLOWED_PATHS

- `scripts/ci/check_repox_rules.py`
- `.aide/reports/**`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/ledgers/migration_ledger.jsonl`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/FAST_GATE_REMEDIATION.md`
- `docs/repo/BUILD_VERIFICATION_PATHS.md`
- `docs/release/NATIVE_BINARY_PROOF.md`

## FORBIDDEN_PATHS

- product/runtime/engine/game/source behavior changes beyond the scoped RepoX rule implementation
- root moves, deletes, renames, active aliases, move maps, salvage maps, or exception retirement
- product boot proof, package proof, release proof, portable projection proof, full eval, or full CTest
- generated local/cache/build outputs

## IMPLEMENTATION

- Preserve POST-CONVERGE-10F and AIDE root/move evidence.
- Fix only safe RepoX stale path/root assumptions and stale rule-cache dependency behavior.
- Keep real RepoX failures blocking.
- Record before/after counts and remaining families.

## VALIDATION

- `ctest --preset verify -N`
- `ctest --preset verify -R inv_repox_rules --output-on-failure`
- `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE.json`
- `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure`
- AIDE doctor/validate/test/selftest/tools/roots/repo/commit checks
- strict repo/root/distribution/component validators
- docs/build/UI/ABI validators
- JSON parsing and git diff checks

## EVIDENCE

- `.aide/reports/POST-CONVERGE-10G-status.md`
- `.aide/reports/POST-CONVERGE-10G-validation.md`
- `.aide/reports/POST-CONVERGE-10G-blockers.md`
- `.aide/reports/POST-CONVERGE-10G-repox-failure-families.md`
- `.aide/reports/POST-CONVERGE-10G-repox-failure-families.json`
- `.aide/reports/POST-CONVERGE-10G-repox-before-after.json`
- `.aide/reports/POST-CONVERGE-10G-product-boot-readiness.md`
- `docs/repo/audits/POST_CONVERGE_10G_REPOX_DRIFT_REMEDIATION.md`

## NON_GOALS

No root moves, deletes, renames, move maps, salvage maps, path aliases, product boot proof, package proof, release proof, full CTest, or feature work.

## ACCEPTANCE

- Safe RepoX drift is fixed without weakening rules.
- Remaining RepoX failures are grouped and left blocking.
- POST-CONVERGE-11 readiness is explicitly decided.
- Validation commands and known warnings are recorded.
- No generated local/cache/build files are committed.

## OUTPUT_SCHEMA

Return branch, HEAD before/after, origin/main, focused RepoX before/after, fixed and remaining families, files changed, validation results, readiness for POST-CONVERGE-11, known warnings, commit status, worktree status, and next task.

## TOKEN_ESTIMATE

- method: concise packet by evidence refs
- approx_tokens: 950
- budget_status: PASS
- warnings:
  - focused RepoX remains blocking

## NEXT

Recommended next task: `POST-CONVERGE-10H - Canonical Documentation Status and Canon Index Remediation`.

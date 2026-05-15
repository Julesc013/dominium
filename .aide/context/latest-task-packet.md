# AIDE Latest Task Packet

## PHASE

AIDE-GREEN-PASS - final warning and blocker cleanup before move planning

## GOAL

Clear remaining AIDE warnings and blockers from the root-recycling readiness
work, refresh local AIDE evidence, and keep move application unauthorized.

## WHY

The root recycling and readiness gates should enter the next user-requested
change from a clean local AIDE validation baseline. This task fixes concrete
AIDE metadata, classifier, controller, export-pack, and release-fixture gaps
without moving files or changing product/runtime behavior.

## CONTEXT_REFS

- `.aide/reports/AIDE-POLISH-02-root-readiness-second-pass.md`
- `.aide/reports/AIDE-GATE-01-root-move-planning-readiness.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/roots/AIDE-ROOT-06-reconciliation.md`
- `.aide/repo/latest-repo-intelligence.md`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/release/latest-release-validation.md`
- `docs/reference/`

## ALLOWED_PATHS

- `.aide/context/**`
- `.aide/controller/**`
- `.aide/evals/**`
- `.aide/export/**`
- `.aide/import/**`
- `.aide/models/**`
- `.aide/policies/**`
- `.aide/release/**`
- `.aide/repo/**`
- `.aide/reports/**`
- `.aide/rollback/**`
- `.aide/scripts/aide_lite.py`
- `.aide/uninstall/**`
- `.aide/verification/**`
- `docs/reference/**`
- `tools/validators/check_repo_layout.py`
- `tools/validators/check_root_allowlist.py`

## FORBIDDEN_PATHS

- `.git/**`
- `.aide.local/**`
- `.env`
- `secrets/**`
- `apps/**`
- `engine/**`
- `game/**`
- `runtime/**`
- `content/**`
- `tests/**`
- `cmake/**`
- `release/*`
- product/version root files
- root move, delete, rename, reference rewrite, path alias activation, salvage
  application, or move-map application

## IMPLEMENTATION

- Patch only AIDE metadata, AIDE validation helpers, generated AIDE evidence,
  portable AIDE reference docs, no-publish AIDE release fixtures, and warning
  cleanup in read-only repo layout validators.
- Preserve all no-apply root recycling invariants.
- Do not change Dominium product/source/runtime/build behavior.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py repo validate`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify --changed-files`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- strict repo/root/distribution/component validators
- docs/build/UI/ABI supplemental checks
- `git diff --check`
- `git diff --cached --check`

## EVIDENCE

- `.aide/verification/latest-verification-report.md`
- `.aide/context/latest-review-packet.md`
- `.aide/controller/latest-outcome-report.md`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/reports/token-savings-summary.md`

## NON_GOALS

- No root moves, deletes, renames, salvage-map application, move-map
  application, path alias activation, or reference rewrites.
- No product/runtime/source/build behavior changes.

## ACCEPTANCE

- AIDE doctor, validate, test, selftest, repo validate, eval, verify,
  review-pack, ledger, outcome, and commit checks pass without warnings.
- Strict repo/root/distribution/component validators and supplemental
  docs/build/UI/ABI checks pass.
- The final commit contains only AIDE evidence/tooling/reference-doc updates
  and preserves move application authorization as false.

## OUTPUT_SCHEMA

- Final response reports branch, before/after HEAD, origin/main, validation
  results, commit, push/sync status, worktree status, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 700
- budget_status: within_budget

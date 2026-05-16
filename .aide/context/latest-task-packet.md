# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10H - Canonical Documentation Status and Canon Index Remediation

## GOAL

Reduce focused `inv_repox_rules` documentation status and canon-index drift without weakening RepoX or altering doctrine.

## WHY

POST-CONVERGE-10G left documentation status headers and canon-index drift as the next safe RepoX families. POST-CONVERGE-10H repairs only clear metadata/index drift and leaves authority-sensitive files deferred.

## CURRENT RESULT

PARTIAL. RepoX was reduced from 1769 failures and 5 warnings to 153 failures and 5 warnings. POST-CONVERGE-11 remains blocked.

## CONTEXT_REFS

- `.aide/reports/POST-CONVERGE-10H-status.md`
- `.aide/reports/POST-CONVERGE-10H-doc-status-findings.json`
- `.aide/reports/POST-CONVERGE-10H-canon-index-findings.json`
- `.aide/reports/POST-CONVERGE-10H-repox-before-after.json`
- `docs/repo/audits/POST_CONVERGE_10H_DOC_STATUS_CANON_INDEX.md`

## ALLOWED_PATHS

- documentation files directly missing or repairing required status headers
- `docs/architecture/CANON_INDEX.md`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/migration_ledger.jsonl`
- post-converge status docs

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- root moves, deletes, renames, aliases, move maps, salvage maps, or exception retirement
- product boot proof, package proof, release proof, portable projection proof, full eval, or full CTest

## IMPLEMENTATION

- Repair only metadata headers for evidence/reference docs with clear DERIVED role.
- Add canon-index entries only for docs that already declared `Status: CANONICAL`.
- Defer ambiguous architecture/runtime/xstack/performance/domain status headers.

## VALIDATION

- focused RepoX direct and tuple CTest
- AIDE doctor/validate/test/selftest/tools/roots/repo/commit checks
- strict repo/root/distribution/component validators
- docs/build/UI/ABI validators
- JSON parse and git diff checks

## EVIDENCE

- `.aide/reports/POST-CONVERGE-10H-*`
- `docs/repo/audits/POST_CONVERGE_10H_DOC_STATUS_CANON_INDEX.md`

## NON_GOALS

No doctrine rewrite, broad docs rewrite, product proof, package proof, release proof, root moves, or feature work.

## ACCEPTANCE

- RepoX doc status and canon-index families are reduced or cleared.
- Remaining failures are classified.
- Product boot readiness is explicitly decided.
- No generated local/cache/build files are committed.

## OUTPUT_SCHEMA

Return branch, HEAD before/after, origin/main, focused RepoX before/after, doc status fixes, canon index fixes, remaining families, validation, readiness, commit, worktree, and next task.

## TOKEN_ESTIMATE

- method: concise packet by evidence refs
- approx_tokens: 800
- budget_status: PASS
- warnings:
  - focused RepoX remains blocking

## NEXT

Recommended next task: `POST-CONVERGE-10I - Historical Reference and Archive Citation Remediation`.

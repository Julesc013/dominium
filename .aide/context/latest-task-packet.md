# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10I - Historical Reference and Archive Citation Remediation

## GOAL

Reduce focused `inv_repox_rules` historical/archive reference debt without weakening RepoX or rewriting audit history.

## WHY

POST-CONVERGE-10H left `INV-CANON-NO-HIST-REF` as the largest focused RepoX family. POST-CONVERGE-10I distinguishes stale current references from legitimate DERIVED quarantine/archive evidence and preserves historical citations.

## CURRENT RESULT

PARTIAL. Focused RepoX was reduced to 71 failures and 5 warnings. `INV-CANON-NO-HIST-REF` was reduced from 81 to 0. POST-CONVERGE-11 remains blocked.

## CONTEXT_REFS

- `.aide/reports/POST-CONVERGE-10I-status.md`
- `.aide/reports/POST-CONVERGE-10I-historical-reference-findings.json`
- `.aide/reports/POST-CONVERGE-10I-repox-before-after.json`
- `docs/repo/audits/POST_CONVERGE_10I_HISTORICAL_REFERENCE_REMEDIATION.md`
- `scripts/ci/check_repox_rules.py`

## ALLOWED_PATHS

- RepoX historical-reference rule/check files directly implicated by the failure
- documentation files directly implicated by historical reference failures
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/migration_ledger.jsonl`
- post-converge status docs

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- root moves, deletes, renames, aliases, move maps, salvage maps, or exception retirement
- product boot proof, package proof, release proof, portable projection proof, full eval, or full CTest

## IMPLEMENTATION

- Preserve DERIVED quarantine/archive evidence references.
- Align `INV-CANON-NO-HIST-REF` enforcement to canonical documents by header or CANON_INDEX membership.
- Record remaining RepoX blocker families without accepting them.

## VALIDATION

- focused RepoX direct and tuple CTest
- AIDE doctor/validate/test/selftest/tools/roots/repo/commit checks
- strict repo/root/distribution/component validators
- docs/build/UI/ABI validators
- JSON parse and git diff checks

## EVIDENCE

- `.aide/reports/POST-CONVERGE-10I-*`
- `docs/repo/audits/POST_CONVERGE_10I_HISTORICAL_REFERENCE_REMEDIATION.md`

## NON_GOALS

No doctrine rewrite, broad docs rewrite, product proof, package proof, release proof, root moves, historical evidence deletion, or feature work.

## ACCEPTANCE

- Historical-reference failures are reduced or classified.
- Legitimate audit/generated/root-recycling history is preserved.
- Remaining failures are classified.
- Product boot readiness is explicitly decided.
- No generated local/cache/build files are committed.

## OUTPUT_SCHEMA

Return branch, HEAD before/after, origin/main, focused RepoX before/after, historical reference fixes, preserved references, remaining families, validation, readiness, commit, worktree, and next task.

## TOKEN_ESTIMATE

- method: concise packet by evidence refs
- approx_tokens: 760
- budget_status: PASS
- warnings:
  - focused RepoX remains blocking

## NEXT

Recommended next task: `POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review`.

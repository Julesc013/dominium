# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10J - Authority-Sensitive Documentation Status Review

## GOAL

Resolve or classify the remaining authority-sensitive documentation status backlog without promoting unclear docs to canonical authority.

## WHY

POST-CONVERGE-10I left 71 focused RepoX failures and the 12-entry `INV-DOC-STATUS-HEADER` backlog from POST-CONVERGE-10H. Authority-sensitive docs require explicit evidence before metadata repair.

## CURRENT RESULT

PARTIAL. Focused RepoX was reduced to 60 failures and 5 warnings. `INV-DOC-STATUS-HEADER` was reduced from 12 to 0. POST-CONVERGE-11 remains blocked.

## CONTEXT_REFS

- `.aide/reports/POST-CONVERGE-10J-status.md`
- `.aide/reports/POST-CONVERGE-10J-authority-doc-findings.json`
- `.aide/reports/POST-CONVERGE-10J-repox-before-after.json`
- `docs/repo/audits/POST_CONVERGE_10J_AUTHORITY_DOC_STATUS.md`
- `docs/architecture/CANON_INDEX.md`

## ALLOWED_PATHS

- authority-sensitive docs directly implicated by doc status failures
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

- Preserve authority-sensitive document body content.
- Complete only top-of-file RepoX status metadata where the authority role is evidence-backed.
- Use `CANON_INDEX.md` only for the seven architecture docs that need DERIVED index entries after their headers become parseable.
- Record remaining RepoX blockers without accepting or weakening them.

## VALIDATION

- focused RepoX direct and tuple CTest
- AIDE doctor/validate/test/selftest/tools/roots/repo/commit checks
- strict repo/root/distribution/component validators
- docs/build/UI/ABI validators
- JSON parse and git diff checks

## EVIDENCE

- `.aide/reports/POST-CONVERGE-10J-*`
- `docs/repo/audits/POST_CONVERGE_10J_AUTHORITY_DOC_STATUS.md`
- `.dominium.local/ctest/repox/proof_manifest_10j_after2.json` (ignored local evidence)
- `.dominium.local/repox-inv-rules-10j-after2.log` (ignored local evidence)

## NON_GOALS

No doctrine rewrite, broad docs rewrite, product proof, package proof, release proof, root moves, exception retirement, warning conversion, or feature work.

## ACCEPTANCE

- Authority doc status failures are reduced or classified.
- No unclear document is promoted to canonical authority.
- Focused RepoX before/after counts are recorded.
- Remaining failures are classified.
- Product boot readiness is explicitly decided.
- No generated local/cache/build files are committed.

## OUTPUT_SCHEMA

Return branch, HEAD before/after, origin/main, focused RepoX before/after, authority doc fixes, deferred docs, remaining families, validation, readiness, commit, worktree, and next task.

## TOKEN_ESTIMATE

- method: concise packet by evidence refs
- approx_tokens: 680
- budget_status: PASS
- warnings:
  - focused RepoX remains blocking

## NEXT

Recommended next task: `POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation`.

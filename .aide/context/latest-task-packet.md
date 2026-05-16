# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10O - RepoX Closeout and Product Boot Readiness Gate

## GOAL

Review POST-CONVERGE-10F through POST-CONVERGE-10N RepoX remediation evidence, reproduce current focused RepoX, and decide whether POST-CONVERGE-11 may proceed.

## WHY

After POST-CONVERGE-10N, focused RepoX is much smaller but still failing. The next step must be selected from evidence: product boot proof, warning acceptance, test discovery/performance work, or one more targeted RepoX remediation.

## CURRENT RESULT

PARTIAL. Focused `inv_repox_rules` remains expected-failing at 20 failures / 5 warnings. Canonical `ctest --preset verify -N` reports 493 tests. POST-CONVERGE-11 is not ready because real non-proof governance/source-policy failures remain.

## CONTEXT_REFS

- `docs/repo/audits/POST_CONVERGE_10O_REPOX_CLOSEOUT_GATE.md`
- `.aide/reports/POST-CONVERGE-10O-repox-closeout.json`
- `.aide/reports/POST-CONVERGE-10O-repox-closeout.md`
- `.aide/reports/POST-CONVERGE-10O-post-converge-11-readiness.md`
- `.aide/reports/POST-CONVERGE-10O-next-task-decision.md`
- `.aide/reports/POST-CONVERGE-10N-repox-before-after.json`

## IMPLEMENTATION

POST-CONVERGE-10O is evidence-only. It creates closeout reports, updates status docs, and records the next task decision without changing RepoX rules or product/runtime/source behavior.

## EVIDENCE

- `ctest --preset verify -N` reports 493 tests.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` reports 20 failures / 5 warnings.
- Tuple fallback was not required because canonical verify discovery found and ran `inv_repox_rules`.

## NON_GOALS

- no root moves, deletes, renames, aliases, move maps, or salvage maps
- no product boot proof
- no portable projection proof
- no package or release generation
- no product/runtime/source behavior changes
- no RepoX/AuditX/TestX weakening

## ACCEPTANCE

- focused RepoX status is reproduced
- remaining failures and warnings are classified
- POST-CONVERGE-11 readiness is explicit
- exact next task is recommended
- no product proof or broad remediation is performed

## OUTPUT_SCHEMA

Human-readable reports plus JSON evidence:

- `.aide/reports/POST-CONVERGE-10O-repox-closeout.json`

## TOKEN_ESTIMATE

Latest packet is intended to stay below the AIDE compact-context budget.

## ALLOWED_PATHS

- AIDE reports/context/ledger
- post-converge and release status docs
- closeout audit evidence

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- generated product/projection/package/release artifacts
- root moves, deletes, renames, aliases, or move maps
- broad AuditX output regeneration
- RepoX/AuditX/TestX weakening

## VALIDATION

Focused RepoX was rerun for the closeout gate and remains expected-failing at 20 failures / 5 warnings. Final command details are recorded in `.aide/reports/POST-CONVERGE-10O-validation.md`.

## NEXT

Recommended semantic task: `POST-CONVERGE-10P - Residual RepoX Governance and Source-Policy Remediation`. TEST-PERF follow-up remains appropriate for validation speed, but it is not the semantic gate blocker.

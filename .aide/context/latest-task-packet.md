# AIDE Latest Task Packet

## PHASE

RESTRUCTURE-REPAIR-00 - Full remediation, repair, proof, and origin sync attempt.

## GOAL

Repair safe post-restructure drift, rerun the strongest feasible validation suite, and classify remaining blockers without weakening gates.

## WHY

MOVE-BULK and POST-RESTRUCTURE evidence left deferred roots, skipped references, and proof blockers. This task turns the current state into an auditable repair baseline.

## CONTEXT_REFS

- `.aide/reports/RESTRUCTURE-REPAIR-00-status.md`
- `.aide/reports/RESTRUCTURE-REPAIR-00-validation.md`
- `.aide/reports/RESTRUCTURE-REPAIR-00-blockers.md`
- `.aide/reports/RESTRUCTURE-REPAIR-00-final-readiness.md`
- `docs/repo/audits/RESTRUCTURE_REPAIR_00_FULL_REMEDIATION.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`

## ALLOWED_PATHS

- Safe stale-path tests, proof docs, AIDE reports/context/ledger, root-recycling docs, release proof docs, and deterministic proof metadata.

## FORBIDDEN_PATHS

- Feature work, public release artifacts, tags, GitHub releases, force-pushes, root moves without a valid gate, frozen-hash refresh without review, override renewal without review, and replay-hash acceptance without semantic proof.

## IMPLEMENTATION

Applied safe path/test/doc/proof repairs. Remaining root, policy, frozen-hash, replay, and full CTest blockers are classified instead of suppressed.

## VALIDATION

AIDE, strict structural validators, focused RepoX, smoke CTest, native configure, build-only `ALL_BUILD`, product boot, portable projection, and internal pilot pass. Full CTest remains failing/incomplete.

## EVIDENCE

- `.aide/reports/RESTRUCTURE-REPAIR-00-evidence-index.md`
- `.aide/reports/RESTRUCTURE-REPAIR-00-master-remediation-ledger.md`
- `.aide/reports/RESTRUCTURE-REPAIR-00-final-root-matrix.md`
- `.aide/reports/RESTRUCTURE-REPAIR-00-final-readiness.md`
- `docs/repo/audits/RESTRUCTURE_REPAIR_00_FULL_REMEDIATION.md`

## NON_GOALS

No DOE-00 execution, no feature implementation, no public release, no root move batch, no validator weakening.

## ACCEPTANCE

Partial repair baseline is acceptable only as blocker evidence. DOE-00 is not ready and feature implementation remains blocked.

## OUTPUT_SCHEMA

Evidence is emitted as Markdown status reports, JSON readiness/root-matrix reports, and one appended migration ledger JSONL event.

## TOKEN_ESTIMATE

Small. The packet is intended to remain below AIDE Lite task-packet budget.

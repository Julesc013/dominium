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
- `.aide/context/latest-context-packet.md`
- `.aide/verification/latest-verification-report.md`
- `docs/repo/audits/RESTRUCTURE_REPAIR_00_FULL_REMEDIATION.md`
- `docs/repo/RESTRUCTURE_REPAIR_STATUS.md`

## ALLOWED_PATHS

- Safe stale-path tests, proof docs, AIDE reports/context/ledger, root-recycling docs, release proof docs, deterministic hash evidence, replay fixtures, and AuditX scan-scope code.

## FORBIDDEN_PATHS

- Feature work.
- Public release artifacts, tags, installers, uploads, and GitHub releases.
- Root moves without a valid gate.
- Validator weakening.
- `.aide.local/**`
- `.dominium.local/**`
- Generated build/projection/release outputs.

## IMPLEMENTATION

Applied safe path/test/doc/proof repairs, refreshed deterministic hash evidence, removed expired overrides, refreshed replay fixtures from current stubs, and narrowed AuditX generated-evidence scanning. Remaining root, semantic lint, and AuditX wall-time blockers are classified instead of suppressed.

## VALIDATION

AIDE, strict structural validators, focused RepoX, smoke CTest, native configure, build-only `ALL_BUILD`, product boot, portable projection, internal pilot, frozen contract guard, override policy tests, and replay hash invariance pass. Full CTest remains not green.

## COMMITS

- Commit a scoped partial repair follow-up if commit policy passes.
- Do not push while blockers remain.

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

Return a compact final report with status, commits, validation, blockers, push state, DOE-00 readiness, and next task.

## TOKEN_ESTIMATE

Small. The packet is intended to remain below AIDE Lite task-packet budget.

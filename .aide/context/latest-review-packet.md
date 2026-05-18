# AIDE Review Packet

## Review Objective

Review MOVE-ROUTER-01: physical `git mv` application of the deterministic bad-root route table, quarantine handling, exception retirement, stale-reference evidence, rollback evidence, and no-semantic-mutation compliance.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `contracts/repo/naming.contract.toml`
- `contracts/repo/bad_root_routing.contract.toml`
- `contracts/repo/layout_exceptions.toml`
- `docs/repo/bad_root_routing.md`
- `docs/repo/final_repository_structure.md`
- `.aide/reports/MOVE-ROUTER-01-moved-items.json`
- `.aide/reports/MOVE-ROUTER-01-root-matrix.json`
- `.aide/reports/MOVE-ROUTER-01-exception-actions.json`
- `.aide/reports/MOVE-ROUTER-01-stale-reference-scan.json`
- `.aide/reports/MOVE-ROUTER-01-rollback.json`
- `.aide/reports/MOVE-ROUTER-01-validation.md`
- `.aide/reports/MOVE-ROUTER-01-status.md`
- `.aide/reports/MOVE-ROUTER-01-blockers.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

## Changed Files Summary

The task moves tracked files out of former bad roots into canonical owners or quarantine, retires only empty-root exceptions, and writes apply evidence. It does not delete files, edit moved file contents, perform semantic rewrites, repair broad references/imports, or run feature work.

## Validation Summary

Expected validation: preapply router refresh, bad-root absence checks, AIDE doctor/validate/test/selftest/tools/roots/repo, strict repo/root/distribution/component validators, new validators, docs/build/UI/ABI checks, JSON parse checks, git diff checks, and commit check.

## Risk Summary

Reference/import/build breakage is expected until MOVE-ROUTER-02 repairs stale paths. Quarantined files are intentionally inactive. Feature work remains blocked.

## Token Summary

The task and review packets stay compact and reference evidence by path instead of embedding full validator output.

## Non-Goals / Scope Guard

No file deletion, moved-file content edit, broad reference rewrite, import repair, shim creation, feature work, generated local output commit, package/release generation, tag, or GitHub release.

## Reviewer Instructions

Confirm that every tracked bad-root file moved, remaining bad-root tracked count is zero, quarantine routes are recorded, exception retirement is limited to empty roots, and stale-reference repair is assigned to MOVE-ROUTER-02.

## MOVE-ROUTER-02 Review Note

MOVE-ROUTER-02 closes as PARTIAL. Review should verify that the routed structure
was preserved, no former bad-root ownership was restored, no generated/local
outputs were staged, and the remaining TestX/RepoX/import blockers are assigned
to MOVE-ROUTER-02R.

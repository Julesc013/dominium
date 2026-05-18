# AIDE Review Packet

## Review Objective

Review NAME-00 naming canon work for scope, no-apply discipline, validator warning posture, and consistency with the post-CONVERGE layout authority.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `.aide/reports/NAME-00-status.md`
- `.aide/reports/NAME-00-validation.md`
- `.aide/reports/NAME-00-blockers.md`
- `.aide/reports/NAME-00-path-conflicts.md`
- `.aide/reports/NAME-00-language-ownership-findings.md`
- `.aide/reports/NAME-00-next-readiness.md`
- `.aide/verification/review-decision-policy.yaml`
- `docs/repo/audits/NAME_00_NAMING_CANON_AUDIT.md`
- `contracts/repo/naming.contract.toml`

## Changed Files Summary

NAME-00 adds a machine-readable naming contract, human naming docs, warning-oriented naming validators, and evidence reports. It does not move, delete, rename, rewrite, create shims, apply move maps, or retire exceptions.

## Validation Summary

Expected validation: AIDE doctor/validate, Python compile for new validators, JSON parse for naming evidence/schema, naming validators, strict layout/root/distribution/component validators, focused RepoX, smoke CTest, and `git diff --check`. Full CTest remains out of scope for NAME-00.

## Token Summary

The task and review packets are compact and reference evidence by path rather than embedding long outputs.

## Risk Summary

Root debt remains excepted, semantic lint gates are not waived, AuditX still needs partitioning/performance repair, and DOE-00 remains blocked.

## Non-Goals / Scope Guard

No feature work, public release, root move batch, force push, validator weakening, or generated local proof output commit.

## Reviewer Instructions

Check that repaired evidence is deterministic, that no policy was weakened, that generated local outputs are not staged, and that the remaining blockers are reported honestly.

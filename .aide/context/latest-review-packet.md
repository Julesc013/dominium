# AIDE Review Packet

## Review Objective

Review TEST-PERF-01 CTest sharding, timing evidence, AuditX wall-time classification, and XStack impacted-shard fallback.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/verification/latest-verification-report.md`

## Evidence Packet References

- `.aide/reports/TEST-PERF-01-status.md`
- `.aide/reports/TEST-PERF-01-validation.md`
- `.aide/reports/TEST-PERF-01-blockers.md`
- `.aide/reports/TEST-PERF-01-ctest-inventory.json`
- `.aide/reports/TEST-PERF-01-ctest-timing.md`
- `.aide/reports/TEST-PERF-01-auditx-walltime.md`
- `.aide/reports/TEST-PERF-01-shard-plan.md`
- `.aide/reports/TEST-PERF-01-next-readiness.md`
- `.aide/verification/review-decision-policy.yaml`
- `docs/repo/audits/TEST_PERF_01_CTEST_SHARDING_AUDIT.md`
- `docs/testing/CTEST_SHARDING_AND_TIMEOUTS.md`
- `docs/testing/SLOW_TEST_BASELINE.md`

## Changed Files Summary

TEST-PERF-01 adds CTest label metadata for `fast`, `audit`, `slow`, and `nightly`, keeps AuditX required in a bounded slow shard, and adds an XStack impact fallback so unmapped dirty paths still select core TestX/AuditX shard groups.

## Validation Summary

Expected validation: AIDE doctor/validate/test/selftest/tools/roots/repo, strict repo/root/distribution/component validators, NAME-00 validators, docs/build/UI/ABI supplemental checks, focused RepoX, smoke, fast, AuditX slow shard, Python compile for touched tooling, JSON parse for evidence, and git diff checks. Full CTest remains not green because the semantic lint lanes are still failing.

## Risk Summary

`slice0_hardcoded_ids` and `slice1_hardcoded_constants` remain real blockers for the next task. AuditX is bounded but slow at roughly 825 seconds on the current machine. Full CTest is still a promotion lane, not a green local proof.

## Token Summary

The task and review packets stay compact and reference evidence by path instead of embedding full CTest output.

## Non-Goals / Scope Guard

No test deletion, assertion weakening, root movement, semantic lint repair, product/runtime feature work, release generation, public release, tag, or generated local output commit.

## Reviewer Instructions

Check that the new labels are additive, the AuditX shard still runs, the impact fallback strengthens rather than weakens shard selection, and the semantic lint failures remain visible.

# AIDE Review Packet

## Review Objective

Review `AIDE-WORKUNIT-SCHEMA-01`: structured AIDE task/work/evidence schema
layer for bounded parallel development.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

For this queue, `PASS_WITH_WARNINGS` maps to `PASS_WITH_NOTES`.

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/AIDE-WORKUNIT-SCHEMA-01-validation.json`

## Evidence Packet References

- `.aide/schema/work_unit.schema.json`
- `.aide/schema/task_attempt.schema.json`
- `.aide/schema/blocker.schema.json`
- `.aide/schema/evidence_packet.schema.json`
- `.aide/schema/repair_task.schema.json`
- `.aide/schema/resume_task.schema.json`
- `.aide/schema/checkpoint_candidate.schema.json`
- `.aide/schema/promotion_decision.schema.json`
- `.aide/schema/warning_disposition.schema.json`
- `.aide/schema/capability_reality_record.schema.json`
- `.aide/fixtures/work_unit/`
- `.aide/policy/workunit_schema_law.md`
- `tools/aide/validate_workunits.py`
- `.aide/reports/AIDE-WORKUNIT-SCHEMA-01-validation.json`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`

## Changed Files Summary

WorkUnit-family schemas, tiny valid/invalid fixtures, a dependency-free targeted
validator, schema-law documentation, audit, and AIDE queue/status/review packet
surfaces were added or updated. Pre-existing workflow-law policy surfaces were
preserved as the governing prerequisite layer.

No product runtime, package runtime, replay runtime, provider runtime, runtime
module loader, Workbench shell, renderer/native GUI, gameplay, release artifact,
branch automation, merge automation, promotion automation, or CMake target was
implemented.

## Validation Summary

Targeted WorkUnit schema validation passed:

```text
py -3 -m tools.aide.validate_workunits --repo-root . --json-out .aide/reports/AIDE-WORKUNIT-SCHEMA-01-validation.json
```

It checked that required schema files exist, valid fixtures pass, invalid
fixtures fail, blocker classes match `.aide/policy/blocker_taxonomy.md`, and
WorkUnit status values match `.aide/policy/task_lifecycle.md`.

## Token Summary

This review packet is compact. Full schema detail is in `.aide/schema/`, and
full task evidence is in `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`.

## Warning Summary

Full CTest remains T4/full-gate debt. Existing AIDE review-packet reference
warnings remain known. Large parallel execution remains unauthorized.

## Risk Summary

The schema layer records task objects but does not provide dev/main policy,
checkpoint loop policy, repair engine, scheduler, or automation. Capability
reality ledger population is explicitly deferred.

## Reviewer Instructions

Check that schemas are strict, fixtures are tiny, invalid fixtures fail, schema
law preserves workflow-law doctrine, and queue/status points next to
`AIDE-DEV-MAIN-POLICY-01`.

## Non-Goals / Scope Guard

No scheduler, automatic branch/worktree automation, merge automation, promotion
automation, repair engine, Workbench Agent Board, product/runtime behavior, or
release publication was implemented.

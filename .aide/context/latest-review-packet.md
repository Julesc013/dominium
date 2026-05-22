# AIDE Review Packet

## Review Objective

Review `AIDE-WORKFLOW-LAW-01`: minimum AIDE task operating system law before a
larger parallel wave.

## Decision Requested

`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`

For this queue, `PASS_WITH_WARNINGS` maps to `PASS_WITH_NOTES`.

## Task Packet Reference

`.aide/context/latest-task-packet.md`

## Context Packet Reference

`.aide/context/latest-context-packet.md`

## Verification Report Reference

`.aide/reports/AIDE-WORKFLOW-LAW-01-summary.md`

## Evidence Packet References

- `contracts/aide/aide_workflow_law.v1.json`
- `docs/development/aide/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `.aide/reports/AIDE-WORKFLOW-LAW-01-summary.md`
- `.aide/reports/AIDE-WORKFLOW-LAW-01-validation.json`

## Changed Files Summary

Workflow law contract, derived AIDE development doc, audit, queue/status
packets, warning/status packets, public surface registration, and evidence were
updated. No product runtime, package runtime, replay runtime, provider runtime,
runtime module loader, Workbench shell, renderer/native GUI, gameplay, release
artifact, branch automation, or CMake target was implemented.

## Validation Summary

Targeted governance validators and parse checks are recorded in
`.aide/reports/AIDE-WORKFLOW-LAW-01-validation.json`.

## Token Summary

This review packet is compact. Full law detail is in
`contracts/aide/aide_workflow_law.v1.json` and
`docs/development/aide/AIDE_WORKFLOW_LAW_01.md`.

## Risk Summary

The law is provisional and does not yet provide full WorkUnit/attempt/blocker
schemas. Full CTest remains T4/full-gate debt. Existing known warnings remain
classified.

## Reviewer Instructions

Check that branch roles, lifecycle states, blocker taxonomy, evidence
requirements, repair/resume behavior, warning policy, and promotion gates are
explicit, and that next task advances to `AIDE-WORKUNIT-SCHEMA-01`.

## Non-Goals / Scope Guard

No automation or product/runtime behavior was implemented.

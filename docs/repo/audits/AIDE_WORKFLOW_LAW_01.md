Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: AIDE-WORKFLOW-LAW-01
Result: PASS_WITH_WARNINGS

# AIDE-WORKFLOW-LAW-01

## Decision

`PASS_WITH_WARNINGS`

Next task: `AIDE-WORKUNIT-SCHEMA-01`.

Alternate next task: `PRESENTATION-CONTRACT-01`.

Secondary follow-up: `AIDE-DEV-MAIN-POLICY-01`.

Tertiary follow-up: `POINTER-WIDTH-SERIALIZATION-AUDIT-01`.

## Summary

This slice defines the minimum AIDE task operating system law after the product
spine review. It binds existing AIDE policy fragments into one provisional
machine-readable workflow contract and one derived explanatory document.

The core rule is:

```text
Development should be non-blocking.
Promotion should be evidence-blocked.
```

## Surfaces Added

| Surface | Path |
| --- | --- |
| machine-readable workflow law | `contracts/aide/aide_workflow_law.v1.json` |
| human-readable workflow law | `docs/development/aide/AIDE_WORKFLOW_LAW_01.md` |
| audit | `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md` |
| summary evidence | `.aide/reports/AIDE-WORKFLOW-LAW-01-summary.md` |
| validation evidence | `.aide/reports/AIDE-WORKFLOW-LAW-01-validation.json` |

## Law Coverage

| Area | Result |
| --- | --- |
| branch roles | PASS |
| task lifecycle states | PASS |
| blocker taxonomy | PASS |
| warning policy | PASS |
| workunit minimum fields | PASS |
| repair/resume behavior | PASS |
| task/dev/checkpoint/main promotion gates | PASS |
| parallel-wave limits | PASS |
| broad feature blockers preserved | PASS |

## Existing Policies Reused

- `.aide/policies/branch-roles.yaml`
- `.aide/policies/git-workflow.yaml`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
- `.aide/policies/promotion-rules.yaml`
- `.aide/policies/workunit-sizing.yaml`

## Non-Goals Preserved

No product runtime, package runtime, replay runtime, provider runtime, runtime
module loader, Workbench shell, broad Workbench UI, renderer, native GUI,
gameplay, release publication, branch automation, force-push automation, or
direct main-promotion automation was implemented.

## Warning Classification

Known warnings remain accepted for narrow progress:

- full CTest remains T4/full-gate debt
- dependency-direction warnings remain known with 0 violations
- AIDE review-ref warnings may remain
- stale AuditX output warning remains
- contract-only/runtime-not-implemented gaps remain visible

## Next

Run `AIDE-WORKUNIT-SCHEMA-01` to define explicit WorkUnit, attempt, blocker,
evidence packet, checkpoint, and promotion-report schemas.

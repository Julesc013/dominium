# MOVE-FAMILY-00-PLAN Blockers

Status: DERIVED
Last Reviewed: 2026-05-17

## Result

The family-level apply plan is blocked. The planning task is complete as blocker evidence, but the draft is not ready for `MOVE-FAMILY-00-GATE`.

## Blocking Conditions

| Blocker | Affected Roots | Reason |
| --- | --- | --- |
| No safe docs-only candidate remains | all target roots | AIDE-MOVE-01 already moved `ide/README.md`; no remaining target-family file is simple docs-only cleanup. |
| Active Python import surface | `governance/`, `meta/`, `performance/`, `validation/` | Moving these files would require module ownership decisions, import rewrites, consumer proofs, and broader validation. |
| IDE manifest consumer uncertainty | `ide/` | Remaining files are machine-readable schema/examples consumed by CMake, scripts, docs, and registry surfaces. |
| High reference complexity | all target roots | Root reference reports and direct scans show active references across release, runtime, tools, tests, docs, and generated evidence. |
| No approved move map | all target roots | This task is planning-only; apply remains unauthorized. |

## Non-Blocking Baseline Warnings

- Full CTest and full eval remain out of scope from BASELINE-00.
- Generated release/projection evidence remains local and ignored.
- No public package, installer, tag, GitHub release, upload, or publication exists.

## Required Refinement

Before a gate can approve MOVE-FAMILY-00 apply, a refinement task must define active-module ownership and consumer-safe destinations for `governance/`, `meta/`, `performance/`, `validation/`, and `ide/manifests/**`.

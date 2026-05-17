Status: DRAFT
Last Reviewed: 2026-05-17
Approval Status: not_approved
Apply Allowed: false

# MOVE-FAMILY-00 Governance, Meta, Performance, Validation, And IDE Plan

## Status

- Task: `MOVE-FAMILY-00-PLAN`
- Result: `BLOCKED`
- Baseline: `BASELINE-00`
- Baseline commit: `6ed2516ea9570bd54cdd3f1d94ed347f48cf6447`
- Ready for `MOVE-FAMILY-00-GATE`: false

## Scope

This is a no-apply planning artifact for the first family-level cleanup wave after BASELINE-00. It inspects:

- `governance/`
- `meta/`
- `performance/`
- `validation/`
- `ide/`

It applies no moves, deletes, renames, reference rewrites, compatibility shims, active aliases, salvage maps, move maps, or exception updates.

## Baseline

BASELINE-00 freezes RELEASE-00 as the structural regression baseline. Any future apply task must preserve the release/projection/product proof posture recorded in:

- `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`
- `docs/repo/audits/BASELINE_00_RELEASE_STRUCTURAL_REGRESSION_BASELINE.md`

## Target Roots

The current tracked target-family state contains 36 files:

- `governance/`: 2 files
- `meta/`: 26 files
- `performance/`: 3 files
- `validation/`: 2 files
- `ide/`: 3 files

`ide/README.md` is already gone from `ide/` and exists at `docs/architecture/IDE_PROJECTIONS.md`.

## Candidate Classification

| Root | Fate | Count | Reason |
| --- | --- | ---: | --- |
| `governance/` | preserve/defer | 2 | Active governance Python helpers with release/setup/dist/tool consumers. |
| `meta/` | preserve/defer | 26 | Broad active Python subsystem with runtime, game, release, tool, AuditX, RepoX, TestX, and test consumers. |
| `performance/` | preserve/defer | 3 | Active product/runtime performance helpers imported by client and XStack paths. |
| `validation/` | preserve/defer | 2 | Active validation pipeline imported by runtime, tools, shims, AuditX, RepoX, and TestX. |
| `ide/` | convert later | 3 | Machine-readable projection schema/examples with CMake, script, docs, and registry consumers. |

## Planned Moves

No moves are planned for MOVE-FAMILY-00.

The first family-level cleanup wave cannot safely select an apply subset because every remaining file is either active executable/tooling import surface or machine-readable projection metadata.

## Deferred Material

Deferred material is recorded in `.aide/reports/MOVE-FAMILY-00-PLAN-candidate-table.json` and `.aide/refactors/MOVE-FAMILY-00.salvage_plan.json`.

The next refinement must decide whether active Python modules should remain in place, move to a package-owned implementation root, or receive a broader contract/tooling migration plan. IDE manifests need an explicit projection/contract owner decision before path changes.

## Blocked Material

The blocker groups are:

- no remaining docs-only target-family candidate after AIDE-MOVE-01;
- active Python import surface in `governance/`, `meta/`, `performance/`, and `validation/`;
- machine-readable IDE projection manifests with active consumers;
- high reference complexity across runtime, release, tools, tests, docs, and generated evidence;
- no approved move map or salvage map.

## Reference Rewrite Plan

No reference rewrites are planned. Future rewrites must be produced only after active-module destinations and IDE projection ownership are known.

## Validation Plan

If a later refinement creates an apply-ready scope, the apply task must run Tier 0 plus focused RepoX. Active tooling moves must add affected wrapper/tool validation and consumer proof. Full CTest, CMake build, product boot, projection proof, and internal pilot proof are not required for this blocked planning result.

## Rollback Plan

There is no tracked path rollback for this planning task. Future apply tasks must name exact reverse moves, reverse reference rewrites, reverse exception updates, and post-rollback validation before applying changes.

## Exception Update Plan

No exception ledger change is planned. All five target roots remain in their current exception posture until a later approved apply task narrows them.

## Readiness For MOVE-FAMILY-00-GATE

Not ready. The recommended next task is:

```text
MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES - Define ownership and consumer-safe destinations for active governance/meta/performance/validation modules and IDE projection manifests
```

## No Moves/Deletes/Renames Confirmation

MOVE-FAMILY-00-PLAN made no source-root moves, deletes, renames, reference rewrites, active aliases, compatibility shims, salvage-map applications, move-map applications, or exception retirements.

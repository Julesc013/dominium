# MOVE-BULK-00-GATE Readiness

## Status

- Task: `MOVE-BULK-00-GATE`
- Gate result: `PASS_WITH_WARNINGS`
- Branch: `main`
- HEAD at gate start: `414c5150630c47b7233e489d7bb86581207c5400`
- origin/main at gate start: `d84d4442165f1e80d00584a966487814a540a8c1`
- Baseline: `BASELINE-00`
- Authorized next task: `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`

## Purpose

The global MOVE-BULK plan is intentionally aggressive. This gate prevents it from becoming reckless by authorizing only the safest apply scope and deferring higher-risk batches behind stronger gates.

## Plan Artifact Review

All required global and batch MOVE-BULK-00 artifacts are present and parse as JSON. The TOML plan remains draft/no-apply and is manually inspected when no local TOML parser is available.

| Artifact Group | Result |
| --- | --- |
| Global plan | present, parsed, draft, not approved, no-apply |
| Global salvage/move maps | present, parsed, no maps applied |
| Import/reference rewrite maps | present, parsed, no rewrites applied |
| Shim plan | present, parsed, no shims created |
| Validation/rollback/exception plans | present, parsed |
| Batch plans A-H | present and parsed |

## Batch Review

| Batch | Scope | Files | Gate Decision | Reason |
| --- | --- | ---: | --- | --- |
| A | docs/evidence/archive-only | 309 | authorize safe subset | Low-risk, Tier 0, no active import/shim/build dependency. |
| B | templates/models/modding | 6 | defer | Needs owner split. |
| C | content identity | 1230 | defer | Needs identity/projection/pack validation gate. |
| D | authority/policy/spec/update | 50 | defer | Needs authority and contract gate. |
| E | active tools/modules | 33 | defer | Needs shim/import/static-check gate. |
| F | runtime/core/control/net | 54 | defer | Needs runtime/build/product gate. |
| G | libraries/ABI | 108 | defer | Needs ABI/build gate; includes CMake blocker. |
| H | final closure | 0 | block until prior proof | Cannot precede earlier apply/proof waves. |

## Authorized Batches

Batch A is authorized as `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.

The apply task must use safe-subset behavior and must not apply any other batch.

## Deferred Batches

Batches B through G are deferred. Batch H is blocked until prior apply/proof tasks complete.

## No-Apply Invariant Check

- moves applied: no
- deletes applied: no
- renames applied: no
- imports rewritten: no
- references rewritten: no
- shims created: no
- move maps applied: no
- salvage maps applied: no
- exceptions retired: no
- product/runtime/source behavior changed: no

## Baseline/Regression Check

The gate keeps BASELINE-00 as the regression baseline. Batch A requires Tier 0 validation and stale-reference classification. Higher-risk batches retain the stronger validation tiers defined in `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`.

## Validation Results

See `.aide/reports/MOVE-BULK-00-GATE-validation.md`.

## Known Warnings

- Only Batch A is authorized.
- Batches B-G need stronger gates.
- Batch H must wait for prior proof.
- Full CTest, full eval, CMake configure/build, product binaries, package/release generation, and projection regeneration are out of scope.

## Gate Decision

`PASS_WITH_WARNINGS`.

## Next Task

`MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.

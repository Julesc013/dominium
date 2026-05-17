# AIDE Latest Task Packet

## PHASE

MOVE-FAMILY-00-PLAN - Governance, Meta, Performance, Validation, and IDE Cleanup Plan

## GOAL

Produce a reviewable no-apply cleanup plan for `governance/`, `meta/`, `performance/`, `validation/`, and `ide/` using BASELINE-00 as the structural regression baseline.

## WHY

The repository has a frozen internal pilot release proof. The first family-level physical cleanup needs an exact plan before any move application so active tooling, policy, machine-readable metadata, and generated evidence are not moved by convenience.

## CONTEXT_REFS

- `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`
- `docs/repo/audits/BASELINE_00_RELEASE_STRUCTURAL_REGRESSION_BASELINE.md`
- `docs/repo/root-recycling/AIDE_ROOT_01_FIRST_WAVE_INVENTORY.md`
- `docs/repo/root-recycling/AIDE_ROOT_06_RECONCILIATION_AND_MOVE_SELECTION.md`
- `.aide/reports/AIDE-MOVE-02-REFINE-decision.md`
- `.aide/reports/roots/governance.inventory.json`
- `.aide/reports/roots/meta.inventory.json`
- `.aide/reports/roots/performance.inventory.json`
- `.aide/reports/roots/validation.inventory.json`
- `.aide/reports/roots/ide.inventory.json`

## ALLOWED_PATHS

- `.aide/refactors/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/STRUCTURAL_REGRESSION_BASELINE.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`

## FORBIDDEN_PATHS

- target-root file edits under `governance/**`, `meta/**`, `performance/**`, `validation/**`, or `ide/**`
- product/runtime/source behavior changes
- source-root moves, deletes, renames, reference rewrites, active aliases, compatibility shims, approved move maps, applied move maps, applied salvage maps, or exception retirements
- generated build/package/release/projection/local output commits

## IMPLEMENTATION

- Inspect current target-root files and existing root evidence.
- Produce draft/not-approved/no-apply plan artifacts.
- Classify every current target-family tracked file as move now, move later, convert later, archive later, preserve/defer, or block.
- Record validation, rollback, reference rewrite, exception update, and reviewer-facing blocker evidence.

## VALIDATION

- AIDE doctor/validate/test/selftest/tools/roots/repo validation.
- AIDE latest commit check.
- Plan JSON and TOML parsing.
- Strict repo/root/distribution/component validators.
- Docs/build/UI/ABI checks.
- Git diff checks and generated-output staging checks.

## EVIDENCE

- `.aide/refactors/MOVE-FAMILY-00.plan.toml`
- `.aide/refactors/MOVE-FAMILY-00.plan.json`
- `.aide/refactors/MOVE-FAMILY-00.salvage_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.reference_rewrite_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.validation_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.rollback_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.exception_update_plan.json`
- `.aide/reports/MOVE-FAMILY-00-PLAN-*`
- `docs/repo/root-recycling/MOVE_FAMILY_00_GOVERNANCE_META_PERFORMANCE_VALIDATION_IDE_PLAN.md`

## NON_GOALS

- No move application.
- No file delete or rename.
- No reference rewrite.
- No root exception retirement.
- No feature/domain/product/runtime implementation.
- No full CTest, full eval, CMake configure/build, product binary execution, package generation, or release generation.

## ACCEPTANCE

- Required plan and report artifacts exist.
- Apply remains unauthorized.
- The plan truthfully records whether `MOVE-FAMILY-00-GATE` is ready.
- Validation is run and recorded.
- Only scoped planning evidence and docs are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS

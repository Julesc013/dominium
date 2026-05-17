# AIDE Latest Task Packet

## PHASE

MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES - Refine Governance, Meta, Performance, Validation, and IDE Active-Module Ownership

## GOAL

Produce ownership boundary evidence for the blocked MOVE-FAMILY-00 plan without applying moves.

## WHY

MOVE-FAMILY-00-PLAN found no safe apply set because the remaining target-family files are active Python/tooling surfaces or machine-readable IDE projection metadata. The next cleanup step needs precise ownership destinations, consumer evidence, and a staged strategy before any move gate.

## CONTEXT_REFS

- `.aide/refactors/MOVE-FAMILY-00.plan.json`
- `.aide/refactors/MOVE-FAMILY-00.salvage_plan.json`
- `.aide/refactors/MOVE-FAMILY-00.reference_rewrite_plan.json`
- `.aide/reports/MOVE-FAMILY-00-PLAN-candidate-table.json`
- `docs/repo/root-recycling/MOVE_FAMILY_00_GOVERNANCE_META_PERFORMANCE_VALIDATION_IDE_PLAN.md`
- `contracts/repo/root_constitution.toml`
- `contracts/repo/ownership_slots.toml`
- `contracts/repo/layout_exceptions.toml`

## ALLOWED_PATHS

- `.aide/refactors/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`

## FORBIDDEN_PATHS

- target-root file edits under `governance/**`, `meta/**`, `performance/**`, `validation/**`, or `ide/**`
- product/runtime/source behavior changes
- moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, move map approvals, salvage map approvals, map applications, or exception retirements
- generated build/package/release/projection/local output commits

## IMPLEMENTATION

- Inspect current target-root file list.
- Map active Python modules and machine-readable IDE manifests to ownership destinations.
- Record import/reference consumers and future migration modes.
- Produce a revised cleanup strategy and next planning task.

## VALIDATION

- AIDE doctor/validate/test/selftest/tools/roots/repo validation.
- AIDE latest commit check.
- JSON and TOML parsing for new artifacts.
- Strict repo/root/distribution/component validators.
- Docs/build/UI/ABI checks.
- Git diff checks and generated-output staging checks.

## EVIDENCE

- `.aide/refactors/MOVE-FAMILY-00.active_module_ownership.json`
- `.aide/refactors/MOVE-FAMILY-00.ide_manifest_ownership.json`
- `.aide/refactors/MOVE-FAMILY-00.import_reference_map.json`
- `.aide/refactors/MOVE-FAMILY-00.refined_cleanup_strategy.json`
- `.aide/refactors/MOVE-FAMILY-00.refined_cleanup_strategy.toml`
- `.aide/reports/MOVE-FAMILY-00-REFINE-*`
- `docs/repo/root-recycling/MOVE_FAMILY_00_ACTIVE_MODULE_BOUNDARY_REFINEMENT.md`

## NON_GOALS

- No move application.
- No file delete or rename.
- No import or reference rewrite.
- No compatibility shim or active path alias.
- No root exception retirement.
- No feature/domain/product/runtime implementation.
- No full CTest, full eval, CMake configure/build, product binary execution, package generation, or release generation.

## ACCEPTANCE

- Required ownership/refinement artifacts exist and parse.
- Apply remains unauthorized.
- The refined strategy names the next planning task.
- Validation is run and recorded.
- Only scoped refinement evidence and docs are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS

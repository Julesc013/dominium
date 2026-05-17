# AIDE Latest Task Packet

## PHASE

MOVE-FAMILY-00B-PLAN - IDE Manifest Contract and Projection Ownership Plan

## GOAL

Produce a no-apply migration plan for tracked `ide/manifests/**` source metadata and decide whether the files can move to `contracts/projections/ide/**` under a later gate.

## WHY

MOVE-FAMILY-00-REFINE found that `ide/manifests/**` is the smallest remaining root-family group with a clear owner. The `ide` source root cannot retire until tracked manifest source metadata has a contract/projection home, consumer rewrites are known, generated-output behavior is separated, and exception retirement conditions are explicit.

## CONTEXT_REFS

- `.aide/refactors/MOVE-FAMILY-00.ide_manifest_ownership.json`
- `.aide/refactors/MOVE-FAMILY-00.refined_cleanup_strategy.json`
- `.aide/reports/MOVE-FAMILY-00-REFINE-ide-manifest-boundaries.md`
- `.aide/reports/MOVE-FAMILY-00-REFINE-next-plan.md`
- `docs/repo/root-recycling/MOVE_FAMILY_00_ACTIVE_MODULE_BOUNDARY_REFINEMENT.md`
- `docs/repo/root-recycling/MOVE_FAMILY_00_GOVERNANCE_META_PERFORMANCE_VALIDATION_IDE_PLAN.md`
- `contracts/repo/root_constitution.toml`
- `contracts/repo/ownership_slots.toml`
- `contracts/repo/layout_exceptions.toml`
- `contracts/README.md`
- `contracts/MANIFEST.md`
- `docs/architecture/IDE_PROJECTIONS.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`

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

- `ide/**`
- `contracts/**`
- `tools/**`
- product/runtime/engine/game/source behavior paths
- moves, deletes, renames, reference rewrites, active aliases, compatibility shims, move map approvals, salvage map approvals, map applications, or exception retirements
- generated build/package/release/projection/local output commits

## IMPLEMENTATION

- Inspect current tracked `ide/manifests/**` files.
- Classify schema/examples as contract metadata, tooling input, generated evidence, historical metadata, or unknown.
- Produce inventory, ownership, move, reference rewrite, validation, rollback, and exception update plans.
- Keep every plan draft/not-approved/no-apply.

## VALIDATION

- AIDE doctor/validate/test/selftest/tools/roots/repo validation.
- AIDE latest commit check.
- JSON and TOML parsing for new artifacts.
- Strict repo/root/distribution/component validators.
- Docs/build/UI/ABI checks.
- Git diff checks and generated-output staging checks.

## EVIDENCE

- `.aide/refactors/MOVE-FAMILY-00B.plan.toml`
- `.aide/refactors/MOVE-FAMILY-00B.plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.ide_manifest_inventory.json`
- `.aide/refactors/MOVE-FAMILY-00B.ide_manifest_ownership.json`
- `.aide/refactors/MOVE-FAMILY-00B.reference_rewrite_plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.validation_plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.rollback_plan.json`
- `.aide/refactors/MOVE-FAMILY-00B.exception_update_plan.json`
- `.aide/reports/MOVE-FAMILY-00B-PLAN-*`
- `docs/repo/root-recycling/MOVE_FAMILY_00B_IDE_MANIFEST_CONTRACT_PROJECTION_PLAN.md`

## MOVE-FAMILY-00B-PROOF TASK UPDATE

Current proof task:

```text
MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof
```

Proof target:

- prove `git ls-files ide` is empty;
- prove filesystem `ide/` is absent or empty;
- prove `ide_root` exception retirement remains valid;
- prove moved manifests under `contracts/projections/ide/**` parse;
- classify old `ide/manifests/**` references;
- run Tier 0 plus focused RepoX validation.

Next recommended task after proof:

```text
MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan
```

## NON_GOALS

- No move application.
- No file delete or rename.
- No reference rewrite.
- No compatibility shim or active path alias.
- No root exception retirement.
- No feature/domain/product/runtime implementation.
- No full CTest, full eval, CMake configure/build, product binary execution, package generation, or release generation.

## ACCEPTANCE

- Required plan artifacts exist and parse.
- Apply remains unauthorized.
- The plan names exact target paths, rewrites, validation, rollback, and exception effects.
- Validation is run and recorded.
- Only scoped planning evidence and docs are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS

## MOVE-FAMILY-00B-GATE UPDATE

- Phase: MOVE-FAMILY-00B-GATE - IDE Manifest Projection Apply Readiness Gate
- Goal: review the draft MOVE-FAMILY-00B plan and decide whether the next apply task may move only the three tracked IDE manifest files.
- Result: PASS_WITH_WARNINGS
- Authorized next task: MOVE-FAMILY-00B-APPLY - Apply IDE Manifest Projection Migration
- Authorized scope: `ide/manifests/**` to `contracts/projections/ide/**` for the three planned tracked files only.
- Move apply authorized: true, limited to MOVE-FAMILY-00B-APPLY only.
- Feature work authorized: false.
- No moves, deletes, renames, reference rewrites, aliases, maps, or exception retirements were applied by the gate.

## MOVE-FAMILY-00B-APPLY UPDATE

- Phase: MOVE-FAMILY-00B-APPLY - Apply IDE Manifest Projection Migration
- Result: PASS_WITH_WARNINGS.
- Moves applied: 3 tracked files from `ide/manifests/**` to `contracts/projections/ide/**`.
- Reference rewrite groups applied: 5.
- `git ls-files ide`: empty.
- `ide_root` exception retired after strict validators passed.
- Authorized scope consumed: true.
- Additional moves authorized: false.
- Feature work authorized: false.
- Next recommended task: MOVE-FAMILY-00B-PROOF - IDE Root Retirement Proof.

## MOVE-FAMILY-00C-PLAN TASK UPDATE

- Phase: MOVE-FAMILY-00C-PLAN - Active Validation, Meta, and Governance Tool Namespace Plan.
- Result: BLOCKED.
- Target roots inspected: `validation/`, `meta/`, `governance/`, and `performance/`.
- Active Python files found: 33.
- Package init files: 14.
- Direct CLI entrypoints under target roots: 0.
- Active Python import files: validation 8, meta 104, governance 9, performance 4.
- Planned move count: 0.
- Shim-required public surfaces: `validation`, `meta.identity`, `meta.stability`, and `governance`.
- Preserve-current groups: semantic/runtime `meta/**` and product/runtime `performance/**`.
- Move apply authorized: false.
- Feature work authorized: false.
- Next recommended task: MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan.

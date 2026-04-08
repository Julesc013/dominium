Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: authoritative next-order handoff after the final repo-structure review checkpoint; downstream of the repo-structure series packets and the pre-relayout decision checkpoint
Replacement Target: later first-slice execution receipt or explicit replacement checkpoint after RMS-001 execution
Binding Sources: `docs/repo/CHECKPOINT_C_REPO_MEGA_STRUCTURE_REVIEW.md`, `data/repo/checkpoint_c_repo_mega_structure_review.json`, `docs/repo/REPO_PHASED_MIGRATION_SHIMS_VALIDATION_AND_ROLLBACK.md`, `data/repo/repo_phased_migration_shims_validation_and_rollback.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`

# Next Execution Order Post Repo Structure Review

## Recommended Next Prompt

The recommended next prompt is:

- `REPO-MIGRATION-Ω1 — RMS-001_NO_MOVE_PATH_AUTHORITY_AND_WRAPPER_PRECEDENCE_NORMALIZATION-0`

## Is Relayout Execution Approved Now?

- `yes, but only for MP-0 / RMS-001`

Scope note:

- this is approval for the bounded no-move documentation-and-mirror slice only
- this is not approval for `RMS-002`, `MP-1`, or any physical relayout

## Immediate Post-Slice Validation Sequence

1. parse all touched JSON mirrors
2. confirm prose and machine-readable mirrors still align to live root names, ownership claims, and canonical wrapper precedence
3. run `git diff --check`
4. run `python tools/validation/tool_run_validation.py --profile FAST`
5. verify that no runtime, entrypoint, manifest, or path-resolution code was touched; if any was, stop and reclassify the work
6. roll back immediately if ambiguity increased or `FAST` regressed

## What Remains Explicitly Deferred

- all `MP-1` through `MP-5` work
- `RMS-002` and every later migration slice
- canonical playtest-path hardening itself
- `server/server_main.py` repo-root correction
- session save-root correction
- launcher supervision stabilization
- split-root convergence for `schema/` / `schemas/` and `packs/` / `data/packs/`
- any XStack/AIDE extraction or platformization work

## Why This Order Is Best

This order is best because:

- the repo-structure series is complete enough to approve a bounded first execution slice
- `RMS-001` reduces real drift without destabilizing baseline-critical runtime seams
- stopping after `RMS-001` preserves the stronger product priority: hardening one canonical repo-local playable baseline
- it prevents the repo from flattening planning, approval, and execution into one over-broad relayout step

## Follow-On Constraint

After `RMS-001` succeeds, the repo should not automatically continue to `RMS-002`.

The next broader work after the slice remains:

- canonical playable-baseline hardening and its blockers

Only after that baseline exists with fresh `FAST` and the agreed smoke slice may later relayout phases be reconsidered.

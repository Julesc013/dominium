Status: DERIVED
Last Reviewed: 2026-03-01
Scope: CTRL-4 planning vs execution baseline

# Planning vs Execution Baseline

## Plan Artifact Lifecycle
- `process.plan_create` creates deterministic `plan_artifact` rows under `universe_state.plan_artifacts`.
- Planning remains derived-only:
  - blueprint compilation, BOM estimation, and preview generation occur in `src/control/planning/plan_engine.py`.
  - no `installed_structure_instances` mutation is performed by plan creation.
- Lifecycle states in current baseline:
  - `draft`: incremental/manual edits (`process.plan_update_incremental`)
  - `validated`: new plan artifacts after policy validation
  - `approved`: execution intent accepted and compiled via Control IR
  - `executed` and `cancelled`: reserved terminal states for downstream lifecycle completion logic

## Ghost Behavior
- Ghost overlays are derived from `plan_artifact.spatial_preview_data`.
- UI path:
  - `src/client/interaction/inspection_overlays.py` adds `_plan_overlay_payload`.
  - `build_inspection_overlays` routes `plan.*`/`plan_artifacts` to the plan ghost overlay.
- Ghost overlays are explicitly marked derived-only:
  - `extensions.overlay_kind = "plan_ghost"`
  - `extensions.derived_only = true`
- Ghosts remain RenderModel overlays only; no TruthModel registration/mutation.

## Execution via Commitments
- `process.plan_execute`:
  - validates execution request with control-plane negotiation.
  - compiles plan artifact to Control IR (`build_plan_execution_ir`).
  - compiles IR via verifier/compiler path (`compile_ir_program`) with deterministic ordering.
- Emission path:
  - Control IR commitment ops become deterministic `construction_commitments`.
  - provenance events are emitted (`construction.plan.commitment_emitted`).
  - material commitment mirror state is synchronized through existing commitment sync path.
- Direct installation guard:
  - no direct structure install operation exists in the `process.plan_execute` branch.

## Manual Placement Unification
- `process.plan_update_incremental` is the canonical manual/incremental edit path.
- Manual placement updates:
  - mutate only plan artifact preview/resource summaries.
  - produce deterministic `plan.update.*` IDs.
  - keep execution separate and explicit via `process.plan_execute`.

## Inspection and Epistemic Gating
- New inspection sections:
  - `section.plan_summary`
  - `section.plan_resource_requirements`
- Inspection request target kind now includes `plan`.
- Epistemic behavior:
  - diegetic/coarse scopes receive summarized resource totals.
  - hidden-state scopes can receive full material/part breakdown.

## Extension Points (MOB Track/Vehicle Planning)
- `plan_type_id` currently supports `structure|track|road|vehicle|custom`.
- Future MOB extensions can map additional plan types to:
  - specialized IR generators
  - domain-specific commitment kinds
  - simulation-grade validation policies


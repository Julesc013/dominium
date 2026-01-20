# Render Prep Migration Guide (ADOPT2)

This guide defines the Work IR migration for render frame preparation.
Render prep is **derived work** and must be schedulable, budgeted, and degradable.

## Migration State
- **MIGRATION_STATE = IR-ONLY**
- Legacy inline prep is removed; no dual path remains.

## System Overview
`RenderPrepSystem` implements `ISimSystem` and emits Work IR tasks only.

Required identity:
- `system_id = "RENDER_PREP"` (stable hash)
- `category = DERIVED`
- `determinism_class = DERIVED`
- `law_targets = [EXEC.DERIVED_TASK, UI.PRESENTATION]`

## Task Emission
Render prep tasks:
- `OP_BUILD_VISIBILITY_MASK`
- `OP_BUILD_INSTANCE_LIST`
- `OP_BUILD_DRAW_LIST`

Each task declares:
- AccessSet reads:
  - packed ECS view set(s)
  - visibility mask buffers (read-only)
- AccessSet writes:
  - derived render buffers only
- CostModel:
  - CPU-heavy, degradable priority

Tasks are placed in phase order to avoid read/write conflicts:
- Phase 0: visibility mask
- Phase 1: instance list
- Phase 2: draw list

## Degradation Ladder
Deterministic degradation by fidelity tier:
- **focus**: full culling, instancing, and draw list
- **micro**: simplified culling, instancing, draw list
- **meso**: coarse region-level culling + draw list
- **macro**: fixed draw list only (reuses stale buffers)
- **latent**: reuse previous frame (no tasks)

Budget hints clamp task emission deterministically.
Draw list generation is prioritized so presentation remains available.

## Law & Capability Integration
Law can disable presentation (headless/server) or restrict features.
Render prep respects law by:
- emitting `UI.PRESENTATION` law targets
- allowing presentation to be disabled by policy before emission

## Execution Integration
- Render prep tasks are scheduled by the engine scheduler.
- The client consumes derived buffers when ready.
- If tasks are delayed or skipped, stale buffers are reused.

## Tests
`engine/tests/render_prep_work_ir_tests.cpp` validates:
- deterministic emission
- budget degradation
- presentation disabled -> no tasks emitted
- stale-buffer fallback behavior

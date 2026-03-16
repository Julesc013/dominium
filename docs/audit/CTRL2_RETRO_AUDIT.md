Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Scope: CTRL-2 Phase 0 retro-consistency audit
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CTRL2 Retro-Consistency Audit

## Canon Inputs
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`
- `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`
- `docs/architecture/BOUNDARY_ENFORCEMENT.md`

## Audit Method
- Automation/macro scan:
  - `rg -n "autopilot|controller|blueprint|task_tick|construction_project_tick|execute_intent\\(" src tools -g "*.py"`
- Control-plane bypass scan:
  - `rg -n "build_control_resolution\\(|execute_single_intent_srz\\(|execute_intent\\(" src tools -g "*.py"`
- Commitment linkage spot-check:
  - `src/materials/construction/construction_engine.py`
  - `src/interaction/task/task_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`

## Findings

### F1 - Construction multi-step execution is deterministic but not IR-backed
- Audit Item: blueprint-driven construction step loop
- Paths:
  - `src/materials/construction/construction_engine.py` (`create_construction_project`, `tick_construction_projects`)
  - `tools/xstack/sessionx/process_runtime.py` (`process.construction_project_create`, `process.construction_project_tick`)
- Subsystem: MAT construction runtime
- Current State:
  - Blueprint compile + AG node execution steps are handled in a deterministic process loop.
  - Commitment creation is present, but orchestration is not expressed as Control IR.
- Classification:
  - `migrate_now`
- Migration to Control IR:
  - Emit Control IR from blueprint execution planning.
  - Compile IR ops to control-plane actions for per-step commitment emission and task starts.

### F2 - Task completion queue remains runtime-local multi-step automation
- Audit Item: task completion intent queue
- Paths:
  - `src/interaction/task/task_engine.py` (`tick_tasks` returns `completion_intents`)
  - `tools/xstack/sessionx/process_runtime.py` (`pending_task_completion_intents`)
- Subsystem: ACT task runtime
- Current State:
  - Completion intents are generated/queued/executed deterministically.
  - Queue advancement is not represented as Control IR and is not statically verified against ControlPolicy.
- Classification:
  - `migrate_now`
- Migration to Control IR:
  - Represent completion transitions as bounded IR op sequences (`op.run_task`, `op.wait_event`, `op.emit_commitment`).
  - Require verifier + compiler path before enqueue/dispatch.

### F3 - Scheduler and tool UI paths still execute intents directly
- Audit Item: multi-step orchestration bypassing ControlIntent/ControlResolution in runtime tools
- Paths:
  - `tools/xstack/sessionx/scheduler.py` (`replay_intent_script_srz`, direct `execute_intent`)
  - `tools/control/control_cli.py` (`execute_single_intent_srz` with direct intent construction)
  - `tools/xstack/sessionx/ui_host.py` (`dispatch_window_action` -> `execute_single_intent_srz`)
- Subsystem: tool/runtime orchestration
- Current State:
  - Deterministic dispatch remains, but control-plane negotiation is bypassed for scripted/tool flows.
- Classification:
  - `quarantine/deprecate`
- Migration to Control IR:
  - Tool/scheduler/UI flows must emit Control IR first, then compile through control-plane resolution.

### F4 - Autopilot and AI controller runtime stubs are not yet standardized
- Audit Item: autopilot and AI controller macro behavior surfaces
- Paths:
  - `tools/control/control_cli.py` (controller command stubs)
  - `src/client/interaction/interaction_dispatch.py` (controller-facing command dispatch)
- Subsystem: control automation entrypoints
- Current State:
  - No canonical Control IR-backed autopilot/AI program builder exists yet.
  - Risk remains of bespoke per-feature automation code.
- Classification:
  - `migrate_now`
- Migration to Control IR:
  - Add canonical IR stubs for autopilot and AI controller orders.
  - Enforce verifier/compiler path for all automation and scripted multi-step behavior.

## Multi-Step Actions Without Commitments or Control Resolution
- Runtime-local queues/loops not yet IR-backed:
  - `pending_task_completion_intents` flow in `process_runtime.py`
  - construction project tick loop in `construction_engine.py`
- Tooling/script paths that bypass control-plane resolution:
  - `scheduler.py`, `control_cli.py`, `ui_host.py`

## Migration Queue (CTRL-2)
1. Add Control IR schemas + CompatX registration.
2. Add deterministic static verifier (ops, block graph, entitlement/capability closure, bounded flow).
3. Add IR compiler that always routes emitted actions through control-plane resolution.
4. Add blueprint/autopilot/AI IR builders and replace bespoke multi-step orchestration paths.
5. Extend decision log with IR execution metadata and proof hash hooks.
6. Add RepoX/AuditX enforcement for non-IR macro behavior and dynamic eval prohibition.
7. Add deterministic TestX coverage for verifier, compiler, budget, and replay equivalence.

## Invariants Mapped
- A1 Determinism primary (`constitution_v1.md` §3 A1)
- A2 Process-only mutation (`constitution_v1.md` §3 A2)
- A3 Law-gated authority (`constitution_v1.md` §3 A3)
- A5 Event-driven advancement (`constitution_v1.md` §3 A5)
- A10 Explicit degradation/refusal (`constitution_v1.md` §3 A10)

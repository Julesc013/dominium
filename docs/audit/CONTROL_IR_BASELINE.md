Status: DERIVED
Last Reviewed: 2026-03-01
Version: 1.0.0
Compatibility: Bound to `schema/control/control_ir*.schema`, `src/control/ir/*`, and control-plane decision logs.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Control IR Baseline

## Scope
- Introduce deterministic Control IR for bounded multi-step control programs.
- Enforce Control IR verification + compilation through ControlPlane resolution.
- Prevent macro behavior drift into ad hoc runtime logic.

## Invariants
- `INV-CONTROL-PLANE-ONLY-DISPATCH`
- `INV-NO-MACRO-BEHAVIOR-WITHOUT-IR`
- `INV-NO-DYNAMIC-EVAL`
- Existing deterministic ordering and canonical hash invariants remain in force.

## Control IR Op Types
- `op.acquire_pose`
- `op.release_pose`
- `op.bind_tool`
- `op.unbind_tool`
- `op.run_task`
- `op.emit_commitment`
- `op.wait_event`
- `op.check_condition`
- `op.request_view_change`
- `op.request_fidelity`
- `op.noop`

## Verification Rules
- Verifier is deterministic and pure on `(ir_program, control_policy, authority_context, capability_registry)`.
- Forbidden op types are rejected with `refusal.ctrl.ir_forbidden_op`.
- Dynamic eval/branch keys are rejected.
- Block graph must be acyclic or explicitly bounded by visit bounds.
- Static requirements must be a subset of requester entitlements and not violate policy forbids.
- Deterministic report emits:
  - `required_entitlements`
  - `required_capabilities`
  - `max_cost_estimate`
  - `deterministic_fingerprint`

## Compiler Behavior
- Compiler consumes verified IR and emits ordered control-plane resolutions.
- Deterministic op ordering follows block traversal + per-block `op_sequence`.
- RS-5 budget enforcement returns `refusal.ctrl.ir_cost_exceeded`.
- Output includes:
  - `compiled_actions`
  - `op_to_emitted`
  - `task_starts`
  - `commitment_creations`
  - `wait_conditions`
  - `decision_log_refs`
  - deterministic compile fingerprint

## Integration Points
- Blueprint execution:
  - `process.construction_project_create` now generates/stores a blueprint execution Control IR program in project extensions.
- Autopilot stub:
  - `process.control_ir.autopilot_stub` builds autopilot IR and compiles via control-plane.
- AI controller stub:
  - `process.control_ir.ai_controller_stub` builds per-order IR and compiles via control-plane.

## DecisionLog + Replay
- Control-plane decision logs now carry `extensions.control_ir_execution` context per compiled IR op:
  - `ir_id`
  - `verification_report_hash`
  - op/block/action mapping fields
- Replay reconstruction support added via:
  - `reconstruct_ir_action_sequence(decision_log_rows, ir_id)`

## Multiplayer + Proof Hooks
- Multiplayer guard validates Control IR verification for:
  - `policy.net.server_authoritative`
  - `policy.net.srz_hybrid`
  - `policy.net.lockstep`
- Ranked proof bundles include:
  - `control_ir_verification_report_hashes`
  - deterministic seed contribution hash for IR verification set

## Contract/Schema Impact
- Added/active schema contracts:
  - `control_ir` / `control_ir_block` / `control_ir_op` / `control_ir_verification_report` (`1.0.0`)
- `control_decision_log` schema shape unchanged (`extensions` open-map used for IR metadata).
- Refusal contract extended with:
  - `refusal.ctrl.ir_invalid`
  - `refusal.ctrl.ir_forbidden_op`
  - `refusal.ctrl.ir_cost_exceeded`

## Future Extensions (AI/MOB)
- Add bounded multi-block orchestration policies for squad/MOB controllers.
- Add explicit declared concurrency op semantics (currently sequential only).
- Add proof-bundle witness link to per-op decision log IDs for dispute tooling.

Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Embodied Movement Baseline (EB-3)
Status: DERIVED BASELINE  
Last Updated: 2026-02-16  
Scope: `EB-3/5` movement processes, SRZ routing, anti-cheat signal wiring, and regression checks.

## Implemented Processes
- `process.agent_move`
  - Kinematic, process-only mutation path.
  - Requires embodied target (`agent.body_id` + body assembly present).
  - Routes movement through `process.body_move_attempt` for collision mediation.
- `process.agent_rotate`
  - Quantized orientation deltas (`yaw`/`pitch`/`roll`) with deterministic integer updates.
- `process.srz_transfer_entity`
  - Explicit shard transfer process for embodied agents.
  - Controlled by deterministic policy gates (`allow_srz_transfer` / `control_policy.allow_srz_transfer`).

## Entitlement Mapping
- `process.agent_move` -> `entitlement.agent.move`
- `process.agent_rotate` -> `entitlement.agent.rotate`
- `process.body_move_attempt` -> `entitlement.control.possess`
- `process.srz_transfer_entity` -> law/profile + policy gate; transfer remains server/policy controlled.

## Ownership and Authority Enforcement
- Movement ownership checks are centralized in `_movement_context`.
- Ownership mismatch or spoofed owner claims deterministically refuse with:
  - `refusal.agent.ownership_violation`
- Unembodied movement requests deterministically refuse with:
  - `refusal.agent.unembodied`

## SRZ Routing Rules
- Hybrid routing targets `agent.shard_id` ownership.
- Wrong target shard continues to refuse with:
  - `refusal.net.shard_target_invalid`
- Boundary movement without explicit transfer process is refused by policy with:
  - `refusal.agent.boundary_cross_forbidden`

## Collision Integration
- `process.agent_move` computes world delta from quantized local input.
- Final mutation path executes `process.body_move_attempt`.
- Collision broadphase/narrowphase resolution remains deterministic and process-scoped.
- Runtime fix included in this baseline: post-collision body state is reloaded from authoritative `state.body_assemblies` to prevent stale pre-collision overwrite.

## Anti-Cheat Movement Signals
Movement-related anti-cheat signals are emitted from existing policy modules and ingresses:
- Input frequency/rate checks (tick-window based).
- Requested displacement threshold checks.
- Actual displacement behavioral checks after execution.
- Ownership/authority violation signaling through existing authority integrity handling.

Deterministic movement anti-cheat events are emitted under `ac.movement.*` reason codes and validated by TestX.

## RepoX and AuditX Guardrails
- RepoX invariants:
  - `INV-MOVE-USES-BODY_MOVE_ATTEMPT`
  - `INV-OWNERSHIP-CHECK-REQUIRED`
- AuditX analyzers:
  - `E16_MOVEMENT_BYPASS_SMELL`
  - `E17_OWNERSHIP_BYPASS_SMELL`

## Test Coverage Added
- `testx.embodiment.move_determinism`
- `testx.embodiment.move_refuse_unembodied`
- `testx.embodiment.move_refuse_ownership_violation`
- `testx.embodiment.cross_shard_move_handling`
- `testx.embodiment.movement_collision_blocking`
- `testx.embodiment.movement_anti_cheat_event`

## Validation Snapshot
- `python tools/xstack/run.py --skip-testx strict --cache off` -> pass
  - Includes registry/lockfile/session smoke, RepoX, AuditX, packaging validation, and UI bind checks.
- `python tools/xstack/testx_all.py --profile STRICT --cache off --subset ...` (EB-3 subset) -> pass (8/8)
  - Includes movement determinism, movement refusals, SRZ cross-shard handling, collision blocking, and movement anti-cheat events.

## Limitations
- No client prediction/rollback.
- No force-based physics model (kinematic movement only).
- No gameplay semantics layered onto movement (stamina/injury/damage/survival remain out of scope).
- Cross-shard movement requires explicit transfer policy/process; dynamic auto-migration is not in this baseline.

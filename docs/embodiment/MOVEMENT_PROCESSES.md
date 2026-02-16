Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: Bound to `tools/xstack/sessionx/process_runtime.py`, SRZ routing/coordinator modules, and `docs/contracts/refusal_contract.md`.

# Embodied Movement Processes

## Purpose
Define deterministic, process-only movement for embodied agents.

## Scope (EB-3)
- Kinematic movement only.
- No prediction/rollback.
- No force-based physics, friction, stamina, damage, or survival semantics.
- Movement applies through body collision substrate (`process.body_move_attempt`).

## Process IDs
1. `process.agent_move`
2. `process.agent_rotate`
3. `process.srz_transfer_entity` (explicit shard-transfer hook)

## Entitlement + Law Gates
- `process.agent_move` requires `entitlement.agent.move`.
- `process.agent_rotate` requires `entitlement.agent.rotate`.
- `process.srz_transfer_entity` requires `entitlement.control.admin`.
- All process admission remains law-gated by `LawProfile.allowed_processes`.

## Deterministic Input Rules
- Movement vectors are integer/quantized payloads.
- Tick duration is derived from simulation tick progression (`dt_ticks`/`tick_duration`), never wall clock.
- Ordering remains scheduler-driven by canonical proposal sort key.

## Movement Pipeline
1. Validate process gate (law/entitlement/privilege).
2. Validate agent ownership/control in multiplayer contexts.
3. Resolve `agent.body_id`; refuse when agent is unembodied.
4. Convert local move vector to deterministic world delta using quantized orientation mapping.
5. Dispatch through `process.body_move_attempt`.
6. Run collision resolution before commit.
7. Update agent/body linkage fields deterministically.

## SRZ Routing Rules
- Movement intents target the owning shard for the agent/body.
- Target-shard spoofing is refused (`refusal.net.shard_target_invalid`).
- Cross-shard movement without explicit transfer is refused (`refusal.agent.boundary_cross_forbidden`).
- `process.srz_transfer_entity` provides explicit, policy-gated ownership transfer.

## Refusal Codes
- `refusal.agent.unembodied`
- `refusal.agent.ownership_violation`
- `refusal.agent.boundary_cross_forbidden`
- `refusal.net.shard_target_invalid`
- Existing control/law refusals still apply:
  - `refusal.control.entitlement_missing`
  - `refusal.control.law_forbidden`

## Anti-Cheat Signal Sources
- Input integrity: movement intent frequency and malformed payload checks.
- Behavioral detection: impossible displacement/speed for configured per-tick bounds.
- Authority integrity: ownership spoof attempts and illegal override attempts.
- Sequence integrity and replay protection remain enforced at envelope ingress.

## Determinism Invariants
- Process-only mutation of agent/body transforms.
- Stable collision ordering and SRZ routing decisions.
- Hash anchor equivalence on replay for identical input scripts.
- No wall-clock values in movement admission or enforcement outcomes.

## Cross-References
- `docs/embodiment/BODY_PRIMITIVES_AND_COLLISION.md`
- `docs/embodiment/CONTROL_SUBSTRATE_DOCTRINE.md`
- `docs/net/ANTI_CHEAT_MODULES.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/law_profile.md`

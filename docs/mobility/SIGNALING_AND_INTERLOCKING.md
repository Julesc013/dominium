Status: CANONICAL
Last Reviewed: 2026-03-03
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Signaling And Interlocking (MOB-8)

## Purpose

Define deterministic, process-only network safety signaling for mobility graphs.  
MOB-8 is rail-first in policy packs, but the substrate is generic for road/air/other networked movement.

## Core Model

### Signals As State Machines
- A signal is a canonical row with:
  - identity (`signal_id`)
  - attachment (`node_id` or `edge_id`)
  - declared type/policy (`signal_type_id`, `rule_policy_id`)
  - state-machine binding (`state_machine_id`)
- Signal state is carried by the bound state machine, not by ad-hoc booleans.
- Baseline aspects:
  - `stop`
  - `caution`
  - `clear`

### Blocks
- Network edges are treated as logical safety blocks.
- Occupancy and reservations inform block availability.
- Signal policy resolves block conditions to aspects deterministically.

### Interlocking
- Switch changes are lawfully process-mediated and must pass interlocking checks.
- Interlocking rules enforce:
  - no switch throw while occupied block depends on switch path
  - no switch throw while lock is active
  - deterministic reservation conflict outcomes

## Deterministic Rules

- Signal evaluation order: sorted `signal_id`.
- State-machine transitions: deterministic transition selection and tie-breaks.
- Reservation conflict handling: stable sort by `vehicle_id`, then `reservation_id`.
- Budget degradation: deterministic deferred set ordering; no hidden background mutation.

## Process Surface

Authoritative mutations must occur through process handlers only:
- `process.signal_set_aspect`
- `process.signal_tick`
- `process.route_reserve_blocks`
- `process.switch_lock`
- `process.switch_unlock`
- `process.switch_set_state` (existing MOB-2 path, with interlocking enforcement)

No renderer/UI/tool path may mutate signal or switch truth directly.

## Safety Actions

- `stop` aspect may enforce braking/zero speed cap through effect paths.
- `caution` aspect may enforce reduced speed cap through effect paths.
- Emergency stop remains process/effect-driven and logged.
- Refusals use explicit reason codes (for example `refusal.mob.signal_violation`).

## Integration Contracts

### MOB-5 (Meso Occupancy)
- Occupancy is authoritative input for signal aspect computation.
- Reservation rows can be reused for route/block reservation semantics.

### MOB-6 (Micro Constrained Motion)
- Before edge/junction entry, solver/process checks relevant signal aspect.
- `stop` blocks entry and applies deterministic braking/speed-cap handling.
- `caution` applies deterministic speed limitation.

### CTRL Effects / Decision Logging
- Signal outcomes apply explicit effects (speed cap, warning), never silent modifiers.
- Aspect-driven control decisions are logged for audit and reenactment.

### Hazards / Maintenance
- Failure modes (signal fail, stuck switch) degrade to safe states by policy.
- Maintenance schedules are deterministic schedule-driven processes.

## Diegetic Interaction

- Switch levers and signal panels are action-surface/task mediated.
- Cab indicators expose current aspect and warnings through diegetic instrumentation.
- No omniscient state leakage outside epistemic entitlement.

## Modding And Generalization

- Types and rules are registry-driven:
  - signal type registry
  - signal rule policy registry
- Rail rules are default content policies, not hardcoded mode branches.
- Road/air signal packs can attach new policy tables without runtime refactor.

## Invariants

- A1 Determinism.
- A2 Process-only mutation.
- A4 No mode flags/profile-driven behavior.
- A10 Explicit degradation/refusal.

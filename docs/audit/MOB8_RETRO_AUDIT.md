Status: AUDIT
Scope: MOB-8 signaling/interlocking retrofit
Date: 2026-03-03
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MOB8 Retro Audit

## Audit Method
- Scanned runtime/process paths:
  - `process.switch_set_state`
  - `process.mobility_route_query`
  - `process.travel_tick`
  - `process.mobility_micro_tick`
- Scanned mobility modules for signal/interlocking abstractions:
  - `src/mobility/network/*`
  - `src/mobility/travel/*`
  - `src/mobility/traffic/*`
  - `src/mobility/micro/*`

## Findings

### F1 - Switch state exists, but no generalized signal substrate
- Existing:
  - MOB-2 switch state machines are present (`mobility_switch_state_machines`).
  - Switch changes flow through `process.switch_set_state` + `apply_transition`.
- Gap:
  - No canonical `signal` rows.
  - No signal rule policy registry execution path.
  - No signal aspect state-machine layer for stop/caution/clear.

### F2 - No explicit interlocking lock model
- Existing:
  - Switch transition validation checks transition legitimacy only.
- Gap:
  - No switch lock rows/processes.
  - No lock refusal in `process.switch_set_state` for occupied/reserved routes.

### F3 - Occupancy exists but not bound to a signaling policy
- Existing:
  - MOB-5 occupancy/capacity rows (`edge_occupancies`) are authoritative.
  - Reservations exist (`mobility_reservations`) and deterministic conflict handling is implemented.
- Gap:
  - No deterministic mapping from occupancy/reservation to signal aspects.
  - No route/block reservation process dedicated to interlocking semantics.

### F4 - Micro movement can hand off across junctions without signal gating
- Existing:
  - MOB-6 handoff resolves outgoing geometry via switch state (`_next_geometry_candidate`).
- Gap:
  - No signal stop/caution check before edge/junction entry.
  - No policy-driven stop/go enforcement (only geometric block/end behavior).

### F5 - No diegetic signal interaction objects
- Existing:
  - Switch operations are process-driven.
- Gap:
  - No signal panel/lever action-surface projection specific to signaling.
  - No canonical cab signal indicator rows.

### F6 - Failure/maintenance hooks are not wired to signaling
- Existing:
  - Generic hazard and schedule systems exist.
- Gap:
  - No signal failure hazard mapping (stuck signal, stuck switch).
  - No signal maintenance schedule process/event stream.

## Migration Plan
1. Introduce canonical signal + rule policy + block reservation schemas/registries.
2. Implement deterministic signal engine over existing occupancy/switch/reservation state.
3. Add process-only signaling APIs:
   - `process.signal_set_aspect`
   - `process.signal_tick`
   - `process.route_reserve_blocks`
   - `process.switch_lock`
   - `process.switch_unlock`
4. Enforce interlocking in `process.switch_set_state`:
   - refuse on lock/occupancy/reservation conflict.
5. Gate MOB-6 junction entry using signal aspect -> effect-based stop/caution handling.
6. Add diegetic signal interaction/instrument projection rows.
7. Add hazard + maintenance hooks for signals/switches.
8. Add RepoX/AuditX enforcement to prevent ad-hoc stop/interlocking logic.

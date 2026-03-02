# Meso Traffic Model Doctrine

Status: CANONICAL
Last Updated: 2026-03-02
Scope: MOB-5 deterministic meso occupancy/capacity/congestion layer for mobility.

## 1) Purpose

Meso traffic provides scalable shared-edge movement semantics between macro itineraries and future micro solvers.
It tracks edge occupancy/capacity, computes deterministic congestion penalties, and feeds macro travel execution without global micro simulation.

## 2) Edge Occupancy Model

Each mobility edge has canonical meso state:

- `edge_id`
- `capacity_units`
- `current_occupancy`
- `congestion_ratio = current_occupancy / max(1, capacity_units)`

Rules:

- Occupancy is authoritative state and process-mutated only.
- Capacity comes from edge payload/static spec fallback when available.
- Occupancy changes occur at travel edge transitions (`edge_enter`/`edge_exit`), never via renderer/UI.

## 3) Congestion Delay Policy

Travel-time adjustment uses a deterministic multiplier function:

- If `congestion_ratio <= 1.0`: `multiplier = 1.0`
- If `congestion_ratio > 1.0`: `multiplier = 1.0 + k * (congestion_ratio - 1.0)`

Where:

- `k` is a policy parameter from congestion policy registry.
- Effective speed: `adjusted_speed = base_speed / multiplier`
- Effective edge ETA: deterministic fixed-point/ceil integer ticks from adjusted speed.

No stochastic traffic perturbation is allowed.

## 4) Reservation Model (Optional)

Reservations are commitment-backed claims on edge capacity in a tick window:

- `vehicle_id`, `edge_id`, `start_tick`, `end_tick`
- deterministic conflict resolution (sorted by `vehicle_id`, then reservation id)
- refusal on overflow:
  - `refusal.mob.reservation_conflict`

Reservations may be attached during itinerary planning or dispatch workflows.

## 5) Deterministic Update Rules

- Vehicle processing order is sorted by `vehicle_id`.
- Occupancy updates and reservation checks follow stable ordering.
- Budget degradation is deterministic:
  - bounded vehicles processed per tick
  - deferred vehicles processed later in stable order
  - no silent drops; degrade outcomes logged.

## 6) Control, Authority, and Logging

- All occupancy/reservation mutation occurs through process runtime.
- Congestion-induced delays must emit explicit travel events (no silent itinerary edits).
- Decision/fidelity logs capture congestion-induced degradation or fairness policy outcomes.

## 7) Multiplayer and Fairness

- Authoritative/hybrid: server computes occupancy and congestion outcomes.
- Lockstep: deterministic ordering and formulas must produce identical state.
- Ranked fairness policy can enforce strict deterministic arbitration for reservations/departures.

## 8) Non-Goals (MOB-5)

- No micro kinematic body simulation.
- No signal interlocking solver (MOB-8).
- No wall-clock dependence.

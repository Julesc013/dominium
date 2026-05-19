Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MESO_TRAFFIC_BASELINE

Status: BASELINE
Last Updated: 2026-03-02
Scope: MOB-5 meso occupancy, congestion, reservations, and macro-travel integration.

## 1) Occupancy Model

- Canonical edge occupancy rows are process-owned and deterministic:
  - `edge_id`
  - `capacity_units`
  - `current_occupancy`
  - `congestion_ratio`
- Occupancy state is stored in `state.edge_occupancies`.
- Occupancy is updated via travel edge transitions only (no render/UI mutation path).
- Deterministic ordering:
  - vehicle traversal order by `vehicle_id`
  - canonical row normalization by `edge_id`

## 2) Congestion Function

- Congestion policy rows are resolved from `congestion_policy_registry`.
- Deterministic multiplier function:
  - ratio `<= 1.0`: multiplier `1.0` (`1000` permille)
  - ratio `> 1.0`: `1 + k * (ratio - 1)` (permille math; `k` from policy parameters)
- Effective travel speed uses deterministic integer math:
  - `adjusted_speed_mm_per_tick = floor(base_speed * 1000 / multiplier_permille)`
- Congestion is integrated in `tick_macro_travel` and exposed in travel state/events.

## 3) Reservation Semantics

- Reservation process:
  - `process.mobility_reserve_edge`
- Reservation rows:
  - `reservation_id`
  - `vehicle_id`
  - `edge_id`
  - `start_tick`
  - `end_tick`
- Conflict policy:
  - deterministic overlap detection
  - deterministic ordering by `vehicle_id` and reservation ID
  - explicit refusal on overflow:
    - `refusal.mob.reservation_conflict`
- Strict fairness mode:
  - `cong.rank_strict_fair` deterministic rank arbitration
  - deterministic displacement metadata (`displaced_reservation_ids`)

## 4) Travel Integration

- `process.travel_tick` integration:
  - resolves/normalizes edge occupancy for active mobility graphs
  - resolves congestion policy and applies congestion-adjusted edge ETA
  - emits explicit congestion delay events:
    - `travel_event.kind = "delay"`
    - `details.reason = "event.delay.congestion"`
  - updates `state.edge_occupancies`
  - records congestion decision entries in:
    - `state.mobility_traffic_decision_logs`
    - fidelity decision logs via downgrade entries
- No silent itinerary rewrites were introduced.

## 5) UX and Inspection

- Inspection sections integrated:
  - `section.mob.edge_occupancy`
  - `section.mob.congestion_summary`
- Overlay metadata integrated for mobility graph views:
  - occupancy bar overlays
  - congestion heat materials
  - station-board delayed markers
- All outputs remain derived/inspection surfaces only.

## 6) Multiplayer, Fairness, and Budgeting

- Server-authoritative occupancy + congestion execution preserved.
- Lockstep determinism preserved by stable ordering and integer math.
- Deterministic degradation under budget constraints:
  - bounded `max_vehicle_updates_per_tick`
  - stable deferred vehicle ordering
  - explicit budget outcomes in runtime metadata and decision logs
- Ranked fairness hooks use `cong.rank_strict_fair` policy in reservation/departure ordering.

## 7) Extension Notes

- MOB-8 signals/interlocking:
  - occupancy and reservation rows provide deterministic contention primitives for edge availability.
- MOB-6 micro handoff:
  - macro/meso congestion outputs (delay events, occupancy, multiplier state) are available for ROI handoff policy.
- No global micro motion simulation is introduced by MOB-5.

## 8) Gate Runs (2026-03-02)

- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `pass` (warn findings only; no refusal)
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `pass` (scan executed; findings reported)
- TestX (MOB-5 subset):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset testx.mobility.traffic.occupancy_deterministic,testx.mobility.traffic.congestion_multiplier,testx.mobility.traffic.reservation_conflict,testx.mobility.traffic.delay_event_logged,testx.mobility.traffic.budget_degrade_stable`
  - status: `pass` (5/5)
- strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob5 --cache on --format json`
  - status: `complete` (`result=complete`)
- topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - status: `complete` (`node_count=2395`, `edge_count=104949`)
  - deterministic fingerprint: `2fe4cd40728d6c9a8cd1acc60a10f6044cac54dc00c6ba3eab3804107746061a`

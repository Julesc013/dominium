# Macro Travel Model Doctrine

Status: CANONICAL
Last Updated: 2026-03-02
Scope: MOB-4 commitment-driven macro mobility travel over MobilityNetworkGraph.

## 1) Purpose

Macro travel defines deterministic, watchable movement for large-scale simulation where most vehicles run outside ROI micro simulation.
Authoritative travel is process-driven and commitment-backed.

## 2) Itinerary Model

An itinerary is an ordered network path with deterministic timing metadata.

Required structure:
- ordered `route_edge_ids`
- ordered `route_node_ids`
- `departure_tick`
- `estimated_arrival_tick`
- `speed_policy_id`

Construction:
- created only by `process.itinerary_create`
- route source: MobilityNetworkGraph (ABS routing engine)
- tie-break policy: deterministic lexicographic routing contracts from ABS

## 3) Travel Commitments

Macro travel lifecycle is commitment-backed:
- `depart`
- `waypoint` (intermediate edge/node milestones)
- `arrive`

Rules:
- commitments are canonical records
- all transitions emit provenance-backed travel events
- status changes are deterministic and tick-driven

## 4) Macro Motion State Representation

Vehicles in macro tier store movement as network references, not micro body simulation.

Macro state fields:
- `itinerary_id`
- `eta_tick`
- `current_edge_id`
- `progress_fraction_q16` (deterministic fixed-point progress)

Constraints:
- no wall-clock dependence
- no renderer/UI mutation path
- no hidden teleport updates

## 5) Spec Compatibility Contract

Route assignment must pass vehicle/edge compatibility checks before itinerary creation and travel start.

Checks:
- gauge compatibility
- clearance compatibility (stub metrics permitted)
- policy-specific speed constraints

Failure path:
- deterministic refusal `refusal.mob.spec_noncompliant`

## 6) Control Plane and Authority

All macro travel mutation must execute via control intents and process runtime:
- direct driver destination setting
- autopilot/scheduler dispatch
- plan execution conversion to travel intents

No direct movement mutation from UI, render, or tooling paths is allowed.

## 7) Timetables and ScheduleComponent

Timetables are schedule rows that trigger travel start intents/processes at deterministic ticks.

Usage:
- trains, buses, flights, shipping, and other network-compatible services
- dispatcher institutions can author schedules through control plane surfaces

## 8) Watchability and Reenactment

Travel is event-sourced for inspection and reenactment.

Event kinds include:
- `depart`
- `edge_enter`
- `edge_exit`
- `arrive`
- `delay`
- `incident_stub`

Minimum replay anchors:
- itinerary id
- vehicle id
- tick
- edge geometry refs
- planned speed policy

## 9) Determinism and Performance

Determinism:
- processing order by `vehicle_id`, `itinerary_id`, and commitment/event ids
- deterministic degradation when budget-limited (defer updates in stable sorted order)

Performance:
- macro updates only
- no global micro physics
- budget decisions logged in DecisionLog/Fidelity pathways
- server-authoritative travel tick in hybrid/networked sessions
- lockstep-safe deterministic advancement in synchronized sessions
- optional deterministic far-vehicle cadence buckets:
  non-ROI vehicles may update every `N` ticks by stable vehicle-id hash bucket
  while ROI vehicles keep full cadence

## 10) Non-Goals (MOB-4)

- no micro driving/vehicle physics
- no congestion solver
- no signal interlocking solver
- no wall-clock time integration

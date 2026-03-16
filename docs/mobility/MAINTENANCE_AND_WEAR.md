Status: CANONICAL
Last Reviewed: 2026-03-03
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Maintenance And Wear (MOB-9)

## Purpose

Define deterministic, process-only mobility wear and maintenance for infrastructure and vehicles.
MOB-9 extends existing MAT maintenance substrate with mobility-targeted wear accumulation, hazard coupling, and service workflows.

## Core Model

### Wear Accumulation Drivers
- Wear updates are deterministic functions of:
  - load cycles and stress context (MECH summaries)
  - traffic/traversal activity (MOB-4/5 events)
  - environmental exposure (FIELD values)
  - explicit braking/operational usage (micro controls)
- No wall-clock inputs and no hidden background mutation.

### Hazard Families
Mobility wear maps to hazard families:
- `hazard.track_wear`
- `hazard.wheel_wear`
- `hazard.brake_wear`
- `hazard.signal_wear`
- `hazard.switch_wear`

Threshold crossing behavior is deterministic and process-mediated.

### Canonical Wear State
A mobility wear row is keyed by target + wear type:
- `target_id` (edge/node/vehicle scoped id)
- `wear_type_id`
- `accumulated_value`
- `last_update_tick`
- deterministic fingerprint

Rows are updated only by authoritative process execution.

## Process Surface

Authoritative mutation paths:
- `process.mobility_wear_tick`
- `process.mob_failure`
- `process.mob_track_failure`
- `process.inspect_track`
- `process.service_track`
- `process.inspect_vehicle`
- `process.service_vehicle`

These paths integrate with existing MAT maintenance and hazard infrastructure, not duplicate it.

## Integration Contracts

### MECH Integration
- Structural stress/load context contributes deterministic wear increments.
- Higher stress ratios increase accumulation slope, never mutate wear silently.

### FIELD Integration
- Moisture/corrosive exposure scales wear accumulation.
- Friction/traction context influences brake and track wear accumulation.

### MOB-6 Derailment Coupling
- Track wear lowers effective derailment threshold via deterministic wear modifier.
- Derailment reason/event metadata includes wear context snapshot.

### MOB-8 Signals/Switches
- Signal/switch wear rows can trigger hazard/degraded state.
- Interlocking still remains state-machine/policy driven.

## Inspection and Service

### Inspection
- Inspection processes produce deterministic summary payloads:
  - wear levels by type
  - quantized risk bands
  - next due service hints
- Precision remains subject to epistemic policy.

### Service
- Service reduces wear by deterministic reset fraction.
- Service runs through control/process layer and may consume materials through MAT pathways.
- No direct row mutation outside process handlers.

## Determinism and Budget

- Wear updates are sorted by `(target_id, wear_type_id)`.
- Budget pressure degrades deterministically by deferring a suffix of sorted updates.
- Deferred updates are explicit in metadata/decision logs.

## Invariants

- A1 Determinism.
- A2 Process-only mutation.
- A5 Event-driven advancement.
- A10 Explicit degradation/refusal.
- No train-only branch logic; all behavior is target/spec/policy driven.

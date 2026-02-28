Status: STANDARD
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: ABS-4 unified behavioral component substrate.

# Behavioral Components Standard

## 1) Purpose
This standard defines the canonical reusable behavioral components for deterministic stateful behavior across domains.

## 2) ConstraintComponent
- Constraint components declare relation contracts, not simulation physics.
- Required fields:
  - `constraint_type_id`
  - `participant_ids`
  - `parameters`
  - `enforcement_policy_id`
  - `active`
- Applicable uses:
  - guide geometry constraints
  - docking and mounting
  - sealing
  - coupling
- Tier behavior:
  - Micro: concrete enforcement in ROI.
  - Meso/Macro: policy approximations and consistency checks only.
- Determinism:
  - evaluation order by `constraint_id`
  - participant ordering canonicalized lexicographically

## 3) StateMachineComponent
- State machines are the only canonical mutable state transition model for discrete behavioral modes.
- Required fields:
  - `machine_id`
  - `machine_type_id`
  - `state_id`
  - `transitions` (transition ids)
- Transition records define:
  - `from_state`
  - `to_state`
  - `trigger_process_id`
  - optional deterministic guard conditions
- Rules:
  - transitions are process-triggered only
  - conflict resolution is deterministic (`priority`, then `transition_id`)
  - ad-hoc state flags outside component contract are forbidden

## 4) HazardModelComponent
- Hazard models unify accumulation and threshold-trigger behavior.
- Required fields:
  - `hazard_type_id`
  - `target_id`
  - `accumulation`
  - `threshold`
  - `consequence_process_id`
  - `active`
- Default triggering mode is deterministic threshold crossing.
- Named RNG may be used only when explicitly enabled by policy.
- Hazards are ordered by `hazard_id` for deterministic tick behavior.

## 5) ScheduleComponent
- Schedules provide deterministic recurrence and due-tick evaluation.
- Required fields:
  - `start_tick`
  - `recurrence_rule`
  - `next_due_tick`
  - `cancellation_policy`
  - `active`
- Due handling:
  - emits deterministic schedule due events/process triggers
  - recurrence progression is deterministic and policy-bound
- Schedule ordering is by `schedule_id`.

## 6) Budget and Degradation
- All component engines must provide deterministic budget handling.
- Degradation rule:
  - process first N entries in canonical order
  - defer remainder without mutation
  - emit budget outcome metadata for inspection/audit

## 7) Integration Contracts
- RS-2: consequences and transformations stay ledger-accounted via processes.
- MAT-8: due events and state transitions remain commitment/provenance-linkable.
- RS-5: component tick paths are cost-unit metered and degrade deterministically.

## 8) Migration Requirements
- MAT-6 decay/failure/maintenance must use:
  - `HazardModelComponent` for wear/failure accumulation
  - `ScheduleComponent` for maintenance interval due evaluation
  - `StateMachineComponent` for asset-level state transitions
- INT portal states must use `StateMachineComponent`.
- New domain logic must not duplicate ad-hoc schedulers/state machines/hazard loops.

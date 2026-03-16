Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Task And Work Model

Status: Constitutional (ACT-3)
Version: 1.0.0

## Purpose
Task is the universal deterministic work primitive for time-bearing interaction. It binds ActionSurface affordances and tool effects to commitment-linked, reenactable progress timelines.

## Task Definition
- Task is a deterministic progress container.
- Task is created from:
  - `ActionSurface` (`surface_id`, optional)
  - completion `process_id`
  - tool/effect parameters
  - actor subject context
- Task executors can be:
  - embodied agent
  - cohort/macro executor
  - machine/port executor

## Execution Model
- Lifecycle states:
  - `planned`
  - `running`
  - `paused`
  - `completed`
  - `failed`
  - `cancelled`
- Canonical flow:
  - start -> progress -> complete
- Tasks are interruptible and resumable.
- Progress is deterministic fixed-point and tick-based (`dt_sim` quantized to ticks).

## Process-Only Mutation
- Tasks do not directly mutate TruthModel domain outcomes.
- Completion and milestone outputs are emitted as process intents.
- Authoritative mutation remains process runtime responsibility (A2).

## ActionSurface Integration
- Selecting an affordance tied to `(surface_id, process_id)` may create a task instead of immediate completion process execution.
- Tool effect parameters are copied into task parameters for deterministic progression.
- Task type resolution is registry-driven (`task_type_registry`) and surface-aware.

## Budgeting And Degradation
- Task ticking consumes deterministic cost units per tick.
- Budget pressure degrades deterministically by pausing lower-priority tasks first (stable ordering).
- No wall-clock dependence is allowed.

## Commitments And Causality
- Under causality strictness requiring commitments, task creation also creates a linked commitment.
- Task events and linked commitment IDs preserve “nothing just happens” traceability.

## Reenactment
- Task progress emits deterministic events (`task_started`, `task_progress`, `task_completed`).
- Task timelines are exportable as derived artifacts and can feed reenactment tooling.

## Diegetic Outputs
- Optional channels:
  - `ch.diegetic.task.progress`
  - `ch.diegetic.task.status`
- Diegetic default is coarse status.
- Lab/admin can access numeric progress where law/entitlement allows.

## Non-Goals
- No inventory/crafting.
- No skill trees.
- No nondeterministic success chance.
- No direct UI mutation of authoritative truth.

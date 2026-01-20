# Agent Work IR Guide (ADOPT6)

This guide defines the authoritative AgentSystem Work IR contract for
planning, doctrine, and aggregation. Agents are optional, law-governed
command emitters; they never mutate authoritative state directly.

## Scope

- Authoritative system with ORDERED determinism class.
- IR-only migration state.
- Event-driven planning; no per-tick agent loops.
- Zero-agent runs must remain valid.

## Task Structure

AgentSystem emits tasks in a fixed, deterministic order:

Planning pipeline:
1) `DOM_AGENT_TASK_EVALUATE_GOALS`
2) `DOM_AGENT_TASK_PLAN_ACTIONS`
3) `DOM_AGENT_TASK_VALIDATE_PLAN`
4) `DOM_AGENT_TASK_EMIT_COMMANDS`

Doctrine pipeline:
5) `DOM_AGENT_TASK_APPLY_DOCTRINE`
6) `DOM_AGENT_TASK_UPDATE_ROLES`

Aggregation pipeline:
7) `DOM_AGENT_TASK_AGGREGATE_COHORTS`
8) `DOM_AGENT_TASK_REFINE_INDIVIDUALS`
9) `DOM_AGENT_TASK_COLLAPSE_INDIVIDUALS`

Each task declares:
- AccessSets with explicit reads/writes.
- CostModels with bounded CPU/memory/bandwidth.
- Stable task IDs and commit ordering keys.

## Scheduling Rules

- `next_due_tick` is event-driven by schedules, doctrine updates, and
  aggregation cadence.
- Task emission order is deterministic and stable across runs.
- Planning tasks must complete before command emission.

## Aggregation & Degradation

- Aggregation uses explicit thresholds and cohort policies.
- Refinement and collapse are deterministic and reversible.
- Degradation increases cadence and reduces per-tick slices; it never
  fabricates outcomes or bypasses law gates.

## Law & Capability Integration

- Capability law gates plan validation and command emission.
- Policy law can disable autonomy domains or forbid specific actions.
- Refusals must be auditable; no silent fallbacks are allowed.

## Optionality & Absence

- When agents are disabled, no agent tasks are emitted.
- Simulation remains valid with zero agents.
- Derived systems must not assume agent activity.

## Anti-Patterns (Forbidden)

- Per-tick agent loops or global scans.
- Direct state mutation from agent logic.
- Nondeterministic planning or unordered reductions.
- Bypassing Work IR for "fast" autonomy.

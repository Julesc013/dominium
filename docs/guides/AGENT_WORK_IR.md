# Agent Work IR Guide (ADOPT6)

Scope: authoritative agent Work IR emission for planning, doctrine, aggregation.

## Invariants
- Agents never mutate authoritative state directly.
- Emission is deterministic and law-gated.
- Zero-agent runs are valid.

## Dependencies
- `docs/guides/WORK_IR_EMISSION_GUIDE.md`
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/LIFE_AND_POPULATION.md`

This guide defines the authoritative AgentSystem Work IR contract for
planning, doctrine, and aggregation. Agents are optional, law-governed
command emitters; they never mutate authoritative state directly.

## Scope

- Authoritative system with ORDERED determinism class.
- IR-only migration state.
- Event-driven planning; no per-ACT agent loops.
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

- `next_due_act` (legacy field name: `next_due_tick`, deprecated terminology) is event-driven by schedules, doctrine updates, and
  aggregation cadence.
- Task emission order is deterministic and stable across runs.
- Planning tasks must complete before command emission.

## Aggregation & Degradation

- Aggregation uses explicit thresholds and cohort policies.
- Refinement and collapse are deterministic and contract-driven.
- Degradation increases cadence and reduces per-ACT slices; it never
  fabricates outcomes or bypasses law gates.

## Law & Capability Integration

- Capability law gates plan validation and command emission.
- Policy law can disable autonomy domains or forbid specific actions.
- Refusals must be auditable; no silent fallbacks are allowed.

## Optionality & Absence

- When agents are disabled, no agent tasks are emitted.
- Simulation remains valid with zero agents.
- Derived systems must not assume agent activity.

## Forbidden assumptions

- Per-ACT agent loops or global scans.
- Direct state mutation from agent logic.
- Nondeterministic planning or unordered reductions.
- Bypassing Work IR for "fast" autonomy.

## See also
- `docs/architecture/REALITY_LAYER.md`

Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AGENT1 — Goals, Planning, and Scheduling

Status: draft
Version: 1

## Purpose
Define the AGENT1 implementation contract for deterministic goal evaluation and
bounded planning. Agents issue standard CommandIntents only and never mutate
simulation state directly.

## Scope (AGENT1)
- Goal evaluation from epistemic context.
- Bounded plan generation with fixed limits.
- Event-driven scheduling (next_think_act).
- Epistemic belief updates from outcomes.

## Canonical modules
- `game/agents/agent_goal.*`
- `game/agents/agent_evaluator.*`
- `game/agents/agent_planner.*`
- `game/agents/agent_schedule.*`
- `game/agents/agent_belief_update.*`

Public headers live in `game/include/dominium/agents/`.

## Determinism rules
- Goal selection uses stable ordering and fixed-point scoring.
- Planning is bounded and deterministic for identical inputs.
- No floats, OS time, or nondeterministic RNG in agent logic.
- Batch vs step equivalence must hold for scheduling.

## Epistemic constraints
- Agents operate only on beliefs and knowledge masks.
- Failures update beliefs deterministically.
- No omniscient access or UI-driven shortcuts.

## Refusal codes (AGENT1)
- `GOAL_NOT_FEASIBLE`
- `INSUFFICIENT_CAPABILITY`
- `INSUFFICIENT_AUTHORITY`
- `INSUFFICIENT_KNOWLEDGE`
- `PLAN_EXPIRED`

## Scheduling rules
- Agents are scheduled via `next_think_act` only.
- No per-tick thinking loops.
- Only due agents are processed by the scheduler.

## Tests (AGENT1)
Implemented in `game/tests/agent1_goal_planning_tests.cpp`:
- Deterministic goal selection.
- Bounded planning limits.
- Epistemic failure and belief update.
- Batch vs step equivalence for scheduling.
- Agent absence behavior.
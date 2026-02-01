Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# AGENT3 — Aggregation, Refinement, and Scale

Status: draft
Version: 1

## Purpose
Define how agents scale to massive populations via aggregation while remaining
deterministic, event-driven, and optional for gameplay.

## Scope (AGENT3)
- Aggregate agent representations for cohorts.
- Deterministic refinement and collapse transitions.
- Aggregate beliefs and goals.
- Event-driven scheduling for transitions.

## Canonical modules
- `game/agents/aggregate_beliefs.*`
- `game/agents/aggregate_goals.*`
- `game/agents/agent_aggregate.*`
- `game/agents/agent_refinement.*`
- `game/agents/agent_collapse.*`

Public headers live in `game/include/dominium/agents/`.

## Determinism rules
- Aggregation is order-independent.
- Refinement selection is stable by role rank and agent_id.
- Collapse preserves counts and uncertainty bounds.
- Batch vs step equivalence required.

## Refusal codes (AGENT3)
- `AGGREGATION_NOT_ALLOWED`
- `REFINEMENT_LIMIT_REACHED`
- `COLLAPSE_BLOCKED_BY_INTEREST`
- `AGENT_STATE_INCONSISTENT`

## Refinement/collapse triggers
- Interest set escalation triggers refinement.
- Interest loss triggers collapse.
- No per-tick agent scanning.

## Epistemic constraints
- Aggregate beliefs are less precise than individual beliefs.
- Refinement restores precision deterministically.
- UI visibility remains epistemically gated.

## Tests (AGENT3)
Implemented in `game/tests/agent3_aggregation_tests.cpp`:
- Aggregate vs individual equivalence.
- Deterministic refinement selection.
- Deterministic collapse summaries.
- No agent presence requirement.
- Batch vs step equivalence for transitions.
--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Aggregation rules, goal evaluation, and plan issuance.
SCHEMA:
- Aggregate agent formats, constraints, and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No agent-only mechanics or hidden simulation shortcuts.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_AGGREGATION - Aggregate Agents (AGENT3)

Status: draft
Version: 1

## Purpose
Define aggregate agents that represent cohorts or role groups at macro scale.
Aggregate agents use the same goal evaluation and planning logic as individuals.

## AggregateAgent schema
Required fields:
- aggregate_agent_id
- cohort_ref
- doctrine_ref
- belief_summary
- goal_summary
- next_think_act
- provenance_ref

Recommended fields:
- cohort_count
- refined_count
- active_goal_ref
- active_plan_ref

## Aggregation rules
- Aggregate agents issue standard CommandIntents only.
- No new command types are introduced.
- Aggregates are deterministic summaries of individual states.
- Aggregate beliefs are less precise and include uncertainty bounds.

## Determinism rules
- Aggregation is order-independent.
- Selection and planning use stable ordering.
- No per-tick thinking loops.

## Refusal codes
- AGGREGATION_NOT_ALLOWED
- AGENT_STATE_INCONSISTENT

## Prohibitions
- No fabrication of goals or outcomes.
- No hidden AI shortcuts.

## Test plan (spec-level)
Required scenarios:
- Aggregate vs individual equivalence in goal selection.
- Deterministic aggregation from permuted inputs.
- Batch vs step equivalence for aggregate decision schedules.

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Planning rules, bounded search limits, and schedule integration.
SCHEMA:
- Agent plan and schedule formats, constraints, and versioning metadata.
TOOLS:
- Future editors/validators only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No agent-only mechanics or global planners.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_PLANNING - Agent Planning (AGENT1)

Status: draft
Version: 1

## Purpose
Define deterministic, bounded planning outputs and scheduling for agents.
Plans emit standard CommandIntents and do not mutate state directly.

## AgentPlan schema
Required fields:
- plan_id
- goal_id
- steps (bounded list of CommandIntent templates)
- estimated_costs (time/resources; estimates only)
- estimated_duration_act
- next_due_tick
- provenance_ref

Recommended fields:
- created_act
- expiry_act
- scope_ref

## AgentSchedule schema
Required fields:
- agent_id
- next_think_act
- active_goal_ref (optional)
- active_plan_ref (optional)

Optional fields:
- think_interval_act
- provenance_ref

## Planning rules
- Planning is bounded by max steps and depth.
- No global search or world graph traversal.
- Use only known locations, actors, and resources.
- Output is a sequence of standard CommandIntents.

## Scheduling rules
- Thinking occurs only at next_think_act or on belief updates.
- Agents wait for command outcomes; no per-tick simulation.
- Batch vs step equivalence must hold for scheduling.

## Determinism and epistemics
- Plans must be deterministic from identical beliefs and inputs.
- Belief updates come only via INF systems and command outcomes.
- Agents may act on false beliefs; no auto-correction to truth.

## Refusal codes
- GOAL_NOT_FEASIBLE
- INSUFFICIENT_CAPABILITY
- INSUFFICIENT_AUTHORITY
- INSUFFICIENT_KNOWLEDGE
- PLAN_EXPIRED

## Integration points
- Commands: `docs/SPEC_COMMAND_MODEL.md`
- Epistemics: `docs/SPEC_EPISTEMIC_INTERFACE.md`
- Scheduling: `docs/SPEC_SCHEDULING.md`
- Determinism: `docs/SPEC_DETERMINISM.md`

## Test plan (spec-level)
Required scenarios:
- Bounded planning stops at limits.
- Deterministic planning output from identical inputs.
- Batch vs step equivalence for scheduling.
- Epistemic failure leads to refusal and belief update.

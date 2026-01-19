--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Goal evaluation rules, priority calculation, and refusal handling.
SCHEMA:
- Agent goal formats, constraints, and versioning metadata.
TOOLS:
- Future editors/validators only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No omniscient access or hidden AI advantages.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_GOALS - Agent Goals (AGENT1)

Status: draft
Version: 1

## Purpose
Define the AgentGoal data model used for deterministic goal evaluation.
Goals are data-only intentions evaluated by agents, never a simulation shortcut.

## AgentGoal schema
Required fields:
- goal_id
- type
- priority (bounded fixed-point or bucket)
- preconditions (capability/authority/knowledge)
- satisfaction_criteria (tags or flags)
- expiry_act (optional)
- provenance_ref

Recommended fields:
- scope_ref (locality/org/role)
- creation_act

## Goal types
Canonical types:
- survive
- acquire
- defend
- migrate
- research
- trade

No goal implies simulation state changes without CommandIntents.

## Preconditions
Preconditions are deterministic and explicit:
- required_capabilities
- required_authority
- required_knowledge

Failure to meet preconditions MUST emit refusal codes, never implicit success.

## Priority rules
- All priority evaluation is deterministic and bounded.
- Fixed-point or bucket values only; floats are forbidden.
- Priority must not depend on omniscient state.

## Refusal codes
- GOAL_NOT_FEASIBLE
- INSUFFICIENT_CAPABILITY
- INSUFFICIENT_AUTHORITY
- INSUFFICIENT_KNOWLEDGE
- PLAN_EXPIRED (when goal expiry blocks planning)

## Determinism and performance rules
- Goals evaluated only on schedule or belief change; no per-tick loops.
- No global iteration to discover goals.
- Stable ordering by goal_id for ties.

## Integration points
- Commands: `docs/SPEC_COMMAND_MODEL.md`
- Epistemics: `docs/SPEC_EPISTEMIC_INTERFACE.md`
- Scheduling: `docs/SPEC_SCHEDULING.md`
- Provenance: `docs/SPEC_PROVENANCE.md`

## Test plan (spec-level)
Required scenarios:
- Deterministic goal selection from identical inputs.
- Refusal on missing capability/authority/knowledge.
- Batch vs step equivalence for scheduled evaluation.

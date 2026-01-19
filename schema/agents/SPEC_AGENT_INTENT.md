--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Intent generation policy and command validation rules.
SCHEMA:
- Agent intent formats and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No agent-specific command bypasses.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_INTENT - Agent Intent (AGENT0)

Status: draft
Version: 1

## Purpose
Define agent intents as command proposals identical to player-issued intents.

## AgentIntent schema
Required fields:
- intent_id
- agent_id
- context_ref
- command_intent_ref
- issued_at_act
- desired_execute_act
- refusal_codes_allowed (bounded list)
- provenance_ref

Rules:
- command_intent_ref points to CMD0 intents; no special fields for agents.
- desired_execute_act is a request; scheduling remains authoritative.
- refusal_codes_allowed defines explicit refusal handling.

## IntentQueue schema
Required fields:
- queue_id
- agent_id
- intent_ids (bounded list)
- next_due_tick
- provenance_ref

Rules:
- Intent queues are deterministic and ordered by intent_id.
- Queue processing is event-driven.

## Determinism and multiplayer rules
- Intent generation is deterministic from context inputs.
- Lockstep: intents are commands in replay streams.
- Server-auth: server validates and schedules intents.

## Prohibitions
- No intent-level state mutation.
- No omniscient command parameters.
- No implicit retries without explicit intents.

## Integration points
- Commands: `docs/SPEC_COMMAND_MODEL.md`
- Scheduling: `docs/SPEC_SCHEDULING.md`
- Determinism: `docs/SPEC_DETERMINISM.md`

## Test plan (spec-level)
Required scenarios:
- Identical contexts produce identical intent ordering.
- Refusal codes are applied deterministically.
- Intent queues do not require per-tick scans.

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Agent policies, decision rules, and command issuance.
SCHEMA:
- Agent data formats and versioning metadata.
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
# SPEC_AGENT_CANON - Agent Canon (AGENT0)

Status: draft
Version: 1

## Purpose
Define agents as decision-makers only, never as simulators. Agents observe
epistemic state, form intents, and issue commands identical to player input.

## Core definitions
AGENT:
- A decision-making process bound to a person, organization, or abstract role.
- Has no authority beyond control rules and capability sets.
- Exists only while scheduled or interested.

AGENT CONTEXT:
- Epistemic snapshot (beliefs, uncertainty).
- Capability set (allowed actions).
- Authority scope (command permissions).
- Resource awareness (bounded, not global).

AGENT INTENT:
- A proposed CommandIntent (CMD0).
- Identical to player-issued intents.
- Subject to refusal, delay, or modification.

## AgentRecord schema
Required fields:
- agent_id
- bound_entity_ref (person/org/role)
- context_ref
- intent_queue_ref
- authority_scope_ref
- capability_set_ref
- next_due_tick
- provenance_ref

Rules:
- Agents do not mutate simulation state directly.
- next_due_tick is required for event-driven activation.
- Agent existence must not be required for core gameplay.

## Determinism and performance rules
- Agent decisions are deterministic given identical epistemic inputs.
- Agents activate only on scheduled events or interest.
- No per-tick thinking loops.
- No global iteration over world state.

## Epistemic constraints
- Agents never read authoritative state directly.
- Beliefs update only through INF systems.
- Agents may act on incorrect beliefs.

## Multiplayer parity
- Lockstep: agent decisions are commands recorded in replay streams.
- Server-auth: servers execute authoritative agent logic; clients never do.

## Prohibitions
- No agent-only simulation shortcuts.
- No omniscient access or hidden AI advantages.
- No implicit background NPCs without data-backed agents.

## Integration points
- Commands: `docs/SPEC_COMMAND_MODEL.md`
- Epistemics: `docs/SPEC_EPISTEMIC_INTERFACE.md`
- Scheduling: `docs/SPEC_SCHEDULING.md`
- Provenance: `docs/SPEC_PROVENANCE.md`

## Test plan (spec-level)
Required scenarios:
- Deterministic intent generation from identical epistemic snapshots.
- Batch vs step equivalence for scheduled agent activations.
- No global iteration with many agents.
- No agent required for baseline gameplay progression.

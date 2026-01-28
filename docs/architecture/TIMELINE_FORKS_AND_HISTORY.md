# Timeline Forks and History (EXIST2)

Status: draft.
Scope: forking timelines, replay, and historical integrity.

## Purpose
Define how alternate timelines are created without corrupting original history
and how replay modes preserve truth.

## Forking Rules
Forking is the only valid way to alter archived history:
- Explicit effect: OP_FORK_TIMELINE.
- Source must be ARCHIVED or FROZEN.
- Produces a new world_id/timeline_id with parent provenance.
- Original remains immutable and unchanged.
- Optional deterministic reseeding for future randomness.

See `schema/existence/SPEC_FORKING_RULES.md`.

## Replay Modes
- PASSIVE_REPLAY: read-only, no branching.
- ANALYTICAL_REPLAY: derived analysis allowed, no mutation.
- FORKED_REPLAY: creates a new timeline; mutations allowed only in fork.

Replays must:
- Use deterministic execution rules.
- Respect existence and archival states.
- Preserve provenance and audit records.

## Admin Powers and Integrity
Admin or omnipotent actions cannot silently rewrite history:
- All changes require explicit effects and audit logs.
- Archived history is immutable except via fork.

## Integration Points
- Law kernel: forking requires explicit law targets and authority.
- Work IR: forking is an authoritative effect.
- Sharding: parent/child ownership is explicit and deterministic.

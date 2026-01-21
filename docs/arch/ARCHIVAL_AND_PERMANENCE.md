# Archival and Permanence (EXIST2)

Status: draft.
Scope: freezing, archiving, and destruction without silent edits.

## Purpose
Define how worlds, regions, and entities can be preserved forever while
maintaining deterministic auditability and historical integrity.

## Archival States (Summary)
- LIVE: participates in simulation.
- FROZEN: immutable; time does not advance locally.
- ARCHIVED: persisted snapshot; no simulation.
- FORKED: new timeline derived from archived/frozen parent.

See `schema/existence/SPEC_ARCHIVAL_STATES.md` for definitions.

## Freeze Semantics
Freezing is an explicit effect:
- Requires authority capability and law approval.
- Prevents mutation and scheduled event execution.
- Preserves provenance and causal history.

See `schema/existence/SPEC_FREEZE_SEMANTICS.md`.

## Destruction and Permanence
Destruction is an explicit effect:
- Records cause, authority, and act time.
- Transitions to NONEXISTENT with tombstone or ARCHIVED when mandated.
- Never erases audit trails.

See `schema/existence/SPEC_DESTRUCTION_RULES.md`.

## Law and Authority
Freezing, forking, and destruction are law-gated:
- Jurisdictions may forbid or restrict them.
- Meta-law may override only with audit records.

## Tooling and Inspection
Inspection is allowed for FROZEN/ARCHIVED subjects subject to epistemic law.
Mutation is forbidden without explicit effects.

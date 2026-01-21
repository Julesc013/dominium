# SPEC_DESTRUCTION_RULES (EXIST2)

Schema ID: DESTRUCTION_RULES
Schema Version: 1.0.0
Status: binding.
Scope: destruction and permanence semantics.

## Purpose
Define destruction as an explicit effect that preserves audit trails and
provenance without silent erasure.

## Destruction Semantics
- Destruction is an effect, not an erasure.
- Destroyed subjects transition to:
  - NONEXISTENT with a tombstone record, or
  - ARCHIVED when preservation is mandated.
- Destruction must record:
  - cause_id
  - authority_id
  - act time (authoritative tick)
  - provenance reference

## Invariants (Absolute)
- No silent deletion allowed.
- History must remain auditable after destruction.
- Scheduled events are preserved in the archive or tombstone record.

## Work IR Integration
Destruction is an authoritative effect:
- Tasks performing destruction MUST declare law_targets.
- Audit record includes prior existence state and archival state.

## References
- `schema/existence/SPEC_EXISTENCE_STATES.md`
- `schema/existence/SPEC_ARCHIVAL_STATES.md`

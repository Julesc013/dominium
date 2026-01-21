# SPEC_FORKING_RULES (EXIST2)

Schema ID: FORKING_RULES
Schema Version: 1.0.0
Status: binding.
Scope: deterministic timeline forking and provenance preservation.

## Purpose
Define forking as the only valid way to alter archived history, producing a
new timeline while preserving the original intact.

## Fork Effect
- Operation: OP_FORK_TIMELINE
- Allowed sources: ARCHIVED or FROZEN subjects.
- Produces:
  - new world_id / timeline_id
  - copied snapshot
  - inherited schema and mod graph
  - parent provenance pointer
- Optional: deterministic re-seeding of future randomness.

## Fork Invariants (Absolute)
- Original source remains immutable and unchanged.
- Forked subject carries explicit parent provenance.
- No silent edits of archived history.
- Forking is explicit, law-gated, and auditable.

## Deterministic Reseeding
If future randomness is reseeded:
- Seed must be derived deterministically from parent seed + fork_id.
- No wall-clock or external entropy is permitted.

## Work IR Integration
Forking is an authoritative effect:
- Tasks performing forks MUST declare law_targets.
- Audit record includes parent_id, fork_id, and seed derivation summary.

## References
- `schema/existence/SPEC_ARCHIVAL_STATES.md`
- `schema/existence/SPEC_REFINEMENT_SEEDS.md`

# SPEC_LIFECYCLE_TRANSITIONS (EXIST0)

Schema ID: EXISTENCE_LIFECYCLE
Schema Version: 1.0.0
Status: binding.
Scope: allowed existence transitions and their requirements.

## Purpose
Define the only legal transitions between existence states. Transitions are
explicit effects, law-gated, and auditable. No implicit transitions are allowed.

## Allowed Transitions (Closed Set)
- NONEXISTENT → DECLARED
- DECLARED → LATENT
- LATENT → REFINABLE
- REFINABLE → REALIZED
- REALIZED → LATENT
- ANY → ARCHIVED
- ARCHIVED → REFINABLE (via fork only)

## Transition Requirements (All)
- Caused by an explicit effect.
- Law-gated by the law kernel (existence law + domain target).
- Auditable with provenance.
- Deterministic given the same inputs.

## Transition Record (Conceptual)
Existence transitions are represented as an effect record with:
- subject_id
- from_state
- to_state
- cause_id (intent/action id)
- law_target (must be a valid target from `schema/law/SPEC_LAW_TARGETS.md`)
- provenance_id
- timestamp_or_tick (authoritative act time)

## Fork Rule (ARCHIVED → REFINABLE)
- Forking creates a new identity with new provenance.
- The archived object remains read-only and unchanged.
- The fork transition is explicit and law-gated.

## Collapse Rule (REALIZED → LATENT)
- Collapse must preserve invariants and provenance.
- Any micro-only detail must be reversible or captured in provenance logs.

## Work IR Integration
- Existence transitions are modeled as authoritative effects in Work IR.
- TaskNodes performing transitions MUST declare law_targets.
- Transition ordering is deterministic and recorded in the audit log.

## Sharding Integration
- Ownership and placement respect the current existence state.
- Transitions that cross shard boundaries must use deterministic messages.

## References
- `schema/existence/SPEC_EXISTENCE_STATES.md`
- `schema/existence/SPEC_REFINEMENT_RELATION.md`
- `docs/arch/EXISTENCE_LIFECYCLE.md`

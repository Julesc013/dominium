# Existence Lifecycle (EXIST0)

Status: draft.
Scope: allowed transitions and their enforcement.

## Allowed Transitions
Only the following transitions are permitted:
- NONEXISTENT → DECLARED
- DECLARED → LATENT
- LATENT → REFINABLE
- REFINABLE → REALIZED
- REALIZED → LATENT
- ANY → ARCHIVED
- ARCHIVED → REFINABLE (via fork only)

See `schema/existence/SPEC_LIFECYCLE_TRANSITIONS.md` for the canonical list.

## Transition Rules
Each transition must:
- Be caused by an explicit effect.
- Be law-gated by the law kernel.
- Be auditable with provenance.
- Preserve determinism and history.

No implicit transitions or silent fallbacks are allowed.

## Refinement and Collapse
- Refinement requires a deterministic contract (EXIST1).
- Collapse preserves authoritative invariants and provenance references.
- LATENT and REFINABLE can persist indefinitely without simulation.

## Work IR Integration
Existence transitions are expressed as Work IR effects. Tasks must:
- Declare law_targets.
- Emit deterministic effects with stable ordering.
- Produce audit records for provenance and law decisions.

## Sharding and Ownership
Transitions respect shard ownership and routing. Cross-shard transitions must
use deterministic messages and ownership rules.

# Collapse/Expand Contract (SCALE0)

Status: binding.
Scope: deterministic collapse/expand rules and macro capsule contract.

## Purpose
Define how high-fidelity state collapses into macro capsules and how macro
capsules deterministically expand back into micro state without breaking
invariants.

## Macro capsule definition
A macro capsule is the authoritative, deterministic summary of a domain at a
commit boundary. It is the only valid artifact produced by collapse.

## Macro capsule contents (MUST)
A macro capsule MUST contain:
- exact invariants
- sufficient statistics (with tolerance tags)
- provenance:
  - source domain
  - source tick (ACT)
  - collapse reason
- deterministic reconstruction seeds
- extension bag (namespaced)

Macro capsule schema: `schema/macro_capsule.schema`

## Collapse rules
- Collapse MAY occur only at commit boundaries.
- Collapse MUST be deterministic.
- Collapse MUST be reversible (expandable) within declared tolerances.
- Collapse MUST emit an auditable event with capsule_id and provenance.

## Expand rules
- Expansion MUST be deterministic.
- Expansion MUST reconstruct a microstate consistent with:
  - invariants exactly
  - statistics within tolerance
- Expansion MUST NOT introduce new entities or resources ex nihilo.
- Expansion MUST emit an auditable event with capsule_id and seeds used.

## Extension bag rules
- Extensions MUST be namespaced (`docs/architecture/NAMESPACING_RULES.md`).
- Extensions MAY add metadata but MUST NOT alter invariant semantics.
- Extend-vs-Create applies: extensions refine, they do not redefine.

## See also
- `docs/architecture/INVARIANTS_AND_TOLERANCES.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/MACRO_TIME_MODEL.md`
- `docs/architecture/REFINEMENT_CONTRACTS.md`

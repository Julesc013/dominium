# SPEC_DOMAIN_JURISDICTIONS (DOMAIN2)

Status: draft.
Scope: schema references for binding jurisdictions to domain volumes.

## Purpose
Define how jurisdictions (law + capability sets) attach to domain volumes so
law resolution can be driven by spatial containment.

## Schema Concepts

### Jurisdiction
A jurisdiction is a versioned set of law rules and capability policies.
It is referenced by stable `jurisdiction_id` and versioned by schema.

### Domain-Jurisdiction Binding
Each domain volume may reference zero or more jurisdictions. Each binding
includes a precedence used to order jurisdiction evaluation.

## Required Fields (Reference)
For any domain binding entry:
- `domain_id` (u64, stable)
- `jurisdictions[]` (array)
  - `jurisdiction_id` (u64, stable)
  - `precedence` (u32, higher wins)
  - `flags` (u32, optional; future use)

Optional:
- `parent_domain_id` (u64, 0 = none)
- `domain_precedence` (u32, higher wins in overlap)
- `authoring_version` (u32)

## Invariants
- Bindings are ordered deterministically by precedence then ID.
- Domain precedence is only used for overlap ordering, not existence.
- Absence of bindings is valid (domain has no local law).

## Integration References
- Resolution order is defined in `SPEC_JURISDICTION_PRECEDENCE.md`.
- Domain containment is defined in `schema/domain/README.md`.

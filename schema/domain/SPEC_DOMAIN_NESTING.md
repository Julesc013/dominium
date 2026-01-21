# SPEC_DOMAIN_NESTING (DOMAIN0)

Schema ID: DOMAIN_NESTING
Schema Version: 1.0.0
Status: binding.
Scope: nesting, overlap, and resolution rules for domains.

## Purpose
Define deterministic resolution rules for nested and overlapping domains.

## Nesting and Overlap
Domains may:
- Nest (room ⊂ building ⊂ city ⊂ planet).
- Overlap (jurisdiction overlays, special zones).
- Be disjoint (separate regions or worlds).

## Resolution Order (Deterministic)
When multiple domains apply, resolve in this order:
1) Explicit domain reference.
2) Smallest containing domain.
3) Higher precedence domain.
4) Parent chain.

No ambiguity is allowed. Ties must be resolved deterministically by domain_id.

## Integration Notes
- Domain resolution is independent of fidelity and authority.
- Existence and archival states may exclude domains from resolution.

## References
- `schema/domain/SPEC_DOMAIN_VOLUMES.md`

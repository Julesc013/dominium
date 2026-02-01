Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Domain Jurisdictions and Law (DOMAIN2)

Status: draft.
Scope: binding law and authority to spatial domains.

## Purpose
Attach jurisdictions to domain volumes so laws resolve by spatial containment,
not by hard-coded region types or grids.

## Core Concepts
- Jurisdiction: a set of laws and capability policies.
- Domain binding: domains reference one or more jurisdictions with precedence.
- Resolution context: an ordered list of active jurisdictions for a point.

## Resolution Order
Law resolution uses the deterministic order:
1) Explicit context jurisdiction (contract/event scope)
2) Smallest containing domain’s jurisdictions
3) Higher-precedence containing domains
4) Parent domain chain (increasing scale)
5) World default
6) Server default
7) Canonical fallback (refuse-first)

Within a domain, bindings are ordered by binding precedence, then ID.

## Spatial Application
For single-point actions, resolve jurisdictions at the action point.
For multi-point actions (travel, beams, paths):
- evaluate origin, path samples, and destination
- apply the strongest restriction across all contexts

## Use Cases (Data-Defined)
Examples that require no code changes:
- Spectator-only sphere (observe-only, no interaction)
- Strict client compliance zone (modified clients forbidden)
- No-trespassing corridor
- Anarchy frontier (existence-only law)
- Admin chamber (full authority)

## Integration Points
- Command admission (EXEC0c)
- Work IR task admission
- Information emission (epistemic gating)
- TRAVEL path validation
- REFINEMENT visitability checks

## References
- `schema/domain/README.md`
- `schema/law/SPEC_DOMAIN_JURISDICTIONS.md`
- `schema/law/SPEC_JURISDICTION_PRECEDENCE.md`
# Terrain Macro Capsule (TERRAIN0)

Status: binding.
Scope: collapse/expand semantics for terrain domains.

## Invariants
Terrain collapse/expand MUST preserve:
- mass/volume totals within declared tolerances.
- material totals by id.
- edit provenance and ordering.
- support envelope bounds.

## sufficient statistics
Macro capsules MUST capture:
- roughness distributions per LOD tier.
- support_capacity envelopes.
- material histograms.
- overlay provenance summaries.

## RNG cursor continuity
Macro capsules MUST include RNG cursor state:
- stream name
- cursor position
- seed or derivation tags

The RNG cursor is required to preserve deterministic expand behavior.

## Compatibility
- Collapse/expand contract: `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- Scaling model: `docs/architecture/SCALING_MODEL.md`

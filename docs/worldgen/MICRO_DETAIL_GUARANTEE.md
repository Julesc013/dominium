# Micro-Detail Guarantee

Status: canonical.
Scope: micro-detail refinement boundaries.
Authority: canonical. All worldgen layers MUST follow this.

## Binding rules
- Stones, puddles, and blades of grass MUST remain procedural by default.
- Hand-authored micro detail MAY exist but MUST be optional and removable.
- Micro detail refinement MUST be lazy, collapsible, and budget-bounded.
- Micro detail MUST NOT override higher-level truth or anchors.

## Refinement boundaries
- Macro and regional anchors MAY constrain micro outcomes but MUST NOT precompute them.
- Collapse of micro detail MUST NOT alter objective truth.

## References
- `docs/worldgen/REFINEMENT_CONTRACT.md`
- `docs/worldgen/REFINEMENT_LATTICE.md`

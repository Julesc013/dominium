Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Multiple Cosmologies (Exemplar)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Purpose: demonstrate contradictory cosmological models in different domains.

## Demonstrates
- Alternate physics overlays scoped by domain volume.
- Hyperspace topology layered without default geometry.
- Parallel knowledge models with explicit precedence.

## Dependencies
- Packs: `org.dominium.worldgen.base.cosmology`, `org.dominium.realities.alt_physics`,
  `org.dominium.realities.hyperspace`.
- Pack: `org.dominium.worldgen.base.cosmology` provides the universe node.

## Invariants Proved
- No privileged physics exists in the engine.
- Multiple realities coexist via explicit refinement plans.
- Packs remain optional and removable.

## Safe Removal or Modification
- Remove `org.dominium.examples.multicosmology` to drop overlays.
- Remove `org.dominium.realities.alt_physics` or `org.dominium.realities.hyperspace`
  to disable those domains explicitly.
- Preserve capability IDs to avoid silent fallbacks.

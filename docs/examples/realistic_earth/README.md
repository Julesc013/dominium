Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Realistic Earth (Exemplar)

Purpose: demonstrate real-world overlays, scientific epistemics, and civic institutions.

## Demonstrates
- Real-world overlays (Milky Way -> Sol -> Earth macro).
- Measurement-driven knowledge artifacts and subjective gating.
- Construction, trade, and regulation as capability-resolved processes.

## Dependencies
- Packs: `org.dominium.worldgen.base.cosmology`, `org.dominium.worldgen.base.galaxy`,
  `org.dominium.worldgen.base.system`, `org.dominium.worldgen.base.body`.
- Packs: `org.dominium.worldgen.real.milkyway`, `org.dominium.worldgen.real.sol`,
  `org.dominium.worldgen.real.earth_macro`.
- Packs: `org.dominium.epistemics.core`, `org.dominium.lib.on_planet.primitives`,
  `org.dominium.lib.on_planet.processes`.

## Invariants Proved
- Objective truth is separate from subjective knowledge.
- Capability resolution replaces file paths.
- Deterministic, zero-asset boot remains valid.

## Safe Removal or Modification
- Remove `org.dominium.examples.realistic_earth` from the load list.
- Remove real-world overlay packs to revert to procedural Earth.
- Preserve capability IDs in saves to avoid silent mismatch.
Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EARTH Water Visual Baseline

## Scope

- EARTH-8 adds a compact derived `water_view_artifact`.
- It derives ocean, river, lake, and tide-offset presentation rows from existing Earth macro state.
- No authoritative water state or fluid simulation path is introduced.

## Policy

- canonical policy id: `water.mvp_default`
- canonical river width scale: `220`
- canonical lake fill threshold: `180`
- canonical reflection strength: `520`
- canonical tide visual strength: `80`

## Derived Artifact

- `ocean_mask_ref` marks ocean-present tiles
- `river_mask_ref` marks hydrology rivers and preserves `flow_target_tile_key`
- bounded flow-convergence may promote additional visual river ribbons when canonical hydrology flags are sparse in the sampled region
- `lake_mask_ref` marks sink/basin lakes
- `tide_offset_ref` carries visual-only tide offsets for water tiles

## Renderer Integration

- viewer shell builds the water artifact from derived tile/tide inputs only
- map/minimap layers expose water masks and tide debug data through GEO lens layers
- software renderer applies bounded water patches and lighting-aware color mixing from the derived artifact

## Deterministic Replay Fixture

- canonical replay tick: `15`
- bounded probe region: `39` surface tiles
- replay summary:
  - ocean tiles: `10`
  - river tiles: `3`
  - lake tiles: `1`
  - tide-offset tiles: `11`
- canonical water replay artifact fingerprint:
  `2a718a93c707d3a10a60c008e7693cb0f155cb04c6a69eda98506ff12bbb74a2`
- canonical water replay hash:
  `e31513979d5ab8aad681b1c56df89d48a10042970fbb3e4f3732d5aab763aaae`

## Readiness

- ready for EARTH-9 stress and regression work
- ready for future FLUID ocean replacement without breaking viewer contracts
- ready for future shoreline, foam, and wave presentation layers

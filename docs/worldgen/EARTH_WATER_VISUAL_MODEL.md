Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Earth Water Visual Model

## 1) Purpose

EARTH-8 adds a deterministic water-visual layer for MVP Earth presentation.

It exists to make:

- oceans visibly present
- rivers readable as flow-aligned ribbons
- lakes readable at hydrology sinks
- tide motion perceptible as a subtle visual offset

It does not simulate water volume, shoreline transport, or fluid pressure.

## 2) Activation Surface

- EARTH-8 is derived-view only.
- The canonical output is `water_view_artifact`.
- UI and renderers consume the derived artifact only.
- Mutation of TruthModel is forbidden.

## 3) Water Categories

EARTH-8 derives three water classes from existing macro Earth state:

- ocean tiles from the EARTH-0 ocean mask / surface class
- river tiles from EARTH-1 `river_flag` plus flow routing
- lake tiles from EARTH-1 sink and basin heuristics

No new authoritative water ontology is introduced in MVP.

## 4) Inputs

For each requested region cell:

- surface tile artifact
- hydrology flags and flow target
- tide proxy overlay or `field.tide_height_proxy`
- current tick
- water visual policy
- sky and illumination artifacts for renderer-side reflection mixing

Wall-clock time is forbidden.
Fluid simulation state is forbidden.

## 5) Derived Outputs

`water_view_artifact` contains bounded regional rows for:

- `ocean_mask_ref`
- `river_mask_ref`
- `lake_mask_ref`
- `tide_offset_ref`

These rows remain compactable and cacheable.
They must not mutate authoritative terrain, fields, or body state.

## 6) River and Lake Rules

### 6.1 Rivers

- rivers are present when EARTH-1 marks `river_flag`
- when a bounded region has no explicit river flag on a coherent channel, EARTH-8 may promote a high fan-in flow chain into a visual ribbon
- river visuals may use `flow_target_tile_key` to draw coherent ribbons
- width is derived from bounded drainage accumulation and policy scaling

This promotion is derived-only.
It must not mutate canonical hydrology flags.

### 6.2 Lakes

- lakes are present when EARTH-1 sink and basin heuristics mark `lake_flag`
- lake fill is a visual proxy only
- no lake volume solve is introduced

## 7) Tide Offset Rule

- tide offset is visual only
- it is derived from deterministic tide proxy rows scaled by `tide_visual_strength`
- it may shift ocean-edge appearance or shading
- it must not move canonical terrain or shoreline identity

## 8) Reflection Stub

EARTH-8 reflection is a presentation mix only:

- ocean/lake colors mix base water color with sky and key-light colors
- no ray tracing
- no wave normals
- no material texture dependency

## 9) Region and Budget Rules

- water views are generated only for the requested bounded region
- no global Earth scan is allowed
- ordering is deterministic by stable `geo_cell_key`
- cache keys must include:
  - tick
  - observer or region identity
  - policy id
  - relevant water/tide inputs

## 10) Lens and UX Surface

EARTH-8 exposes:

- `layer.water_ocean`
- `layer.water_river`
- `layer.water_lake`
- `layer.tide_offset`

Physical water layers are ordinarily visible.
`layer.tide_offset` is debug/profile gated.

## 11) Renderer Contract

- software renderer consumes `water_view_artifact` only
- null renderer may ignore the artifact
- future hardware renderers must remain API-compatible with the same derived artifact

Renderer-side fluid simulation is forbidden in MVP.

## 12) Extensibility

EARTH-8 reserves the handoff surface for future:

- FLUID ocean surface state
- river volume flow
- shoreline waves and foam
- erosion and sediment visuals

Future systems may replace the underlying source data.
They must preserve the derived-view contract and bounded artifact surface.

## 13) Non-Goals

- no water volume simulation
- no Navier-Stokes or shallow-water solver
- no shoreline erosion
- no wave spectrum
- no wall-clock animation

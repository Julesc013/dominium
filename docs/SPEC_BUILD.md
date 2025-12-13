# Build / Construction Subsystem

## Overview
- `build/d_build.h` defines a generic placement API used by products/tools.
- The subsystem is responsible for:
  - validating build requests against terrain + basic collision rules
  - committing placement by creating engine objects (structures, splines)
  - persisting placement metadata that is not owned by the target subsystem (e.g. foundation offsets)

## Requests
- `d_build_request` supports:
  - `kind`: structure or spline
  - off-grid positions in `q32_32`
  - discrete yaw in Q16.16 turns (UI can quantize to 90° steps)
  - optional explicit spline node list (polyline)
  - `D_BUILD_FLAG_SNAP_TERRAIN` to sample and snap Z

## Validation / Commit
- `d_build_validate` checks:
  - referenced prototype ids exist
  - structure overlap (simple AABB test vs existing structures)
  - spline segment grade does not exceed `profile.max_grade`
  - optional port requirement (`D_BUILD_FLAG_REQUIRE_PORTS`) for endpoint attachment
- `d_build_commit` performs:
  - structure placement via `d_struct_create`
  - spline placement via `d_trans_spline_create`
  - optional endpoint attachment via `d_trans_spline_set_endpoints`

## Foundations
- When placing a structure, the builder samples terrain height at the footprint corners and sets the structure anchor to the average height.
- Per-corner foundation “down” offsets (`anchor_z - corner_z`) are stored and can be queried via `d_build_get_foundation_down`.


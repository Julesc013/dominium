# SPEC_SURFACE_STREAMING - Surface Streaming and Local Frames (v1)

This spec defines the v1 surface streaming model, coordinate transforms, and
local tangent frames for planetary surfaces. It is authoritative for runtime
behavior but does not describe gameplay features.

## 1. Coordinate spaces
- **Body-fixed**: Cartesian position in the body's rotating frame (meters,
  fixed-point).
- **Lat/long**: Latitude and longitude in **turns** (`Q16.16`), where `1.0` is
  a full rotation.
- **Local tangent frame**: East-North-Up (ENU) orthonormal basis at a given
  lat/long, expressed as fixed-point unit vectors.

## 2. Deterministic conversions
All conversions are integer-only and use deterministic math wrappers.

Required transforms:
- `pos_body_fixed -> lat/long` (sphere v1)
- `lat/long + altitude -> pos_body_fixed` (sphere v1)
- `lat/long -> ENU tangent frame`

Rounding is deterministic:
- Lat/long are returned as `Q16.16` turns.
- Body-fixed positions are stored as segmented `Q16.16` meters.

## 3. Surface chunk model
Chunks are deterministic tiles on the surface projection.

### 3.1 Chunk key
- Chunk keys are derived from:
  - `body_id`
  - quantized `lat/long` grid indices
  - the grid step size in turns (`Q16.16`)
- Grid step size is derived from a **power-of-two** target chunk size in
  meters and the body's radius.

### 3.2 Chunk states
Each chunk transitions through:
- `INACTIVE` → `REQUESTED` → `ACTIVE` → `ACTIVE_READY`

`ACTIVE` indicates placeholder data is available; `ACTIVE_READY` indicates
derived artifacts (meshes, textures) are ready.

## 4. Streaming rules
- Only chunks inside **activation bubble** interest sets are requested.
- Chunk activation is **non-blocking** and uses derived jobs only.
- Missing chunks never block the UI; render placeholders until ready.
- Streaming order and key generation are deterministic.
- Constructions are scoped to active bubbles and reference surface chunk keys;
  missing chunk data must degrade fidelity, not block placement.

## 5. Height sampler (v1)
- A deterministic procedural height sampler provides stub elevation:
  - Inputs: `body_id`, quantized `lat/long`
  - Output: height in meters (`Q48.16`)
- Height sampling is authoritative for landing constraints but does not
  drive global physics.

## 6. Related specs
- `docs/SPEC_SURFACE_TOPOLOGY.md`
- `docs/SPEC_LANES_AND_BUBBLES.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_NO_MODAL_LOADING.md`

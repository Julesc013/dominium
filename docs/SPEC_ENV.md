# Environment (ENV)

The environment subsystem provides deterministic, fixed-point environmental state at two scales:
- **Chunk fields**: coarse per-chunk values for global/world-scale systems (atmosphere, light, radiation, etc.).
- **Volumes**: interior micro-environments (rooms/cabins) coupled through a simple conductance graph.

## 1. Chunk Environmental Fields
- Public API: `source/domino/env/d_env_field.h`
- Each loaded chunk stores an array of `d_env_field_cell { desc, values[4] }`.
  - `values[]` are Q16.16 and interpreted by the owning model.
  - Fields are *coarse* (not per-voxel).

### Reserved field ids (built-in atmosphere)
- `D_ENV_FIELD_PRESSURE` (1)
- `D_ENV_FIELD_TEMPERATURE` (2)
- `D_ENV_FIELD_GAS0_FRACTION` (3)
- `D_ENV_FIELD_GAS1_FRACTION` (4)
- `D_ENV_FIELD_HUMIDITY` (5)
- `D_ENV_FIELD_WIND_X` (6)
- `D_ENV_FIELD_WIND_Y` (7)

## 2. Field Models
- Models register via `d_env_register_model(const d_env_model_vtable *vt)` (model family `D_MODEL_FAMILY_ENV`).
- Built-in model: `D_ENV_MODEL_ATMOSPHERE_DEFAULT` (1)
  - Computes deterministic baselines and performs coarse diffusion between neighboring chunks.
  - Time variation is derived from `world->tick_count` (no wall-clock).

## 3. Interior Volumes
- Public API: `source/domino/env/d_env_volume.h`
- `d_env_volume` nodes store rough world-space AABBs and per-volume averages (pressure/temperature/gases/humidity/pollutant).
- `d_env_volume_edge` links volumes with `gas_conductance` and `heat_conductance` (Q16.16).
  - If one endpoint is `0`, the edge couples the non-zero volume to **exterior** fields at the volume center (using `d_env_sample_exterior_at`).

## 4. Tick and Sampling
- `d_env_tick(d_world *w, u32 ticks)`:
  - Runs registered field models, applies coarse neighbor diffusion, then ticks the volume graph.
- `d_env_sample_at(...)`:
  - Returns resolved field samples at `(x,y,z)`, applying volume overrides when inside a volume.
- `d_env_sample_exterior_at(...)`:
  - Samples chunk fields without applying volume overrides (used for exterior coupling).

## 5. Persistence
- Chunk-level ENV save includes zones/portals and field cells.
- Instance-level ENV save includes the volume graph (volumes + edges).


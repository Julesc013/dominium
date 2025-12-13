# Hydrology (HYDRO)

Hydrology is a deterministic, fixed-point subsystem that simulates coarse surface fluid columns per chunk and optionally exchanges volume with generic RES reservoirs.

## 1. Core API
- Public API: `source/domino/hydro/d_hydro.h`
- Tick: `d_hydro_tick(d_world *w, u32 ticks)`
- Sample: `d_hydro_sample_at(d_world *w, q32_32 x, q32_32 y, q32_32 z, d_hydro_cell *out)`

## 2. Data Model
- Each loaded chunk stores a fixed 2D grid (`16x16`) of `d_hydro_cell`:
  - `depth` (Q16.16) – coarse column depth
  - `surface_height` (Q16.16) – surface elevation relative to datum (currently `= depth`)
  - `velocity_x/velocity_y` (Q16.16) – coarse lateral flux indicators for debugging/visualisation
  - `flags` (Q16.16 bitfield) – reserved for model-defined states

## 3. Built-in Model
- `D_HYDRO_MODEL_SURFACE_WATER` (1)
  - Applies a symmetric, stable explicit diffusion step across cell edges (including across chunk boundaries).
  - Update is order-independent: per-tick snapshots are used and deltas are applied after edge evaluation.

## 4. RES Coupling (Generic Reservoir Exchange)
- Hydrology samples RES channels with `dres_sample_at` and applies deltas with `dres_apply_delta`.
- Deposits tagged with `D_TAG_MATERIAL_FLUID` are treated as generic fluid reservoirs for exchange.
- Exchange is conservative: the amount removed from/added to surface cells matches the delta applied to the RES channel.

## 5. Persistence
- HYDRO stores per-chunk grid state under the hydrology subsystem save tag.
- Hydrology state should be included in determinism hashing to ensure replay bit-identical results.


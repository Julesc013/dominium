--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Field Registry (Terrain/Atmo/Hydro/etc.)

- All continuous scalar/tensor fields register through `dfield` (`include/domino/dfield.h`, `source/domino/dfield.c`). No private, hidden 3D arrays per system.
- Fields are identified by `FieldId` (u16) and described by `FieldDesc { id, name, unit, storage }`.

## Units and storage
- `UnitKind`: `UNIT_NONE`, `UNIT_HEIGHT_M`, `UNIT_DEPTH_M`, `UNIT_TEMP_K`, `UNIT_PRESSURE_PA`, `UNIT_FRACTION`, `UNIT_DENSITY_KG_M3`, `UNIT_WIND_M_S`, `UNIT_RADIATION_SV_S`, `UNIT_POLLUTION`, `UNIT_NOISE`.
- `FieldStorageKind`: `FIELD_STORAGE_BOOL`, `FIELD_STORAGE_U8`, `FIELD_STORAGE_Q4_12`, `FIELD_STORAGE_Q16_16`.

## Built-in fields (pre-registered)
- `terrain_height` (height, Q16.16)
- `water_depth` (depth, Q16.16)
- `soil_moisture` (fraction, Q4.12)
- `fertility` (fraction, Q4.12)
- `air_pressure` (pressure, Q16.16)
- `air_temp` (temperature, Q16.16)
- `humidity` (fraction, Q4.12)
- `wind_u`, `wind_v` (wind components, Q16.16)
- `cloud_cover` (fraction, Q4.12)
- `pollution`, `radiation`, `noise_level` (scalars, U8 for now)
- Climate means: `climate_mean_temp` (Q16.16 K), `climate_mean_precip` (Q16.16 depth proxy), `climate_mean_humidity` (Q16.16 fraction)
- `biome_id` (U8 for now; expand storage if >255 biome types are needed)
- Names are stable; lookup by name or `FieldId` through `dfield_find_by_name` / `dfield_get`.

## Codecs
- Runtime values are Q16.16 unless otherwise noted.
- Storage mappings:
  - Q16.16 ↔ Q4.12 via 4-bit shifts with explicit clamping.
  - Q16.16 ↔ U8 via integer clamp to [0,255] (naïve 1:1 integer mapping; no per-field scaling in this pass).
- Codec helpers are integer-only; no floats.

## Usage rules
- Register any new continuous field via `dfield_register` before storing or sampling it.
- Systems sampling fields must not maintain private arrays; all chunk storage must refer to registered `FieldId` and use the shared codecs.
- Per-field scaling is not implemented in this pass; if a field cannot be represented safely by the shared codecs, it must use an explicit fixed-point storage kind or define an explicit schema-level transform (never implicit).

## Relationship to SIM fields/events/messages
`dfield` defines a low-level registry for world/environment fields. The
deterministic cross-module field update/sampling contract (phase boundaries,
budgets, and packetized field updates) is specified by
`docs/SPEC_FIELDS_EVENTS.md`.

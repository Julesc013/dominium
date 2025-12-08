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
  - Q16.16 ↔ U8 via integer clamp to [0,255]; TODO refine per-field ranges and scaling.
- Codec helpers are integer-only; no floats.

## Usage rules
- Register any new continuous field via `dfield_register` before storing or sampling it.
- Systems sampling fields must not maintain private arrays; all chunk storage must refer to registered `FieldId` and use the shared codecs.
- TODO hooks remain for per-field scaling once climate/weather/hydrology modules arrive.

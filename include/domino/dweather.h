/*
FILE: include/domino/dweather.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dweather
RESPONSIBILITY: Defines the public contract for `dweather` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DWEATHER_H
#define DOMINO_DWEATHER_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dworld.h"
#include "dfield.h"

#ifdef __cplusplus
extern "C" {
#endif

/* WeatherGrid: Public type used by `dweather`. */
typedef struct {
    BodyId   body;
    U32      width;
    U32      height;
    PressurePa *pressure;
    TempK      *temp;
    Q16_16     *humidity;   /* 0..1 */
    Q16_16     *wind_u;     /* m/s */
    Q16_16     *wind_v;     /* m/s */
    Q16_16     *cloud;      /* 0..1 cloud density */
} WeatherGrid;

/* Field handles */
FieldId dweather_field_cloud(void);

/* Grid lifecycle */
bool         dweather_init_grid(BodyId body, U32 width, U32 height);
/* Purpose: Get grid.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
WeatherGrid *dweather_get_grid(BodyId body);

/* Simulation */
bool dweather_seed_from_climate(BodyId body);
/* Purpose: Step dweather.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dweather_step(BodyId body, U32 ticks);

/* Sampling and projection */
bool dweather_get_surface_weather_at_tile(BodyId body, const WPosTile *tile,
    PressurePa *out_pressure, TempK *out_temp, Q16_16 *out_humidity,
    Q16_16 *out_wind_u, Q16_16 *out_wind_v, Q16_16 *out_cloud, Q16_16 *out_precip);

/* Downsample/interpolate grid values for tile fields; outputs raw Q16.16 values */
bool dweather_project_fields_for_tile(BodyId body, const WPosTile *tile,
    Q16_16 *out_pressure_raw, Q16_16 *out_temp_raw, Q16_16 *out_humidity_raw,
    Q16_16 *out_wind_u_raw, Q16_16 *out_wind_v_raw, Q16_16 *out_cloud_raw);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DWEATHER_H */

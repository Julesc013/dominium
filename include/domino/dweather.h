#ifndef DOMINO_DWEATHER_H
#define DOMINO_DWEATHER_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dworld.h"
#include "dfield.h"

#ifdef __cplusplus
extern "C" {
#endif

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
WeatherGrid *dweather_get_grid(BodyId body);

/* Simulation */
bool dweather_seed_from_climate(BodyId body);
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

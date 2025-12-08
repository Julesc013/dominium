#ifndef DOMINO_DCLIMATE_H
#define DOMINO_DCLIMATE_H

#include <stdbool.h>

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
    TempK   *mean_temp_K;   /* per cell */
    Q16_16  *mean_precip;   /* arbitrary units */
    Q16_16  *mean_humidity; /* 0..1 */
} ClimateGrid;

/* Field handles (registered via dfield) */
FieldId dclimate_field_mean_temp(void);
FieldId dclimate_field_mean_precip(void);
FieldId dclimate_field_mean_humidity(void);

/* Grid lifecycle */
bool        dclimate_init_grid(BodyId body, U32 width, U32 height, Q16_16 albedo, Q16_16 greenhouse_factor);
ClimateGrid *dclimate_get_grid(BodyId body);

/* Sampling */
bool dclimate_sample_at_tile(BodyId body, const WPosTile *tile, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity);
bool dclimate_sample_at_lat_lon(BodyId body, Turn lat, Turn lon, Q16_16 height_m, TempK *out_temp_K, Q16_16 *out_precip, Q16_16 *out_humidity);

/* Direct cell set for offline/authoring overrides */
bool dclimate_set_cell(BodyId body, U32 gx, U32 gy, TempK temp_K, Q16_16 precip, Q16_16 humidity);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DCLIMATE_H */

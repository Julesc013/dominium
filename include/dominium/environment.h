#ifndef DOMINIUM_ENVIRONMENT_H
#define DOMINIUM_ENVIRONMENT_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "domino/dworld.h"
#include "dominium/world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_environment_system dom_environment_system;

typedef struct dom_environment_desc {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_world* world;
} dom_environment_desc;

typedef struct dom_environment_sample {
    uint32_t struct_size;
    uint32_t struct_version;
    int32_t  temperature_mK;
    uint32_t pressure_mPa;
    uint32_t humidity_permille;
    uint32_t wind_mm_s;
    uint32_t radiation_uSvph;
} dom_environment_sample;

dom_status dom_environment_create(const dom_environment_desc* desc,
                                  dom_environment_system** out_env);
void       dom_environment_destroy(dom_environment_system* env);
dom_status dom_environment_tick(dom_environment_system* env,
                                uint32_t dt_millis);
dom_status dom_environment_sample_point(dom_environment_system* env,
                                        dom_surface_id surface,
                                        const WPosExact* pos,
                                        dom_environment_sample* out_sample,
                                        size_t out_sample_size);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_ENVIRONMENT_H */

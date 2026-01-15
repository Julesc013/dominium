/*
FILE: source/dominium/game/runtime/dom_weather_provider.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/weather_provider
RESPONSIBILITY: Weather provider registry and modifier sampling (stub for v1).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_WEATHER_PROVIDER_H
#define DOM_WEATHER_PROVIDER_H

#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_surface_topology.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_WEATHER_OK = 0,
    DOM_WEATHER_ERR = -1,
    DOM_WEATHER_INVALID_ARGUMENT = -2,
    DOM_WEATHER_NOT_FOUND = -3,
    DOM_WEATHER_NOT_IMPLEMENTED = -4
};

enum {
    DOM_WEATHER_PROVIDER_ID_MAX = 32u
};

typedef struct dom_weather_mods {
    q16_16 density_delta_q16;
    q16_16 pressure_delta_q16;
    q16_16 temperature_delta_q16;
    dom_topo_vec3_q16 wind_delta_q16;
    u32 has_wind;
} dom_weather_mods;

typedef struct dom_weather_binding {
    dom_body_id body_id;
    char provider_id[DOM_WEATHER_PROVIDER_ID_MAX];
    u32 provider_id_len;
    const unsigned char *params;
    u32 params_len;
    u64 params_hash;
} dom_weather_binding;

typedef int (*dom_weather_validate_fn)(dom_body_id body_id,
                                       const dom_weather_binding *binding);
typedef int (*dom_weather_sample_fn)(dom_body_id body_id,
                                     const dom_weather_binding *binding,
                                     const dom_posseg_q16 *pos_body_fixed,
                                     q48_16 altitude_m,
                                     dom_tick tick,
                                     dom_weather_mods *out_mods);

typedef struct dom_weather_provider_vtbl {
    u32 api_version;
    dom_weather_validate_fn validate;
    dom_weather_sample_fn sample_modifiers;
} dom_weather_provider_vtbl;

typedef struct dom_weather_registry dom_weather_registry;

dom_weather_registry *dom_weather_registry_create(void);
void dom_weather_registry_destroy(dom_weather_registry *registry);

int dom_weather_registry_register_provider(dom_weather_registry *registry,
                                           const char *provider_id,
                                           const dom_weather_provider_vtbl *vtbl);
int dom_weather_registry_set_binding(dom_weather_registry *registry,
                                     const dom_weather_binding *binding);
int dom_weather_registry_get_binding(const dom_weather_registry *registry,
                                     dom_body_id body_id,
                                     dom_weather_binding *out_binding);

int dom_weather_sample_modifiers(const dom_weather_registry *registry,
                                 dom_body_id body_id,
                                 const dom_posseg_q16 *pos_body_fixed,
                                 q48_16 altitude_m,
                                 dom_tick tick,
                                 dom_weather_mods *out_mods);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_WEATHER_PROVIDER_H */

/*
FILE: source/dominium/game/runtime/dom_media_provider.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/media_provider
RESPONSIBILITY: Media provider registry, bindings, and sampling helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_MEDIA_PROVIDER_H
#define DOM_MEDIA_PROVIDER_H

#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
#include "domino/core/types.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_surface_topology.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_MEDIA_OK = 0,
    DOM_MEDIA_ERR = -1,
    DOM_MEDIA_INVALID_ARGUMENT = -2,
    DOM_MEDIA_NOT_FOUND = -3,
    DOM_MEDIA_NOT_IMPLEMENTED = -4,
    DOM_MEDIA_INVALID_DATA = -5
};

enum {
    DOM_MEDIA_KIND_VACUUM = 0u,
    DOM_MEDIA_KIND_ATMOSPHERE = 1u,
    DOM_MEDIA_KIND_OCEAN = 2u
};

enum {
    DOM_MEDIA_PROVIDER_ID_MAX = 32u
};

typedef struct dom_media_sample {
    q16_16 density_q16;
    q16_16 pressure_q16;
    q16_16 temperature_q16;
    dom_topo_vec3_q16 wind_body_q16;
    u32 has_wind;
} dom_media_sample;

typedef struct dom_media_binding {
    dom_body_id body_id;
    u32 kind;
    char provider_id[DOM_MEDIA_PROVIDER_ID_MAX];
    u32 provider_id_len;
    const unsigned char *params;
    u32 params_len;
    u64 params_hash;
} dom_media_binding;

typedef int (*dom_media_validate_fn)(dom_body_id body_id,
                                     const dom_media_binding *binding);
typedef int (*dom_media_sample_fn)(dom_body_id body_id,
                                   const dom_media_binding *binding,
                                   const dom_posseg_q16 *pos_body_fixed,
                                   q48_16 altitude_m,
                                   dom_tick tick,
                                   dom_media_sample *out_sample);

typedef struct dom_media_provider_vtbl {
    u32 api_version;
    dom_media_validate_fn validate;
    dom_media_sample_fn sample;
} dom_media_provider_vtbl;

typedef struct dom_media_registry dom_media_registry;

dom_media_registry *dom_media_registry_create(void);
void dom_media_registry_destroy(dom_media_registry *registry);

int dom_media_registry_register_provider(dom_media_registry *registry,
                                         u32 kind,
                                         const char *provider_id,
                                         const dom_media_provider_vtbl *vtbl);
int dom_media_registry_set_binding(dom_media_registry *registry,
                                   const dom_media_binding *binding);
int dom_media_registry_get_binding(const dom_media_registry *registry,
                                   dom_body_id body_id,
                                   u32 kind,
                                   dom_media_binding *out_binding);

int dom_media_sample_query(const dom_media_registry *registry,
                           dom_body_id body_id,
                           u32 kind,
                           const dom_posseg_q16 *pos_body_fixed,
                           q48_16 altitude_m,
                           dom_tick tick,
                           dom_media_sample *out_sample);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MEDIA_PROVIDER_H */

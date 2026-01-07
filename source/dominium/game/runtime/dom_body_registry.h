/*
FILE: source/dominium/game/runtime/dom_body_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/body_registry
RESPONSIBILITY: Deterministic body registry (IDs + baseline constants).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_BODY_REGISTRY_H
#define DOM_BODY_REGISTRY_H

#include "domino/core/fixed.h"
#include "domino/core/types.h"
#include "runtime/dom_system_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_BODY_REGISTRY_OK = 0,
    DOM_BODY_REGISTRY_ERR = -1,
    DOM_BODY_REGISTRY_INVALID_ARGUMENT = -2,
    DOM_BODY_REGISTRY_DUPLICATE_ID = -3,
    DOM_BODY_REGISTRY_INVALID_DATA = -4,
    DOM_BODY_REGISTRY_NOT_FOUND = -5
};

enum {
    DOM_BODY_KIND_STAR = 1u,
    DOM_BODY_KIND_PLANET = 2u,
    DOM_BODY_KIND_MOON = 3u,
    DOM_BODY_KIND_STATION = 4u
};

typedef u64 dom_body_id;

typedef struct dom_body_desc {
    const char *string_id;
    u32 string_id_len;
    dom_body_id id;
    dom_system_id system_id;
    u32 kind;
    q48_16 radius_m;
    u64 mu_m3_s2;
    u64 rotation_period_ticks;
    u64 rotation_epoch_tick;
    q16_16 axial_tilt_turns;
    u8 has_axial_tilt;
} dom_body_desc;

typedef struct dom_body_info {
    dom_body_id id;
    dom_system_id system_id;
    u32 kind;
    q48_16 radius_m;
    u64 mu_m3_s2;
    u64 rotation_period_ticks;
    u64 rotation_epoch_tick;
    q16_16 axial_tilt_turns;
    u8 has_axial_tilt;
    const char *string_id;
    u32 string_id_len;
} dom_body_info;

typedef void (*dom_body_iter_fn)(const dom_body_info *info, void *user);

typedef struct dom_body_registry dom_body_registry;

dom_body_registry *dom_body_registry_create(void);
void dom_body_registry_destroy(dom_body_registry *registry);

int dom_body_registry_register(dom_body_registry *registry,
                               const dom_body_desc *desc);
int dom_body_registry_get(const dom_body_registry *registry,
                          dom_body_id id,
                          dom_body_info *out_info);
int dom_body_registry_iterate(const dom_body_registry *registry,
                              dom_body_iter_fn fn,
                              void *user);

int dom_body_registry_add_baseline(dom_body_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_BODY_REGISTRY_H */

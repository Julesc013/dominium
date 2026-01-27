/*
FILE: include/domino/scale/macro_capsule_store.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / scale
RESPONSIBILITY: Public macro capsule storage contract on d_world.
ALLOWED DEPENDENCIES: include/domino/** plus C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: source/** private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Storage order is deterministic by capsule_id.
*/
#ifndef DOMINO_SCALE_MACRO_CAPSULE_STORE_H
#define DOMINO_SCALE_MACRO_CAPSULE_STORE_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

struct d_world;
typedef struct d_world d_world;

typedef struct dom_macro_capsule_blob {
    u64 capsule_id;
    u64 domain_id;
    dom_act_time_t source_tick;
    const unsigned char* bytes;
    u32 byte_count;
} dom_macro_capsule_blob;

int dom_macro_capsule_store_set_blob(d_world* world,
                                     u64 capsule_id,
                                     u64 domain_id,
                                     dom_act_time_t source_tick,
                                     const unsigned char* bytes,
                                     u32 byte_count);

int dom_macro_capsule_store_get_blob(const d_world* world,
                                     u64 capsule_id,
                                     dom_macro_capsule_blob* out_blob);

u32 dom_macro_capsule_store_count(const d_world* world);

int dom_macro_capsule_store_get_by_index(const d_world* world,
                                         u32 index,
                                         dom_macro_capsule_blob* out_blob);

void dom_macro_capsule_store_clear(d_world* world);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SCALE_MACRO_CAPSULE_STORE_H */

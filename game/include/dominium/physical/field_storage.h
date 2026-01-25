/*
FILE: include/dominium/physical/field_storage.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines deterministic field storage for terrain and deposits.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Field queries and updates are deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_FIELD_STORAGE_H
#define DOMINIUM_PHYSICAL_FIELD_STORAGE_H

#include "domino/core/types.h"
#include "domino/domain.h"
#include "domino/dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_field_value_type {
    DOM_FIELD_VALUE_I32 = 0,
    DOM_FIELD_VALUE_U32 = 1,
    DOM_FIELD_VALUE_Q16_16 = 2
} dom_field_value_type;

typedef enum dom_physical_field_id {
    DOM_FIELD_ELEVATION = 1,
    DOM_FIELD_SLOPE = 2,
    DOM_FIELD_SOIL_TYPE = 3,
    DOM_FIELD_BEARING_CAPACITY = 4,
    DOM_FIELD_MOISTURE = 5,
    DOM_FIELD_VEGETATION_BIOMASS = 6,
    DOM_FIELD_SURFACE_WATER = 7,
    DOM_FIELD_SUBSURFACE_WATER = 8,
    DOM_FIELD_POLLUTION = 9,
    DOM_FIELD_RADIATION = 10,
    DOM_FIELD_ORE_DENSITY = 11,
    DOM_FIELD_FOSSIL_ENERGY = 12,
    DOM_FIELD_GROUNDWATER = 13,
    DOM_FIELD_BIOMASS_POTENTIAL = 14
} dom_physical_field_id;

#define DOM_FIELD_BIT(id) (1u << ((id) - 1u))
#define DOM_FIELD_VALUE_UNKNOWN ((i32)0x80000000)

typedef struct dom_field_layer {
    u32 field_id;
    u32 value_type;
    i32 default_value;
    i32 unknown_value;
    i32* values;
} dom_field_layer;

typedef struct dom_field_storage {
    dom_domain_volume_ref domain;
    u32 width;
    u32 height;
    u32 lod_level;
    dom_field_layer* layers;
    u32 layer_count;
    u32 layer_capacity;
} dom_field_storage;

void dom_field_storage_init(dom_field_storage* storage,
                            dom_domain_volume_ref domain,
                            u32 width,
                            u32 height,
                            u32 lod_level,
                            dom_field_layer* layers,
                            u32 layer_capacity);
dom_field_layer* dom_field_layer_add(dom_field_storage* storage,
                                     u32 field_id,
                                     u32 value_type,
                                     i32 default_value,
                                     i32 unknown_value,
                                     i32* values);
dom_field_layer* dom_field_layer_find(dom_field_storage* storage,
                                      u32 field_id);
int dom_field_get_value(const dom_field_storage* storage,
                        u32 field_id,
                        u32 x,
                        u32 y,
                        i32* out_value);
int dom_field_set_value(dom_field_storage* storage,
                        u32 field_id,
                        u32 x,
                        u32 y,
                        i32 value);
int dom_field_fill(dom_field_storage* storage,
                   u32 field_id,
                   i32 value);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_FIELD_STORAGE_H */

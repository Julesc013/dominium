/*
FILE: game/rules/physical/field_storage.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements deterministic field storage for terrain and deposits.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Field queries and updates are deterministic for identical inputs.
*/
#include "dominium/physical/field_storage.h"

#include <string.h>

void dom_field_storage_init(dom_field_storage* storage,
                            dom_domain_volume_ref domain,
                            u32 width,
                            u32 height,
                            u32 lod_level,
                            dom_field_layer* layers,
                            u32 layer_capacity)
{
    if (!storage) {
        return;
    }
    storage->domain = domain;
    storage->width = width;
    storage->height = height;
    storage->lod_level = lod_level;
    storage->layers = layers;
    storage->layer_count = 0u;
    storage->layer_capacity = layer_capacity;
    if (layers && layer_capacity > 0u) {
        memset(layers, 0, sizeof(dom_field_layer) * (size_t)layer_capacity);
    }
}

dom_field_layer* dom_field_layer_add(dom_field_storage* storage,
                                     u32 field_id,
                                     u32 value_type,
                                     i32 default_value,
                                     i32 unknown_value,
                                     i32* values)
{
    dom_field_layer* layer;
    if (!storage || !storage->layers || storage->layer_count >= storage->layer_capacity) {
        return 0;
    }
    layer = &storage->layers[storage->layer_count++];
    memset(layer, 0, sizeof(*layer));
    layer->field_id = field_id;
    layer->value_type = value_type;
    layer->default_value = default_value;
    layer->unknown_value = unknown_value;
    layer->values = values;
    if (values && storage->width > 0u && storage->height > 0u) {
        u32 count = storage->width * storage->height;
        u32 i;
        for (i = 0u; i < count; ++i) {
            values[i] = default_value;
        }
    }
    return layer;
}

dom_field_layer* dom_field_layer_find(dom_field_storage* storage,
                                      u32 field_id)
{
    u32 i;
    if (!storage || !storage->layers) {
        return 0;
    }
    for (i = 0u; i < storage->layer_count; ++i) {
        if (storage->layers[i].field_id == field_id) {
            return &storage->layers[i];
        }
    }
    return 0;
}

static int dom_field_index(const dom_field_storage* storage,
                           u32 x,
                           u32 y,
                           u32* out_index)
{
    if (!storage || !out_index) {
        return -1;
    }
    if (x >= storage->width || y >= storage->height) {
        return -2;
    }
    *out_index = y * storage->width + x;
    return 0;
}

int dom_field_get_value(const dom_field_storage* storage,
                        u32 field_id,
                        u32 x,
                        u32 y,
                        i32* out_value)
{
    u32 index;
    dom_field_layer* layer;
    if (!storage || !out_value) {
        return -1;
    }
    layer = dom_field_layer_find((dom_field_storage*)storage, field_id);
    if (!layer || !layer->values) {
        return -2;
    }
    if (dom_field_index(storage, x, y, &index) != 0) {
        return -3;
    }
    *out_value = layer->values[index];
    return 0;
}

int dom_field_set_value(dom_field_storage* storage,
                        u32 field_id,
                        u32 x,
                        u32 y,
                        i32 value)
{
    u32 index;
    dom_field_layer* layer;
    if (!storage) {
        return -1;
    }
    layer = dom_field_layer_find(storage, field_id);
    if (!layer || !layer->values) {
        return -2;
    }
    if (dom_field_index(storage, x, y, &index) != 0) {
        return -3;
    }
    layer->values[index] = value;
    return 0;
}

int dom_field_fill(dom_field_storage* storage,
                   u32 field_id,
                   i32 value)
{
    dom_field_layer* layer;
    u32 count;
    u32 i;
    if (!storage) {
        return -1;
    }
    layer = dom_field_layer_find(storage, field_id);
    if (!layer || !layer->values) {
        return -2;
    }
    count = storage->width * storage->height;
    for (i = 0u; i < count; ++i) {
        layer->values[i] = value;
    }
    return 0;
}

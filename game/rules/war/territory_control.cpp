/*
FILE: game/rules/war/territory_control.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic territory control registries and estimates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Territory control ordering and updates are deterministic.
*/
#include "dominium/rules/war/territory_control.h"

#include <string.h>

static u32 territory_control_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

void territory_control_registry_init(territory_control_registry* reg,
                                     territory_control* storage,
                                     u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->controls = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(territory_control) * (size_t)capacity);
    }
}

static u32 territory_control_find_index(const territory_control_registry* reg,
                                        u64 territory_id,
                                        int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->controls) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->controls[i].territory_id == territory_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->controls[i].territory_id > territory_id) {
            break;
        }
    }
    return i;
}

territory_control* territory_control_find(territory_control_registry* reg,
                                          u64 territory_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->controls) {
        return 0;
    }
    idx = territory_control_find_index(reg, territory_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->controls[idx];
}

int territory_control_register(territory_control_registry* reg,
                               u64 territory_id,
                               u64 controller_id,
                               u32 control_strength)
{
    int found = 0;
    u32 idx;
    u32 i;
    territory_control* entry;
    if (!reg || !reg->controls || territory_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = territory_control_find_index(reg, territory_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->controls[i] = reg->controls[i - 1u];
    }
    entry = &reg->controls[idx];
    memset(entry, 0, sizeof(*entry));
    entry->territory_id = territory_id;
    entry->current_controller = controller_id;
    entry->control_strength = (control_strength > TERRITORY_CONTROL_SCALE) ? TERRITORY_CONTROL_SCALE : control_strength;
    entry->contested_flag = 0u;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

int territory_control_set_controller(territory_control_registry* reg,
                                     u64 territory_id,
                                     u64 controller_id,
                                     u32 control_strength)
{
    territory_control* entry = territory_control_find(reg, territory_id);
    if (!entry) {
        return -1;
    }
    entry->current_controller = controller_id;
    entry->control_strength = (control_strength > TERRITORY_CONTROL_SCALE) ? TERRITORY_CONTROL_SCALE : control_strength;
    return 0;
}

int territory_control_apply_delta(territory_control_registry* reg,
                                  u64 territory_id,
                                  i32 delta)
{
    territory_control* entry = territory_control_find(reg, territory_id);
    i32 next;
    if (!entry) {
        return -1;
    }
    next = (i32)entry->control_strength + delta;
    if (next < 0) {
        next = 0;
    }
    if ((u32)next > TERRITORY_CONTROL_SCALE) {
        next = (i32)TERRITORY_CONTROL_SCALE;
    }
    entry->control_strength = (u32)next;
    return 0;
}

int territory_control_set_contested(territory_control_registry* reg,
                                    u64 territory_id,
                                    u32 contested_flag)
{
    territory_control* entry = territory_control_find(reg, territory_id);
    if (!entry) {
        return -1;
    }
    entry->contested_flag = contested_flag ? 1u : 0u;
    return 0;
}

int territory_control_estimate_from_view(const dom_epistemic_view* view,
                                         const territory_control* actual,
                                         territory_control_estimate* out)
{
    int is_known = 0;
    if (!out || !actual) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out->controller_id = actual->current_controller;
        out->control_strength = actual->control_strength;
        out->contested_flag = actual->contested_flag;
        out->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out->is_exact = 1;
        return 0;
    }
    out->controller_id = 0u;
    out->control_strength = territory_control_bucket_u32(actual->control_strength, 100u);
    out->contested_flag = actual->contested_flag ? 1u : 0u;
    out->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out->is_exact = 0;
    return 0;
}

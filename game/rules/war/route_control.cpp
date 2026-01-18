/*
FILE: game/rules/war/route_control.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic route control registries and message queues.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Route control ordering and message queues are deterministic.
*/
#include "dominium/rules/war/route_control.h"

#include <string.h>

static u32 route_control_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

void route_control_registry_init(route_control_registry* reg,
                                 route_control* storage,
                                 u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->controls = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(route_control) * (size_t)capacity);
    }
}

static u32 route_control_find_index(const route_control_registry* reg,
                                    u64 route_id,
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
        if (reg->controls[i].route_id == route_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->controls[i].route_id > route_id) {
            break;
        }
    }
    return i;
}

route_control* route_control_find(route_control_registry* reg,
                                  u64 route_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->controls) {
        return 0;
    }
    idx = route_control_find_index(reg, route_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->controls[idx];
}

int route_control_register(route_control_registry* reg,
                           u64 route_id,
                           u64 controller_id,
                           u32 control_strength,
                           u32 access_policy)
{
    int found = 0;
    u32 idx;
    u32 i;
    route_control* entry;
    if (!reg || !reg->controls || route_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = route_control_find_index(reg, route_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->controls[i] = reg->controls[i - 1u];
    }
    entry = &reg->controls[idx];
    memset(entry, 0, sizeof(*entry));
    entry->route_id = route_id;
    entry->controlling_force_ref = controller_id;
    entry->control_strength = (control_strength > ROUTE_CONTROL_SCALE) ? ROUTE_CONTROL_SCALE : control_strength;
    entry->access_policy = access_policy;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

int route_control_apply_delta(route_control_registry* reg,
                              u64 route_id,
                              i32 delta)
{
    route_control* entry = route_control_find(reg, route_id);
    i32 next;
    if (!entry) {
        return -1;
    }
    next = (i32)entry->control_strength + delta;
    if (next < 0) {
        next = 0;
    }
    if ((u32)next > ROUTE_CONTROL_SCALE) {
        next = (i32)ROUTE_CONTROL_SCALE;
    }
    entry->control_strength = (u32)next;
    return 0;
}

int route_control_set_policy(route_control_registry* reg,
                             u64 route_id,
                             u32 access_policy)
{
    route_control* entry = route_control_find(reg, route_id);
    if (!entry) {
        return -1;
    }
    entry->access_policy = access_policy;
    return 0;
}

int route_control_estimate_from_view(const dom_epistemic_view* view,
                                     const route_control* actual,
                                     route_control_estimate* out)
{
    int is_known = 0;
    if (!out || !actual) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out->controller_id = actual->controlling_force_ref;
        out->control_strength = actual->control_strength;
        out->access_policy = actual->access_policy;
        out->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out->is_exact = 1;
        return 0;
    }
    out->controller_id = 0u;
    out->control_strength = route_control_bucket_u32(actual->control_strength, 100u);
    out->access_policy = actual->access_policy;
    out->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out->is_exact = 0;
    return 0;
}

void route_control_message_queue_init(route_control_message_queue* queue,
                                      route_control_message* storage,
                                      u32 capacity,
                                      u64 start_id)
{
    if (!queue) {
        return;
    }
    queue->messages = storage;
    queue->count = 0u;
    queue->capacity = capacity;
    queue->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(route_control_message) * (size_t)capacity);
    }
}

static int route_control_message_before(const route_control_message* a,
                                        const route_control_message* b)
{
    if (a->arrival_act != b->arrival_act) {
        return (a->arrival_act < b->arrival_act);
    }
    if (a->order_key != b->order_key) {
        return (a->order_key < b->order_key);
    }
    if (a->route_id != b->route_id) {
        return (a->route_id < b->route_id);
    }
    return (a->message_id < b->message_id);
}

int route_control_message_queue_push(route_control_message_queue* queue,
                                     const route_control_message* input,
                                     u64* out_id)
{
    int found = 0;
    u32 i;
    u64 message_id;
    route_control_message entry;
    if (!queue || !queue->messages || !input) {
        return -1;
    }
    if (queue->count >= queue->capacity) {
        return -2;
    }
    message_id = input->message_id;
    if (message_id == 0u) {
        message_id = queue->next_id++;
        if (message_id == 0u) {
            message_id = queue->next_id++;
        }
    }
    entry = *input;
    entry.message_id = message_id;
    if (entry.provenance_ref == 0u) {
        entry.provenance_ref = message_id;
    }
    for (i = 0u; i < queue->count; ++i) {
        if (queue->messages[i].message_id == message_id) {
            found = 1;
            break;
        }
        if (route_control_message_before(&entry, &queue->messages[i])) {
            break;
        }
    }
    if (found) {
        return -3;
    }
    if (queue->count > i) {
        u32 j;
        for (j = queue->count; j > i; --j) {
            queue->messages[j] = queue->messages[j - 1u];
        }
    }
    queue->messages[i] = entry;
    queue->count += 1u;
    if (out_id) {
        *out_id = message_id;
    }
    return 0;
}

const route_control_message* route_control_message_at(const route_control_message_queue* queue,
                                                      u32 index)
{
    if (!queue || !queue->messages) {
        return 0;
    }
    if (index >= queue->count) {
        return 0;
    }
    return &queue->messages[index];
}

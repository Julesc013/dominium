/*
FILE: game/rules/scale/interstellar_logistics.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale
RESPONSIBILITY: Implements interstellar logistics flows and scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Flow ordering and arrival processing are deterministic.
*/
#include "dominium/rules/scale/interstellar_logistics.h"

#include <string.h>

void scale_interstellar_registry_init(scale_interstellar_registry* reg,
                                      scale_interstellar_flow* storage,
                                      u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->flows = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(scale_interstellar_flow) * (size_t)capacity);
    }
}

static u32 scale_interstellar_find_index(const scale_interstellar_registry* reg,
                                         u64 flow_id,
                                         int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->flows) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->flows[i].flow_id == flow_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->flows[i].flow_id > flow_id) {
            break;
        }
    }
    return i;
}

int scale_interstellar_register(scale_interstellar_registry* reg,
                                u64 flow_id,
                                u64 src_domain_id,
                                u64 dst_domain_id,
                                u64 asset_id,
                                u64 qty,
                                dom_act_time_t departure_act,
                                dom_act_time_t arrival_act,
                                u64 capacity_ref,
                                u64 provenance_summary)
{
    int found = 0;
    u32 idx;
    u32 i;
    scale_interstellar_flow* entry;
    if (!reg || !reg->flows) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = scale_interstellar_find_index(reg, flow_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->flows[i] = reg->flows[i - 1u];
    }
    entry = &reg->flows[idx];
    memset(entry, 0, sizeof(*entry));
    entry->flow_id = flow_id;
    entry->src_domain_id = src_domain_id;
    entry->dst_domain_id = dst_domain_id;
    entry->asset_id = asset_id;
    entry->qty = qty;
    entry->departure_act = departure_act;
    entry->arrival_act = arrival_act;
    entry->capacity_ref = capacity_ref;
    entry->provenance_summary = provenance_summary;
    entry->next_due_tick = arrival_act;
    entry->status = SCALE_FLOW_PENDING;
    reg->count += 1u;
    return 0;
}

scale_interstellar_flow* scale_interstellar_find(scale_interstellar_registry* reg,
                                                 u64 flow_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->flows) {
        return 0;
    }
    idx = scale_interstellar_find_index(reg, flow_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->flows[idx];
}

u32 scale_interstellar_travel_time(u32 distance_units,
                                   u32 tech_level,
                                   u32 warp)
{
    u64 base = 1000u;
    u64 per_unit = 50u;
    u64 tech_div = (u64)(tech_level + 1u);
    u64 total = base + (u64)distance_units * per_unit;
    u64 time = total / tech_div;
    if (warp == 0u) {
        warp = 1u;
    }
    time = time / (u64)warp;
    if (time == 0u) {
        time = 1u;
    }
    if (time > 0xFFFFFFFFu) {
        return 0xFFFFFFFFu;
    }
    return (u32)time;
}

dom_act_time_t scale_interstellar_compute_arrival(dom_act_time_t departure_act,
                                                  u32 distance_units,
                                                  u32 tech_level,
                                                  u32 warp)
{
    u32 travel = scale_interstellar_travel_time(distance_units, tech_level, warp);
    return departure_act + (dom_act_time_t)travel;
}

static dom_act_time_t interstellar_due_next_tick(void* user, dom_act_time_t now_tick)
{
    scale_interstellar_due_user* due = (scale_interstellar_due_user*)user;
    (void)now_tick;
    if (!due || !due->flow) {
        return DG_DUE_TICK_NONE;
    }
    if (due->flow->status != SCALE_FLOW_PENDING) {
        return DG_DUE_TICK_NONE;
    }
    return due->flow->next_due_tick;
}

static int interstellar_due_process_until(void* user, dom_act_time_t target_tick)
{
    scale_interstellar_due_user* due = (scale_interstellar_due_user*)user;
    scale_interstellar_scheduler* sched;
    scale_interstellar_flow* flow;

    if (!due || !due->scheduler || !due->flow) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    flow = due->flow;
    if (flow->status != SCALE_FLOW_PENDING) {
        return DG_DUE_OK;
    }
    if (flow->next_due_tick == DG_DUE_TICK_NONE ||
        flow->next_due_tick > target_tick) {
        return DG_DUE_OK;
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    flow->status = SCALE_FLOW_ARRIVED;
    flow->next_due_tick = DG_DUE_TICK_NONE;
    if (sched->hook.on_arrival) {
        (void)sched->hook.on_arrival(sched->hook.user, flow);
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_interstellar_due_vtable = {
    interstellar_due_next_tick,
    interstellar_due_process_until
};

int scale_interstellar_scheduler_init(scale_interstellar_scheduler* sched,
                                      dom_time_event* event_storage,
                                      u32 event_capacity,
                                      dg_due_entry* entry_storage,
                                      scale_interstellar_due_user* user_storage,
                                      u32 entry_capacity,
                                      dom_act_time_t start_tick,
                                      scale_interstellar_registry* registry)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage || !registry) {
        return -1;
    }
    rc = dg_due_scheduler_init(&sched->due,
                               event_storage,
                               event_capacity,
                               entry_storage,
                               entry_capacity,
                               start_tick);
    if (rc != DG_DUE_OK) {
        return -2;
    }
    sched->due_events = event_storage;
    sched->due_entries = entry_storage;
    sched->due_users = user_storage;
    sched->registry = registry;
    sched->hook.on_arrival = 0;
    sched->hook.user = 0;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(scale_interstellar_due_user) * (size_t)entry_capacity);
    return 0;
}

void scale_interstellar_set_hook(scale_interstellar_scheduler* sched,
                                 const scale_interstellar_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->hook = *hook;
    } else {
        sched->hook.on_arrival = 0;
        sched->hook.user = 0;
    }
}

static int scale_interstellar_alloc_handle(scale_interstellar_scheduler* sched,
                                           u32* out_handle)
{
    u32 i;
    if (!sched || !sched->due.entries || !out_handle) {
        return -1;
    }
    for (i = 0u; i < sched->due.entry_capacity; ++i) {
        if (!sched->due.entries[i].in_use) {
            *out_handle = i;
            return 0;
        }
    }
    return -2;
}

int scale_interstellar_scheduler_register(scale_interstellar_scheduler* sched,
                                          scale_interstellar_flow* flow)
{
    u32 handle;
    scale_interstellar_due_user* due;
    if (!sched || !flow) {
        return -1;
    }
    if (scale_interstellar_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    if (flow->next_due_tick == DOM_TIME_ACT_MAX) {
        flow->next_due_tick = flow->arrival_act;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->flow = flow;
    if (dg_due_scheduler_register(&sched->due, &g_interstellar_due_vtable, due,
                                  flow->flow_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int scale_interstellar_scheduler_advance(scale_interstellar_scheduler* sched,
                                         dom_act_time_t target_tick)
{
    if (!sched) {
        return -1;
    }
    sched->processed_last = 0u;
    if (dg_due_scheduler_advance(&sched->due, target_tick) != DG_DUE_OK) {
        return -2;
    }
    return 0;
}

dom_act_time_t scale_interstellar_scheduler_next_due(const scale_interstellar_scheduler* sched)
{
    dom_time_event ev;
    if (!sched) {
        return DG_DUE_TICK_NONE;
    }
    if (dom_time_event_peek(&sched->due.queue, &ev) != DOM_TIME_OK) {
        return DG_DUE_TICK_NONE;
    }
    return ev.trigger_time;
}

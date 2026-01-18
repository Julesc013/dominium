/*
FILE: game/rules/logistics/logistics_flow.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / logistics
RESPONSIBILITY: Implements logistics flows and deterministic scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Flow ordering and arrival processing are deterministic.
*/
#include "dominium/rules/logistics/logistics_flow.h"

#include <string.h>

void logistics_flow_registry_init(logistics_flow_registry* reg,
                                  logistics_flow* storage,
                                  u32 capacity,
                                  u64 start_flow_id)
{
    if (!reg) {
        return;
    }
    reg->flows = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_flow_id = start_flow_id ? start_flow_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(logistics_flow) * (size_t)capacity);
    }
}

static u32 logistics_flow_find_index(const logistics_flow_registry* reg,
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

logistics_flow* logistics_flow_find(logistics_flow_registry* reg, u64 flow_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->flows) {
        return 0;
    }
    idx = logistics_flow_find_index(reg, flow_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->flows[idx];
}

static u64 logistics_flow_id_from_input(const logistics_flow_input* input,
                                        u64 seed)
{
    u64 h = seed ? seed : 0xA11CEu;
    if (!input) {
        return h;
    }
    h ^= input->src_store_ref + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->dst_store_ref + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->asset_id + (h << 6) + (h >> 2);
    h ^= (u64)input->qty + (h << 6) + (h >> 2);
    h ^= (u64)input->arrival_act + (h << 6) + (h >> 2);
    if (h == 0u) {
        h = 1u;
    }
    return h;
}

int logistics_flow_schedule(logistics_flow_registry* reg,
                            const logistics_flow_input* input,
                            infra_store_registry* stores,
                            transport_capacity_registry* capacities,
                            civ1_refusal_code* out_refusal)
{
    int found = 0;
    u32 idx;
    u32 i;
    logistics_flow* entry;
    u64 flow_id;

    if (out_refusal) {
        *out_refusal = CIV1_REFUSAL_NONE;
    }
    if (!reg || !reg->flows || !input || !stores || !capacities) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    if (infra_store_consume(stores, input->src_store_ref, input->asset_id, input->qty) != 0) {
        if (out_refusal) {
            *out_refusal = CIV1_REFUSAL_INSUFFICIENT_INPUTS;
        }
        return -3;
    }
    if (transport_capacity_reserve(capacities, input->capacity_ref, input->qty) != 0) {
        if (out_refusal) {
            *out_refusal = CIV1_REFUSAL_CAPACITY_UNAVAILABLE;
        }
        (void)infra_store_add(stores, input->src_store_ref, input->asset_id, input->qty);
        return -4;
    }
    flow_id = input->flow_id ? input->flow_id : logistics_flow_id_from_input(input, reg->next_flow_id++);
    idx = logistics_flow_find_index(reg, flow_id, &found);
    if (found) {
        (void)transport_capacity_release(capacities, input->capacity_ref, input->qty);
        (void)infra_store_add(stores, input->src_store_ref, input->asset_id, input->qty);
        return -5;
    }
    for (i = reg->count; i > idx; --i) {
        reg->flows[i] = reg->flows[i - 1u];
    }
    entry = &reg->flows[idx];
    memset(entry, 0, sizeof(*entry));
    entry->flow_id = flow_id;
    entry->src_store_ref = input->src_store_ref;
    entry->dst_store_ref = input->dst_store_ref;
    entry->asset_id = input->asset_id;
    entry->qty = input->qty;
    entry->departure_act = input->departure_act;
    entry->arrival_act = input->arrival_act;
    entry->capacity_ref = input->capacity_ref;
    entry->provenance_summary = input->provenance_summary ? input->provenance_summary : flow_id;
    entry->status = LOG_FLOW_ACTIVE;
    reg->count += 1u;
    return 0;
}

int logistics_flow_apply_arrival(logistics_flow* flow,
                                 infra_store_registry* stores,
                                 transport_capacity_registry* capacities)
{
    if (!flow || !stores || !capacities) {
        return -1;
    }
    if (flow->status != LOG_FLOW_ACTIVE) {
        return 0;
    }
    (void)infra_store_add(stores, flow->dst_store_ref, flow->asset_id, flow->qty);
    (void)transport_capacity_release(capacities, flow->capacity_ref, flow->qty);
    flow->status = LOG_FLOW_ARRIVED;
    return 0;
}

static dom_act_time_t logistics_flow_next_due(void* user, dom_act_time_t now_tick)
{
    logistics_flow_due_user* due = (logistics_flow_due_user*)user;
    (void)now_tick;
    if (!due || !due->flow) {
        return DG_DUE_TICK_NONE;
    }
    if (due->flow->status != LOG_FLOW_ACTIVE) {
        return DG_DUE_TICK_NONE;
    }
    return due->flow->arrival_act;
}

static int logistics_flow_process_until(void* user, dom_act_time_t target_tick)
{
    logistics_flow_due_user* due = (logistics_flow_due_user*)user;
    logistics_flow_scheduler* sched;
    if (!due || !due->scheduler || !due->flow) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->flow->status != LOG_FLOW_ACTIVE) {
        return DG_DUE_OK;
    }
    if (due->flow->arrival_act == DG_DUE_TICK_NONE ||
        due->flow->arrival_act > target_tick) {
        return DG_DUE_OK;
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    (void)logistics_flow_apply_arrival(due->flow, sched->stores, sched->capacities);
    due->flow->arrival_act = DG_DUE_TICK_NONE;
    return DG_DUE_OK;
}

static dg_due_vtable g_flow_due_vtable = {
    logistics_flow_next_due,
    logistics_flow_process_until
};

int logistics_flow_scheduler_init(logistics_flow_scheduler* sched,
                                  dom_time_event* event_storage,
                                  u32 event_capacity,
                                  dg_due_entry* entry_storage,
                                  logistics_flow_due_user* user_storage,
                                  u32 entry_capacity,
                                  dom_act_time_t start_tick,
                                  logistics_flow_registry* flows,
                                  infra_store_registry* stores,
                                  transport_capacity_registry* capacities)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !flows || !stores || !capacities) {
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
    sched->flows = flows;
    sched->stores = stores;
    sched->capacities = capacities;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(logistics_flow_due_user) * (size_t)entry_capacity);
    return 0;
}

static int logistics_flow_scheduler_alloc_handle(logistics_flow_scheduler* sched, u32* out_handle)
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

int logistics_flow_scheduler_register(logistics_flow_scheduler* sched,
                                      logistics_flow* flow)
{
    u32 handle;
    logistics_flow_due_user* due;
    if (!sched || !flow) {
        return -1;
    }
    if (logistics_flow_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->flow = flow;
    if (dg_due_scheduler_register(&sched->due, &g_flow_due_vtable, due,
                                  flow->flow_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int logistics_flow_scheduler_advance(logistics_flow_scheduler* sched,
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

dom_act_time_t logistics_flow_scheduler_next_due(const logistics_flow_scheduler* sched)
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

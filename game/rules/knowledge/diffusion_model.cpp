/*
FILE: game/rules/knowledge/diffusion_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / knowledge
RESPONSIBILITY: Implements deterministic knowledge diffusion events and scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Diffusion ordering and delivery are deterministic.
*/
#include "dominium/rules/knowledge/diffusion_model.h"

#include <string.h>

void knowledge_diffusion_registry_init(knowledge_diffusion_registry* reg,
                                       knowledge_diffusion_event* storage,
                                       u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->events = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(knowledge_diffusion_event) * (size_t)capacity);
    }
}

static u32 knowledge_diffusion_find_index(const knowledge_diffusion_registry* reg,
                                          u64 diffusion_id,
                                          int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->events) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->events[i].diffusion_id == diffusion_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->events[i].diffusion_id > diffusion_id) {
            break;
        }
    }
    return i;
}

int knowledge_diffusion_register(knowledge_diffusion_registry* reg,
                                 u64 diffusion_id,
                                 u64 knowledge_id,
                                 u64 src_actor_id,
                                 u64 dst_actor_id,
                                 u64 channel_id,
                                 dom_act_time_t send_act,
                                 dom_act_time_t receive_act,
                                 u32 fidelity,
                                 u32 uncertainty,
                                 u64 secrecy_policy_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    knowledge_diffusion_event* entry;
    if (!reg || !reg->events) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = knowledge_diffusion_find_index(reg, diffusion_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->events[i] = reg->events[i - 1u];
    }
    entry = &reg->events[idx];
    memset(entry, 0, sizeof(*entry));
    entry->diffusion_id = diffusion_id;
    entry->knowledge_id = knowledge_id;
    entry->src_actor_id = src_actor_id;
    entry->dst_actor_id = dst_actor_id;
    entry->channel_id = channel_id;
    entry->send_act = send_act;
    entry->receive_act = receive_act;
    entry->fidelity = fidelity;
    entry->uncertainty = uncertainty;
    entry->secrecy_policy_id = secrecy_policy_id;
    entry->next_due_tick = receive_act;
    entry->status = KNOW_DIFFUSION_PENDING;
    reg->count += 1u;
    return 0;
}

knowledge_diffusion_event* knowledge_diffusion_find(knowledge_diffusion_registry* reg,
                                                    u64 diffusion_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->events) {
        return 0;
    }
    idx = knowledge_diffusion_find_index(reg, diffusion_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->events[idx];
}

static dom_act_time_t diffusion_due_next_tick(void* user, dom_act_time_t now_tick)
{
    knowledge_diffusion_due_user* due = (knowledge_diffusion_due_user*)user;
    (void)now_tick;
    if (!due || !due->event) {
        return DG_DUE_TICK_NONE;
    }
    if (due->event->status != KNOW_DIFFUSION_PENDING) {
        return DG_DUE_TICK_NONE;
    }
    return due->event->next_due_tick;
}

static int diffusion_deliver(knowledge_diffusion_scheduler* sched,
                             const knowledge_diffusion_event* ev)
{
    if (sched->hook.deliver) {
        return sched->hook.deliver(sched->hook.user, ev);
    }
    if (sched->institutions) {
        return knowledge_institution_add_holding(sched->institutions,
                                                 ev->dst_actor_id,
                                                 ev->knowledge_id);
    }
    return 0;
}

static int diffusion_due_process_until(void* user, dom_act_time_t target_tick)
{
    knowledge_diffusion_due_user* due = (knowledge_diffusion_due_user*)user;
    knowledge_diffusion_scheduler* sched;
    knowledge_diffusion_event* ev;
    const knowledge_secrecy_policy* policy = 0;

    if (!due || !due->scheduler || !due->event) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    ev = due->event;
    if (ev->status != KNOW_DIFFUSION_PENDING) {
        return DG_DUE_OK;
    }
    if (ev->next_due_tick == DG_DUE_TICK_NONE || ev->next_due_tick > target_tick) {
        return DG_DUE_OK;
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    if (sched->secrecy && ev->secrecy_policy_id) {
        policy = knowledge_secrecy_find((knowledge_secrecy_registry*)sched->secrecy,
                                        ev->secrecy_policy_id);
        if (!policy || !knowledge_secrecy_allows(policy, ev->fidelity)) {
            ev->status = KNOW_DIFFUSION_BLOCKED;
            ev->next_due_tick = DG_DUE_TICK_NONE;
            return DG_DUE_OK;
        }
    }
    if (diffusion_deliver(sched, ev) != 0) {
        ev->status = KNOW_DIFFUSION_BLOCKED;
    } else {
        ev->status = KNOW_DIFFUSION_DELIVERED;
    }
    ev->next_due_tick = DG_DUE_TICK_NONE;
    return DG_DUE_OK;
}

static dg_due_vtable g_diffusion_due_vtable = {
    diffusion_due_next_tick,
    diffusion_due_process_until
};

int knowledge_diffusion_scheduler_init(knowledge_diffusion_scheduler* sched,
                                       dom_time_event* event_storage,
                                       u32 event_capacity,
                                       dg_due_entry* entry_storage,
                                       knowledge_diffusion_due_user* user_storage,
                                       u32 entry_capacity,
                                       dom_act_time_t start_tick,
                                       knowledge_diffusion_registry* registry,
                                       knowledge_institution_registry* institutions,
                                       const knowledge_secrecy_registry* secrecy)
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
    sched->institutions = institutions;
    sched->secrecy = secrecy;
    sched->hook.deliver = 0;
    sched->hook.user = 0;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(knowledge_diffusion_due_user) * (size_t)entry_capacity);
    return 0;
}

void knowledge_diffusion_set_hook(knowledge_diffusion_scheduler* sched,
                                  const knowledge_diffusion_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->hook = *hook;
    } else {
        sched->hook.deliver = 0;
        sched->hook.user = 0;
    }
}

static int knowledge_diffusion_alloc_handle(knowledge_diffusion_scheduler* sched,
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

int knowledge_diffusion_scheduler_register(knowledge_diffusion_scheduler* sched,
                                           knowledge_diffusion_event* event)
{
    u32 handle;
    knowledge_diffusion_due_user* due;
    if (!sched || !event) {
        return -1;
    }
    if (knowledge_diffusion_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    if (event->next_due_tick == DOM_TIME_ACT_MAX) {
        event->next_due_tick = event->receive_act;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->event = event;
    if (dg_due_scheduler_register(&sched->due, &g_diffusion_due_vtable, due,
                                  event->diffusion_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int knowledge_diffusion_scheduler_advance(knowledge_diffusion_scheduler* sched,
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

dom_act_time_t knowledge_diffusion_scheduler_next_due(const knowledge_diffusion_scheduler* sched)
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

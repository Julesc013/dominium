/*
FILE: source/domino/sim/dg_due_sched.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/dg_due_sched
RESPONSIBILITY: Deterministic due-event scheduler for macro stepping.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89 headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Stable ordering by (due_tick, stable_key, event_id).
*/
#include "domino/sim/dg_due_sched.h"

#include <string.h>

static int dg_due_entry_is_valid(const dg_due_entry* entry)
{
    if (!entry) {
        return 0;
    }
    if (!entry->vtable.get_next_due_tick || !entry->vtable.process_until) {
        return 0;
    }
    return 1;
}

static int dg_due_schedule_event(dg_due_scheduler* sched, u32 handle, dom_act_time_t due)
{
    dom_time_event ev;
    dom_time_event_id id;
    int rc;
    dg_due_entry* entry;

    if (!sched || !sched->entries || handle >= sched->entry_capacity) {
        return DG_DUE_INVALID;
    }
    entry = &sched->entries[handle];
    if (!entry->in_use) {
        return DG_DUE_NOT_FOUND;
    }
    rc = dom_time_event_id_next(&sched->id_gen, &id);
    if (rc != DOM_TIME_OK) {
        return DG_DUE_ERR;
    }
    ev.event_id = id;
    ev.trigger_time = due;
    ev.order_key = entry->stable_key;
    ev.payload_id = (u64)handle;
    rc = dom_time_event_schedule(&sched->queue, &ev);
    if (rc != DOM_TIME_OK) {
        return DG_DUE_FULL;
    }
    entry->event_id = id;
    entry->next_due = due;
    return DG_DUE_OK;
}

int dg_due_scheduler_init(dg_due_scheduler* sched,
                          dom_time_event* event_storage,
                          u32 event_capacity,
                          dg_due_entry* entry_storage,
                          u32 entry_capacity,
                          dom_act_time_t start_tick)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || event_capacity == 0u || entry_capacity == 0u) {
        return DG_DUE_INVALID;
    }
    rc = dom_time_event_queue_init(&sched->queue, event_storage, event_capacity);
    if (rc != DOM_TIME_OK) {
        return DG_DUE_ERR;
    }
    rc = dom_time_event_id_init(&sched->id_gen, 1u);
    if (rc != DOM_TIME_OK) {
        return DG_DUE_ERR;
    }
    sched->current_tick = start_tick;
    sched->entries = entry_storage;
    sched->entry_capacity = entry_capacity;
    sched->entry_count = 0u;
    memset(entry_storage, 0, sizeof(dg_due_entry) * entry_capacity);
    return DG_DUE_OK;
}

int dg_due_scheduler_register(dg_due_scheduler* sched,
                              const dg_due_vtable* vtable,
                              void* user,
                              u64 stable_key,
                              u32* out_handle)
{
    u32 i;
    dg_due_entry* entry;
    if (!sched || !vtable || !sched->entries) {
        return DG_DUE_INVALID;
    }
    for (i = 0u; i < sched->entry_capacity; ++i) {
        if (sched->entries[i].in_use && sched->entries[i].stable_key == stable_key) {
            return DG_DUE_DUPLICATE;
        }
    }
    for (i = 0u; i < sched->entry_capacity; ++i) {
        if (!sched->entries[i].in_use) {
            entry = &sched->entries[i];
            memset(entry, 0, sizeof(*entry));
            entry->user = user;
            entry->stable_key = stable_key;
            entry->vtable = *vtable;
            entry->next_due = DG_DUE_TICK_NONE;
            entry->event_id = 0u;
            entry->in_use = 1;
            sched->entry_count += 1u;
            if (out_handle) {
                *out_handle = i;
            }
            return dg_due_scheduler_refresh(sched, i);
        }
    }
    return DG_DUE_FULL;
}

int dg_due_scheduler_unregister(dg_due_scheduler* sched, u32 handle)
{
    dg_due_entry* entry;
    if (!sched || !sched->entries || handle >= sched->entry_capacity) {
        return DG_DUE_INVALID;
    }
    entry = &sched->entries[handle];
    if (!entry->in_use) {
        return DG_DUE_NOT_FOUND;
    }
    if (entry->event_id != 0u) {
        (void)dom_time_event_cancel(&sched->queue, entry->event_id);
    }
    memset(entry, 0, sizeof(*entry));
    if (sched->entry_count > 0u) {
        sched->entry_count -= 1u;
    }
    return DG_DUE_OK;
}

int dg_due_scheduler_refresh(dg_due_scheduler* sched, u32 handle)
{
    dg_due_entry* entry;
    dom_act_time_t due;
    int rc = DG_DUE_OK;
    if (!sched || !sched->entries || handle >= sched->entry_capacity) {
        return DG_DUE_INVALID;
    }
    entry = &sched->entries[handle];
    if (!entry->in_use || !dg_due_entry_is_valid(entry)) {
        return DG_DUE_NOT_FOUND;
    }
    due = entry->vtable.get_next_due_tick(entry->user, sched->current_tick);
    if (due == DG_DUE_TICK_NONE) {
        if (entry->event_id != 0u) {
            (void)dom_time_event_cancel(&sched->queue, entry->event_id);
        }
        entry->event_id = 0u;
        entry->next_due = DG_DUE_TICK_NONE;
        return DG_DUE_OK;
    }
    if (due < sched->current_tick) {
        due = sched->current_tick;
        rc = DG_DUE_BACKWARDS;
    }
    if (entry->event_id != 0u) {
        (void)dom_time_event_cancel(&sched->queue, entry->event_id);
        entry->event_id = 0u;
    }
    if (dg_due_schedule_event(sched, handle, due) != DG_DUE_OK) {
        return DG_DUE_FULL;
    }
    return rc;
}

int dg_due_scheduler_advance(dg_due_scheduler* sched, dom_act_time_t target_tick)
{
    dom_time_event ev;
    int rc;
    if (!sched) {
        return DG_DUE_INVALID;
    }
    if (target_tick < sched->current_tick) {
        return DG_DUE_BACKWARDS;
    }
    while (dom_time_event_peek(&sched->queue, &ev) == DOM_TIME_OK) {
        u32 handle;
        dg_due_entry* entry;
        if (ev.trigger_time > target_tick) {
            break;
        }
        rc = dom_time_event_pop(&sched->queue, &ev);
        if (rc != DOM_TIME_OK) {
            return DG_DUE_ERR;
        }
        handle = (u32)ev.payload_id;
        if (!sched->entries || handle >= sched->entry_capacity) {
            continue;
        }
        entry = &sched->entries[handle];
        if (!entry->in_use || entry->event_id != ev.event_id) {
            continue;
        }
        entry->event_id = 0u;
        if (!dg_due_entry_is_valid(entry)) {
            return DG_DUE_INVALID;
        }
        rc = entry->vtable.process_until(entry->user, target_tick);
        if (rc != 0) {
            return DG_DUE_ERR;
        }
        rc = dg_due_scheduler_refresh(sched, handle);
        if (rc == DG_DUE_BACKWARDS) {
            return rc;
        }
        if (rc != DG_DUE_OK) {
            return rc;
        }
    }
    sched->current_tick = target_tick;
    return DG_DUE_OK;
}

dom_act_time_t dg_due_scheduler_current_tick(const dg_due_scheduler* sched)
{
    if (!sched) {
        return 0;
    }
    return sched->current_tick;
}

u32 dg_due_scheduler_pending(const dg_due_scheduler* sched)
{
    u32 count = 0u;
    if (!sched) {
        return 0u;
    }
    (void)dom_time_event_queue_size(&sched->queue, &count);
    return count;
}

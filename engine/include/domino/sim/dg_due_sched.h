/*
FILE: include/domino/sim/dg_due_sched.h
MODULE: Domino
RESPONSIBILITY: Deterministic due-event scheduler for macro stepping.
NOTES: Pure C90 header; no platform headers, no gameplay logic.
*/
#ifndef DOMINO_SIM_DG_DUE_SCHED_H
#define DOMINO_SIM_DG_DUE_SCHED_H

#include "domino/core/dom_time_events.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DG_DUE_OK = 0,
    DG_DUE_ERR = -1,
    DG_DUE_INVALID = -2,
    DG_DUE_FULL = -3,
    DG_DUE_DUPLICATE = -4,
    DG_DUE_NOT_FOUND = -5,
    DG_DUE_BACKWARDS = -6
};

#define DG_DUE_TICK_NONE DOM_TIME_ACT_MAX

typedef struct dg_due_vtable {
    dom_act_time_t (*get_next_due_tick)(void* user, dom_act_time_t now_tick);
    int            (*process_until)(void* user, dom_act_time_t target_tick);
} dg_due_vtable;

typedef struct dg_due_entry {
    void*             user;
    u64               stable_key;
    dom_time_event_id event_id;
    dom_act_time_t    next_due;
    dg_due_vtable     vtable;
    int               in_use;
} dg_due_entry;

typedef struct dg_due_scheduler {
    dom_time_event_queue  queue;
    dom_time_event_id_gen id_gen;
    dom_act_time_t        current_tick;
    dg_due_entry*         entries;
    u32                   entry_capacity;
    u32                   entry_count;
} dg_due_scheduler;

int dg_due_scheduler_init(dg_due_scheduler* sched,
                          dom_time_event* event_storage,
                          u32 event_capacity,
                          dg_due_entry* entry_storage,
                          u32 entry_capacity,
                          dom_act_time_t start_tick);

int dg_due_scheduler_register(dg_due_scheduler* sched,
                              const dg_due_vtable* vtable,
                              void* user,
                              u64 stable_key,
                              u32* out_handle);

int dg_due_scheduler_unregister(dg_due_scheduler* sched, u32 handle);
int dg_due_scheduler_refresh(dg_due_scheduler* sched, u32 handle);

int dg_due_scheduler_advance(dg_due_scheduler* sched, dom_act_time_t target_tick);
dom_act_time_t dg_due_scheduler_current_tick(const dg_due_scheduler* sched);
u32 dg_due_scheduler_pending(const dg_due_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SIM_DG_DUE_SCHED_H */

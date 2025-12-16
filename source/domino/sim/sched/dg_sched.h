/*
FILE: source/domino/sim/sched/dg_sched.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sched/dg_sched
RESPONSIBILITY: Implements `dg_sched`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic tick scheduler (C89).
 *
 * The scheduler defines canonical phase execution order, bounded work budgets,
 * deterministic carryover queues, and the sorted delta commit point.
 */
#ifndef DG_SCHED_H
#define DG_SCHED_H

#include "sim/sched/dg_phase.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"
#include "sim/sched/dg_sched_hash.h"
#include "sim/sched/dg_sched_replay.h"

#include "sim/act/dg_delta_registry.h"
#include "sim/act/dg_delta_buffer.h"
#include "sim/act/dg_delta_commit.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dg_sched;

typedef void (*dg_sched_phase_handler_fn)(struct dg_sched *sched, void *user_ctx);
typedef void (*dg_sched_work_fn)(struct dg_sched *sched, const dg_work_item *item, void *user_ctx);

typedef struct dg_sched_phase_handler {
    dg_sched_phase_handler_fn fn;
    void                     *user_ctx;
    u64                       priority_key;
    u32                       insert_index;
} dg_sched_phase_handler;

typedef struct dg_sched_phase_handlers {
    dg_sched_phase_handler *handlers;
    u32                     count;
    u32                     capacity;
} dg_sched_phase_handlers;

typedef struct dg_sched {
    dg_tick tick;
    dg_phase current_phase;

    dg_budget budget; /* reused per phase (begin_tick called per phase) */
    u32       phase_budget_limit[DG_PH_COUNT];
    u32       domain_default_limit;
    u32       chunk_default_limit;

    dg_work_queue phase_queues[DG_PH_COUNT];

    dg_sched_phase_handlers phase_handlers[DG_PH_COUNT];
    u32 next_phase_handler_insert;
    u32 probe_phase_handler_refused;

    dg_sched_work_fn work_fn;
    void            *work_user;

    dg_delta_registry delta_registry;
    dg_delta_buffer   delta_buffer;

    dg_sched_hash_ctx   hash;
    dg_sched_replay_ctx replay;
} dg_sched;

void dg_sched_init(dg_sched *s);
void dg_sched_free(dg_sched *s);

/* Reserve bounded storage for queues/handlers/budgets/delta buffer. */
int dg_sched_reserve(
    dg_sched *s,
    u32       phase_work_capacity,
    u32       phase_handler_capacity,
    u32       budget_domain_capacity,
    u32       budget_chunk_capacity,
    u32       max_deltas_per_tick,
    u32       delta_arena_bytes
);

/* Configure per-phase budget limits (global units per phase). */
void dg_sched_set_phase_budget_limit(dg_sched *s, dg_phase phase, u32 global_limit);
void dg_sched_set_domain_chunk_defaults(dg_sched *s, u32 domain_default_limit, u32 chunk_default_limit);

/* Register deterministic phase handlers (sorted by priority_key then stable). */
int dg_sched_register_phase_handler(
    dg_sched                 *s,
    dg_phase                  phase,
    dg_sched_phase_handler_fn handler_fn,
    u64                       priority_key,
    void                     *user_ctx
);

u32 dg_sched_probe_phase_handler_refused(const dg_sched *s);

/* Set work callback used when processing work queues. */
void dg_sched_set_work_handler(dg_sched *s, dg_sched_work_fn fn, void *user_ctx);

/* Enqueue a work item into a per-phase carryover queue (bounded). */
int dg_sched_enqueue_work(dg_sched *s, dg_phase phase, const dg_work_item *it);

/* Buffer a delta packet for later commit. */
int dg_sched_emit_delta(dg_sched *s, const dg_order_key *commit_key, const dg_pkt_delta *delta);

/* Process queued work for a phase under current budget, using 'fn' if non-NULL
 * (defaults to scheduler's work handler). Returns number processed.
 */
u32 dg_sched_process_phase_work(dg_sched *s, dg_phase phase, dg_sched_work_fn fn, void *user_ctx);

/* Run a full tick skeleton (no domain semantics). */
int dg_sched_tick(dg_sched *s, void *world, dg_tick tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_SCHED_H */

/*
FILE: source/domino/sim/sched/dg_sched.c
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
#include <stdlib.h>
#include <string.h>

#include "sim/sched/dg_sched.h"

static void dg_sched_phase_handlers_init(dg_sched_phase_handlers *ph) {
    if (!ph) {
        return;
    }
    ph->handlers = (dg_sched_phase_handler *)0;
    ph->count = 0u;
    ph->capacity = 0u;
}

static void dg_sched_phase_handlers_free(dg_sched_phase_handlers *ph) {
    if (!ph) {
        return;
    }
    if (ph->handlers) {
        free(ph->handlers);
    }
    dg_sched_phase_handlers_init(ph);
}

static int dg_sched_phase_handlers_reserve(dg_sched_phase_handlers *ph, u32 capacity) {
    dg_sched_phase_handler *h;
    if (!ph) {
        return -1;
    }
    dg_sched_phase_handlers_free(ph);
    if (capacity == 0u) {
        return 0;
    }
    h = (dg_sched_phase_handler *)malloc(sizeof(dg_sched_phase_handler) * (size_t)capacity);
    if (!h) {
        return -2;
    }
    memset(h, 0, sizeof(dg_sched_phase_handler) * (size_t)capacity);
    ph->handlers = h;
    ph->capacity = capacity;
    ph->count = 0u;
    return 0;
}

void dg_sched_init(dg_sched *s) {
    u32 i;
    if (!s) {
        return;
    }
    memset(s, 0, sizeof(*s));
    s->tick = 0u;
    s->current_phase = DG_PH_INPUT;
    dg_budget_init(&s->budget);
    for (i = 0u; i < (u32)DG_PH_COUNT; ++i) {
        s->phase_budget_limit[i] = DG_BUDGET_UNLIMITED;
        dg_work_queue_init(&s->phase_queues[i]);
        dg_sched_phase_handlers_init(&s->phase_handlers[i]);
    }
    s->domain_default_limit = DG_BUDGET_UNLIMITED;
    s->chunk_default_limit = DG_BUDGET_UNLIMITED;
    s->next_phase_handler_insert = 0u;
    s->probe_phase_handler_refused = 0u;
    s->work_fn = (dg_sched_work_fn)0;
    s->work_user = (void *)0;
    dg_delta_registry_init(&s->delta_registry);
    dg_delta_buffer_init(&s->delta_buffer);
    dg_sched_hash_init(&s->hash);
    dg_sched_replay_init(&s->replay);
}

void dg_sched_free(dg_sched *s) {
    u32 i;
    if (!s) {
        return;
    }
    for (i = 0u; i < (u32)DG_PH_COUNT; ++i) {
        dg_work_queue_free(&s->phase_queues[i]);
        dg_sched_phase_handlers_free(&s->phase_handlers[i]);
    }
    dg_budget_free(&s->budget);
    dg_delta_registry_free(&s->delta_registry);
    dg_delta_buffer_free(&s->delta_buffer);
    dg_sched_init(s);
}

int dg_sched_reserve(
    dg_sched *s,
    u32       phase_work_capacity,
    u32       phase_handler_capacity,
    u32       budget_domain_capacity,
    u32       budget_chunk_capacity,
    u32       max_deltas_per_tick,
    u32       delta_arena_bytes
) {
    u32 i;
    int rc;

    if (!s) {
        return -1;
    }

    /* (Re)initialize everything with new bounded storage. */
    dg_sched_free(s);

    rc = dg_budget_reserve(&s->budget, budget_domain_capacity, budget_chunk_capacity);
    if (rc != 0) {
        dg_sched_free(s);
        return -2;
    }

    for (i = 0u; i < (u32)DG_PH_COUNT; ++i) {
        rc = dg_work_queue_reserve(&s->phase_queues[i], phase_work_capacity);
        if (rc != 0) {
            dg_sched_free(s);
            return -3;
        }
        rc = dg_sched_phase_handlers_reserve(&s->phase_handlers[i], phase_handler_capacity);
        if (rc != 0) {
            dg_sched_free(s);
            return -4;
        }
    }

    rc = dg_delta_buffer_reserve(&s->delta_buffer, max_deltas_per_tick, delta_arena_bytes);
    if (rc != 0) {
        dg_sched_free(s);
        return -5;
    }

    return 0;
}

void dg_sched_set_phase_budget_limit(dg_sched *s, dg_phase phase, u32 global_limit) {
    if (!s) {
        return;
    }
    if (!dg_phase_is_valid(phase)) {
        return;
    }
    s->phase_budget_limit[(u32)phase] = global_limit;
}

void dg_sched_set_domain_chunk_defaults(dg_sched *s, u32 domain_default_limit, u32 chunk_default_limit) {
    if (!s) {
        return;
    }
    s->domain_default_limit = domain_default_limit;
    s->chunk_default_limit = chunk_default_limit;
}

static u32 dg_sched_phase_handler_upper_bound(const dg_sched_phase_handlers *ph, u64 priority_key) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;

    if (!ph) {
        return 0u;
    }
    hi = ph->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (ph->handlers[mid].priority_key <= priority_key) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

int dg_sched_register_phase_handler(
    dg_sched                 *s,
    dg_phase                  phase,
    dg_sched_phase_handler_fn handler_fn,
    u64                       priority_key,
    void                     *user_ctx
) {
    dg_sched_phase_handlers *ph;
    dg_sched_phase_handler h;
    u32 idx;

    if (!s || !handler_fn) {
        return -1;
    }
    if (!dg_phase_is_valid(phase)) {
        return -2;
    }

    ph = &s->phase_handlers[(u32)phase];
    if (!ph->handlers || ph->capacity == 0u || ph->count >= ph->capacity) {
        s->probe_phase_handler_refused += 1u;
        return -3;
    }

    memset(&h, 0, sizeof(h));
    h.fn = handler_fn;
    h.user_ctx = user_ctx;
    h.priority_key = priority_key;
    h.insert_index = s->next_phase_handler_insert++;

    idx = dg_sched_phase_handler_upper_bound(ph, priority_key);
    if (idx < ph->count) {
        memmove(&ph->handlers[idx + 1u], &ph->handlers[idx],
                sizeof(dg_sched_phase_handler) * (size_t)(ph->count - idx));
    }
    ph->handlers[idx] = h;
    ph->count += 1u;
    return 0;
}

u32 dg_sched_probe_phase_handler_refused(const dg_sched *s) {
    return s ? s->probe_phase_handler_refused : 0u;
}

void dg_sched_set_work_handler(dg_sched *s, dg_sched_work_fn fn, void *user_ctx) {
    if (!s) {
        return;
    }
    s->work_fn = fn;
    s->work_user = user_ctx;
}

int dg_sched_enqueue_work(dg_sched *s, dg_phase phase, const dg_work_item *it) {
    if (!s || !it) {
        return -1;
    }
    if (!dg_phase_is_valid(phase)) {
        return -2;
    }
    if (it->key.phase != (u16)phase) {
        return -3;
    }
    return dg_work_queue_push(&s->phase_queues[(u32)phase], it);
}

int dg_sched_emit_delta(dg_sched *s, const dg_order_key *commit_key, const dg_pkt_delta *delta) {
    if (!s || !commit_key || !delta) {
        return -1;
    }
    return dg_delta_buffer_push(&s->delta_buffer, commit_key, delta);
}

u32 dg_sched_process_phase_work(dg_sched *s, dg_phase phase, dg_sched_work_fn fn, void *user_ctx) {
    dg_work_queue *q;
    u32 processed = 0u;
    dg_sched_work_fn use_fn;
    void *use_user;

    if (!s || !dg_phase_is_valid(phase)) {
        return 0u;
    }
    q = &s->phase_queues[(u32)phase];
    use_fn = fn ? fn : s->work_fn;
    use_user = fn ? user_ctx : s->work_user;

    if (!use_fn) {
        return 0u;
    }

    for (;;) {
        const dg_work_item *next = dg_work_queue_peek_next(q);
        dg_budget_scope scope;
        dg_work_item item;

        if (!next) {
            break;
        }

        scope = dg_budget_scope_domain_chunk(next->key.domain_id, next->key.chunk_id);
        if (!dg_budget_try_consume(&s->budget, &scope, next->cost_units)) {
            break; /* deterministic deferral: do not skip */
        }

        if (!dg_work_queue_pop_next(q, &item)) {
            break;
        }
        use_fn(s, &item, use_user);
        processed += 1u;
    }

    return processed;
}

static void dg_sched_run_phase_handlers(dg_sched *s, dg_phase phase) {
    dg_sched_phase_handlers *ph;
    u32 i;

    if (!s || !dg_phase_is_valid(phase)) {
        return;
    }
    ph = &s->phase_handlers[(u32)phase];
    for (i = 0u; i < ph->count; ++i) {
        if (ph->handlers[i].fn) {
            ph->handlers[i].fn(s, ph->handlers[i].user_ctx);
        }
    }
}

int dg_sched_tick(dg_sched *s, void *world, dg_tick tick) {
    dg_phase phase;
    dg_delta_commit_stats commit_stats;
    u32 i;

    if (!s) {
        return -1;
    }

    s->tick = tick;
    dg_sched_hash_begin_tick(&s->hash, tick);
    dg_sched_replay_begin_tick(&s->replay, tick);
    dg_delta_buffer_begin_tick(&s->delta_buffer, tick);

    for (phase = (dg_phase)0; phase < DG_PH_COUNT; phase = (dg_phase)(phase + 1)) {
        s->current_phase = phase;

        dg_budget_set_limits(&s->budget, s->phase_budget_limit[(u32)phase], s->domain_default_limit, s->chunk_default_limit);
        dg_budget_begin_tick(&s->budget, tick);

        dg_sched_hash_phase_begin(&s->hash, phase);
        dg_sched_replay_phase_begin(&s->replay, phase);

        dg_sched_run_phase_handlers(s, phase);
        (void)dg_sched_process_phase_work(s, phase, (dg_sched_work_fn)0, (void *)0);

        if (phase == DG_PH_COMMIT) {
            (void)dg_delta_commit_apply(world, &s->delta_registry, &s->delta_buffer, &commit_stats);
            /* Record committed deltas in the same canonical order (sorted in-place). */
            for (i = 0u; i < s->delta_buffer.count; ++i) {
                const dg_delta_record *r = dg_delta_buffer_at(&s->delta_buffer, i);
                const dg_delta_registry_entry *e;
                dg_pkt_delta pkt;
                if (!r) {
                    continue;
                }
                e = dg_delta_registry_find(&s->delta_registry, r->hdr.type_id);
                if (!e || !e->vtbl.apply) {
                    continue;
                }
                pkt.hdr = r->hdr;
                pkt.payload = r->payload;
                pkt.payload_len = r->payload_len;
                dg_sched_hash_record_committed_delta(&s->hash, &r->key, &pkt);
                dg_sched_replay_record_committed_delta(&s->replay, &r->key, &pkt);
            }
        }

        dg_sched_hash_phase_end(&s->hash, phase);
        dg_sched_replay_phase_end(&s->replay, phase);
    }

    return 0;
}

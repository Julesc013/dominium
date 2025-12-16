/*
FILE: source/domino/sim/lod/dg_promo.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_promo
RESPONSIBILITY: Implements `dg_promo`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "sim/lod/dg_promo.h"
#include "sim/sched/dg_sched.h"

#include "core/det_invariants.h"

static dg_rep_state dg_promo_desired_state(q16_16 score, const dg_promo_thresholds *t) {
    if (!t) {
        return DG_REP_R3_DORMANT;
    }
    if (score >= t->thr_r0) return DG_REP_R0_FULL;
    if (score >= t->thr_r1) return DG_REP_R1_LITE;
    if (score >= t->thr_r2) return DG_REP_R2_AGG;
    return DG_REP_R3_DORMANT;
}

static u32 dg_promo_cost_units(const dg_promo_config *cfg, dg_rep_state from, dg_rep_state to) {
    u32 steps;
    if (!cfg) {
        return 1u;
    }
    if (from == to) {
        return 0u;
    }
    if (from < to) {
        steps = (u32)((u32)to - (u32)from);
        return steps * (cfg->demote_cost_per_step ? cfg->demote_cost_per_step : 1u);
    }
    steps = (u32)((u32)from - (u32)to);
    return steps * (cfg->promote_cost_per_step ? cfg->promote_cost_per_step : 1u);
}

dg_promo_config dg_promo_config_defaults(void) {
    dg_promo_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.thresholds.thr_r0 = (q16_16)(2 << Q16_16_FRAC_BITS);
    cfg.thresholds.thr_r1 = (q16_16)(1 << Q16_16_FRAC_BITS);
    cfg.thresholds.thr_r2 = (q16_16)(1 << (Q16_16_FRAC_BITS - 1)); /* 0.5 */
    cfg.promote_cost_per_step = 1u;
    cfg.demote_cost_per_step = 1u;
    return cfg;
}

void dg_promo_init(dg_promo_ctx *pc) {
    if (!pc) return;
    memset(pc, 0, sizeof(*pc));
    pc->cfg = dg_promo_config_defaults();
    dg_interest_list_init(&pc->interest_list);
}

void dg_promo_free(dg_promo_ctx *pc) {
    if (!pc) return;
    if (pc->chunk_scratch) free(pc->chunk_scratch);
    if (pc->candidates) free(pc->candidates);
    if (pc->transition_scratch) free(pc->transition_scratch);
    if (pc->queue.items) free(pc->queue.items);
    dg_interest_list_free(&pc->interest_list);
    dg_promo_init(pc);
}

int dg_promo_reserve(
    dg_promo_ctx *pc,
    u32           max_chunks,
    u32           max_candidates,
    u32           max_transitions,
    u32           max_interest_vols
) {
    if (!pc) return -1;

    dg_promo_free(pc);

    if (max_chunks > 0u) {
        pc->chunk_scratch = (dg_chunk_id *)malloc(sizeof(dg_chunk_id) * (size_t)max_chunks);
        if (!pc->chunk_scratch) {
            dg_promo_free(pc);
            return -2;
        }
        memset(pc->chunk_scratch, 0, sizeof(dg_chunk_id) * (size_t)max_chunks);
        pc->chunk_capacity = max_chunks;
    }

    if (max_candidates > 0u) {
        pc->candidates = (dg_lod_candidate *)malloc(sizeof(dg_lod_candidate) * (size_t)max_candidates);
        if (!pc->candidates) {
            dg_promo_free(pc);
            return -3;
        }
        memset(pc->candidates, 0, sizeof(dg_lod_candidate) * (size_t)max_candidates);
        pc->candidate_capacity = max_candidates;
    }

    if (max_transitions > 0u) {
        pc->transition_scratch = (dg_promo_transition *)malloc(sizeof(dg_promo_transition) * (size_t)max_transitions);
        if (!pc->transition_scratch) {
            dg_promo_free(pc);
            return -4;
        }
        memset(pc->transition_scratch, 0, sizeof(dg_promo_transition) * (size_t)max_transitions);
        pc->transition_capacity = max_transitions;

        pc->queue.items = (dg_promo_transition *)malloc(sizeof(dg_promo_transition) * (size_t)max_transitions);
        if (!pc->queue.items) {
            dg_promo_free(pc);
            return -5;
        }
        memset(pc->queue.items, 0, sizeof(dg_promo_transition) * (size_t)max_transitions);
        pc->queue.capacity = max_transitions;
        pc->queue.count = 0u;
        pc->queue.next = 0u;
        pc->queue.probe_refused = 0u;
    }

    if (max_interest_vols > 0u) {
        if (dg_interest_list_reserve(&pc->interest_list, max_interest_vols) != 0) {
            dg_promo_free(pc);
            return -6;
        }
    }

    pc->cfg = dg_promo_config_defaults();
    return 0;
}

void dg_promo_set_index(dg_promo_ctx *pc, const dg_lod_index *index) {
    if (!pc) return;
    pc->index = index;
}

void dg_promo_set_interest(dg_promo_ctx *pc, dg_interest_ctx *interest) {
    if (!pc) return;
    pc->interest = interest;
}

void dg_promo_set_resolver(dg_promo_ctx *pc, dg_promo_resolve_fn fn, void *user_ctx) {
    if (!pc) return;
    pc->resolve_fn = fn;
    pc->resolve_user = user_ctx;
}

void dg_promo_set_config(dg_promo_ctx *pc, const dg_promo_config *cfg) {
    if (!pc || !cfg) return;
    pc->cfg = *cfg;
}

u32 dg_promo_queue_count(const dg_promo_ctx *pc) {
    return pc ? pc->queue.count : 0u;
}

u32 dg_promo_queue_pending(const dg_promo_ctx *pc) {
    if (!pc) return 0u;
    if (pc->queue.next >= pc->queue.count) return 0u;
    return pc->queue.count - pc->queue.next;
}

const dg_promo_transition *dg_promo_queue_at(const dg_promo_ctx *pc, u32 index) {
    if (!pc || !pc->queue.items) return (const dg_promo_transition *)0;
    if (index >= pc->queue.count) return (const dg_promo_transition *)0;
    return &pc->queue.items[index];
}

u32 dg_promo_probe_candidates_truncated(const dg_promo_ctx *pc) {
    return pc ? pc->probe_candidates_truncated : 0u;
}

u32 dg_promo_probe_transitions_truncated(const dg_promo_ctx *pc) {
    return pc ? pc->probe_transitions_truncated : 0u;
}

static int dg_promo_cmp_u64(u64 a, u64 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_promo_cmp_i32_desc(i32 a, i32 b) {
    if (a > b) return -1;
    if (a < b) return 1;
    return 0;
}

static int dg_promo_transition_cmp(const dg_promo_transition *a, const dg_promo_transition *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    /* desired rep state priority (R0 first). */
    c = (int)a->to_state - (int)b->to_state;
    if (c) return c;

    /* descending score */
    c = dg_promo_cmp_i32_desc((i32)a->score, (i32)b->score);
    if (c) return c;

    /* stable tiebreak key: (domain_id, chunk_id, entity_id, sub_id) */
    c = dg_promo_cmp_u64(a->key.domain_id, b->key.domain_id);
    if (c) return c;
    c = dg_promo_cmp_u64(a->key.chunk_id, b->key.chunk_id);
    if (c) return c;
    c = dg_promo_cmp_u64(a->key.entity_id, b->key.entity_id);
    if (c) return c;
    c = dg_promo_cmp_u64(a->key.sub_id, b->key.sub_id);
    if (c) return c;

    /* last-resort tie-break for total ordering (should rarely differ). */
    c = dg_promo_cmp_u64((u64)a->class_id, (u64)b->class_id);
    if (c) return c;
    return 0;
}

static void dg_promo_insertion_sort(dg_promo_transition *arr, u32 count) {
    u32 i;
    if (!arr) return;
    for (i = 1u; i < count; ++i) {
        dg_promo_transition key = arr[i];
        u32 j = i;
        while (j > 0u && dg_promo_transition_cmp(&arr[j - 1u], &key) > 0) {
            arr[j] = arr[j - 1u];
            --j;
        }
        arr[j] = key;
    }
}

static void dg_promo_queue_clear(dg_promo_ctx *pc) {
    if (!pc) return;
    pc->queue.count = 0u;
    pc->queue.next = 0u;
}

int dg_promo_plan_and_enqueue(dg_promo_ctx *pc, dg_tick tick) {
    u32 chunk_count;
    u32 cand_count = 0u;
    u32 tr_count = 0u;
    u32 i;

    if (!pc || !pc->index) return -1;
    if (!pc->chunk_scratch || pc->chunk_capacity == 0u) return -2;
    if (!pc->candidates || pc->candidate_capacity == 0u) return -3;
    if (!pc->transition_scratch || pc->transition_capacity == 0u) return -4;
    if (!pc->queue.items || pc->queue.capacity == 0u) return -5;

    /* If we still have pending transitions, do not re-plan; carryover must keep order. */
    if (dg_promo_queue_pending(pc) > 0u) {
        return 1;
    }

    dg_promo_queue_clear(pc);
    pc->probe_candidates_truncated = 0u;
    pc->probe_transitions_truncated = 0u;

    /* Collect interest volumes (may be empty). */
    if (pc->interest) {
        (void)dg_interest_collect(pc->interest, tick, &pc->interest_list);
    } else {
        dg_interest_list_clear(&pc->interest_list);
    }

    /* Determine chunk scan set in deterministic order. */
    chunk_count = dg_lod_index_collect_chunks(pc->index, pc->chunk_scratch, pc->chunk_capacity);

    /* Gather candidates chunk-locally. */
    for (i = 0u; i < chunk_count; ++i) {
        dg_chunk_id cid = pc->chunk_scratch[i];
        u32 remaining = (cand_count < pc->candidate_capacity) ? (pc->candidate_capacity - cand_count) : 0u;
        u32 got;
        if (remaining == 0u) {
            pc->probe_candidates_truncated += 1u;
            break;
        }
        got = dg_lod_index_query(pc->index, cid, 0u, &pc->candidates[cand_count], remaining);
        cand_count += got;
    }

    /* Score candidates and build transition list. */
    for (i = 0u; i < cand_count; ++i) {
        const dg_lod_candidate *c = &pc->candidates[i];
        q16_16 score;
        dg_rep_state desired;
        dg_representable *r;
        dg_rep_state cur;

        if (!pc->resolve_fn) {
            break;
        }

        score = dg_interest_score_object(&c->key, &c->pos, c->class_id, &pc->interest_list);
        desired = dg_promo_desired_state(score, &pc->cfg.thresholds);

        r = pc->resolve_fn(pc->resolve_user, &c->key, c->class_id);
        if (!r) {
            continue;
        }
        cur = dg_representable_get_rep_state(r);

        if (cur == desired) {
            continue;
        }

        if (tr_count >= pc->transition_capacity) {
            pc->probe_transitions_truncated += 1u;
            break;
        }

        memset(&pc->transition_scratch[tr_count], 0, sizeof(pc->transition_scratch[tr_count]));
        pc->transition_scratch[tr_count].key = c->key;
        pc->transition_scratch[tr_count].class_id = c->class_id;
        pc->transition_scratch[tr_count].from_state = cur;
        pc->transition_scratch[tr_count].to_state = desired;
        pc->transition_scratch[tr_count].score = score;
        pc->transition_scratch[tr_count].cost_units = dg_promo_cost_units(&pc->cfg, cur, desired);
        tr_count += 1u;
    }

    dg_promo_insertion_sort(pc->transition_scratch, tr_count);

#ifndef NDEBUG
    for (i = 1u; i < tr_count; ++i) {
        DG_DET_GUARD_SORTED(dg_promo_transition_cmp(&pc->transition_scratch[i - 1u], &pc->transition_scratch[i]) <= 0);
    }
#endif

    /* Enqueue into the carryover queue in the same deterministic order. */
    if (tr_count > pc->queue.capacity) {
        tr_count = pc->queue.capacity;
        pc->queue.probe_refused += 1u;
    }
    if (tr_count > 0u) {
        memcpy(pc->queue.items, pc->transition_scratch, sizeof(dg_promo_transition) * (size_t)tr_count);
    }
    pc->queue.count = tr_count;
    pc->queue.next = 0u;

    return 0;
}

u32 dg_promo_apply_transitions_under_budget(dg_promo_ctx *pc, dg_budget *budget) {
    u32 applied = 0u;

    if (!pc || !budget) return 0u;
    if (!pc->queue.items) return 0u;
    if (!pc->resolve_fn) return 0u;

    while (pc->queue.next < pc->queue.count) {
        dg_promo_transition *t = &pc->queue.items[pc->queue.next];
        dg_budget_scope scope;
        dg_representable *r;

        scope = dg_budget_scope_domain_chunk(t->key.domain_id, t->key.chunk_id);
        if (!dg_budget_try_consume(budget, &scope, t->cost_units)) {
            break; /* deterministic deferral: do not skip */
        }

        r = pc->resolve_fn(pc->resolve_user, &t->key, t->class_id);
        if (r) {
            (void)dg_representable_set_rep_state(r, t->to_state);
            (void)dg_representable_rep_invariants_check(r);
        }

        pc->queue.next += 1u;
        applied += 1u;
    }

    /* If fully drained, clear queue for the next planning pass. */
    if (pc->queue.next >= pc->queue.count) {
        dg_promo_queue_clear(pc);
    }

    return applied;
}

void dg_promo_topology_phase_handler(struct dg_sched *sched, void *user_ctx) {
    dg_promo_ctx *pc;
    if (!sched || !user_ctx) {
        return;
    }
    pc = (dg_promo_ctx *)user_ctx;
    (void)dg_promo_plan_and_enqueue(pc, sched->tick);
    (void)dg_promo_apply_transitions_under_budget(pc, &sched->budget);
}

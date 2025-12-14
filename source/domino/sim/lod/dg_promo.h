/* Deterministic promotion/demotion planner for the representation ladder (C89).
 *
 * Algorithm (authoritative; see docs/SPEC_LOD.md):
 *  1) Gather candidates from chunk-aligned indices (no unordered iteration).
 *  2) Compute deterministic interest score for each candidate (fixed-point).
 *  3) Determine desired rep state from score thresholds (engine defaults).
 *  4) Sort candidates by:
 *      - desired rep priority (R0 first, then R1, R2, R3)
 *      - descending interest score
 *      - stable tiebreak key: (domain_id, chunk_id, entity_id, sub_id)
 *  5) Apply transitions in that order under deterministic budgets:
 *      - costs consume dg_budget units in the candidate's (domain_id,chunk_id) scope
 *      - if the next transition does not fit, stop (no skipping) and carry over
 *        the remaining suffix unchanged to later ticks.
 */
#ifndef DG_PROMO_H
#define DG_PROMO_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_budget.h"

#include "sim/lod/dg_rep.h"
#include "sim/lod/dg_lod_index.h"
#include "sim/lod/dg_interest.h"
#include "sim/lod/dg_representable.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_promo_thresholds {
    q16_16 thr_r0; /* score >= thr_r0 => R0 */
    q16_16 thr_r1; /* else if >= thr_r1 => R1 */
    q16_16 thr_r2; /* else if >= thr_r2 => R2 */
    /* else => R3 */
} dg_promo_thresholds;

typedef struct dg_promo_config {
    dg_promo_thresholds thresholds;
    u32 promote_cost_per_step;
    u32 demote_cost_per_step;
} dg_promo_config;

typedef struct dg_promo_transition {
    dg_lod_obj_key  key;
    dg_lod_class_id class_id;
    dg_rep_state    from_state;
    dg_rep_state    to_state;
    q16_16          score;
    u32             cost_units;
} dg_promo_transition;

typedef dg_representable *(*dg_promo_resolve_fn)(void *user_ctx, const dg_lod_obj_key *key, dg_lod_class_id class_id);

typedef struct dg_promo_queue {
    dg_promo_transition *items;
    u32                 count;
    u32                 next;     /* next item index to apply */
    u32                 capacity;
    u32                 probe_refused;
} dg_promo_queue;

typedef struct dg_promo_ctx {
    dg_promo_config cfg;

    const dg_lod_index *index; /* not owned */

    dg_interest_ctx  *interest;      /* not owned */
    dg_interest_list  interest_list; /* owned storage via reserve */

    dg_promo_resolve_fn resolve_fn;
    void              *resolve_user;

    /* Scratch buffers (owned storage via reserve). */
    dg_chunk_id       *chunk_scratch;
    u32                chunk_capacity;

    dg_lod_candidate  *candidates;
    u32                candidate_capacity;

    dg_promo_transition *transition_scratch;
    u32                 transition_capacity;

    dg_promo_queue queue;

    u32 probe_candidates_truncated;
    u32 probe_transitions_truncated;
} dg_promo_ctx;

void dg_promo_init(dg_promo_ctx *pc);
void dg_promo_free(dg_promo_ctx *pc);

/* Reserve bounded scratch/queue storage.
 * max_chunks:         unique chunks scanned per plan
 * max_candidates:     candidates gathered per plan
 * max_transitions:    planned transitions per plan
 * max_interest_vols:  interest volumes collected per plan
 */
int dg_promo_reserve(
    dg_promo_ctx *pc,
    u32           max_chunks,
    u32           max_candidates,
    u32           max_transitions,
    u32           max_interest_vols
);

void dg_promo_set_index(dg_promo_ctx *pc, const dg_lod_index *index);
void dg_promo_set_interest(dg_promo_ctx *pc, dg_interest_ctx *interest);
void dg_promo_set_resolver(dg_promo_ctx *pc, dg_promo_resolve_fn fn, void *user_ctx);
void dg_promo_set_config(dg_promo_ctx *pc, const dg_promo_config *cfg);

dg_promo_config dg_promo_config_defaults(void);

/* Planned transitions (queue view). */
u32 dg_promo_queue_count(const dg_promo_ctx *pc);
u32 dg_promo_queue_pending(const dg_promo_ctx *pc);
const dg_promo_transition *dg_promo_queue_at(const dg_promo_ctx *pc, u32 index);

u32 dg_promo_probe_candidates_truncated(const dg_promo_ctx *pc);
u32 dg_promo_probe_transitions_truncated(const dg_promo_ctx *pc);

/* Topology substeps (called at scheduler phase boundaries). */
int dg_promo_plan_and_enqueue(dg_promo_ctx *pc, dg_tick tick);
u32 dg_promo_apply_transitions_under_budget(dg_promo_ctx *pc, dg_budget *budget);

/* Convenience scheduler hook for DG_PH_TOPOLOGY.
 * user_ctx must be a dg_promo_ctx*.
 */
struct dg_sched;
void dg_promo_topology_phase_handler(struct dg_sched *sched, void *user_ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PROMO_H */

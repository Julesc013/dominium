/* Mind/controller interface (deterministic; C89).
 *
 * Minds are semantic-free decision layers:
 *   observations + internal state -> intent packets
 *
 * Minds MUST NOT mutate authoritative state; they only emit intents.
 */
#ifndef DG_MIND_H
#define DG_MIND_H

#include "agent/dg_agent_ids.h"
#include "domino/core/rng.h"
#include "core/dg_det_hash.h"
#include "sim/lod/dg_stride.h"
#include "sim/pkt/dg_pkt_intent.h"
#include "sim/sense/dg_observation_buffer.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef int (*dg_intent_emit_fn)(const dg_pkt_intent *intent, void *user_ctx);

typedef struct dg_vm_budget {
    u32 instr_limit; /* instruction limit */
    u32 instr_used;  /* instructions consumed */
} dg_vm_budget;

#define DG_VM_BUDGET_UNLIMITED 0xFFFFFFFFu

void dg_vm_budget_init(dg_vm_budget *b, u32 instr_limit);
d_bool dg_vm_budget_try_consume(dg_vm_budget *b, u32 instr);
u32 dg_vm_budget_remaining(const dg_vm_budget *b);

/* Deterministic PRNG stream keyed by (agent_id, stream_id). */
typedef struct dg_mind_prng {
    d_rng_state rng;
} dg_mind_prng;

void dg_mind_prng_init(dg_mind_prng *p, dg_agent_id agent_id, u64 stream_id);
u32  dg_mind_prng_next_u32(dg_mind_prng *p);
i32  dg_mind_prng_next_i32(dg_mind_prng *p);
u32  dg_mind_prng_peek_u32(const dg_mind_prng *p);

typedef struct dg_mind_desc dg_mind_desc;

typedef struct dg_mind_vtbl {
    /* Step decision-making and emit intent packets through 'emit'.
     * budget_units is a caller-provided deterministic work allowance.
     * io_seq is a caller-managed sequence source for mind-local emission.
     */
    int (*step)(
        dg_agent_id                agent_id,
        const dg_observation_buffer *observations,
        void                      *internal_state,
        dg_tick                    tick,
        u32                        budget_units,
        u32                       *io_seq,
        dg_intent_emit_fn          emit,
        void                      *emit_ctx
    );

    /* Optional deterministic work estimate (units). */
    u32 (*estimate_cost)(
        dg_agent_id                 agent_id,
        const dg_observation_buffer *observations,
        const void                 *internal_state
    );

    /* Optional state serialization for replay/debug. */
    int (*serialize_state)(const void *state, unsigned char *out, u32 out_cap, u32 *out_len);
} dg_mind_vtbl;

struct dg_mind_desc {
    dg_type_id    mind_id;              /* stable taxonomy id */
    dg_mind_vtbl  vtbl;
    u32           stride;               /* cadence decimation; 0/1 means always */
    u32           internal_state_bytes; /* optional; 0 allowed */
    const char   *name;                /* optional; not used for determinism */
};

/* Deterministic stride check keyed by (agent_id, mind_id). */
d_bool dg_mind_should_run(const dg_mind_desc *m, dg_tick tick, dg_agent_id agent_id);

/* Estimate cost or return a default. */
u32 dg_mind_estimate_cost(
    const dg_mind_desc            *m,
    dg_agent_id                    agent_id,
    const dg_observation_buffer   *observations,
    const void                    *internal_state,
    u32                            default_cost
);

/* Minimal behavior-VM hook (stub only; no VM implementation here). */
typedef struct dg_vm_iface {
    int (*run)(
        dg_agent_id                 agent_id,
        const dg_observation_buffer *observations,
        void                       *internal_state,
        dg_tick                     tick,
        dg_vm_budget               *vm_budget,
        dg_mind_prng               *prng,
        u32                        *io_seq,
        dg_intent_emit_fn           emit,
        void                       *emit_ctx
    );
} dg_vm_iface;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_MIND_H */

/*
FILE: source/domino/agent/mind/dg_mind.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/mind/dg_mind
RESPONSIBILITY: Implements `dg_mind`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "agent/mind/dg_mind.h"

void dg_vm_budget_init(dg_vm_budget *b, u32 instr_limit) {
    if (!b) {
        return;
    }
    b->instr_limit = instr_limit;
    b->instr_used = 0u;
}

d_bool dg_vm_budget_try_consume(dg_vm_budget *b, u32 instr) {
    u32 remaining;
    if (!b) {
        return D_FALSE;
    }
    if (b->instr_limit == DG_VM_BUDGET_UNLIMITED) {
        b->instr_used += instr;
        return D_TRUE;
    }
    remaining = (b->instr_used <= b->instr_limit) ? (b->instr_limit - b->instr_used) : 0u;
    if (instr > remaining) {
        return D_FALSE;
    }
    b->instr_used += instr;
    return D_TRUE;
}

u32 dg_vm_budget_remaining(const dg_vm_budget *b) {
    if (!b) {
        return 0u;
    }
    if (b->instr_limit == DG_VM_BUDGET_UNLIMITED) {
        return DG_VM_BUDGET_UNLIMITED;
    }
    if (b->instr_used >= b->instr_limit) {
        return 0u;
    }
    return b->instr_limit - b->instr_used;
}

void dg_mind_prng_init(dg_mind_prng *p, dg_agent_id agent_id, u64 stream_id) {
    u64 h;
    u32 seed;
    if (!p) {
        return;
    }
    h = (u64)agent_id ^ (stream_id * 11400714819323198485ULL);
    h = dg_det_hash_u64(h);
    seed = (u32)(h ^ (h >> 32));
    d_rng_seed(&p->rng, seed);
}

u32 dg_mind_prng_next_u32(dg_mind_prng *p) {
    if (!p) {
        return 0u;
    }
    return d_rng_next_u32(&p->rng);
}

i32 dg_mind_prng_next_i32(dg_mind_prng *p) {
    if (!p) {
        return 0;
    }
    return d_rng_next_i32(&p->rng);
}

u32 dg_mind_prng_peek_u32(const dg_mind_prng *p) {
    if (!p) {
        return 0u;
    }
    return d_rng_peek_u32(&p->rng);
}

d_bool dg_mind_should_run(const dg_mind_desc *m, dg_tick tick, dg_agent_id agent_id) {
    u64 stable_id;
    if (!m) {
        return D_FALSE;
    }
    stable_id = ((u64)agent_id) ^ (m->mind_id * 11400714819323198485ULL);
    return dg_stride_should_run(tick, stable_id, m->stride);
}

u32 dg_mind_estimate_cost(
    const dg_mind_desc          *m,
    dg_agent_id                  agent_id,
    const dg_observation_buffer *observations,
    const void                  *internal_state,
    u32                          default_cost
) {
    if (!m) {
        return default_cost;
    }
    if (m->vtbl.estimate_cost) {
        return m->vtbl.estimate_cost(agent_id, observations, internal_state);
    }
    return default_cost;
}

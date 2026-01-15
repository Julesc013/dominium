/*
FILE: source/domino/agent/act/dg_intent_dispatch.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/act/dg_intent_dispatch
RESPONSIBILITY: Implements `dg_intent_dispatch`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "agent/act/dg_intent_dispatch.h"
#include "core/dg_order_key.h"

void dg_action_request_buffer_init(dg_action_request_buffer *b) {
    if (!b) {
        return;
    }
    b->tick = 0u;
    b->reqs = (dg_action_request *)0;
    b->count = 0u;
    b->capacity = 0u;
    b->owns_storage = D_FALSE;
    b->probe_refused = 0u;
}

void dg_action_request_buffer_free(dg_action_request_buffer *b) {
    if (!b) {
        return;
    }
    if (b->owns_storage && b->reqs) {
        free(b->reqs);
    }
    dg_action_request_buffer_init(b);
}

int dg_action_request_buffer_reserve(dg_action_request_buffer *b, u32 max_reqs) {
    dg_action_request *reqs;
    if (!b) {
        return -1;
    }
    dg_action_request_buffer_free(b);
    if (max_reqs == 0u) {
        return 0;
    }
    reqs = (dg_action_request *)malloc(sizeof(dg_action_request) * (size_t)max_reqs);
    if (!reqs) {
        return -2;
    }
    memset(reqs, 0, sizeof(dg_action_request) * (size_t)max_reqs);
    b->reqs = reqs;
    b->capacity = max_reqs;
    b->count = 0u;
    b->owns_storage = D_TRUE;
    b->probe_refused = 0u;
    return 0;
}

void dg_action_request_buffer_begin_tick(dg_action_request_buffer *b, dg_tick tick) {
    if (!b) {
        return;
    }
    b->tick = tick;
    b->count = 0u;
}

u32 dg_action_request_buffer_count(const dg_action_request_buffer *b) {
    return b ? b->count : 0u;
}

const dg_action_request *dg_action_request_buffer_at(const dg_action_request_buffer *b, u32 index) {
    if (!b || !b->reqs || index >= b->count) {
        return (const dg_action_request *)0;
    }
    return &b->reqs[index];
}

u32 dg_action_request_buffer_probe_refused(const dg_action_request_buffer *b) {
    return b ? b->probe_refused : 0u;
}

int dg_intent_dispatch_build_requests(const dg_intent_buffer *intents, dg_action_request_buffer *out_reqs) {
    u32 i;

    if (!intents || !out_reqs) {
        return -1;
    }
    if (!out_reqs->reqs || out_reqs->capacity == 0u) {
        out_reqs->probe_refused += 1u;
        return -2;
    }
    if (out_reqs->capacity < intents->count) {
        out_reqs->probe_refused += 1u;
        return -3;
    }
    if (out_reqs->tick != intents->tick) {
        return -4;
    }

    out_reqs->count = 0u;
    for (i = 0u; i < intents->count; ++i) {
        const dg_intent_record *r = &intents->records[i];
        dg_action_request *q = &out_reqs->reqs[out_reqs->count];

        q->tick = r->hdr.tick;
        q->agent_id = r->hdr.src_entity;
        q->intent_type_id = r->hdr.type_id;
        q->intent_seq = r->hdr.seq;
        q->action_type_id = r->hdr.type_id; /* default mapping */
        q->intent_index = i;
        out_reqs->count += 1u;
    }

    return 0;
}

typedef struct dg_intent_dispatch_emit_ctx {
    dg_delta_buffer *out_deltas;
    u16              phase;
    u64              component_id;
    u32              next_seq;
} dg_intent_dispatch_emit_ctx;

static int dg_intent_dispatch_emit_delta(const dg_pkt_delta *delta, void *emit_ctx) {
    dg_intent_dispatch_emit_ctx *ctx;
    dg_pkt_delta tmp;
    dg_order_key key;

    if (!delta || !emit_ctx) {
        return -1;
    }
    ctx = (dg_intent_dispatch_emit_ctx *)emit_ctx;
    if (!ctx->out_deltas) {
        return -2;
    }
    if (delta->payload_len != delta->hdr.payload_len) {
        return -3;
    }
    if (delta->hdr.tick != ctx->out_deltas->tick) {
        return -4;
    }

    tmp = *delta;
    tmp.hdr.seq = ctx->next_seq++;
    key = dg_order_key_from_pkt_hdr(ctx->phase, &tmp.hdr, ctx->component_id);
    return dg_delta_buffer_push(ctx->out_deltas, &key, &tmp);
}

int dg_intent_dispatch_to_deltas(
    const dg_intent_buffer   *intents,
    const dg_action_registry *actions,
    const void               *world_state,
    dg_delta_buffer          *out_deltas,
    u16                       phase
) {
    dg_intent_dispatch_emit_ctx emit_ctx;
    u32 i;

    if (!intents || !actions || !out_deltas) {
        return -1;
    }
    if (out_deltas->tick != intents->tick) {
        return -2;
    }

    emit_ctx.out_deltas = out_deltas;
    emit_ctx.phase = phase;
    emit_ctx.component_id = 0u;
    emit_ctx.next_seq = 0u;

    for (i = 0u; i < intents->count; ++i) {
        const dg_intent_record *r = &intents->records[i];
        dg_pkt_intent pkt;
        const dg_action_registry_entry *a = dg_action_registry_find(actions, r->hdr.type_id);

        if (!a || !a->vtbl.apply) {
            continue;
        }

        pkt.hdr = r->hdr;
        pkt.payload = r->payload;
        pkt.payload_len = r->payload_len;

        if (a->vtbl.validate) {
            u32 reason = 0u;
            if (!a->vtbl.validate(pkt.hdr.src_entity, &pkt, world_state, &reason)) {
                continue;
            }
        }

        if (a->vtbl.apply(pkt.hdr.src_entity, &pkt, world_state, dg_intent_dispatch_emit_delta, &emit_ctx) != 0) {
            return -3;
        }
    }

    return 0;
}

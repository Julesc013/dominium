#include <stdlib.h>
#include <string.h>

#include "agent/mind/dg_mind_registry.h"
#include "sim/sched/dg_phase.h"

typedef struct dg_mind_emit_ctx {
    dg_intent_buffer *out_intents;
    dg_tick           tick;
    dg_agent_id       agent_id;
} dg_mind_emit_ctx;

static int dg_mind_emit_intent_to_buffer(const dg_pkt_intent *intent, void *user_ctx) {
    dg_mind_emit_ctx *ctx;
    dg_pkt_intent tmp;

    if (!intent || !user_ctx) {
        return -1;
    }
    ctx = (dg_mind_emit_ctx *)user_ctx;
    if (!ctx->out_intents) {
        return -2;
    }

    tmp = *intent;
    tmp.hdr.tick = ctx->tick;
    tmp.hdr.src_entity = ctx->agent_id;
    tmp.payload_len = tmp.hdr.payload_len;
    return dg_intent_buffer_push(ctx->out_intents, &tmp);
}

static int dg_mind_entry_cmp(const dg_mind_registry_entry *a, const dg_mind_registry_entry *b) {
    if (a->desc.mind_id < b->desc.mind_id) return -1;
    if (a->desc.mind_id > b->desc.mind_id) return 1;
    return 0;
}

void dg_mind_registry_init(dg_mind_registry *reg) {
    if (!reg) {
        return;
    }
    reg->entries = (dg_mind_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
    reg->next_insert_index = 0u;
}

void dg_mind_registry_free(dg_mind_registry *reg) {
    if (!reg) {
        return;
    }
    if (reg->entries) {
        free(reg->entries);
    }
    dg_mind_registry_init(reg);
}

int dg_mind_registry_reserve(dg_mind_registry *reg, u32 capacity) {
    dg_mind_registry_entry *new_entries;
    if (!reg) {
        return -1;
    }
    if (capacity <= reg->capacity) {
        return 0;
    }
    new_entries = (dg_mind_registry_entry *)realloc(reg->entries, sizeof(dg_mind_registry_entry) * (size_t)capacity);
    if (!new_entries) {
        return -2;
    }
    reg->entries = new_entries;
    reg->capacity = capacity;
    return 0;
}

static u32 dg_mind_registry_lower_bound(const dg_mind_registry *reg, dg_type_id mind_id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;
    dg_mind_registry_entry key;

    if (out_found) {
        *out_found = 0;
    }
    if (!reg || reg->count == 0u) {
        return 0u;
    }

    memset(&key, 0, sizeof(key));
    key.desc.mind_id = mind_id;

    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_mind_entry_cmp(&reg->entries[mid], &key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        cmp = dg_mind_entry_cmp(&reg->entries[lo], &key);
        if (cmp == 0 && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_mind_registry_add(dg_mind_registry *reg, const dg_mind_desc *desc) {
    dg_mind_registry_entry entry;
    u32 idx;
    int found;
    int rc;

    if (!reg || !desc || !desc->vtbl.step) {
        return -1;
    }
    if (desc->mind_id == 0u) {
        return -2;
    }

    memset(&entry, 0, sizeof(entry));
    entry.desc = *desc;
    entry.insert_index = reg->next_insert_index++;

    idx = dg_mind_registry_lower_bound(reg, desc->mind_id, &found);
    if (found) {
        return -3;
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 16u : (reg->capacity * 2u);
        rc = dg_mind_registry_reserve(reg, new_cap);
        if (rc != 0) {
            return -4;
        }
    }

    if (idx < reg->count) {
        memmove(&reg->entries[idx + 1u], &reg->entries[idx],
                sizeof(dg_mind_registry_entry) * (size_t)(reg->count - idx));
    }
    reg->entries[idx] = entry;
    reg->count += 1u;
    return 0;
}

u32 dg_mind_registry_count(const dg_mind_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_mind_registry_entry *dg_mind_registry_at(const dg_mind_registry *reg, u32 index) {
    if (!reg || !reg->entries || index >= reg->count) {
        return (const dg_mind_registry_entry *)0;
    }
    return &reg->entries[index];
}

const dg_mind_registry_entry *dg_mind_registry_find(const dg_mind_registry *reg, dg_type_id mind_id) {
    u32 idx;
    int found;
    if (!reg || !reg->entries || reg->count == 0u || mind_id == 0u) {
        return (const dg_mind_registry_entry *)0;
    }
    idx = dg_mind_registry_lower_bound(reg, mind_id, &found);
    if (!found) {
        return (const dg_mind_registry_entry *)0;
    }
    return &reg->entries[idx];
}

int dg_mind_registry_step_agent(
    const dg_mind_registry       *reg,
    dg_type_id                    mind_id,
    dg_tick                       tick,
    dg_agent_id                   agent_id,
    const dg_observation_buffer  *observations,
    void                         *internal_state,
    dg_budget                    *budget,
    const dg_budget_scope        *scope,
    dg_work_queue                *defer_q,
    dg_intent_buffer             *out_intents,
    u32                          *io_seq
) {
    const dg_mind_registry_entry *e;
    const dg_mind_desc *m;
    dg_budget_scope global_scope;
    const dg_budget_scope *use_scope;
    u32 local_seq = 0u;
    u32 *seqp = io_seq ? io_seq : &local_seq;
    u32 cost;
    dg_mind_emit_ctx emit_ctx;

    if (!reg || mind_id == 0u || agent_id == 0u || !out_intents) {
        return -1;
    }
    if (out_intents->tick != tick) {
        return -2;
    }

    e = dg_mind_registry_find(reg, mind_id);
    if (!e) {
        return -3;
    }
    m = &e->desc;

    if (!dg_mind_should_run(m, tick, agent_id)) {
        return 0;
    }

    global_scope = dg_budget_scope_global();
    use_scope = scope ? scope : &global_scope;

    cost = dg_mind_estimate_cost(m, agent_id, observations, internal_state, 1u);
    if (budget && cost != 0u) {
        if (!dg_budget_try_consume(budget, use_scope, cost)) {
            if (defer_q) {
                dg_work_item it;
                dg_work_item_clear(&it);
                it.key = dg_order_key_make(
                    (u16)DG_PH_MIND,
                    use_scope->domain_id,
                    use_scope->chunk_id,
                    (dg_entity_id)agent_id,
                    0u,
                    mind_id,
                    0u
                );
                it.work_type_id = mind_id;
                it.cost_units = cost;
                it.enqueue_tick = tick;
                (void)dg_work_queue_push(defer_q, &it);
            }
            return 1;
        }
    }

    emit_ctx.out_intents = out_intents;
    emit_ctx.tick = tick;
    emit_ctx.agent_id = agent_id;

    if (m->vtbl.step(agent_id, observations, internal_state, tick, cost, seqp, dg_mind_emit_intent_to_buffer, &emit_ctx) != 0) {
        return -4;
    }

    return 0;
}

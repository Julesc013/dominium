/*
FILE: source/domino/sim/sense/dg_sensor_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sense/dg_sensor_registry
RESPONSIBILITY: Implements `dg_sensor_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "sim/sense/dg_sensor_registry.h"
#include "sim/sched/dg_phase.h"

static int dg_sensor_entry_cmp(const dg_sensor_registry_entry *a, const dg_sensor_registry_entry *b) {
    if (a->desc.sensor_id < b->desc.sensor_id) return -1;
    if (a->desc.sensor_id > b->desc.sensor_id) return 1;
    return 0;
}

void dg_sensor_registry_init(dg_sensor_registry *reg) {
    if (!reg) {
        return;
    }
    reg->entries = (dg_sensor_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
    reg->next_insert_index = 0u;
}

void dg_sensor_registry_free(dg_sensor_registry *reg) {
    if (!reg) {
        return;
    }
    if (reg->entries) {
        free(reg->entries);
    }
    dg_sensor_registry_init(reg);
}

int dg_sensor_registry_reserve(dg_sensor_registry *reg, u32 capacity) {
    dg_sensor_registry_entry *new_entries;
    if (!reg) {
        return -1;
    }
    if (capacity <= reg->capacity) {
        return 0;
    }
    new_entries = (dg_sensor_registry_entry *)realloc(reg->entries, sizeof(dg_sensor_registry_entry) * (size_t)capacity);
    if (!new_entries) {
        return -2;
    }
    reg->entries = new_entries;
    reg->capacity = capacity;
    return 0;
}

static u32 dg_sensor_registry_lower_bound(const dg_sensor_registry *reg, dg_type_id sensor_id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;
    dg_sensor_registry_entry key;

    if (out_found) {
        *out_found = 0;
    }
    if (!reg || reg->count == 0u) {
        return 0u;
    }

    memset(&key, 0, sizeof(key));
    key.desc.sensor_id = sensor_id;

    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_sensor_entry_cmp(&reg->entries[mid], &key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        cmp = dg_sensor_entry_cmp(&reg->entries[lo], &key);
        if (cmp == 0 && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_sensor_registry_add(dg_sensor_registry *reg, const dg_sensor_desc *desc) {
    dg_sensor_registry_entry entry;
    u32 idx;
    int found;
    int rc;

    if (!reg || !desc || !desc->vtbl.sample) {
        return -1;
    }
    if (desc->sensor_id == 0u) {
        return -2;
    }

    memset(&entry, 0, sizeof(entry));
    entry.desc = *desc;
    entry.insert_index = reg->next_insert_index++;

    idx = dg_sensor_registry_lower_bound(reg, desc->sensor_id, &found);
    if (found) {
        return -3;
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 16u : (reg->capacity * 2u);
        rc = dg_sensor_registry_reserve(reg, new_cap);
        if (rc != 0) {
            return -4;
        }
    }

    if (idx < reg->count) {
        memmove(&reg->entries[idx + 1u], &reg->entries[idx],
                sizeof(dg_sensor_registry_entry) * (size_t)(reg->count - idx));
    }
    reg->entries[idx] = entry;
    reg->count += 1u;
    return 0;
}

u32 dg_sensor_registry_count(const dg_sensor_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_sensor_registry_entry *dg_sensor_registry_at(const dg_sensor_registry *reg, u32 index) {
    if (!reg || !reg->entries || index >= reg->count) {
        return (const dg_sensor_registry_entry *)0;
    }
    return &reg->entries[index];
}

const dg_sensor_registry_entry *dg_sensor_registry_find(const dg_sensor_registry *reg, dg_type_id sensor_id) {
    u32 idx;
    int found;
    if (!reg || !reg->entries || reg->count == 0u || sensor_id == 0u) {
        return (const dg_sensor_registry_entry *)0;
    }
    idx = dg_sensor_registry_lower_bound(reg, sensor_id, &found);
    if (!found) {
        return (const dg_sensor_registry_entry *)0;
    }
    return &reg->entries[idx];
}

int dg_sensor_registry_sample_agent(
    const dg_sensor_registry   *reg,
    dg_tick                     tick,
    dg_agent_id                 agent_id,
    const void                 *observer_ctx,
    dg_budget                  *budget,
    const dg_budget_scope      *scope,
    dg_work_queue              *defer_q,
    dg_observation_buffer      *out_obs,
    u32                        *io_seq
) {
    u32 i;
    dg_budget_scope global_scope;
    const dg_budget_scope *use_scope;
    u32 local_seq = 0u;
    u32 *seqp = io_seq ? io_seq : &local_seq;

    if (!reg || !out_obs || agent_id == 0u) {
        return -1;
    }
    if (out_obs->tick != tick) {
        return -2;
    }

    global_scope = dg_budget_scope_global();
    use_scope = scope ? scope : &global_scope;

    for (i = 0u; i < reg->count; ++i) {
        const dg_sensor_desc *s = &reg->entries[i].desc;
        u32 cost;
        int rc;

        if (!dg_sensor_should_run(s, tick, agent_id)) {
            continue;
        }

        cost = dg_sensor_estimate_cost(s, agent_id, observer_ctx, 1u);
        if (budget && cost != 0u) {
            if (!dg_budget_try_consume(budget, use_scope, cost)) {
                /* Defer this sensor and any remaining eligible sensors. */
                if (defer_q) {
                    u32 j;
                    for (j = i; j < reg->count; ++j) {
                        const dg_sensor_desc *sd = &reg->entries[j].desc;
                        u32 cst;
                        dg_work_item it;

                        if (!dg_sensor_should_run(sd, tick, agent_id)) {
                            continue;
                        }

                        cst = dg_sensor_estimate_cost(sd, agent_id, observer_ctx, 1u);
                        dg_work_item_clear(&it);
                        it.key = dg_order_key_make(
                            (u16)DG_PH_SENSE,
                            use_scope->domain_id,
                            use_scope->chunk_id,
                            (dg_entity_id)agent_id,
                            0u,
                            sd->sensor_id,
                            0u
                        );
                        it.work_type_id = sd->sensor_id;
                        it.cost_units = cst;
                        it.enqueue_tick = tick;
                        (void)dg_work_queue_push(defer_q, &it);
                    }
                }
                return 1;
            }
        }

        rc = s->vtbl.sample(agent_id, observer_ctx, tick, seqp, out_obs);
        if (rc != 0) {
            return -3;
        }
    }

    return 0;
}

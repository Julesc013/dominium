#include <stdlib.h>
#include <string.h>

#include "sim/bus/dg_field.h"
#include "sim/sched/dg_sched.h"
#include "res/dg_tlv_canon.h"

/* Update queue keys:
 * We map (tick, domain_id, chunk_id, field_type_id, seq) into dg_order_key:
 *   phase        = PH_SENSE (update application boundary)
 *   domain_id    = tick
 *   chunk_id     = domain_id
 *   entity_id    = chunk_id
 *   component_id = field_type_id
 *   type_id      = 0 (reserved)
 *   seq          = hdr.seq
 */
static dg_order_key dg_field_update_key_from_hdr(const dg_pkt_hdr *hdr) {
    dg_order_key k;
    dg_order_key_clear(&k);
    if (!hdr) {
        return k;
    }
    k.phase = (u16)DG_PH_SENSE;
    k.domain_id = (dg_domain_id)hdr->tick;
    k.chunk_id = (dg_chunk_id)hdr->domain_id;
    k.entity_id = (dg_entity_id)hdr->chunk_id;
    k.component_id = (u64)hdr->type_id;
    k.type_id = 0u;
    k.seq = hdr->seq;
    return k;
}

static u32 dg_field_type_lower_bound(const dg_field *f, dg_type_id field_type_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!f) {
        return 0u;
    }
    hi = f->type_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (f->types[mid].field_type_id < field_type_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static const dg_field_type_desc *dg_field_type_find(const dg_field *f, dg_type_id field_type_id) {
    u32 idx;
    if (!f || !f->types || f->type_count == 0u) {
        return (const dg_field_type_desc *)0;
    }
    idx = dg_field_type_lower_bound(f, field_type_id);
    if (idx < f->type_count && f->types[idx].field_type_id == field_type_id) {
        return &f->types[idx];
    }
    return (const dg_field_type_desc *)0;
}

static int dg_field_ensure_type_capacity(dg_field *f, u32 need_count) {
    u32 new_cap;
    dg_field_type_desc *new_types;

    if (!f) {
        return -1;
    }
    if (need_count <= f->type_capacity) {
        return 0;
    }

    new_cap = (f->type_capacity == 0u) ? 16u : (f->type_capacity * 2u);
    while (new_cap < need_count) {
        new_cap *= 2u;
    }

    new_types = (dg_field_type_desc *)realloc(f->types, sizeof(dg_field_type_desc) * (size_t)new_cap);
    if (!new_types) {
        return -2;
    }
    if (new_cap > f->type_capacity) {
        memset(new_types + f->type_capacity, 0, sizeof(dg_field_type_desc) * (size_t)(new_cap - f->type_capacity));
    }
    f->types = new_types;
    f->type_capacity = new_cap;
    return 0;
}

static u32 dg_field_layer_lower_bound(const dg_field *f, dg_domain_id domain_id, dg_chunk_id chunk_id, dg_type_id field_type_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;

    if (!f) {
        return 0u;
    }
    hi = f->layer_count;
    while (lo < hi) {
        const dg_field_layer *m;
        int cmp;
        mid = lo + ((hi - lo) / 2u);
        m = &f->layers[mid];

        if (m->domain_id < domain_id) {
            cmp = -1;
        } else if (m->domain_id > domain_id) {
            cmp = 1;
        } else if (m->chunk_id < chunk_id) {
            cmp = -1;
        } else if (m->chunk_id > chunk_id) {
            cmp = 1;
        } else if (m->field_type_id < field_type_id) {
            cmp = -1;
        } else if (m->field_type_id > field_type_id) {
            cmp = 1;
        } else {
            cmp = 0;
        }

        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static dg_field_layer *dg_field_layer_find(dg_field *f, dg_domain_id domain_id, dg_chunk_id chunk_id, dg_type_id field_type_id) {
    u32 idx;
    if (!f || !f->layers || f->layer_count == 0u) {
        return (dg_field_layer *)0;
    }
    idx = dg_field_layer_lower_bound(f, domain_id, chunk_id, field_type_id);
    if (idx < f->layer_count) {
        dg_field_layer *l = &f->layers[idx];
        if (l->domain_id == domain_id && l->chunk_id == chunk_id && l->field_type_id == field_type_id) {
            return l;
        }
    }
    return (dg_field_layer *)0;
}

static int dg_field_ensure_layer_capacity(dg_field *f, u32 need_count) {
    u32 new_cap;
    dg_field_layer *new_layers;

    if (!f) {
        return -1;
    }
    if (need_count <= f->layer_capacity) {
        return 0;
    }

    new_cap = (f->layer_capacity == 0u) ? 16u : (f->layer_capacity * 2u);
    while (new_cap < need_count) {
        new_cap *= 2u;
    }

    new_layers = (dg_field_layer *)realloc(f->layers, sizeof(dg_field_layer) * (size_t)new_cap);
    if (!new_layers) {
        return -2;
    }
    if (new_cap > f->layer_capacity) {
        memset(new_layers + f->layer_capacity, 0, sizeof(dg_field_layer) * (size_t)(new_cap - f->layer_capacity));
    }
    f->layers = new_layers;
    f->layer_capacity = new_cap;
    return 0;
}

static dg_field_layer *dg_field_get_or_create_layer(
    dg_field     *f,
    dg_domain_id  domain_id,
    dg_chunk_id   chunk_id,
    dg_type_id    field_type_id
) {
    dg_field_layer *existing;
    const dg_field_type_desc *td;
    u32 idx;
    int rc;

    if (!f) {
        return (dg_field_layer *)0;
    }
    existing = dg_field_layer_find(f, domain_id, chunk_id, field_type_id);
    if (existing) {
        return existing;
    }

    td = dg_field_type_find(f, field_type_id);
    if (!td) {
        return (dg_field_layer *)0;
    }

    rc = dg_field_ensure_layer_capacity(f, f->layer_count + 1u);
    if (rc != 0) {
        return (dg_field_layer *)0;
    }

    idx = dg_field_layer_lower_bound(f, domain_id, chunk_id, field_type_id);
    if (idx < f->layer_count) {
        memmove(&f->layers[idx + 1u], &f->layers[idx],
                sizeof(dg_field_layer) * (size_t)(f->layer_count - idx));
    }

    dg_field_layer_init(&f->layers[idx]);
    rc = dg_field_layer_configure(
        &f->layers[idx],
        domain_id,
        chunk_id,
        field_type_id,
        td->dim,
        td->res,
        td->res,
        td->res
    );
    if (rc != 0) {
        /* Leave a deterministic empty slot; caller will treat as missing. */
        dg_field_layer_free(&f->layers[idx]);
        return (dg_field_layer *)0;
    }

    f->layer_count += 1u;
    return &f->layers[idx];
}

static int dg_field_grow_update_q(dg_field *f, u32 min_capacity) {
    dg_work_queue new_q;
    u32 new_cap;
    int rc;

    if (!f) {
        return -1;
    }

    new_cap = f->update_q.capacity;
    if (new_cap == 0u) {
        new_cap = 32u;
    }
    while (new_cap < min_capacity) {
        new_cap *= 2u;
    }

    dg_work_queue_init(&new_q);
    rc = dg_work_queue_reserve(&new_q, new_cap);
    if (rc != 0) {
        dg_work_queue_free(&new_q);
        return -2;
    }

    rc = dg_work_queue_merge(&new_q, &f->update_q);
    if (rc != 0) {
        dg_work_queue_free(&new_q);
        return -3;
    }

    dg_work_queue_free(&f->update_q);
    f->update_q = new_q;
    return 0;
}

static d_bool dg_field_has_pending_updates_for_tick(const dg_field *f, dg_tick tick) {
    const dg_work_item *next;
    if (!f) {
        return D_FALSE;
    }
    next = dg_work_queue_peek_next(&f->update_q);
    if (!next) {
        return D_FALSE;
    }
    return ((dg_tick)next->key.domain_id <= tick) ? D_TRUE : D_FALSE;
}

void dg_field_init(dg_field *f) {
    if (!f) {
        return;
    }
    memset(f, 0, sizeof(*f));
    dg_type_registry_init(&f->type_registry);
    dg_work_queue_init(&f->update_q);
}

void dg_field_free(dg_field *f) {
    u32 i;

    if (!f) {
        return;
    }

    if (f->layers) {
        for (i = 0u; i < f->layer_count; ++i) {
            dg_field_layer_free(&f->layers[i]);
        }
        free(f->layers);
    }
    if (f->types) {
        free(f->types);
    }

    /* Free owned payload copies still in the update queue. */
    for (i = 0u; i < f->update_q.count; ++i) {
        const dg_work_item *it = dg_work_queue_at(&f->update_q, i);
        if (it && it->payload_ptr) {
            free((void *)it->payload_ptr);
        }
    }
    dg_work_queue_free(&f->update_q);
    dg_type_registry_free(&f->type_registry);

    memset(f, 0, sizeof(*f));
}

int dg_field_reserve(dg_field *f, u32 type_cap, u32 layer_cap, u32 update_queue_cap) {
    dg_field_type_desc *types;
    dg_field_layer *layers;
    int rc;

    if (!f) {
        return -1;
    }

    dg_field_free(f);
    dg_field_init(f);

    types = (dg_field_type_desc *)0;
    layers = (dg_field_layer *)0;

    if (type_cap != 0u) {
        types = (dg_field_type_desc *)malloc(sizeof(dg_field_type_desc) * (size_t)type_cap);
        if (!types) {
            dg_field_free(f);
            return -2;
        }
        memset(types, 0, sizeof(dg_field_type_desc) * (size_t)type_cap);
    }
    if (layer_cap != 0u) {
        layers = (dg_field_layer *)malloc(sizeof(dg_field_layer) * (size_t)layer_cap);
        if (!layers) {
            if (types) free(types);
            dg_field_free(f);
            return -3;
        }
        memset(layers, 0, sizeof(dg_field_layer) * (size_t)layer_cap);
    }

    f->types = types;
    f->type_capacity = type_cap;
    f->type_count = 0u;

    f->layers = layers;
    f->layer_capacity = layer_cap;
    f->layer_count = 0u;

    if (update_queue_cap != 0u) {
        rc = dg_work_queue_reserve(&f->update_q, update_queue_cap);
        if (rc != 0) {
            dg_field_free(f);
            return -4;
        }
    }

    return 0;
}

int dg_field_register_type(dg_field *f, const dg_field_type_desc *desc) {
    u32 idx;
    int rc;
    dg_field_type_desc d;

    if (!f || !desc) {
        return -1;
    }
    if (desc->field_type_id == 0u) {
        return -2;
    }
    if (desc->dim == 0u || desc->dim > (u8)DG_FIELD_MAX_DIM) {
        return -3;
    }
    if (desc->res == 0u || desc->res > 1024u) {
        return -4;
    }

    if (dg_field_type_find(f, desc->field_type_id)) {
        return -5;
    }

    rc = dg_field_ensure_type_capacity(f, f->type_count + 1u);
    if (rc != 0) {
        return -6;
    }

    d = *desc;
    idx = dg_field_type_lower_bound(f, d.field_type_id);
    if (idx < f->type_count) {
        memmove(&f->types[idx + 1u], &f->types[idx],
                sizeof(dg_field_type_desc) * (size_t)(f->type_count - idx));
    }
    f->types[idx] = d;
    f->type_count += 1u;
    return 0;
}

int dg_field_register_schema(dg_field *f, const dg_type_registry_entry *entry) {
    if (!f || !entry) {
        return -1;
    }
    return dg_type_registry_add(&f->type_registry, entry);
}

int dg_field_publish_update(dg_field *f, const dg_pkt_field_update *update) {
    const dg_type_registry_entry *type_entry;
    const dg_field_type_desc *td;
    unsigned char *payload_copy;
    dg_work_item it;
    int rc;

    if (!f || !update) {
        return -1;
    }
    if (update->payload_len != update->hdr.payload_len) {
        return -2;
    }
    if (update->payload_len != 0u && !update->payload) {
        return -3;
    }

    td = dg_field_type_find(f, update->hdr.type_id);
    if (!td) {
        return -4;
    }

    if (dg_type_registry_count(&f->type_registry) != 0u) {
        type_entry = dg_type_registry_find(&f->type_registry, update->hdr.type_id, update->hdr.schema_id, update->hdr.schema_ver);
        if (!type_entry) {
            return -5;
        }
        if (type_entry->validate_fn) {
            rc = type_entry->validate_fn(update->hdr.type_id, update->hdr.schema_id, update->hdr.schema_ver, update->payload, update->payload_len);
            if (rc != 0) {
                return -6;
            }
        }
    }

    payload_copy = (unsigned char *)0;
    if (update->payload_len != 0u) {
        payload_copy = (unsigned char *)malloc((size_t)update->payload_len);
        if (!payload_copy) {
            return -7;
        }
        memcpy(payload_copy, update->payload, (size_t)update->payload_len);
    }

    dg_work_item_clear(&it);
    it.key = dg_field_update_key_from_hdr(&update->hdr);
    it.work_type_id = 0u;
    it.cost_units = 1u;
    it.enqueue_tick = update->hdr.tick;
    dg_work_item_set_payload_ref(&it, payload_copy, update->payload_len);

    if (f->update_q.capacity == 0u || f->update_q.items == (dg_work_item *)0) {
        rc = dg_field_grow_update_q(f, 32u);
        if (rc != 0) {
            if (payload_copy) free(payload_copy);
            return -8;
        }
    } else if (f->update_q.count >= f->update_q.capacity) {
        rc = dg_field_grow_update_q(f, f->update_q.capacity + 1u);
        if (rc != 0) {
            if (payload_copy) free(payload_copy);
            return -9;
        }
    }

    rc = dg_work_queue_push(&f->update_q, &it);
    if (rc != 0) {
        rc = dg_field_grow_update_q(f, f->update_q.capacity + 1u);
        if (rc != 0 || dg_work_queue_push(&f->update_q, &it) != 0) {
            if (payload_copy) free(payload_copy);
            return -10;
        }
    }

    (void)td; /* td reserved for future cost estimation */
    return 0;
}

static void dg_field_apply_update_payload(dg_field_layer *layer, u8 dim, const unsigned char *payload, u32 payload_len) {
    u32 off;
    u32 tag;
    const unsigned char *rec_payload;
    u32 rec_len;
    int rc;

    if (!layer) {
        return;
    }

    off = 0u;
    for (;;) {
        rc = dg_tlv_next(payload, payload_len, &off, &tag, &rec_payload, &rec_len);
        if (rc != 0) {
            break;
        }

        if (tag == DG_FIELD_TLV_SET_CELL) {
            u32 need = 6u + (u32)dim * 4u;
            u16 x;
            u16 y;
            u16 z;
            q16_16 vals[DG_FIELD_MAX_DIM];
            u32 i;

            if (dim == 0u || dim > (u8)DG_FIELD_MAX_DIM) {
                continue;
            }
            if (rec_len < need) {
                continue;
            }

            x = dg_le_read_u16(rec_payload + 0u);
            y = dg_le_read_u16(rec_payload + 2u);
            z = dg_le_read_u16(rec_payload + 4u);

            for (i = 0u; i < (u32)dim; ++i) {
                u32 bits = dg_le_read_u32(rec_payload + 6u + (i * 4u));
                vals[i] = (q16_16)(i32)bits;
            }

            (void)dg_field_layer_set_cell(layer, x, y, z, vals, (u32)dim);
        }
    }
}

u32 dg_field_apply_updates(dg_field *f, dg_budget *budget, dg_tick current_tick) {
    u32 applied = 0u;

    if (!f || !budget) {
        return 0u;
    }

    f->current_tick = current_tick;

    for (;;) {
        const dg_work_item *next;
        dg_tick tick;
        dg_domain_id domain_id;
        dg_chunk_id chunk_id;
        dg_type_id field_type_id;
        const dg_field_type_desc *td;
        dg_field_layer *layer;
        dg_budget_scope scope;
        dg_work_item item;

        next = dg_work_queue_peek_next(&f->update_q);
        if (!next) {
            break;
        }

        tick = (dg_tick)next->key.domain_id;
        if (tick > current_tick) {
            break;
        }

        domain_id = (dg_domain_id)next->key.chunk_id;
        chunk_id = (dg_chunk_id)next->key.entity_id;
        scope = dg_budget_scope_domain_chunk(domain_id, chunk_id);
        if (!dg_budget_try_consume(budget, &scope, 1u)) {
            f->probe_deferred_work += 1u;
            break;
        }

        if (!dg_work_queue_pop_next(&f->update_q, &item)) {
            break;
        }

        domain_id = (dg_domain_id)item.key.chunk_id;
        chunk_id = (dg_chunk_id)item.key.entity_id;
        field_type_id = (dg_type_id)item.key.component_id;

        td = dg_field_type_find(f, field_type_id);
        layer = dg_field_get_or_create_layer(f, domain_id, chunk_id, field_type_id);
        if (layer && td) {
            dg_field_apply_update_payload(layer, td->dim, item.payload_ptr, item.payload_len);
        }

        if (item.payload_ptr) {
            free((void *)item.payload_ptr);
        }

        f->probe_updates_applied += 1u;
        applied += 1u;
    }

    /* If updates for <= current_tick remain, sampling must be deferred by callers. */
    if (dg_field_has_pending_updates_for_tick(f, current_tick)) {
        f->probe_deferred_work += 1u;
    }

    return applied;
}

int dg_field_sample(
    dg_field           *f,
    dg_budget          *budget,
    dg_domain_id        domain_id,
    const dg_field_pos *pos,
    dg_type_id          field_type_id,
    q16_16             *out_values,
    u32                 out_dim
) {
    const dg_field_type_desc *td;
    dg_budget_scope scope;
    dg_field_layer *layer;
    u32 i;

    if (!f || !budget || !pos || !out_values) {
        return -1;
    }

    td = dg_field_type_find(f, field_type_id);
    if (!td) {
        return -2;
    }
    if (out_dim < (u32)td->dim) {
        return -3;
    }

    if (dg_field_has_pending_updates_for_tick(f, f->current_tick)) {
        f->probe_deferred_work += 1u;
        return 1;
    }

    scope = dg_budget_scope_domain_chunk(domain_id, pos->chunk_id);
    if (!dg_budget_try_consume(budget, &scope, 1u)) {
        f->probe_deferred_work += 1u;
        return 2;
    }

    layer = dg_field_layer_find(f, domain_id, pos->chunk_id, field_type_id);
    if (!layer) {
        for (i = 0u; i < out_dim; ++i) {
            out_values[i] = 0;
        }
        f->probe_samples_performed += 1u;
        return 0;
    }

    (void)dg_field_layer_sample_trilinear(layer, pos->x, pos->y, pos->z, out_values, out_dim);
    f->probe_samples_performed += 1u;
    return 0;
}

static void dg_field_sched_update_handler(struct dg_sched *sched, void *user_ctx) {
    dg_field *f = (dg_field *)user_ctx;
    if (!sched || !f) {
        return;
    }
    (void)dg_field_apply_updates(f, &sched->budget, sched->tick);
}

int dg_field_install_sense_update(dg_field *f, struct dg_sched *sched, u64 priority_key) {
    if (!f || !sched) {
        return -1;
    }
    return dg_sched_register_phase_handler(sched, DG_PH_SENSE, dg_field_sched_update_handler, priority_key, f);
}

u32 dg_field_probe_updates_applied(const dg_field *f) {
    return f ? f->probe_updates_applied : 0u;
}

u32 dg_field_probe_samples_performed(const dg_field *f) {
    return f ? f->probe_samples_performed : 0u;
}

u32 dg_field_probe_deferred_work(const dg_field *f) {
    return f ? f->probe_deferred_work : 0u;
}

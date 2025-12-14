#include <stdlib.h>
#include <string.h>

#include "sim/bus/dg_event_bus.h"
#include "sim/sched/dg_sched.h"
#include "res/dg_tlv_canon.h"

/* Delivery queue keys:
 * We map (tick, event_type_id, src_entity, dst_entity, seq) into dg_order_key:
 *   phase       = PH_SENSE (delivery boundary)
 *   domain_id   = tick
 *   chunk_id    = event_type_id
 *   entity_id   = src_entity
 *   component_id= dst_entity
 *   type_id     = 0 (reserved)
 *   seq         = hdr.seq
 */
static dg_order_key dg_event_bus_key_from_hdr(const dg_pkt_hdr *hdr) {
    dg_order_key k;
    dg_order_key_clear(&k);
    if (!hdr) {
        return k;
    }
    k.phase = (u16)DG_PH_SENSE;
    k.domain_id = (dg_domain_id)hdr->tick;
    k.chunk_id = (dg_chunk_id)hdr->type_id;
    k.entity_id = hdr->src_entity;
    k.component_id = hdr->dst_entity;
    k.type_id = 0u;
    k.seq = hdr->seq;
    return k;
}

static int dg_event_bus_sub_cmp(const dg_event_bus_sub *a, const dg_event_bus_sub *b) {
    if (a->event_type_id < b->event_type_id) return -1;
    if (a->event_type_id > b->event_type_id) return 1;
    if (a->priority_key < b->priority_key) return -1;
    if (a->priority_key > b->priority_key) return 1;
    if (a->insert_index < b->insert_index) return -1;
    if (a->insert_index > b->insert_index) return 1;
    return 0;
}

static u32 dg_event_bus_sub_upper_bound(const dg_event_bus *bus, const dg_event_bus_sub *key) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!bus || !key) {
        return 0u;
    }
    hi = bus->sub_count;
    while (lo < hi) {
        int cmp;
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_event_bus_sub_cmp(&bus->subs[mid], key);
        if (cmp <= 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static int dg_event_bus_ensure_sub_capacity(dg_event_bus *bus, u32 need_count) {
    u32 new_cap;
    dg_event_bus_sub *new_subs;

    if (!bus) {
        return -1;
    }
    if (need_count <= bus->sub_capacity) {
        return 0;
    }

    new_cap = (bus->sub_capacity == 0u) ? 16u : (bus->sub_capacity * 2u);
    while (new_cap < need_count) {
        new_cap *= 2u;
    }

    new_subs = (dg_event_bus_sub *)realloc(bus->subs, sizeof(dg_event_bus_sub) * (size_t)new_cap);
    if (!new_subs) {
        return -2;
    }
    if (new_cap > bus->sub_capacity) {
        memset(new_subs + bus->sub_capacity, 0, sizeof(dg_event_bus_sub) * (size_t)(new_cap - bus->sub_capacity));
    }
    bus->subs = new_subs;
    bus->sub_capacity = new_cap;
    return 0;
}

static int dg_event_bus_ensure_record_capacity(dg_event_bus *bus, u32 need_count) {
    u32 new_cap;
    dg_event_bus_record *new_recs;

    if (!bus) {
        return -1;
    }
    if (need_count <= bus->record_capacity) {
        return 0;
    }

    new_cap = (bus->record_capacity == 0u) ? 16u : (bus->record_capacity * 2u);
    while (new_cap < need_count) {
        new_cap *= 2u;
    }

    new_recs = (dg_event_bus_record *)realloc(bus->records, sizeof(dg_event_bus_record) * (size_t)new_cap);
    if (!new_recs) {
        return -2;
    }
    if (new_cap > bus->record_capacity) {
        memset(new_recs + bus->record_capacity, 0, sizeof(dg_event_bus_record) * (size_t)(new_cap - bus->record_capacity));
    }
    bus->records = new_recs;
    bus->record_capacity = new_cap;
    return 0;
}

static int dg_event_bus_ensure_free_id_capacity(dg_event_bus *bus, u32 need_count) {
    u32 new_cap;
    u32 *new_ids;

    if (!bus) {
        return -1;
    }
    if (need_count <= bus->free_record_capacity) {
        return 0;
    }

    new_cap = (bus->free_record_capacity == 0u) ? 16u : (bus->free_record_capacity * 2u);
    while (new_cap < need_count) {
        new_cap *= 2u;
    }

    new_ids = (u32 *)realloc(bus->free_record_ids, sizeof(u32) * (size_t)new_cap);
    if (!new_ids) {
        return -2;
    }
    bus->free_record_ids = new_ids;
    bus->free_record_capacity = new_cap;
    return 0;
}

static int dg_event_bus_grow_deliver_q(dg_event_bus *bus, u32 min_capacity) {
    dg_work_queue new_q;
    u32 new_cap;
    int rc;

    if (!bus) {
        return -1;
    }

    new_cap = bus->deliver_q.capacity;
    if (new_cap == 0u) {
        new_cap = 16u;
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

    rc = dg_work_queue_merge(&new_q, &bus->deliver_q);
    if (rc != 0) {
        dg_work_queue_free(&new_q);
        return -3;
    }

    dg_work_queue_free(&bus->deliver_q);
    bus->deliver_q = new_q;
    return 0;
}

static void dg_event_bus_sub_range(const dg_event_bus *bus, dg_type_id event_type_id, u32 *out_start, u32 *out_count) {
    u32 lo;
    u32 hi;
    u32 mid;
    u32 start;
    u32 count;

    if (out_start) *out_start = 0u;
    if (out_count) *out_count = 0u;
    if (!bus || !bus->subs || bus->sub_count == 0u || !out_start || !out_count) {
        return;
    }

    lo = 0u;
    hi = bus->sub_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (bus->subs[mid].event_type_id < event_type_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    start = lo;
    count = 0u;
    while ((start + count) < bus->sub_count && bus->subs[start + count].event_type_id == event_type_id) {
        count += 1u;
    }
    *out_start = start;
    *out_count = count;
}

static int dg_event_bus_alloc_record_id(dg_event_bus *bus, u32 *out_id) {
    u32 id;
    int rc;

    if (!bus || !out_id) {
        return -1;
    }

    if (bus->free_record_count != 0u) {
        id = bus->free_record_ids[bus->free_record_count - 1u];
        bus->free_record_count -= 1u;
        *out_id = id;
        return 0;
    }

    id = bus->record_count;
    rc = dg_event_bus_ensure_record_capacity(bus, id + 1u);
    if (rc != 0) {
        return -2;
    }
    bus->record_count += 1u;
    *out_id = id;
    return 0;
}

static void dg_event_bus_free_record(dg_event_bus *bus, u32 id) {
    dg_event_bus_record *r;
    int rc;

    if (!bus || !bus->records || id >= bus->record_count) {
        return;
    }
    r = &bus->records[id];
    if (r->payload_owned) {
        free(r->payload_owned);
    }
    memset(r, 0, sizeof(*r));
    r->in_use = D_FALSE;

    rc = dg_event_bus_ensure_free_id_capacity(bus, bus->free_record_count + 1u);
    if (rc == 0) {
        bus->free_record_ids[bus->free_record_count] = id;
        bus->free_record_count += 1u;
    }
}

void dg_event_bus_init(dg_event_bus *bus) {
    if (!bus) {
        return;
    }
    memset(bus, 0, sizeof(*bus));
    dg_type_registry_init(&bus->type_registry);
    dg_work_queue_init(&bus->deliver_q);
}

void dg_event_bus_free(dg_event_bus *bus) {
    u32 i;
    if (!bus) {
        return;
    }

    if (bus->records) {
        for (i = 0u; i < bus->record_count; ++i) {
            if (bus->records[i].in_use && bus->records[i].payload_owned) {
                free(bus->records[i].payload_owned);
                bus->records[i].payload_owned = (unsigned char *)0;
            }
        }
        free(bus->records);
    }
    if (bus->subs) {
        free(bus->subs);
    }
    if (bus->free_record_ids) {
        free(bus->free_record_ids);
    }
    dg_work_queue_free(&bus->deliver_q);
    dg_type_registry_free(&bus->type_registry);

    memset(bus, 0, sizeof(*bus));
}

int dg_event_bus_reserve(dg_event_bus *bus, u32 subs_cap, u32 records_cap, u32 deliver_queue_cap) {
    dg_event_bus_sub *subs;
    dg_event_bus_record *recs;
    u32 *free_ids;
    int rc;

    if (!bus) {
        return -1;
    }

    dg_event_bus_free(bus);
    dg_event_bus_init(bus);

    subs = (dg_event_bus_sub *)0;
    recs = (dg_event_bus_record *)0;
    free_ids = (u32 *)0;

    if (subs_cap != 0u) {
        subs = (dg_event_bus_sub *)malloc(sizeof(dg_event_bus_sub) * (size_t)subs_cap);
        if (!subs) {
            dg_event_bus_free(bus);
            return -2;
        }
        memset(subs, 0, sizeof(dg_event_bus_sub) * (size_t)subs_cap);
    }
    if (records_cap != 0u) {
        recs = (dg_event_bus_record *)malloc(sizeof(dg_event_bus_record) * (size_t)records_cap);
        if (!recs) {
            if (subs) free(subs);
            dg_event_bus_free(bus);
            return -3;
        }
        memset(recs, 0, sizeof(dg_event_bus_record) * (size_t)records_cap);

        free_ids = (u32 *)malloc(sizeof(u32) * (size_t)records_cap);
        if (!free_ids) {
            if (subs) free(subs);
            free(recs);
            dg_event_bus_free(bus);
            return -4;
        }
        memset(free_ids, 0, sizeof(u32) * (size_t)records_cap);
    }

    bus->subs = subs;
    bus->sub_capacity = subs_cap;
    bus->sub_count = 0u;
    bus->next_sub_insert = 0u;

    bus->records = recs;
    bus->record_capacity = records_cap;
    bus->record_count = 0u;

    bus->free_record_ids = free_ids;
    bus->free_record_capacity = records_cap;
    bus->free_record_count = 0u;

    if (deliver_queue_cap != 0u) {
        rc = dg_work_queue_reserve(&bus->deliver_q, deliver_queue_cap);
        if (rc != 0) {
            dg_event_bus_free(bus);
            return -5;
        }
    }

    return 0;
}

int dg_event_bus_register_type(dg_event_bus *bus, const dg_type_registry_entry *entry) {
    if (!bus || !entry) {
        return -1;
    }
    return dg_type_registry_add(&bus->type_registry, entry);
}

int dg_event_bus_subscribe(
    dg_event_bus          *bus,
    dg_type_id             event_type_id,
    dg_event_bus_sub_fn    fn,
    u64                    priority_key,
    void                  *user_ctx
) {
    dg_event_bus_sub sub;
    u32 idx;
    int rc;

    if (!bus || !fn) {
        return -1;
    }
    if (event_type_id == 0u) {
        return -2;
    }

    memset(&sub, 0, sizeof(sub));
    sub.event_type_id = event_type_id;
    sub.fn = fn;
    sub.user_ctx = user_ctx;
    sub.priority_key = priority_key;
    sub.insert_index = bus->next_sub_insert++;

    rc = dg_event_bus_ensure_sub_capacity(bus, bus->sub_count + 1u);
    if (rc != 0) {
        return -3;
    }

    idx = dg_event_bus_sub_upper_bound(bus, &sub);
    if (idx < bus->sub_count) {
        memmove(&bus->subs[idx + 1u], &bus->subs[idx],
                sizeof(dg_event_bus_sub) * (size_t)(bus->sub_count - idx));
    }
    bus->subs[idx] = sub;
    bus->sub_count += 1u;
    return 0;
}

int dg_event_bus_publish(dg_event_bus *bus, const dg_pkt_event *ev) {
    const dg_type_registry_entry *type_entry;
    unsigned char *payload_copy;
    u32 rec_id;
    dg_event_bus_record *r;
    dg_work_item it;
    unsigned char ref[8];
    int rc;

    if (!bus || !ev) {
        return -1;
    }
    if (ev->payload_len != ev->hdr.payload_len) {
        return -2;
    }
    if (ev->payload_len != 0u && !ev->payload) {
        return -3;
    }

    if (dg_type_registry_count(&bus->type_registry) != 0u) {
        type_entry = dg_type_registry_find(&bus->type_registry, ev->hdr.type_id, ev->hdr.schema_id, ev->hdr.schema_ver);
        if (!type_entry) {
            return -4;
        }
        if (type_entry->validate_fn) {
            rc = type_entry->validate_fn(ev->hdr.type_id, ev->hdr.schema_id, ev->hdr.schema_ver, ev->payload, ev->payload_len);
            if (rc != 0) {
                return -5;
            }
        }
    }

    payload_copy = (unsigned char *)0;
    if (ev->payload_len != 0u) {
        payload_copy = (unsigned char *)malloc((size_t)ev->payload_len);
        if (!payload_copy) {
            return -6;
        }
        memcpy(payload_copy, ev->payload, (size_t)ev->payload_len);
    }

    rc = dg_event_bus_alloc_record_id(bus, &rec_id);
    if (rc != 0) {
        if (payload_copy) free(payload_copy);
        return -7;
    }

    r = &bus->records[rec_id];
    if (r->in_use) {
        /* Should not happen; record ids are recycled only after being freed. */
        if (payload_copy) free(payload_copy);
        return -8;
    }
    memset(r, 0, sizeof(*r));
    r->hdr = ev->hdr;
    r->payload_owned = payload_copy;
    r->payload_len = ev->payload_len;
    r->in_use = D_TRUE;

    dg_work_item_clear(&it);
    it.key = dg_event_bus_key_from_hdr(&ev->hdr);
    it.work_type_id = 0u;
    it.cost_units = 1u;
    it.enqueue_tick = ev->hdr.tick;

    dg_le_write_u32(ref + 0u, rec_id);
    dg_le_write_u32(ref + 4u, 0u); /* subscriber offset */
    rc = dg_work_item_set_payload_inline(&it, ref, 8u);
    if (rc != 0) {
        dg_event_bus_free_record(bus, rec_id);
        return -9;
    }

    if (bus->deliver_q.capacity == 0u || bus->deliver_q.items == (dg_work_item *)0) {
        rc = dg_event_bus_grow_deliver_q(bus, 16u);
        if (rc != 0) {
            dg_event_bus_free_record(bus, rec_id);
            return -10;
        }
    } else if (bus->deliver_q.count >= bus->deliver_q.capacity) {
        rc = dg_event_bus_grow_deliver_q(bus, bus->deliver_q.capacity + 1u);
        if (rc != 0) {
            dg_event_bus_free_record(bus, rec_id);
            return -11;
        }
    }

    rc = dg_work_queue_push(&bus->deliver_q, &it);
    if (rc != 0) {
        /* Try one growth step (should be rare). */
        rc = dg_event_bus_grow_deliver_q(bus, bus->deliver_q.capacity + 1u);
        if (rc != 0 || dg_work_queue_push(&bus->deliver_q, &it) != 0) {
            dg_event_bus_free_record(bus, rec_id);
            return -12;
        }
    }

    bus->probe_events_published += 1u;
    return 0;
}

u32 dg_event_bus_deliver(dg_event_bus *bus, dg_budget *budget, dg_tick current_tick) {
    u32 processed = 0u;

    if (!bus || !budget) {
        return 0u;
    }

    for (;;) {
        const dg_work_item *next;
        u64 item_tick;
        u32 rec_id;
        u32 sub_ofs;
        dg_event_bus_record *r;
        u32 sub_start;
        u32 sub_count;

        next = dg_work_queue_peek_next(&bus->deliver_q);
        if (!next) {
            break;
        }

        item_tick = (u64)next->key.domain_id;
        if (item_tick > current_tick) {
            break;
        }

        if (next->payload_inline_len < 8u) {
            /* Malformed internal record; drop it deterministically. */
            (void)dg_work_queue_pop_next(&bus->deliver_q, (dg_work_item *)0);
            continue;
        }

        rec_id = dg_le_read_u32(next->payload_inline + 0u);
        sub_ofs = dg_le_read_u32(next->payload_inline + 4u);

        if (rec_id >= bus->record_count || !bus->records || !bus->records[rec_id].in_use) {
            (void)dg_work_queue_pop_next(&bus->deliver_q, (dg_work_item *)0);
            continue;
        }

        r = &bus->records[rec_id];
        dg_event_bus_sub_range(bus, r->hdr.type_id, &sub_start, &sub_count);

        if (sub_count == 0u || sub_ofs >= sub_count) {
            (void)dg_work_queue_pop_next(&bus->deliver_q, (dg_work_item *)0);
            dg_event_bus_free_record(bus, rec_id);
            continue;
        }

        {
            dg_budget_scope scope = dg_budget_scope_domain_chunk(r->hdr.domain_id, r->hdr.chunk_id);
            if (!dg_budget_try_consume(budget, &scope, 1u)) {
                bus->probe_deferred_deliveries += 1u;
                break;
            }
        }

        {
            dg_work_item item;
            dg_event_bus_sub *sub;
            dg_pkt_event pkt;

            if (!dg_work_queue_pop_next(&bus->deliver_q, &item)) {
                break;
            }

            rec_id = dg_le_read_u32(item.payload_inline + 0u);
            sub_ofs = dg_le_read_u32(item.payload_inline + 4u);

            if (rec_id >= bus->record_count || !bus->records || !bus->records[rec_id].in_use) {
                continue;
            }

            r = &bus->records[rec_id];
            dg_event_bus_sub_range(bus, r->hdr.type_id, &sub_start, &sub_count);
            if (sub_count == 0u || sub_ofs >= sub_count) {
                dg_event_bus_free_record(bus, rec_id);
                continue;
            }

            sub = &bus->subs[sub_start + sub_ofs];

            pkt.hdr = r->hdr;
            pkt.payload = (const unsigned char *)r->payload_owned;
            pkt.payload_len = r->payload_len;

            if (sub->fn) {
                sub->fn(&pkt, sub->user_ctx);
            }

            bus->probe_events_delivered += 1u;
            processed += 1u;

            sub_ofs += 1u;
            if (sub_ofs < sub_count) {
                unsigned char ref[8];
                dg_work_item next_it;
                int push_rc;

                dg_work_item_clear(&next_it);
                next_it.key = item.key;
                next_it.work_type_id = item.work_type_id;
                next_it.cost_units = 1u;
                next_it.enqueue_tick = item.enqueue_tick;

                dg_le_write_u32(ref + 0u, rec_id);
                dg_le_write_u32(ref + 4u, sub_ofs);
                (void)dg_work_item_set_payload_inline(&next_it, ref, 8u);

                push_rc = dg_work_queue_push(&bus->deliver_q, &next_it);
                if (push_rc != 0) {
                    /* Should have room (pop then push), but keep deterministically. */
                    (void)dg_event_bus_grow_deliver_q(bus, bus->deliver_q.capacity + 1u);
                    (void)dg_work_queue_push(&bus->deliver_q, &next_it);
                }
            } else {
                dg_event_bus_free_record(bus, rec_id);
            }
        }
    }

    return processed;
}

static void dg_event_bus_sched_handler(struct dg_sched *sched, void *user_ctx) {
    dg_event_bus *bus = (dg_event_bus *)user_ctx;
    if (!sched || !bus) {
        return;
    }
    (void)dg_event_bus_deliver(bus, &sched->budget, sched->tick);
}

int dg_event_bus_install_sense(dg_event_bus *bus, struct dg_sched *sched, u64 priority_key) {
    if (!bus || !sched) {
        return -1;
    }
    return dg_sched_register_phase_handler(sched, DG_PH_SENSE, dg_event_bus_sched_handler, priority_key, bus);
}

u32 dg_event_bus_probe_events_published(const dg_event_bus *bus) {
    return bus ? bus->probe_events_published : 0u;
}

u32 dg_event_bus_probe_events_delivered(const dg_event_bus *bus) {
    return bus ? bus->probe_events_delivered : 0u;
}

u32 dg_event_bus_probe_deferred_deliveries(const dg_event_bus *bus) {
    return bus ? bus->probe_deferred_deliveries : 0u;
}


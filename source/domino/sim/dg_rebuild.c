#include <string.h>

#include "sim/dg_rebuild.h"

void dg_rebuild_init(dg_rebuild_ctx *r) {
    if (!r) {
        return;
    }
    r->tick = 0u;
    r->next_seq = 0u;
}

void dg_rebuild_begin_tick(dg_rebuild_ctx *r, dg_tick tick) {
    if (!r) {
        return;
    }
    r->tick = tick;
}

static u32 dg_rebuild_estimate_cost(const dg_rebuild_target *t, const dg_rebuild_work *w) {
    if (t && t->rebuild_vtbl.estimate_cost_units) {
        u32 c = t->rebuild_vtbl.estimate_cost_units(t->user_ctx, w);
        return (c == 0u) ? 1u : c;
    }
    return 1u;
}

static int dg_rebuild_enqueue_one(
    dg_sched               *sched,
    dg_rebuild_ctx         *r,
    const dg_rebuild_target *t,
    dg_part_id              part_id,
    dg_rebuild_work_kind    kind,
    u64                     item_id
) {
    dg_work_item it;
    dg_rebuild_work w;

    if (!sched || !r || !t) {
        return -1;
    }

    memset(&w, 0, sizeof(w));
    w.graph_type_id = t->graph_type_id;
    w.graph_instance_id = t->graph_instance_id;
    w.part_id = part_id;
    w.kind = kind;
    w.item_id = item_id;

    dg_work_item_clear(&it);
    it.key = dg_order_key_make(
        (u16)DG_PH_TOPOLOGY,
        t->domain_id,
        (dg_chunk_id)part_id,
        (dg_entity_id)t->graph_instance_id,
        dg_rebuild_pack_component(kind, item_id),
        (dg_type_id)t->graph_type_id,
        r->next_seq++
    );
    it.work_type_id = (dg_type_id)t->graph_type_id;
    it.cost_units = dg_rebuild_estimate_cost(t, &w);
    it.enqueue_tick = r->tick;
    it.payload_ptr = (const unsigned char *)0;
    it.payload_len = 0u;
    it.payload_inline_len = 0u;

    return dg_sched_enqueue_work(sched, DG_PH_TOPOLOGY, &it);
}

int dg_rebuild_enqueue_from_dirty(
    dg_sched               *sched,
    dg_rebuild_ctx         *r,
    const dg_dirtyset      *dirty,
    const dg_rebuild_target *target
) {
    u32 i;
    int rc;

    if (!sched || !r || !dirty || !target) {
        return -1;
    }

    /* Canonical kind ordering: partition, then node, then edge. */
    for (i = 0u; i < dg_dirtyset_part_count(dirty); ++i) {
        dg_part_id pid = dg_dirtyset_part_at(dirty, i);
        rc = dg_rebuild_enqueue_one(sched, r, target, pid, DG_REBUILD_WORK_PARTITION, 0u);
        if (rc != 0) {
            return -2;
        }
    }

    for (i = 0u; i < dg_dirtyset_node_count(dirty); ++i) {
        dg_node_id nid = dg_dirtyset_node_at(dirty, i);
        rc = dg_rebuild_enqueue_one(sched, r, target, DG_PART_ID_INVALID, DG_REBUILD_WORK_NODE, (u64)nid);
        if (rc != 0) {
            return -3;
        }
    }

    for (i = 0u; i < dg_dirtyset_edge_count(dirty); ++i) {
        dg_edge_id eid = dg_dirtyset_edge_at(dirty, i);
        rc = dg_rebuild_enqueue_one(sched, r, target, DG_PART_ID_INVALID, DG_REBUILD_WORK_EDGE, (u64)eid);
        if (rc != 0) {
            return -4;
        }
    }

    return 0;
}

void dg_rebuild_sched_work_handler(struct dg_sched *sched, const dg_work_item *item, void *user_ctx) {
    const dg_rebuild_target *t = (const dg_rebuild_target *)user_ctx;
    dg_rebuild_work w;
    int rc;

    (void)sched;

    if (!t || !item) {
        return;
    }
    if (item->key.phase != (u16)DG_PH_TOPOLOGY) {
        return;
    }
    if ((dg_graph_type_id)item->work_type_id != t->graph_type_id) {
        return;
    }
    if ((dg_graph_instance_id)item->key.entity_id != t->graph_instance_id) {
        return;
    }

    rc = dg_rebuild_work_from_item(item, &w);
    if (rc != 0) {
        return;
    }
    if (w.graph_type_id != t->graph_type_id || w.graph_instance_id != t->graph_instance_id) {
        return;
    }

    if (t->rebuild_vtbl.execute) {
        (void)t->rebuild_vtbl.execute(t->user_ctx, &w);
    }
}

int dg_rebuild_enqueue_from_dirty_registry(
    dg_sched                *sched,
    dg_rebuild_ctx          *r,
    const dg_dirtyset       *dirty,
    const dg_graph_registry *registry,
    dg_graph_type_id         graph_type_id,
    dg_graph_instance_id     graph_instance_id,
    dg_domain_id             domain_id
) {
    dg_rebuild_target t;
    const dg_graph_registry_type *gt;
    const dg_graph_registry_instance *gi;

    if (!sched || !r || !dirty || !registry) {
        return -1;
    }

    gt = dg_graph_registry_find_type(registry, graph_type_id);
    if (!gt) {
        return -2;
    }
    gi = dg_graph_registry_find_instance(registry, graph_type_id, graph_instance_id);
    if (!gi) {
        return -3;
    }

    memset(&t, 0, sizeof(t));
    t.graph_type_id = graph_type_id;
    t.graph_instance_id = graph_instance_id;
    t.domain_id = domain_id;
    t.user_ctx = gi->user_ctx;
    if (gt->has_rebuild_vtbl) {
        t.rebuild_vtbl = gt->rebuild_vtbl;
    } else {
        memset(&t.rebuild_vtbl, 0, sizeof(t.rebuild_vtbl));
    }

    return dg_rebuild_enqueue_from_dirty(sched, r, dirty, &t);
}

void dg_rebuild_registry_sched_work_handler(struct dg_sched *sched, const dg_work_item *item, void *user_ctx) {
    const dg_graph_registry *registry = (const dg_graph_registry *)user_ctx;
    dg_rebuild_work w;
    dg_graph_type_id type_id;
    dg_graph_instance_id inst_id;
    const dg_graph_registry_type *gt;
    const dg_graph_registry_instance *gi;
    int rc;

    (void)sched;

    if (!registry || !item) {
        return;
    }
    if (item->key.phase != (u16)DG_PH_TOPOLOGY) {
        return;
    }

    type_id = (dg_graph_type_id)item->work_type_id;
    if (type_id == 0u) {
        return;
    }
    if ((dg_graph_type_id)item->key.type_id != type_id) {
        return;
    }
    inst_id = (dg_graph_instance_id)item->key.entity_id;
    if (inst_id == 0u) {
        return;
    }

    gt = dg_graph_registry_find_type(registry, type_id);
    if (!gt || !gt->has_rebuild_vtbl || !gt->rebuild_vtbl.execute) {
        return;
    }
    gi = dg_graph_registry_find_instance(registry, type_id, inst_id);
    if (!gi) {
        return;
    }

    rc = dg_rebuild_work_from_item(item, &w);
    if (rc != 0) {
        return;
    }
    if (w.graph_type_id != type_id || w.graph_instance_id != inst_id) {
        return;
    }
    (void)gt->rebuild_vtbl.execute(gi->user_ctx, &w);
}

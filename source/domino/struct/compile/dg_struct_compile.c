/* STRUCT deterministic compilation pipeline (C89). */
#include "struct/compile/dg_struct_compile.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_order_key.h"
#include "sim/sched/dg_phase.h"

static void dg_struct_compiled_init(dg_struct_compiled *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
    dg_struct_occ_spatial_index_init(&c->occupancy_spatial);
    dg_struct_room_spatial_index_init(&c->enclosure_spatial);
    dg_struct_surface_spatial_index_init(&c->surface_spatial);
    dg_struct_support_spatial_index_init(&c->support_spatial);
    dg_struct_carrier_spatial_index_init(&c->carrier_spatial);
}

static void dg_struct_compiled_struct_init(dg_struct_compiled_struct *s) {
    if (!s) return;
    memset(s, 0, sizeof(*s));
    dg_struct_occupancy_init(&s->occupancy);
    dg_struct_enclosure_graph_init(&s->enclosures);
    dg_struct_surface_graph_init(&s->surfaces);
    dg_struct_support_graph_init(&s->supports);
    dg_struct_carrier_compiled_init(&s->carriers);
}

static void dg_struct_compiled_struct_free(dg_struct_compiled_struct *s) {
    if (!s) return;
    dg_struct_occupancy_free(&s->occupancy);
    dg_struct_enclosure_graph_free(&s->enclosures);
    dg_struct_surface_graph_free(&s->surfaces);
    dg_struct_support_graph_free(&s->supports);
    dg_struct_carrier_compiled_free(&s->carriers);
    dg_struct_compiled_struct_init(s);
}

static void dg_struct_compiled_free(dg_struct_compiled *c) {
    u32 i;
    if (!c) return;
    if (c->structs) {
        for (i = 0u; i < c->struct_count; ++i) {
            dg_struct_compiled_struct_free(&c->structs[i]);
        }
        free(c->structs);
    }
    dg_struct_occ_spatial_index_free(&c->occupancy_spatial);
    dg_struct_room_spatial_index_free(&c->enclosure_spatial);
    dg_struct_surface_spatial_index_free(&c->surface_spatial);
    dg_struct_support_spatial_index_free(&c->support_spatial);
    dg_struct_carrier_spatial_index_free(&c->carrier_spatial);
    dg_struct_compiled_init(c);
}

static u32 dg_struct_compiled_lower_bound(const dg_struct_compiled *c, dg_struct_id struct_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!c) return 0u;
    hi = c->struct_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (c->structs[mid].struct_id >= struct_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static dg_struct_compiled_struct *dg_struct_compiled_get_or_add(dg_struct_compiled *c, dg_struct_id struct_id) {
    u32 idx;
    dg_struct_compiled_struct *arr;
    u32 new_cap;
    if (!c || struct_id == 0u) return (dg_struct_compiled_struct *)0;

    idx = dg_struct_compiled_lower_bound(c, struct_id);
    if (idx < c->struct_count && c->structs[idx].struct_id == struct_id) {
        return &c->structs[idx];
    }

    if (c->struct_count + 1u > c->struct_capacity) {
        new_cap = c->struct_capacity ? c->struct_capacity : 8u;
        while (new_cap < c->struct_count + 1u) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = c->struct_count + 1u; break; }
            new_cap *= 2u;
        }
        arr = (dg_struct_compiled_struct *)realloc(c->structs, sizeof(dg_struct_compiled_struct) * (size_t)new_cap);
        if (!arr) return (dg_struct_compiled_struct *)0;
        if (new_cap > c->struct_capacity) {
            memset(&arr[c->struct_capacity], 0, sizeof(dg_struct_compiled_struct) * (size_t)(new_cap - c->struct_capacity));
        }
        c->structs = arr;
        c->struct_capacity = new_cap;
    }

    if (idx < c->struct_count) {
        memmove(&c->structs[idx + 1u], &c->structs[idx],
                sizeof(dg_struct_compiled_struct) * (size_t)(c->struct_count - idx));
    }

    dg_struct_compiled_struct_init(&c->structs[idx]);
    c->structs[idx].struct_id = struct_id;
    c->struct_count += 1u;
    return &c->structs[idx];
}

static dg_struct_compiled_struct *dg_struct_compiled_find_mut(dg_struct_compiled *c, dg_struct_id struct_id) {
    u32 idx;
    if (!c || struct_id == 0u) return (dg_struct_compiled_struct *)0;
    idx = dg_struct_compiled_lower_bound(c, struct_id);
    if (idx < c->struct_count && c->structs[idx].struct_id == struct_id) {
        return &c->structs[idx];
    }
    return (dg_struct_compiled_struct *)0;
}

static const dg_struct_instance *dg_struct_find_instance(const dg_struct_compile_input *in, dg_struct_id struct_id) {
    u32 i;
    if (!in || !in->instances || struct_id == 0u) return (const dg_struct_instance *)0;
    for (i = 0u; i < in->instance_count; ++i) {
        if (in->instances[i].id == struct_id) return &in->instances[i];
    }
    return (const dg_struct_instance *)0;
}

void dg_struct_compiler_init(dg_struct_compiler *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
    dg_struct_compiled_init(&c->compiled);
    dg_struct_dirty_init(&c->dirty);
    dg_work_queue_init(&c->work_q);
}

void dg_struct_compiler_free(dg_struct_compiler *c) {
    if (!c) return;
    dg_struct_compiled_free(&c->compiled);
    dg_struct_dirty_free(&c->dirty);
    dg_work_queue_free(&c->work_q);
    dg_struct_compiler_init(c);
}

int dg_struct_compiler_reserve(dg_struct_compiler *c, u32 work_queue_capacity, u32 spatial_capacity) {
    int rc;
    if (!c) return -1;
    rc = dg_work_queue_reserve(&c->work_q, work_queue_capacity);
    if (rc != 0) return -2;
    rc = dg_struct_occ_spatial_index_reserve(&c->compiled.occupancy_spatial, spatial_capacity);
    if (rc != 0) return -3;
    rc = dg_struct_room_spatial_index_reserve(&c->compiled.enclosure_spatial, spatial_capacity);
    if (rc != 0) return -4;
    rc = dg_struct_surface_spatial_index_reserve(&c->compiled.surface_spatial, spatial_capacity);
    if (rc != 0) return -5;
    rc = dg_struct_support_spatial_index_reserve(&c->compiled.support_spatial, spatial_capacity);
    if (rc != 0) return -6;
    rc = dg_struct_carrier_spatial_index_reserve(&c->compiled.carrier_spatial, spatial_capacity);
    if (rc != 0) return -7;
    return 0;
}

int dg_struct_compiler_set_params(dg_struct_compiler *c, dg_q chunk_size_q) {
    if (!c) return -1;
    if (chunk_size_q <= 0) return -2;
    c->chunk_size_q = chunk_size_q;
    return 0;
}

int dg_struct_compiler_sync(dg_struct_compiler *c, const dg_struct_compile_input *in) {
    u32 i;
    if (!c || !in) return -1;
    if (!in->instances && in->instance_count != 0u) return -2;
    for (i = 0u; i < in->instance_count; ++i) {
        dg_struct_id id = in->instances[i].id;
        if (id == 0u) return -3;
        if (!dg_struct_compiled_get_or_add(&c->compiled, id)) return -4;
    }
    return 0;
}

static int dg_struct_compiler_push_work(dg_work_queue *q, dg_struct_id struct_id, dg_type_id type_id, dg_type_id work_type_id, u32 cost_units, dg_tick tick) {
    dg_work_item it;
    dg_order_key k;
    if (!q || struct_id == 0u) return -1;
    dg_work_item_clear(&it);
    dg_order_key_clear(&k);
    k.phase = (u16)DG_PH_TOPOLOGY;
    k.domain_id = 0u;
    k.chunk_id = 0u;
    k.entity_id = (dg_entity_id)struct_id;
    k.component_id = 0u;
    k.type_id = type_id;
    k.seq = 0u;
    it.key = k;
    it.work_type_id = work_type_id;
    it.cost_units = cost_units;
    it.enqueue_tick = tick;
    return dg_work_queue_push(q, &it);
}

int dg_struct_compiler_enqueue_dirty(dg_struct_compiler *c, dg_tick tick) {
    u32 i;
    if (!c) return -1;
    for (i = 0u; i < c->dirty.count; ++i) {
        dg_struct_dirty_record *r = &c->dirty.items[i];
        u32 flags;
        d_bool need_occ;
        d_bool need_encl;
        d_bool need_surf;
        d_bool need_supp;
        d_bool need_car;
        int rc;

        if (r->struct_id == 0u) continue;
        flags = r->dirty_flags;
        if (flags == 0u) continue;

        need_occ = (flags & (DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME)) ? D_TRUE : D_FALSE;
        need_encl = (flags & (DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_FOOTPRINT)) ? D_TRUE : D_FALSE;
        need_surf = (flags & (DG_STRUCT_DIRTY_SURFACE | DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_ENCLOSURE)) ? D_TRUE : D_FALSE;
        need_supp = (flags & (DG_STRUCT_DIRTY_SUPPORT | DG_STRUCT_DIRTY_FOOTPRINT | DG_STRUCT_DIRTY_VOLUME)) ? D_TRUE : D_FALSE;
        need_car = (flags & DG_STRUCT_DIRTY_CARRIER) ? D_TRUE : D_FALSE;

        if (need_occ) {
            rc = dg_struct_compiler_push_work(&c->work_q, r->struct_id, DG_STRUCT_WORK_OCCUPANCY, DG_STRUCT_WORK_OCCUPANCY, 5u, tick);
            if (rc != 0) return -2;
        }
        if (need_encl) {
            rc = dg_struct_compiler_push_work(&c->work_q, r->struct_id, DG_STRUCT_WORK_ENCLOSURE, DG_STRUCT_WORK_ENCLOSURE, 3u, tick);
            if (rc != 0) return -3;
        }
        if (need_surf) {
            rc = dg_struct_compiler_push_work(&c->work_q, r->struct_id, DG_STRUCT_WORK_SURFACE, DG_STRUCT_WORK_SURFACE, 4u, tick);
            if (rc != 0) return -4;
        }
        if (need_supp) {
            rc = dg_struct_compiler_push_work(&c->work_q, r->struct_id, DG_STRUCT_WORK_SUPPORT, DG_STRUCT_WORK_SUPPORT, 2u, tick);
            if (rc != 0) return -5;
        }
        if (need_car) {
            rc = dg_struct_compiler_push_work(&c->work_q, r->struct_id, DG_STRUCT_WORK_CARRIER, DG_STRUCT_WORK_CARRIER, 4u, tick);
            if (rc != 0) return -6;
        }

        dg_struct_dirty_clear_flags(&c->dirty, r->struct_id, 0xFFFFFFFFu);
    }
    return 0;
}

u32 dg_struct_compiler_process(dg_struct_compiler *c, const dg_struct_compile_input *in, dg_tick tick, u32 budget_units) {
    u32 processed = 0u;
    u32 remaining = budget_units;
    if (!c || !in) return 0u;

    while (remaining > 0u) {
        const dg_work_item *next = dg_work_queue_peek_next(&c->work_q);
        dg_work_item it;
        dg_struct_id struct_id;
        dg_struct_compiled_struct *cs;
        const dg_struct_instance *inst;
        int rc;

        if (!next) break;
        if (next->cost_units > remaining) break;

        (void)dg_work_queue_pop_next(&c->work_q, &it);
        remaining -= it.cost_units;
        processed += 1u;

        struct_id = (dg_struct_id)it.key.entity_id;
        cs = dg_struct_compiled_find_mut(&c->compiled, struct_id);
        if (!cs) {
            cs = dg_struct_compiled_get_or_add(&c->compiled, struct_id);
            if (!cs) break;
        }

        inst = dg_struct_find_instance(in, struct_id);
        if (!inst) {
            /* Deterministic: skip unknown structs (caller keeps IDs stable). */
            continue;
        }

        rc = 0;
        switch (it.work_type_id) {
        case DG_STRUCT_WORK_OCCUPANCY:
            rc = dg_struct_occupancy_rebuild(
                &cs->occupancy,
                &c->compiled.occupancy_spatial,
                inst,
                struct_id,
                in->footprints,
                in->footprint_count,
                in->volumes,
                in->volume_count,
                in->frames,
                tick,
                c->chunk_size_q
            );
            break;
        case DG_STRUCT_WORK_ENCLOSURE:
            rc = dg_struct_enclosure_graph_rebuild(
                &cs->enclosures,
                &c->compiled.enclosure_spatial,
                inst,
                struct_id,
                in->enclosures,
                in->enclosure_count,
                &cs->occupancy,
                c->chunk_size_q
            );
            break;
        case DG_STRUCT_WORK_SURFACE:
            rc = dg_struct_surface_graph_rebuild(
                &cs->surfaces,
                &c->compiled.surface_spatial,
                inst,
                struct_id,
                in->surface_templates,
                in->surface_template_count,
                in->sockets,
                in->socket_count,
                in->footprints,
                in->footprint_count,
                in->volumes,
                in->volume_count,
                in->frames,
                tick,
                c->chunk_size_q
            );
            break;
        case DG_STRUCT_WORK_SUPPORT:
            rc = dg_struct_support_graph_rebuild(
                &cs->supports,
                &c->compiled.support_spatial,
                struct_id,
                &cs->occupancy,
                c->chunk_size_q
            );
            break;
        case DG_STRUCT_WORK_CARRIER:
            rc = dg_struct_carrier_compile_rebuild(
                &cs->carriers,
                &c->compiled.carrier_spatial,
                inst,
                struct_id,
                in->carrier_intents,
                in->carrier_intent_count,
                in->frames,
                tick,
                c->chunk_size_q
            );
            break;
        default:
            break;
        }

        /* Deterministic: ignore partial index returns (>0), but stop on hard errors (<0). */
        if (rc < 0) {
            break;
        }
    }

    return processed;
}

u32 dg_struct_compiler_pending_work(const dg_struct_compiler *c) {
    if (!c) return 0u;
    return dg_work_queue_count(&c->work_q);
}

static int dg_struct_chunk_coord_cmp_local(const dg_struct_chunk_coord *a, const dg_struct_chunk_coord *b) {
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP3_I32(a->cx, a->cy, a->cz, b->cx, b->cy, b->cz);
}

int dg_struct_compiler_check_invariants(const dg_struct_compiler *c, const dg_struct_compile_input *in) {
    u32 i;
    (void)in;
    if (!c) return -1;

    /* Compiled struct table must be strictly sorted by struct_id. */
    for (i = 1u; i < c->compiled.struct_count; ++i) {
        if (c->compiled.structs[i - 1u].struct_id >= c->compiled.structs[i].struct_id) return -2;
    }

    for (i = 0u; i < c->compiled.struct_count; ++i) {
        const dg_struct_compiled_struct *s = &c->compiled.structs[i];
        u32 j;
        if (s->struct_id == 0u) return -3;

        for (j = 1u; j < s->occupancy.region_count; ++j) {
            if (s->occupancy.regions[j - 1u].volume_id >= s->occupancy.regions[j].volume_id) return -10;
        }
        for (j = 1u; j < s->enclosures.room_count; ++j) {
            if (s->enclosures.rooms[j - 1u].id >= s->enclosures.rooms[j].id) return -11;
        }
        for (j = 1u; j < s->enclosures.edge_count; ++j) {
            const dg_struct_room_edge *a = &s->enclosures.edges[j - 1u];
            const dg_struct_room_edge *b = &s->enclosures.edges[j];
            if (D_DET_CMP_U64(a->room_a, b->room_a) > 0) return -12;
            if (a->room_a == b->room_a && D_DET_CMP_U64(a->room_b, b->room_b) > 0) return -13;
            if (a->room_a == b->room_a && a->room_b == b->room_b && D_DET_CMP_I32((i32)a->kind, (i32)b->kind) > 0) return -14;
            if (a->room_a == b->room_a && a->room_b == b->room_b && a->kind == b->kind && a->id > b->id) return -15;
        }
        for (j = 1u; j < s->surfaces.surface_count; ++j) {
            if (s->surfaces.surfaces[j - 1u].id >= s->surfaces.surfaces[j].id) return -16;
        }
        for (j = 1u; j < s->surfaces.socket_count; ++j) {
            if (s->surfaces.sockets[j - 1u].id >= s->surfaces.sockets[j].id) return -17;
        }
        for (j = 1u; j < s->supports.node_count; ++j) {
            if (s->supports.nodes[j - 1u].id >= s->supports.nodes[j].id) return -18;
        }
        for (j = 1u; j < s->supports.edge_count; ++j) {
            if (s->supports.edges[j - 1u].id >= s->supports.edges[j].id) return -19;
        }
        for (j = 1u; j < s->carriers.count; ++j) {
            if (s->carriers.items[j - 1u].id >= s->carriers.items[j].id) return -20;
        }
    }

    /* Spatial indices must be in canonical sorted order. */
    for (i = 1u; i < c->compiled.occupancy_spatial.count; ++i) {
        const dg_struct_occ_spatial_entry *a = &c->compiled.occupancy_spatial.entries[i - 1u];
        const dg_struct_occ_spatial_entry *b = &c->compiled.occupancy_spatial.entries[i];
        int c0 = dg_struct_chunk_coord_cmp_local(&a->chunk, &b->chunk);
        if (c0 > 0) return -30;
        if (c0 == 0 && (a->struct_id > b->struct_id)) return -31;
        if (c0 == 0 && a->struct_id == b->struct_id && a->region_id >= b->region_id) return -32;
    }

    for (i = 1u; i < c->compiled.enclosure_spatial.count; ++i) {
        const dg_struct_room_spatial_entry *a = &c->compiled.enclosure_spatial.entries[i - 1u];
        const dg_struct_room_spatial_entry *b = &c->compiled.enclosure_spatial.entries[i];
        int c0 = dg_struct_chunk_coord_cmp_local(&a->chunk, &b->chunk);
        if (c0 > 0) return -33;
        if (c0 == 0 && (a->struct_id > b->struct_id)) return -34;
        if (c0 == 0 && a->struct_id == b->struct_id && a->room_id >= b->room_id) return -35;
    }

    for (i = 1u; i < c->compiled.surface_spatial.count; ++i) {
        const dg_struct_surface_spatial_entry *a = &c->compiled.surface_spatial.entries[i - 1u];
        const dg_struct_surface_spatial_entry *b = &c->compiled.surface_spatial.entries[i];
        int c0 = dg_struct_chunk_coord_cmp_local(&a->chunk, &b->chunk);
        if (c0 > 0) return -36;
        if (c0 == 0 && (a->struct_id > b->struct_id)) return -37;
        if (c0 == 0 && a->struct_id == b->struct_id && a->surface_id >= b->surface_id) return -38;
    }

    for (i = 1u; i < c->compiled.support_spatial.count; ++i) {
        const dg_struct_support_spatial_entry *a = &c->compiled.support_spatial.entries[i - 1u];
        const dg_struct_support_spatial_entry *b = &c->compiled.support_spatial.entries[i];
        int c0 = dg_struct_chunk_coord_cmp_local(&a->chunk, &b->chunk);
        if (c0 > 0) return -39;
        if (c0 == 0 && (a->struct_id > b->struct_id)) return -40;
        if (c0 == 0 && a->struct_id == b->struct_id && a->node_id >= b->node_id) return -41;
    }

    for (i = 1u; i < c->compiled.carrier_spatial.count; ++i) {
        const dg_struct_carrier_spatial_entry *a = &c->compiled.carrier_spatial.entries[i - 1u];
        const dg_struct_carrier_spatial_entry *b = &c->compiled.carrier_spatial.entries[i];
        int c0 = dg_struct_chunk_coord_cmp_local(&a->chunk, &b->chunk);
        if (c0 > 0) return -42;
        if (c0 == 0 && (a->struct_id > b->struct_id)) return -43;
        if (c0 == 0 && a->struct_id == b->struct_id && a->artifact_id >= b->artifact_id) return -44;
    }

    return 0;
}


/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_ecs.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/dom_sim_ecs
RESPONSIBILITY: Implements `dom_sim_ecs`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_sim_ecs.h"
#include "dom_core_mem.h"
#include <string.h>

typedef struct DomSimComponentStore {
    DomComponentInfo info;
    dom_u8          *data;
    dom_entity_id   *entities;    /* sorted by entity index */
    dom_u32         *entity_slot; /* mapping: entity index -> slot+1 */
    dom_u32          count;
} DomSimComponentStore;

static dom_entity_id g_entities[DOM_SIM_ECS_MAX_ENTITIES];
static dom_bool8     g_alive[DOM_SIM_ECS_MAX_ENTITIES];
static dom_u32       g_generation[DOM_SIM_ECS_MAX_ENTITIES];
static dom_entity_id g_active[DOM_SIM_ECS_MAX_ENTITIES];
static dom_u32       g_active_count;
static dom_u32       g_next_unused;
static dom_u32       g_free_indices[DOM_SIM_ECS_MAX_ENTITIES];
static dom_u32       g_free_count;

static DomSimComponentStore g_components[DOM_SIM_ECS_MAX_COMPONENTS];
static dom_u32 g_component_count;

static void dom_sim_ecs_reset_entities(void)
{
    memset(g_entities, 0, sizeof(g_entities));
    memset(g_alive, 0, sizeof(g_alive));
    memset(g_generation, 0, sizeof(g_generation));
    memset(g_active, 0, sizeof(g_active));
    memset(g_free_indices, 0, sizeof(g_free_indices));
    g_active_count = 0;
    g_next_unused = 0;
    g_free_count = 0;
}

static void dom_sim_ecs_reset_components(void)
{
    dom_u32 i;
    for (i = 0; i < DOM_SIM_ECS_MAX_COMPONENTS; ++i) {
        g_components[i].info.id = 0;
        g_components[i].info.name = 0;
        g_components[i].info.size = 0;
        g_components[i].info.align = 0;
        g_components[i].info.flags = 0;
        g_components[i].count = 0;
        g_components[i].data = 0;
        g_components[i].entities = 0;
        g_components[i].entity_slot = 0;
    }
    g_component_count = 0;
}

dom_err_t dom_sim_ecs_init(void)
{
    dom_sim_ecs_reset_entities();
    dom_sim_ecs_reset_components();
    return DOM_OK;
}

void dom_sim_ecs_reset(void)
{
    dom_sim_ecs_reset_entities();
    /* keep registered components but clear their contents */
    {
        dom_u32 i;
        for (i = 0; i < g_component_count; ++i) {
            DomSimComponentStore *st = &g_components[i];
            if (st->data) {
                dom_u32 bytes = st->info.size * DOM_SIM_ECS_MAX_ENTITIES;
                memset(st->data, 0, bytes);
            }
            if (st->entities) {
                memset(st->entities, 0, sizeof(dom_entity_id) * DOM_SIM_ECS_MAX_ENTITIES);
            }
            if (st->entity_slot) {
                memset(st->entity_slot, 0, sizeof(dom_u32) * DOM_SIM_ECS_MAX_ENTITIES);
            }
            st->count = 0;
        }
    }
}

static DomSimComponentStore *dom_sim_ecs_store(DomComponentId cid)
{
    dom_u32 idx = (dom_u32)(cid ? cid - 1 : 0);
    if (cid == 0 || idx >= g_component_count) return 0;
    return &g_components[idx];
}

DomComponentId dom_sim_ecs_register_component(const DomComponentInfo *info)
{
    DomSimComponentStore *st;
    DomComponentId id;
    dom_u32 bytes;
    if (!info) return 0;
    if (g_component_count >= DOM_SIM_ECS_MAX_COMPONENTS) return 0;
    id = (DomComponentId)(g_component_count + 1);
    st = &g_components[g_component_count];
    st->info = *info;
    st->info.id = id;
    st->count = 0;
    bytes = info->size * DOM_SIM_ECS_MAX_ENTITIES;
    st->data = (dom_u8 *)dom_alloc_zero(bytes);
    st->entities = (dom_entity_id *)dom_alloc_zero((dom_u32)sizeof(dom_entity_id) * DOM_SIM_ECS_MAX_ENTITIES);
    st->entity_slot = (dom_u32 *)dom_alloc_zero((dom_u32)sizeof(dom_u32) * DOM_SIM_ECS_MAX_ENTITIES);
    if (!st->data || !st->entities || !st->entity_slot) {
        if (st->data) dom_free(st->data);
        if (st->entities) dom_free(st->entities);
        if (st->entity_slot) dom_free(st->entity_slot);
        st->data = 0;
        st->entities = 0;
        st->entity_slot = 0;
        memset(&st->info, 0, sizeof(st->info));
        return 0;
    }
    g_component_count++;
    return id;
}

const DomComponentInfo *dom_sim_ecs_component_info(DomComponentId id)
{
    DomSimComponentStore *st = dom_sim_ecs_store(id);
    return st ? &st->info : 0;
}

static dom_u32 dom_sim_ecs_take_index(void)
{
    dom_u32 idx;
    if (g_free_count > 0) {
        dom_u32 pos = 0;
        idx = g_free_indices[0];
        for (pos = 1; pos < g_free_count; ++pos) {
            g_free_indices[pos - 1] = g_free_indices[pos];
        }
        g_free_count -= 1;
        return idx;
    }
    if (g_next_unused >= DOM_SIM_ECS_MAX_ENTITIES) return DOM_SIM_ECS_MAX_ENTITIES;
    idx = g_next_unused;
    g_next_unused += 1;
    return idx;
}

static void dom_sim_ecs_insert_active(dom_entity_id e, dom_u32 idx)
{
    dom_u32 pos;
    dom_u32 i;
    pos = g_active_count;
    for (i = 0; i < g_active_count; ++i) {
        dom_u32 existing_idx = dom_entity_index(g_active[i]);
        if (idx < existing_idx) {
            pos = i;
            break;
        }
    }
    if (pos < g_active_count) {
        memmove(&g_active[pos + 1], &g_active[pos],
                (g_active_count - pos) * sizeof(dom_entity_id));
    }
    g_active[pos] = e;
    g_active_count += 1;
}

static void dom_sim_ecs_remove_active(dom_entity_id e, dom_u32 idx)
{
    dom_u32 i;
    for (i = 0; i < g_active_count; ++i) {
        if (g_active[i] == e) {
            if (i + 1 < g_active_count) {
                memmove(&g_active[i], &g_active[i + 1],
                        (g_active_count - i - 1) * sizeof(dom_entity_id));
            }
            g_active_count -= 1;
            break;
        }
    }
    if (g_free_count < DOM_SIM_ECS_MAX_ENTITIES) {
        dom_u32 pos = g_free_count;
        for (i = 0; i < g_free_count; ++i) {
            if (idx < g_free_indices[i]) {
                pos = i;
                break;
            }
        }
        if (pos < g_free_count) {
            memmove(&g_free_indices[pos + 1], &g_free_indices[pos],
                    (g_free_count - pos) * sizeof(dom_u32));
        }
        g_free_indices[pos] = idx;
        g_free_count += 1;
    }
}

dom_entity_id dom_sim_ecs_create_entity(void)
{
    dom_u32 idx;
    dom_entity_id e;
    idx = dom_sim_ecs_take_index();
    if (idx >= DOM_SIM_ECS_MAX_ENTITIES) return 0;
    e = dom_entity_make(idx, g_generation[idx]);
    g_entities[idx] = e;
    g_alive[idx] = 1;
    dom_sim_ecs_insert_active(e, idx);
    return e;
}

static void dom_sim_ecs_remove_from_components(dom_entity_id e)
{
    dom_u32 comp;
    dom_u32 entity_idx = dom_entity_index(e);
    for (comp = 0; comp < g_component_count; ++comp) {
        DomSimComponentStore *st = &g_components[comp];
        dom_u32 slot = st->entity_slot[entity_idx];
        if (slot) {
            dom_u32 pos = slot - 1;
            dom_u32 trailing;
            if (pos + 1 < st->count) {
                memmove(&st->entities[pos], &st->entities[pos + 1],
                        (st->count - pos - 1) * sizeof(dom_entity_id));
                memmove(st->data + (pos * st->info.size),
                        st->data + ((pos + 1) * st->info.size),
                        (st->count - pos - 1) * st->info.size);
                trailing = pos;
                while (trailing < st->count - 1) {
                    dom_u32 shifted_idx = dom_entity_index(st->entities[trailing]);
                    st->entity_slot[shifted_idx] = trailing + 1;
                    trailing += 1;
                }
            }
            st->count -= 1;
            st->entity_slot[entity_idx] = 0;
        }
    }
}

dom_err_t dom_sim_ecs_destroy_entity(dom_entity_id e)
{
    dom_u32 idx = dom_entity_index(e);
    if (idx >= DOM_SIM_ECS_MAX_ENTITIES) return DOM_ERR_BOUNDS;
    if (!g_alive[idx]) return DOM_ERR_NOT_FOUND;
    dom_sim_ecs_remove_from_components(e);
    g_alive[idx] = 0;
    g_generation[idx] += 1;
    dom_sim_ecs_remove_active(e, idx);
    return DOM_OK;
}

dom_bool8 dom_sim_ecs_is_alive(dom_entity_id e)
{
    dom_u32 idx = dom_entity_index(e);
    if (idx >= DOM_SIM_ECS_MAX_ENTITIES) return 0;
    return g_alive[idx];
}

dom_u32 dom_sim_ecs_active_count(void)
{
    return g_active_count;
}

dom_entity_id dom_sim_ecs_active_at(dom_u32 index)
{
    if (index >= g_active_count) return 0;
    return g_active[index];
}

static dom_err_t dom_sim_ecs_insert_component(DomSimComponentStore *st,
                                              dom_entity_id e,
                                              const void *data)
{
    dom_u32 entity_idx;
    dom_u32 pos;
    dom_u32 i;
    dom_u32 size;
    if (!st) return DOM_ERR_INVALID_ARG;
    entity_idx = dom_entity_index(e);
    if (entity_idx >= DOM_SIM_ECS_MAX_ENTITIES) return DOM_ERR_BOUNDS;
    if (st->entity_slot[entity_idx]) return DOM_OK; /* already present */
    if (st->count >= DOM_SIM_ECS_MAX_ENTITIES) return DOM_ERR_BOUNDS;
    pos = st->count;
    for (i = 0; i < st->count; ++i) {
        dom_u32 existing_idx = dom_entity_index(st->entities[i]);
        if (entity_idx < existing_idx) {
            pos = i;
            break;
        }
    }
    size = st->info.size;
    if (pos < st->count) {
        memmove(&st->entities[pos + 1], &st->entities[pos],
                (st->count - pos) * sizeof(dom_entity_id));
        memmove(st->data + ((pos + 1) * size),
                st->data + (pos * size),
                (st->count - pos) * size);
        for (i = pos; i < st->count; ++i) {
            dom_u32 shifted_idx = dom_entity_index(st->entities[i + 1]);
            st->entity_slot[shifted_idx] = (i + 1) + 1;
        }
    }
    st->entities[pos] = e;
    st->entity_slot[entity_idx] = pos + 1;
    if (data) {
        memcpy(st->data + (pos * size), data, size);
    } else {
        memset(st->data + (pos * size), 0, size);
    }
    st->count += 1;
    return DOM_OK;
}

dom_err_t dom_sim_ecs_add_component(dom_entity_id e, DomComponentId cid, const void *data)
{
    DomSimComponentStore *st = dom_sim_ecs_store(cid);
    dom_u32 idx = dom_entity_index(e);
    if (!st) return DOM_ERR_INVALID_ARG;
    if (!dom_sim_ecs_is_alive(e)) return DOM_ERR_NOT_FOUND;
    if (idx >= DOM_SIM_ECS_MAX_ENTITIES) return DOM_ERR_BOUNDS;
    return dom_sim_ecs_insert_component(st, e, data);
}

dom_err_t dom_sim_ecs_remove_component(dom_entity_id e, DomComponentId cid)
{
    DomSimComponentStore *st = dom_sim_ecs_store(cid);
    dom_u32 entity_idx;
    dom_u32 slot;
    dom_u32 pos;
    dom_u32 i;
    dom_u32 size;
    if (!st) return DOM_ERR_INVALID_ARG;
    entity_idx = dom_entity_index(e);
    if (entity_idx >= DOM_SIM_ECS_MAX_ENTITIES) return DOM_ERR_BOUNDS;
    slot = st->entity_slot[entity_idx];
    if (!slot) return DOM_ERR_NOT_FOUND;
    pos = slot - 1;
    size = st->info.size;
    if (pos + 1 < st->count) {
        memmove(&st->entities[pos], &st->entities[pos + 1],
                (st->count - pos - 1) * sizeof(dom_entity_id));
        memmove(st->data + (pos * size),
                st->data + ((pos + 1) * size),
                (st->count - pos - 1) * size);
        for (i = pos; i < st->count - 1; ++i) {
            dom_u32 shifted_idx = dom_entity_index(st->entities[i]);
            st->entity_slot[shifted_idx] = i + 1;
        }
    }
    st->count -= 1;
    st->entity_slot[entity_idx] = 0;
    return DOM_OK;
}

void *dom_sim_ecs_component_ptr(DomComponentId cid, dom_entity_id e)
{
    DomSimComponentStore *st = dom_sim_ecs_store(cid);
    dom_u32 entity_idx;
    dom_u32 slot;
    if (!st) return 0;
    entity_idx = dom_entity_index(e);
    if (entity_idx >= DOM_SIM_ECS_MAX_ENTITIES) return 0;
    slot = st->entity_slot[entity_idx];
    if (!slot) return 0;
    return st->data + ((slot - 1) * st->info.size);
}

dom_u32 dom_sim_ecs_component_count(DomComponentId cid)
{
    DomSimComponentStore *st = dom_sim_ecs_store(cid);
    return st ? st->count : 0;
}

dom_entity_id dom_sim_ecs_component_entity_at(DomComponentId cid, dom_u32 index)
{
    DomSimComponentStore *st = dom_sim_ecs_store(cid);
    if (!st || index >= st->count) return 0;
    return st->entities[index];
}

DomLaneId dom_sim_ecs_lane_of(dom_entity_id e)
{
    return dom_sim_tick_lane_for_entity(e);
}

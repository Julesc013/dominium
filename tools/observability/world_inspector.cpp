/*
FILE: tools/observability/world_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements read-only world and topology inspection over observation stores.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and iteration.
*/
#include "world_inspector.h"

#include <string.h>

static void tool_world_access_default(tool_access_context* access)
{
    if (!access) {
        return;
    }
    access->mode = TOOL_ACCESS_EPISTEMIC;
    access->knowledge_mask = 0u;
}

int tool_world_inspector_init(tool_world_inspector* insp,
                              const tool_observation_store* store,
                              const tool_access_context* access)
{
    if (!insp || !store) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(insp, 0, sizeof(*insp));
    insp->store = store;
    if (access) {
        insp->access = *access;
    } else {
        tool_world_access_default(&insp->access);
    }
    return TOOL_OBSERVE_OK;
}

int tool_world_inspector_seek(tool_world_inspector* insp,
                              const tool_world_query* query)
{
    if (!insp) {
        return TOOL_OBSERVE_INVALID;
    }
    if (query) {
        insp->query = *query;
    } else {
        memset(&insp->query, 0, sizeof(insp->query));
    }
    insp->cursor = 0u;
    return TOOL_OBSERVE_OK;
}

int tool_world_inspector_next(tool_world_inspector* insp,
                              tool_world_view_cell* out_cell)
{
    if (!insp || !out_cell || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->world_cells || insp->store->world_cell_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->cursor < insp->store->world_cell_count) {
        const tool_world_cell* cell = &insp->store->world_cells[insp->cursor++];
        if (insp->query.field_id != 0u && cell->field_id != insp->query.field_id) {
            continue;
        }
        if (insp->query.use_bounds != 0u) {
            if (cell->x < insp->query.x_min || cell->x > insp->query.x_max) {
                continue;
            }
            if (cell->y < insp->query.y_min || cell->y > insp->query.y_max) {
                continue;
            }
        }
        if ((cell->flags & TOOL_WORLD_VALUE_UNKNOWN) != 0u &&
            insp->query.include_unknown == 0u) {
            continue;
        }
        if ((cell->flags & TOOL_WORLD_VALUE_LATENT) != 0u &&
            insp->query.include_latent == 0u) {
            continue;
        }
        out_cell->cell = *cell;
        out_cell->visible = 1u;
        if (insp->access.mode != TOOL_ACCESS_PRIVILEGED) {
            if ((cell->flags & (TOOL_WORLD_VALUE_UNKNOWN | TOOL_WORLD_VALUE_LATENT)) != 0u) {
                out_cell->visible = 0u;
                out_cell->cell.value_q16 = 0;
            }
        }
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_topology_inspector_init(tool_topology_inspector* insp,
                                 const tool_observation_store* store,
                                 const tool_topology_query* query)
{
    if (!insp || !store) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(insp, 0, sizeof(*insp));
    insp->store = store;
    if (query) {
        insp->query = *query;
    }
    return TOOL_OBSERVE_OK;
}

int tool_topology_inspector_next(tool_topology_inspector* insp,
                                 tool_topology_view* out_view)
{
    if (!insp || !out_view || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->topology || insp->store->topology_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->cursor < insp->store->topology_count) {
        const tool_topology_node* node = &insp->store->topology[insp->cursor++];
        if (insp->query.parent_id != 0u && node->parent_id != insp->query.parent_id) {
            continue;
        }
        out_view->node = *node;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

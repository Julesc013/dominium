/*
FILE: tools/observability/visualization_view.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements ASCII visualization helpers for read-only snapshots and fields.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic rendering for identical inputs.
*/
#include "visualization_view.h"

#include <string.h>

static void tool_vis_access_default(tool_access_context* access)
{
    if (!access) {
        return;
    }
    access->mode = TOOL_ACCESS_EPISTEMIC;
    access->knowledge_mask = 0u;
}

static char tool_vis_value_char(i32 value_q16)
{
    static const char palette[] = " .:-=+*#%@";
    u32 level;
    if (value_q16 <= 0) {
        return palette[0];
    }
    level = (u32)(value_q16 >> 12);
    if (level >= 9u) {
        level = 9u;
    }
    return palette[level];
}

static const tool_world_cell* tool_vis_find_cell(const tool_observation_store* store,
                                                 u32 x,
                                                 u32 y,
                                                 u32 field_id)
{
    u32 i;
    if (!store || !store->world_cells || store->world_cell_count == 0u) {
        return 0;
    }
    for (i = 0u; i < store->world_cell_count; ++i) {
        const tool_world_cell* cell = &store->world_cells[i];
        if (field_id != 0u && cell->field_id != field_id) {
            continue;
        }
        if (cell->x == x && cell->y == y) {
            return cell;
        }
    }
    return 0;
}

int tool_visualization_render_ascii(const tool_observation_store* store,
                                    const tool_visualization_request* request,
                                    const tool_access_context* access,
                                    char* out_buffer,
                                    u32 buffer_size,
                                    u32* out_written)
{
    tool_access_context local_access;
    const tool_access_context* ctx = access;
    u32 width;
    u32 height;
    u32 required;
    u32 y;
    u32 x;
    u32 written = 0u;
    if (!store || !request || !out_buffer || !out_written) {
        return TOOL_OBSERVE_INVALID;
    }
    width = request->width;
    height = request->height;
    if (width == 0u || height == 0u) {
        return TOOL_OBSERVE_INVALID;
    }
    required = (width + 1u) * height + 1u;
    if (buffer_size < required) {
        return TOOL_OBSERVE_REFUSED;
    }
    if (!ctx) {
        tool_vis_access_default(&local_access);
        ctx = &local_access;
    }
    for (y = 0u; y < height; ++y) {
        for (x = 0u; x < width; ++x) {
            u32 world_x = x;
            u32 world_y = y;
            char ch = '?';
            if (request->use_bounds != 0u) {
                u32 span_x = (request->x_max > request->x_min)
                    ? (request->x_max - request->x_min)
                    : 0u;
                u32 span_y = (request->y_max > request->y_min)
                    ? (request->y_max - request->y_min)
                    : 0u;
                if (width > 1u) {
                    world_x = request->x_min + (span_x * x) / (width - 1u);
                } else {
                    world_x = request->x_min;
                }
                if (height > 1u) {
                    world_y = request->y_min + (span_y * y) / (height - 1u);
                } else {
                    world_y = request->y_min;
                }
            }
            if (store->world_cells && store->world_cell_count != 0u) {
                const tool_world_cell* cell = tool_vis_find_cell(store, world_x, world_y, request->field_id);
                if (!cell) {
                    ch = '.';
                } else {
                    if ((cell->flags & TOOL_WORLD_VALUE_UNKNOWN) != 0u &&
                        (request->flags & TOOL_VIS_FLAG_INCLUDE_UNKNOWN) == 0u) {
                        ch = '.';
                    } else if ((cell->flags & TOOL_WORLD_VALUE_LATENT) != 0u &&
                               (request->flags & TOOL_VIS_FLAG_INCLUDE_LATENT) == 0u) {
                        ch = '.';
                    } else if (ctx->mode != TOOL_ACCESS_PRIVILEGED &&
                               (cell->flags & (TOOL_WORLD_VALUE_UNKNOWN | TOOL_WORLD_VALUE_LATENT)) != 0u) {
                        ch = '?';
                    } else {
                        ch = tool_vis_value_char(cell->value_q16);
                    }
                }
            } else {
                ch = '.';
            }
            out_buffer[written++] = ch;
        }
        out_buffer[written++] = '\n';
    }
    out_buffer[written] = '\0';
    *out_written = written;
    return TOOL_OBSERVE_OK;
}

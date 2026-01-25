/*
FILE: tools/observability/visualization_view.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: ASCII visualization helpers for read-only snapshots and fields.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic rendering for identical inputs.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_VISUALIZATION_VIEW_H
#define DOMINIUM_TOOLS_OBSERVABILITY_VISUALIZATION_VIEW_H

#include "domino/core/types.h"
#include "inspect_access.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    TOOL_VIS_FLAG_INCLUDE_UNKNOWN = 1u << 0,
    TOOL_VIS_FLAG_INCLUDE_LATENT = 1u << 1
};

typedef struct tool_visualization_request {
    u32 field_id;
    u32 width;
    u32 height;
    u32 use_bounds;
    u32 x_min;
    u32 y_min;
    u32 x_max;
    u32 y_max;
    u32 flags;
} tool_visualization_request;

int tool_visualization_render_ascii(const tool_observation_store* store,
                                    const tool_visualization_request* request,
                                    const tool_access_context* access,
                                    char* out_buffer,
                                    u32 buffer_size,
                                    u32* out_written);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_VISUALIZATION_VIEW_H */

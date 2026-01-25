/*
FILE: tools/observability/world_inspector.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Read-only world and topology inspection over observation stores.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and iteration.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_WORLD_INSPECTOR_H
#define DOMINIUM_TOOLS_OBSERVABILITY_WORLD_INSPECTOR_H

#include "domino/core/types.h"
#include "inspect_access.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_world_query {
    u32 field_id;
    u32 use_bounds;
    u32 x_min;
    u32 y_min;
    u32 x_max;
    u32 y_max;
    u32 include_unknown;
    u32 include_latent;
} tool_world_query;

typedef struct tool_world_view_cell {
    tool_world_cell cell;
    u32 visible;
} tool_world_view_cell;

typedef struct tool_world_inspector {
    const tool_observation_store* store;
    tool_access_context access;
    tool_world_query query;
    u32 cursor;
} tool_world_inspector;

typedef struct tool_topology_query {
    u64 parent_id;
} tool_topology_query;

typedef struct tool_topology_view {
    tool_topology_node node;
} tool_topology_view;

typedef struct tool_topology_inspector {
    const tool_observation_store* store;
    tool_topology_query query;
    u32 cursor;
} tool_topology_inspector;

int tool_world_inspector_init(tool_world_inspector* insp,
                              const tool_observation_store* store,
                              const tool_access_context* access);
int tool_world_inspector_seek(tool_world_inspector* insp,
                              const tool_world_query* query);
int tool_world_inspector_next(tool_world_inspector* insp,
                              tool_world_view_cell* out_cell);

int tool_topology_inspector_init(tool_topology_inspector* insp,
                                 const tool_observation_store* store,
                                 const tool_topology_query* query);
int tool_topology_inspector_next(tool_topology_inspector* insp,
                                 tool_topology_view* out_view);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_WORLD_INSPECTOR_H */

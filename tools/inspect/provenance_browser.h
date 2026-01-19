/*
FILE: tools/inspect/provenance_browser.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Provenance trace utilities for audit-safe inspection.
ALLOWED DEPENDENCIES: Engine public headers and C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic parent selection and traversal.
*/
#ifndef DOMINIUM_TOOLS_INSPECT_PROVENANCE_BROWSER_H
#define DOMINIUM_TOOLS_INSPECT_PROVENANCE_BROWSER_H

#include "domino/core/types.h"
#include "inspect_access.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_provenance_link {
    u64 child_id;
    u64 parent_id;
    u64 event_id;
    u32 required_knowledge;
} tool_provenance_link;

typedef struct tool_provenance_graph {
    const tool_provenance_link* links;
    u32 link_count;
} tool_provenance_graph;

typedef enum tool_provenance_refusal {
    TOOL_PROVENANCE_OK = 0,
    TOOL_PROVENANCE_NO_DATA = 1,
    TOOL_PROVENANCE_INSUFFICIENT_KNOWLEDGE = 2,
    TOOL_PROVENANCE_CYCLE = 3,
    TOOL_PROVENANCE_OUTPUT_FULL = 4
} tool_provenance_refusal;

int tool_provenance_trace(const tool_provenance_graph* graph,
                          u64 start_id,
                          const tool_access_context* access,
                          u64* out_path,
                          u32 max_len,
                          u32* out_len,
                          tool_provenance_refusal* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_INSPECT_PROVENANCE_BROWSER_H */

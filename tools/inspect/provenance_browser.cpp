/*
FILE: tools/inspect/provenance_browser.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Implements deterministic provenance tracing.
ALLOWED DEPENDENCIES: Engine public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic parent selection and traversal.
*/
#include "provenance_browser.h"

static void tool_provenance_set_refusal(tool_provenance_refusal* out_refusal,
                                        tool_provenance_refusal refusal) {
    if (out_refusal) {
        *out_refusal = refusal;
    }
}

static int tool_provenance_path_contains(const u64* path, u32 count, u64 id) {
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (path[i] == id) {
            return 1;
        }
    }
    return 0;
}

int tool_provenance_trace(const tool_provenance_graph* graph,
                          u64 start_id,
                          const tool_access_context* access,
                          u64* out_path,
                          u32 max_len,
                          u32* out_len,
                          tool_provenance_refusal* out_refusal) {
    u32 count = 0u;
    u64 current = start_id;
    if (!graph || !out_path || !out_len || start_id == 0u || max_len == 0u) {
        tool_provenance_set_refusal(out_refusal, TOOL_PROVENANCE_NO_DATA);
        return TOOL_INSPECT_INVALID;
    }

    while (current != 0u) {
        u32 i;
        u64 best_parent = 0u;
        u64 best_event = 0u;
        int found = 0;

        if (count >= max_len) {
            tool_provenance_set_refusal(out_refusal, TOOL_PROVENANCE_OUTPUT_FULL);
            return TOOL_INSPECT_INVALID;
        }
        if (tool_provenance_path_contains(out_path, count, current)) {
            tool_provenance_set_refusal(out_refusal, TOOL_PROVENANCE_CYCLE);
            return TOOL_INSPECT_INVALID;
        }
        out_path[count++] = current;

        for (i = 0u; i < graph->link_count; ++i) {
            const tool_provenance_link* link = &graph->links[i];
            if (link->child_id != current) {
                continue;
            }
            if (!tool_inspect_access_allows(access, link->required_knowledge)) {
                tool_provenance_set_refusal(out_refusal, TOOL_PROVENANCE_INSUFFICIENT_KNOWLEDGE);
                return TOOL_INSPECT_REFUSED;
            }
            if (!found ||
                link->event_id < best_event ||
                (link->event_id == best_event && link->parent_id < best_parent)) {
                best_parent = link->parent_id;
                best_event = link->event_id;
                found = 1;
            }
        }

        if (!found) {
            break;
        }
        current = best_parent;
    }

    *out_len = count;
    tool_provenance_set_refusal(out_refusal, TOOL_PROVENANCE_OK);
    return TOOL_INSPECT_OK;
}

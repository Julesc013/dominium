/*
FILE: tools/inspect/inspect_access.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Shared access context and refusal helpers for inspection tools.
ALLOWED DEPENDENCIES: Engine public headers and C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pure functions; no RNG or wall-clock time.
*/
#ifndef DOMINIUM_TOOLS_INSPECT_ACCESS_H
#define DOMINIUM_TOOLS_INSPECT_ACCESS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum tool_access_mode {
    TOOL_ACCESS_EPISTEMIC = 0,
    TOOL_ACCESS_PRIVILEGED = 1
} tool_access_mode;

typedef struct tool_access_context {
    tool_access_mode mode;
    u32 knowledge_mask;
} tool_access_context;

enum {
    TOOL_INSPECT_OK = 0,
    TOOL_INSPECT_NO_DATA = -1,
    TOOL_INSPECT_REFUSED = -2,
    TOOL_INSPECT_INVALID = -3
};

static int tool_inspect_access_allows(const tool_access_context* ctx, u32 required_mask) {
    if (!ctx) {
        return 0;
    }
    if (ctx->mode == TOOL_ACCESS_PRIVILEGED) {
        return 1;
    }
    return ((required_mask & ~ctx->knowledge_mask) == 0u) ? 1 : 0;
}

static int tool_inspect_request_mutation(const tool_access_context* ctx) {
    if (!ctx) {
        return TOOL_INSPECT_INVALID;
    }
    return TOOL_INSPECT_REFUSED;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_INSPECT_ACCESS_H */

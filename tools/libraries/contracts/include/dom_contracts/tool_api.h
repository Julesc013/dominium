/*
FILE: include/dominium/tool_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / tool_api
RESPONSIBILITY: Defines the public contract for `tool_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_TOOL_API_H_INCLUDED
#define DOMINIUM_TOOL_API_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Tool invocation context passed to tool entry points.
 *
 * Ownership/lifetime:
 * - The host creates the context and passes it to the tool entry point for the duration
 *   of the call. Tools must not retain the pointer beyond the entry call.
 *
 * ABI:
 * - `dom_tool_ctx` is a POD struct defined in this header for baseline visibility.
 * - See `docs/SPEC_TOOLS_CORE.md#Core types` for the registry/host contract.
 */
typedef struct dom_tool_ctx_t dom_tool_ctx;

/* Purpose: Common tool entry point signature for Dominium tools.
 *
 * Parameters:
 * - `ctx`: Tool context (non-NULL). The host initializes `ctx->env`; tools may use `ctx->user_data`.
 * - `argc`/`argv`: Command-line arguments as provided by the host. Strings are NUL-terminated and
 *   should be treated as read-only.
 *
 * Returns:
 * - Process-style exit code. The tool host forwards this value.
 */
typedef int (*dom_tool_main_fn)(dom_tool_ctx *ctx, int argc, char **argv);

/* Purpose: High-level categorization for tool discovery/UX grouping. */
typedef enum {
    DOM_TOOL_KIND_GENERIC = 0,
    DOM_TOOL_KIND_BUILD,
    DOM_TOOL_KIND_EDITOR,
    DOM_TOOL_KIND_ANALYSIS
} dom_tool_kind;

/* Purpose: Static registry descriptor for a built-in tool.
 *
 * ABI/versioning:
 * - `struct_size` and `struct_version` allow the host to validate the layout when linking
 *   across components. Current `struct_version` is 1 (see `source/dominium/tools/core/tool_core.c`).
 *
 * Ownership:
 * - String pointers refer to NUL-terminated storage owned by the registry for the process lifetime.
 */
typedef struct {
    uint32_t       struct_size;
    uint32_t       struct_version;
    const char    *id;          /* "assetc", "pack", "world_edit", ... */
    const char    *name;        /* "Asset Compiler" */
    const char    *description; /* short human description */
    dom_tool_kind  kind;
    dom_tool_main_fn entry;
} dom_tool_desc;

/* Purpose: Host-provided runtime environment for a tool invocation.
 *
 * ABI/versioning:
 * - The host must set `struct_size` and `struct_version` before calling tools.
 *
 * I/O:
 * - `write_stdout`/`write_stderr` may be NULL to indicate the tool should use stdio.
 * - When non-NULL, callbacks receive NUL-terminated text and `io_user` as provided by the host.
 */
typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    /* stdout/stderr callbacks (may be NULL to use stdio) */
    void (*write_stdout)(const char *text, void *user);
    void (*write_stderr)(const char *text, void *user);
    void *io_user;

    /* optional: pointer to dom_core / file system / paths */
    struct dom_core_t *core;
} dom_tool_env;

/* Purpose: Concrete definition of `dom_tool_ctx`.
 *
 * Notes:
 * - `env` is copied from the host-provided environment (when provided).
 * - `user_data` is owned by the tool; the host does not interpret it.
 */
struct dom_tool_ctx_t {
    dom_tool_env env;
    void        *user_data; /* tool-specific */
};

/* Purpose: Enumerate built-in tool descriptors.
 *
 * Parameters:
 * - `out_array`: Optional output. On success, receives a pointer to the first element of a
 *   contiguous, read-only array of `dom_tool_desc`.
 *
 * Returns:
 * - Number of tools available in the returned array.
 *
 * Lifetime:
 * - The returned array is owned by the registry and remains valid for the process lifetime.
 */
uint32_t dom_tool_list(const dom_tool_desc **out_array);

/* Purpose: Resolve a tool by id and invoke its entry point.
 *
 * Parameters:
 * - `id`: Tool identifier string to match against `dom_tool_desc.id` (non-NULL).
 * - `env`: Optional host environment to copy into `ctx.env`; may be NULL for a zero-initialized env.
 * - `argc`/`argv`: Arguments forwarded to the tool entry point.
 *
 * Returns:
 * - Tool entry return value on success.
 * - -1 if no tool with the requested id exists.
 */
int dom_tool_run(const char *id,
                 dom_tool_env *env,
                 int argc,
                 char **argv);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_TOOL_API_H_INCLUDED */

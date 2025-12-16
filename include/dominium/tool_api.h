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

typedef struct dom_tool_ctx_t dom_tool_ctx;

/* All tools implement a common entry signature */
typedef int (*dom_tool_main_fn)(dom_tool_ctx *ctx, int argc, char **argv);

typedef enum {
    DOM_TOOL_KIND_GENERIC = 0,
    DOM_TOOL_KIND_BUILD,
    DOM_TOOL_KIND_EDITOR,
    DOM_TOOL_KIND_ANALYSIS
} dom_tool_kind;

typedef struct {
    uint32_t       struct_size;
    uint32_t       struct_version;
    const char    *id;          /* "assetc", "pack", "world_edit", ... */
    const char    *name;        /* "Asset Compiler" */
    const char    *description; /* short human description */
    dom_tool_kind  kind;
    dom_tool_main_fn entry;
} dom_tool_desc;

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

struct dom_tool_ctx_t {
    dom_tool_env env;
    void        *user_data; /* tool-specific */
};

/* Tool host may enumerate all built-in tools */
uint32_t dom_tool_list(const dom_tool_desc **out_array);

/* Helpers to run a tool from inside code */
int dom_tool_run(const char *id,
                 dom_tool_env *env,
                 int argc,
                 char **argv);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_TOOL_API_H_INCLUDED */

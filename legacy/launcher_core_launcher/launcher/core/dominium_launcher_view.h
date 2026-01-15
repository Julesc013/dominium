/*
FILE: source/dominium/launcher/core/dominium_launcher_view.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/dominium_launcher_view
RESPONSIBILITY: Defines internal contract for `dominium_launcher_view`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_VIEW_H
#define DOMINIUM_LAUNCHER_VIEW_H

#include "domino/mod.h"

typedef enum {
    DOMINIUM_VIEW_KIND_LIST = 0,
    DOMINIUM_VIEW_KIND_DETAIL,
    DOMINIUM_VIEW_KIND_DASHBOARD,
    DOMINIUM_VIEW_KIND_SETTINGS,
    DOMINIUM_VIEW_KIND_CUSTOM
} dominium_view_kind;

typedef enum {
    DOMINIUM_VIEW_SOURCE_BUILTIN = 0,
    DOMINIUM_VIEW_SOURCE_MOD
} dominium_view_source;

/* Forward declarations for front-ends */
struct dominium_launcher_context;
struct dominium_launcher_view;
struct dominium_launcher_view_cli_ctx;
struct dominium_launcher_view_tui_ctx;
struct dominium_launcher_view_gui_ctx;

/* Per-front-end render callbacks (optional) */
typedef int (*dominium_view_render_cli_fn)(
    struct dominium_launcher_context* lctx,
    struct dominium_launcher_view*    view,
    struct dominium_launcher_view_cli_ctx* cli);

typedef int (*dominium_view_render_tui_fn)(
    struct dominium_launcher_context* lctx,
    struct dominium_launcher_view*    view,
    struct dominium_launcher_view_tui_ctx* tui);

typedef int (*dominium_view_render_gui_fn)(
    struct dominium_launcher_context* lctx,
    struct dominium_launcher_view*    view,
    struct dominium_launcher_view_gui_ctx* gui);

typedef struct dominium_launcher_view_desc {
    char id[64];       /* stable identifier: e.g. "instances", "mods", "packs", "myaddon.servers" */
    char label[64];    /* human-readable name */
    dominium_view_kind   kind;
    dominium_view_source source;
    unsigned int         priority;  /* sort order in tab bar */

    /* Built-in renderers (optional) */
    dominium_view_render_cli_fn render_cli;
    dominium_view_render_tui_fn render_tui;
    dominium_view_render_gui_fn render_gui;

    /* For mod-provided views */
    domino_package_id  owner_package;
    char               script_entry[128]; /* e.g. "myaddon_launcher_view_main" */

    void* user_data;   /* pointer to service-owned data, if any */
} dominium_launcher_view_desc;

#endif /* DOMINIUM_LAUNCHER_VIEW_H */

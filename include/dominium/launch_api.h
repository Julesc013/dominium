/*
FILE: include/dominium/launch_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / launch_api
RESPONSIBILITY: Defines the public contract for `launch_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCH_API_H_INCLUDED
#define DOMINIUM_LAUNCH_API_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/core.h"
#include "domino/view.h"
#include "domino/ui.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_launch_state: Public type used by `launch_api`. */
typedef enum {
    DOM_LAUNCH_STATE_STARTUP = 0,
    DOM_LAUNCH_STATE_MAIN,
    DOM_LAUNCH_STATE_INSTANCE_MANAGER,
    DOM_LAUNCH_STATE_PACKAGE_MANAGER,
    DOM_LAUNCH_STATE_SETTINGS,
    DOM_LAUNCH_STATE_RUNNING_INSTANCE   /* launcher supervising a game process */
} dom_launch_state;

/* dom_launch_action: Public type used by `launch_api`. */
typedef enum {
    DOM_LAUNCH_ACTION_NONE = 0,
    DOM_LAUNCH_ACTION_QUIT,
    DOM_LAUNCH_ACTION_LIST_INSTANCES,
    DOM_LAUNCH_ACTION_CREATE_INSTANCE,
    DOM_LAUNCH_ACTION_EDIT_INSTANCE,
    DOM_LAUNCH_ACTION_DELETE_INSTANCE,
    DOM_LAUNCH_ACTION_LAUNCH_INSTANCE,
    DOM_LAUNCH_ACTION_LIST_PACKAGES,
    DOM_LAUNCH_ACTION_ENABLE_MOD,
    DOM_LAUNCH_ACTION_DISABLE_MOD,
    DOM_LAUNCH_ACTION_OPEN_SETTINGS,
    DOM_LAUNCH_ACTION_VIEW_WORLD
} dom_launch_action;

/* opaque context */
typedef struct dom_launch_ctx_t dom_launch_ctx;

/* dom_launch_desc: Public type used by `launch_api`. */
typedef struct {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_core        *core;           /* already created domino core */
    dom_ui_mode      ui_mode;        /* NONE/CLI/TUI/GUI */
    const char      *product_id;     /* "dominium" */
    const char      *version;        /* "1.0.0" */
} dom_launch_desc;

/* dom_launch_snapshot: Public type used by `launch_api`. */
typedef struct {
    uint32_t          struct_size;
    uint32_t          struct_version;
    dom_launch_state  state;
    /* currently focused instance/package, or 0 if none */
    dom_instance_id   current_instance;
    dom_package_id    current_package;
    /* current view id for UI (e.g. "view_instances") */
    const char       *current_view_id;
} dom_launch_snapshot;

/* lifecycle */
dom_launch_ctx *dom_launch_create(const dom_launch_desc *desc);
/* Purpose: Destroy launch.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            dom_launch_destroy(dom_launch_ctx *ctx);

/* snapshot for UI front-ends */
void            dom_launch_get_snapshot(dom_launch_ctx *ctx,
                                        dom_launch_snapshot *out);

/* main input: high-level action from UI */
void            dom_launch_handle_action(dom_launch_ctx *ctx,
                                         dom_launch_action action,
                                         uint32_t param_u32,
                                         const char *param_str);
/* Purpose: Action dom launch handle custom.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            dom_launch_handle_custom_action(dom_launch_ctx *ctx,
                                               const char *action_id,
                                               const char *payload);

/* helper: enumerate views that the launcher wants to expose in the UI */
uint32_t        dom_launch_list_views(dom_launch_ctx *ctx,
                                      dom_view_desc *out,
                                      uint32_t max_out);

/* helper: launch or attach to a game instance (spawns process) */
int             dom_launch_run_instance(dom_launch_ctx *ctx,
                                        dom_instance_id inst_id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_LAUNCH_API_H_INCLUDED */

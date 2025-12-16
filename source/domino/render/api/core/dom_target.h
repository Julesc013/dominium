/*
FILE: source/domino/render/api/core/dom_target.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_target
RESPONSIBILITY: Defines internal contract for `dom_target`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TARGET_H
#define DOM_TARGET_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dom_u32 dom_target_id;
#define DOM_TARGET_ID_INVALID ((dom_target_id)0u)

typedef enum dom_target_type_e {
    DOM_TARGET_WINDOW_BACKBUFFER = 0,
    DOM_TARGET_OFFSCREEN_TEXTURE = 1
} dom_target_type;

typedef struct dom_target_s {
    dom_target_type type;
    dom_u32 width;
    dom_u32 height;
    void *platform_window; /* opaque window handle for backbuffer targets */
} dom_target;

dom_target_id dom_target_create_backbuffer(void *platform_window,
                                           dom_u32 width,
                                           dom_u32 height);
dom_target_id dom_target_create_offscreen(dom_u32 width, dom_u32 height);
dom_err_t     dom_target_destroy(dom_target_id id);
dom_target   *dom_target_lookup(dom_target_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOM_TARGET_H */

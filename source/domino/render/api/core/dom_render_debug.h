/*
FILE: source/domino/render/api/core/dom_render_debug.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_render_debug
RESPONSIBILITY: Implements `dom_render_debug`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_RENDER_DEBUG_H
#define DOM_RENDER_DEBUG_H

#include "dom_render_api.h"

#ifdef __cplusplus
extern "C" {
#endif

void dom_render_debug_draw_crosshair(DomRenderer *r, DomColor color);
void dom_render_debug_draw_grid(DomRenderer *r, dom_i32 spacing, DomColor color);

#ifdef __cplusplus
}
#endif

#endif /* DOM_RENDER_DEBUG_H */

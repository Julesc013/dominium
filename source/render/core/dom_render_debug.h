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

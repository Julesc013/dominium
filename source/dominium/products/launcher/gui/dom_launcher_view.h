// LEGACY: candidate for removal/refactor
#ifndef DOM_LAUNCHER_VIEW_H
#define DOM_LAUNCHER_VIEW_H

#include "dom_core_types.h"
#include "dom_render_api.h"

/* Simple, system-agnostic launcher layout rendered via DomRenderer. */
void dom_launcher_draw(DomRenderer *r, dom_u32 w, dom_u32 h);

#endif /* DOM_LAUNCHER_VIEW_H */

/*
FILE: include/domino/ui_renderer.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ui_renderer
RESPONSIBILITY: Defines the public contract for `ui_renderer` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_UI_RENDERER_H_INCLUDED
#define DOMINO_UI_RENDERER_H_INCLUDED

#include "domino/ui_layout.h"
#include "domino/ui_widget.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ui_renderer: Public type used by `ui_renderer`. */
typedef struct ui_renderer {
    int      width;
    int      height;
    int      dpi;
    int      viewports;
    ui_style theme;
} ui_renderer;

/* ui_renderer_desc: Public type used by `ui_renderer`. */
typedef struct ui_renderer_desc {
    int width;
    int height;
    int dpi;
    int viewports;
} ui_renderer_desc;

/* Purpose: Create renderer.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
ui_renderer* ui_renderer_create(const ui_renderer_desc* desc);
/* Purpose: Destroy renderer.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         ui_renderer_destroy(ui_renderer* r);
/* Purpose: Set theme.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         ui_renderer_set_theme(ui_renderer* r, const ui_style* theme);
/* Purpose: Draw ui renderer.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         ui_renderer_draw(ui_renderer* r, ui_node* root);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_RENDERER_H_INCLUDED */

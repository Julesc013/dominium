/*
FILE: include/domino/gui/style.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / gui/style
RESPONSIBILITY: Defines the public contract for `style` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_GUI_STYLE_H_INCLUDED
#define DOMINO_GUI_STYLE_H_INCLUDED

#include "domino/render/gui_prim.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dgui_style: Public type used by `style`. */
typedef struct dgui_style {
    dgui_color bg;
    dgui_color panel;
    dgui_color accent;
    dgui_color text;
    int        padding;
    int        spacing;
} dgui_style;

/* Purpose: Default style.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const dgui_style* dgui_style_default(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_GUI_STYLE_H_INCLUDED */

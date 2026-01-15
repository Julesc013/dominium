/*
FILE: source/domino/render/api/core/dom_text_layout.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_text_layout
RESPONSIBILITY: Implements `dom_text_layout`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_text_layout.h"

#include <string.h>

dom_err_t dom_text_layout_measure(const char *text,
                                  dom_i32 *out_width,
                                  dom_i32 *out_height)
{
    size_t len;
    if (!text || !out_width || !out_height) {
        return DOM_ERR_INVALID_ARG;
    }

    /* Simple deterministic placeholder: 8px per glyph, 8px tall. */
    len = strlen(text);
    *out_width = (dom_i32)(len * 8u);
    *out_height = 8;
    return DOM_OK;
}

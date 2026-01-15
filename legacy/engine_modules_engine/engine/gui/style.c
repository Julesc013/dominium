/*
FILE: source/domino/gui/style.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / gui/style
RESPONSIBILITY: Implements `style`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/gui/style.h"

static const dgui_style g_default_style = {
    { 16, 16, 24, 255 },   /* bg */
    { 28, 28, 40, 255 },   /* panel */
    { 64, 160, 255, 255 }, /* accent */
    { 220, 220, 235, 255 },/* text */
    2,                     /* padding */
    1                      /* spacing */
};

const dgui_style* dgui_style_default(void) {
    return &g_default_style;
}

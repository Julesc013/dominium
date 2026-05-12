/*
FILE: source/domino/render/api/core/dom_text_layout.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_text_layout
RESPONSIBILITY: Defines internal contract for `dom_text_layout`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TEXT_LAYOUT_H
#define DOM_TEXT_LAYOUT_H

#include "dom_draw_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Deterministic placeholder text metrics used by vector-only paths. */
dom_err_t dom_text_layout_measure(const char *text,
                                  dom_i32 *out_width,
                                  dom_i32 *out_height);

#ifdef __cplusplus
}
#endif

#endif /* DOM_TEXT_LAYOUT_H */

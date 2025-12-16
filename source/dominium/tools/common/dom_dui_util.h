/*
FILE: source/dominium/tools/common/dom_dui_util.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_dui_util
RESPONSIBILITY: Defines internal contract for `dom_dui_util`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_DUI_UTIL_H
#define DOM_DUI_UTIL_H

extern "C" {
#include "ui/d_ui.h"
}

namespace dom {
namespace tools {

void dui_clear_children(dui_context &ctx, dui_widget *parent);

dui_widget *dui_add_child_end(dui_context &ctx,
                              dui_widget *parent,
                              dui_widget_kind kind);

int dui_try_click(dui_context &ctx, int x, int y);

} // namespace tools
} // namespace dom

#endif /* DOM_DUI_UTIL_H */


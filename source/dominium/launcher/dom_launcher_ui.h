/*
FILE: source/dominium/launcher/dom_launcher_ui.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_ui
RESPONSIBILITY: Implements `dom_launcher_ui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_UI_H
#define DOM_LAUNCHER_UI_H

#include "ui/d_ui.h"
#include "dom_launcher_app.h"

namespace dom {

void dom_launcher_ui_build_root(dui_context &ctx, DomLauncherApp &app);
void dom_launcher_ui_update(dui_context &ctx, DomLauncherApp &app);
int  dom_launcher_ui_try_click(dui_context &ctx, int x, int y);

} // namespace dom

#endif

/*
FILE: source/dominium/launcher/gui/dom_launcher_view.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/gui/dom_launcher_view
RESPONSIBILITY: Implements `dom_launcher_view`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
// LEGACY: candidate for removal/refactor
#ifndef DOM_LAUNCHER_VIEW_H
#define DOM_LAUNCHER_VIEW_H

#include "dom_core_types.h"
#include "dom_render_api.h"

/* Simple, system-agnostic launcher layout rendered via DomRenderer. */
void dom_launcher_draw(DomRenderer *r, dom_u32 w, dom_u32 h);

#endif /* DOM_LAUNCHER_VIEW_H */

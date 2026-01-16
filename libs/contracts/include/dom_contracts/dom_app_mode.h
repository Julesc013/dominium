/*
FILE: include/dominium/dom_app_mode.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_app_mode
RESPONSIBILITY: Defines the public contract for `dom_app_mode` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DOM_APP_MODE_H
#define DOMINIUM_DOM_APP_MODE_H

#include "dom_plat_sys.h"
#include "dom_plat_term.h"
#include "dom_plat_ui.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Constants for `dom_app_mode`. */
enum dom_ui_mode {
    DOM_UI_MODE_HEADLESS = 0,
    DOM_UI_MODE_TERMINAL,
    DOM_UI_MODE_NATIVE_UI,
    DOM_UI_MODE_RENDERED
};

/* Purpose: Mode dom choose ui.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
enum dom_ui_mode dom_choose_ui_mode(int argc, char** argv,
                                    const struct dom_sys_vtable* sys,
                                    const struct dom_term_vtable* term,
                                    const struct dom_ui_vtable* ui,
                                    int rendered_allowed);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_APP_MODE_H */

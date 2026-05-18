/*
FILE: include/dominium/dom_plat_ui.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_plat_ui
RESPONSIBILITY: Defines the public contract for `dom_plat_ui` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DOM_PLAT_UI_H
#define DOMINIUM_DOM_PLAT_UI_H

/* Native UI abstraction (NATIVE_UI mode). Most fields are placeholders. */

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_UI_API_VERSION 1u

struct dom_sys_vtable; /* fwd */

/* dom_ui_app: Public type used by `dom_plat_ui`. */
typedef struct dom_ui_app    dom_ui_app;
/* dom_ui_window: Public type used by `dom_plat_ui`. */
typedef struct dom_ui_window dom_ui_window;
/* dom_ui_widget: Public type used by `dom_plat_ui`. */
typedef struct dom_ui_widget dom_ui_widget;

/* Constants for `dom_plat_ui`. */
enum dom_ui_widget_type {
    DOM_UI_WIDGET_VBOX = 0,
    DOM_UI_WIDGET_HBOX,
    DOM_UI_WIDGET_SPLIT,
    DOM_UI_WIDGET_TABS,
    DOM_UI_WIDGET_LIST,
    DOM_UI_WIDGET_TREE,
    DOM_UI_WIDGET_BUTTON,
    DOM_UI_WIDGET_LABEL,
    DOM_UI_WIDGET_TEXT_ENTRY,
    DOM_UI_WIDGET_CHECKBOX,
    DOM_UI_WIDGET_PROGRESS
};

struct dom_ui_window_desc {
    const char* title;
    int width;
    int height;
};

struct dom_ui_widget_desc {
    const char* text;
};

struct dom_ui_layout {
    int placeholder;
};

struct dom_ui_vtable {
    uint32_t api_version;

    dom_ui_app*    (*app_create)(int argc, char** argv);
/* Purpose: API entry point for `dom_plat_ui`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int            (*app_run)(dom_ui_app*);
/* Purpose: API entry point for `dom_plat_ui`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    void           (*app_quit)(dom_ui_app*);

    dom_ui_window* (*window_create)(dom_ui_app*, const struct dom_ui_window_desc*);
/* Purpose: API entry point for `dom_plat_ui`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    void           (*window_show)(dom_ui_window*);

    dom_ui_widget* (*widget_create)(dom_ui_window*, enum dom_ui_widget_type,
                                    const struct dom_ui_widget_desc*);

/* Purpose: API entry point for `dom_plat_ui`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    void           (*layout_apply)(dom_ui_window*, const struct dom_ui_layout*);
};

/* Purpose: Probe dom plat ui.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const struct dom_ui_vtable* dom_plat_ui_probe(const struct dom_sys_vtable* sys);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_PLAT_UI_H */

/*
FILE: include/domino/tui/tui.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / tui/tui
RESPONSIBILITY: Defines the public contract for `tui` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_TUI_TUI_H_INCLUDED
#define DOMINO_TUI_TUI_H_INCLUDED

/* Domino text UI (C89).
 * Minimal widget tree with deterministic layout and navigation.
 */

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Constants for `tui`. */
enum {
    D_TUI_KEY_NONE  = 0,
    D_TUI_KEY_ENTER = 10,
    D_TUI_KEY_UP    = 1001,
    D_TUI_KEY_DOWN  = 1002,
    D_TUI_KEY_RIGHT = 1003,
    D_TUI_KEY_LEFT  = 1004
};

/* d_tui_widget_type: Public type used by `tui`. */
typedef enum d_tui_widget_type {
    D_TUI_WIDGET_PANEL = 0,
    D_TUI_WIDGET_LABEL,
    D_TUI_WIDGET_BUTTON,
    D_TUI_WIDGET_LIST
} d_tui_widget_type;

/* d_tui_layout: Public type used by `tui`. */
typedef enum d_tui_layout {
    D_TUI_LAYOUT_VERTICAL = 0,
    D_TUI_LAYOUT_HORIZONTAL = 1
} d_tui_layout;

/* d_tui_widget: Public type used by `tui`. */
typedef struct d_tui_widget d_tui_widget;
/* d_tui_context: Public type used by `tui`. */
typedef struct d_tui_context d_tui_context;

/* user: Public type used by `tui`. */
typedef void (*d_tui_activate_fn)(d_tui_widget* self, void* user);

/* Purpose: Create tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_tui_context* d_tui_create(void);
/* Purpose: Destroy tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           d_tui_destroy(d_tui_context* ctx);

/* Purpose: Set root.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           d_tui_set_root(d_tui_context* ctx, d_tui_widget* root);

/* Purpose: Panel tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_tui_widget*  d_tui_panel(d_tui_context* ctx, d_tui_layout layout);
/* Purpose: Label tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_tui_widget*  d_tui_label(d_tui_context* ctx, const char* text);
/* Purpose: Button tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_tui_widget*  d_tui_button(d_tui_context* ctx, const char* text,
                            d_tui_activate_fn on_activate, void* user);
/* Purpose: List tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_tui_widget*  d_tui_list(d_tui_context* ctx, const char* const* items, int item_count);

/* Purpose: Add tui widget.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int            d_tui_widget_add(d_tui_widget* parent, d_tui_widget* child);
/* Purpose: Widget set text.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           d_tui_widget_set_text(d_tui_widget* w, const char* text);
/* Purpose: List set selection.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           d_tui_list_set_selection(d_tui_widget* w, int index);
/* Purpose: List get selection.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int            d_tui_list_get_selection(const d_tui_widget* w);

/* Purpose: Render tui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           d_tui_render(d_tui_context* ctx);
/* Purpose: Handle key.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           d_tui_handle_key(d_tui_context* ctx, int keycode);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_TUI_TUI_H_INCLUDED */

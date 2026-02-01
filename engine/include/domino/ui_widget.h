/*
FILE: include/domino/ui_widget.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ui_widget
RESPONSIBILITY: Defines the public contract for `ui_widget` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_UI_WIDGET_H_INCLUDED
#define DOMINO_UI_WIDGET_H_INCLUDED

#include "domino/baseline.h"
#include "domino/ui_events.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ui_cmd_buffer: Public type used by `ui_widget`. */
typedef dcvs ui_cmd_buffer;

/* ui_style: Public type used by `ui_widget`. */
typedef struct ui_style {
    uint32_t color_bg;
    uint32_t color_fg;
    uint32_t color_accent;
    uint32_t color_border;
    int      radius;
    int      border_px;
    int      font_id;
    int      icon_sheet;
} ui_style;

/* Purpose: Reset ui input.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_input_reset(void);
/* Purpose: Event ui input.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_input_event(const ui_event* ev);

/* Purpose: Frame ui begin.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_begin_frame(ui_cmd_buffer* cb, int width, int height, int time_ms);
/* Purpose: Frame ui end.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_end_frame(void);

/* Purpose: Button ui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  ui_button(const char* id, const char* label, ui_style* style);
/* Purpose: Toggle ui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  ui_toggle(const char* id, int* value, const char* label, ui_style* style);
/* Purpose: List ui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  ui_list(const char* id, const char** items, int count, int* selected, ui_style* style);
/* Purpose: Input ui text.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  ui_text_input(const char* id, char* buf, int buf_sz, ui_style* style);
/* Purpose: Begin ui scroll.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_scroll_begin(const char* id, int* scroll_y, ui_style* style);
/* Purpose: End ui scroll.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_scroll_end(void);
/* Purpose: Label ui.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void ui_label(const char* id, const char* text, ui_style* style);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_WIDGET_H_INCLUDED */

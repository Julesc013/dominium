/*
FILE: include/domino/ui_widget.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ui_widget
RESPONSIBILITY: Defines the public contract for `ui_widget` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_UI_WIDGET_H_INCLUDED
#define DOMINO_UI_WIDGET_H_INCLUDED

#include "domino/baseline.h"
#include "domino/ui_events.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dcvs ui_cmd_buffer;

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

void ui_input_reset(void);
void ui_input_event(const ui_event* ev);

void ui_begin_frame(ui_cmd_buffer* cb, int width, int height, int time_ms);
void ui_end_frame(void);

int  ui_button(const char* id, const char* label, ui_style* style);
int  ui_toggle(const char* id, int* value, const char* label, ui_style* style);
int  ui_list(const char* id, const char** items, int count, int* selected, ui_style* style);
int  ui_text_input(const char* id, char* buf, int buf_sz, ui_style* style);
void ui_scroll_begin(const char* id, int* scroll_y, ui_style* style);
void ui_scroll_end(void);
void ui_label(const char* id, const char* text, ui_style* style);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_WIDGET_H_INCLUDED */

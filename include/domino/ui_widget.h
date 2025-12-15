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

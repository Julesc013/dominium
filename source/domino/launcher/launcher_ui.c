#include <string.h>
#include <stdlib.h>
#include "domino/ui_widget.h"
#include "domino/ui_renderer.h"
#include "domino/gfx.h"

typedef struct ui_input_state {
    int mouse_x;
    int mouse_y;
    int mouse_down;
    int mouse_clicked;
    int mouse_released;
    int wheel;
    char text[8];
    int  text_len;
    int  key_code;
    int  key_pressed;
} ui_input_state;

typedef struct ui_context {
    ui_cmd_buffer* cb;
    int width;
    int height;
    int time_ms;
    int cursor_x;
    int cursor_y;
    int gap;
    int line_height;
    int scroll_offset;
    ui_style default_style;
    const char* active_id;
    ui_input_state input;
} ui_context;

static ui_context g_ui;

static uint32_t ui_color(int r, int g, int b, int a)
{
    return ((uint32_t)r << 24) | ((uint32_t)g << 16) | ((uint32_t)b << 8) | (uint32_t)a;
}

void ui_input_reset(void)
{
    memset(&g_ui.input, 0, sizeof(g_ui.input));
}

void ui_input_event(const ui_event* ev)
{
    if (!ev) {
        return;
    }
    switch (ev->type) {
    case UI_EVT_MOUSE:
        g_ui.input.mouse_x = ev->data.mouse.x;
        g_ui.input.mouse_y = ev->data.mouse.y;
        g_ui.input.wheel += ev->data.mouse.wheel;
        if (ev->data.mouse.pressed) {
            g_ui.input.mouse_down = ev->data.mouse.pressed;
        } else {
            if (g_ui.input.mouse_down) {
                g_ui.input.mouse_clicked = 1;
            }
            g_ui.input.mouse_down = 0;
            g_ui.input.mouse_released = 1;
        }
        break;
    case UI_EVT_KEY:
        g_ui.input.key_code = ev->data.key.code;
        g_ui.input.key_pressed = ev->data.key.pressed;
        break;
    case UI_EVT_TEXT:
        memset(g_ui.input.text, 0, sizeof(g_ui.input.text));
        strncpy(g_ui.input.text, ev->data.text, sizeof(g_ui.input.text) - 1u);
        g_ui.input.text_len = (int)strlen(g_ui.input.text);
        break;
    default:
        break;
    }
}

void ui_begin_frame(ui_cmd_buffer* cb, int width, int height, int time_ms)
{
    g_ui.cb = cb;
    g_ui.width = width;
    g_ui.height = height;
    g_ui.time_ms = time_ms;
    g_ui.cursor_x = 12;
    g_ui.cursor_y = 12;
    g_ui.gap = 8;
    g_ui.line_height = 28;
    g_ui.scroll_offset = 0;
    g_ui.default_style.color_bg = ui_color(24, 24, 28, 255);
    g_ui.default_style.color_fg = ui_color(240, 240, 240, 255);
    g_ui.default_style.color_accent = ui_color(80, 140, 255, 255);
    g_ui.default_style.color_border = ui_color(60, 60, 70, 255);
    g_ui.default_style.radius = 4;
    g_ui.default_style.border_px = 1;
    g_ui.default_style.font_id = 0;
    g_ui.default_style.icon_sheet = 0;
}

void ui_end_frame(void)
{
    g_ui.input.mouse_clicked = 0;
    g_ui.input.mouse_released = 0;
    g_ui.input.wheel = 0;
    g_ui.input.text_len = 0;
    g_ui.input.key_code = 0;
    g_ui.input.key_pressed = 0;
    g_ui.input.text[0] = '\0';
}

static int ui_point_in_box(int x, int y, int bx, int by, int bw, int bh)
{
    if (x < bx || y < by) {
        return 0;
    }
    if (x > bx + bw || y > by + bh) {
        return 0;
    }
    return 1;
}

static void ui_draw_rect(int x, int y, int w, int h, uint32_t color)
{
    dgfx_sprite_t spr;
    if (!g_ui.cb) {
        return;
    }
    spr.x = x;
    spr.y = y;
    spr.w = w;
    spr.h = h;
    spr.color_rgba = color;
    (void)dcvs_draw_sprite(g_ui.cb, &spr);
}

static void ui_draw_text(int x, int y, uint32_t color, const char* text)
{
    dgfx_text_draw_t t;
    if (!g_ui.cb || !text) {
        return;
    }
    t.x = x;
    t.y = y;
    t.color_rgba = color;
    t.utf8_text = text;
    (void)dcvs_draw_text(g_ui.cb, &t);
}

static int ui_allocate_row(int height)
{
    int y;
    y = g_ui.cursor_y;
    g_ui.cursor_y += height + g_ui.gap;
    return y;
}

int ui_button(const char* id, const char* label, ui_style* style)
{
    ui_style* st;
    int x;
    int y;
    int w;
    int h;
    int hovered;
    int clicked;
    uint32_t bg;

    (void)id;
    st = style ? style : &g_ui.default_style;
    x = g_ui.cursor_x;
    w = g_ui.width - (g_ui.cursor_x * 2);
    h = g_ui.line_height;
    y = ui_allocate_row(h);
    y += g_ui.scroll_offset;

    hovered = ui_point_in_box(g_ui.input.mouse_x, g_ui.input.mouse_y, x, y, w, h);
    clicked = hovered && g_ui.input.mouse_clicked;

    bg = st->color_bg;
    if (hovered) {
        bg = st->color_border;
    }
    ui_draw_rect(x, y, w, h, bg);
    ui_draw_rect(x, y, w, st->border_px, st->color_border);
    ui_draw_rect(x, y + h - st->border_px, w, st->border_px, st->color_border);
    ui_draw_rect(x, y, st->border_px, h, st->color_border);
    ui_draw_rect(x + w - st->border_px, y, st->border_px, h, st->color_border);
    ui_draw_text(x + 8, y + (h / 2) - 6, st->color_fg, label ? label : "");

    return clicked ? 1 : 0;
}

int ui_toggle(const char* id, int* value, const char* label, ui_style* style)
{
    ui_style* st;
    int x;
    int y;
    int w;
    int h;
    int box;
    int hovered;
    int clicked;

    (void)id;
    st = style ? style : &g_ui.default_style;
    box = 18;
    w = g_ui.width - (g_ui.cursor_x * 2);
    h = box;
    x = g_ui.cursor_x;
    y = ui_allocate_row(h);
    y += g_ui.scroll_offset;

    hovered = ui_point_in_box(g_ui.input.mouse_x, g_ui.input.mouse_y, x, y, box, box);
    clicked = hovered && g_ui.input.mouse_clicked;
    ui_draw_rect(x, y, box, box, st->color_border);
    if (value && *value) {
        ui_draw_rect(x + 3, y + 3, box - 6, box - 6, st->color_accent);
    } else {
        ui_draw_rect(x + 3, y + 3, box - 6, box - 6, st->color_bg);
    }
    ui_draw_text(x + box + 6, y + 2, st->color_fg, label ? label : "");
    if (clicked && value) {
        *value = *value ? 0 : 1;
        return 1;
    }
    return 0;
}

int ui_list(const char* id, const char** items, int count, int* selected, ui_style* style)
{
    int i;
    int clicked_index;
    ui_style* st;
    int x;
    int y;
    int w;
    int h;

    (void)id;
    if (!items || count <= 0) {
        return -1;
    }
    st = style ? style : &g_ui.default_style;
    clicked_index = -1;
    x = g_ui.cursor_x;
    w = g_ui.width - (g_ui.cursor_x * 2);
    h = g_ui.line_height;
    for (i = 0; i < count; ++i) {
        uint32_t bg;
        int row_y;
        int hovered;

        row_y = ui_allocate_row(h);
        row_y += g_ui.scroll_offset;
        hovered = ui_point_in_box(g_ui.input.mouse_x, g_ui.input.mouse_y, x, row_y, w, h);
        bg = st->color_bg;
        if (selected && *selected == i) {
            bg = st->color_accent;
        } else if (hovered) {
            bg = st->color_border;
        }
        ui_draw_rect(x, row_y, w, h, bg);
        ui_draw_text(x + 8, row_y + (h / 2) - 6, st->color_fg, items[i] ? items[i] : "");
        if (hovered && g_ui.input.mouse_clicked) {
            clicked_index = i;
            if (selected) {
                *selected = i;
            }
        }
    }
    return clicked_index;
}

int ui_text_input(const char* id, char* buf, int buf_sz, ui_style* style)
{
    ui_style* st;
    int x;
    int y;
    int w;
    int h;
    int hovered;
    int clicked;
    int active;

    st = style ? style : &g_ui.default_style;
    x = g_ui.cursor_x;
    w = g_ui.width - (g_ui.cursor_x * 2);
    h = g_ui.line_height;
    y = ui_allocate_row(h);
    y += g_ui.scroll_offset;

    hovered = ui_point_in_box(g_ui.input.mouse_x, g_ui.input.mouse_y, x, y, w, h);
    clicked = hovered && g_ui.input.mouse_clicked;
    if (clicked) {
        g_ui.active_id = id;
    }
    active = (g_ui.active_id == id);

    ui_draw_rect(x, y, w, h, active ? st->color_border : st->color_bg);
    ui_draw_rect(x, y, w, st->border_px, st->color_border);
    ui_draw_rect(x, y + h - st->border_px, w, st->border_px, st->color_border);
    ui_draw_rect(x, y, st->border_px, h, st->color_border);
    ui_draw_rect(x + w - st->border_px, y, st->border_px, h, st->color_border);
    ui_draw_text(x + 8, y + (h / 2) - 6, st->color_fg, buf ? buf : "");

    if (active && buf && buf_sz > 1) {
        if (g_ui.input.text_len > 0) {
            int i;
            int cur_len;
            cur_len = (int)strlen(buf);
            for (i = 0; i < g_ui.input.text_len; ++i) {
                if (cur_len + 1 < buf_sz) {
                    buf[cur_len] = g_ui.input.text[i];
                    cur_len += 1;
                    buf[cur_len] = '\0';
                }
            }
        }
        if (g_ui.input.key_pressed && g_ui.input.key_code == 8) {
            int cur_len;
            cur_len = (int)strlen(buf);
            if (cur_len > 0) {
                buf[cur_len - 1] = '\0';
            }
        }
    }
    return active;
}

void ui_scroll_begin(const char* id, int* scroll_y, ui_style* style)
{
    (void)id;
    (void)style;
    if (scroll_y && g_ui.input.wheel != 0) {
        *scroll_y += g_ui.input.wheel * 16;
        if (*scroll_y < 0) {
            *scroll_y = 0;
        }
    }
    if (scroll_y) {
        g_ui.scroll_offset = -(*scroll_y);
    } else {
        g_ui.scroll_offset = 0;
    }
}

void ui_scroll_end(void)
{
    g_ui.scroll_offset = 0;
}

void ui_label(const char* id, const char* text, ui_style* style)
{
    ui_style* st;
    int x;
    int y;
    int h;
    (void)id;
    st = style ? style : &g_ui.default_style;
    x = g_ui.cursor_x;
    h = g_ui.line_height;
    y = ui_allocate_row(h);
    y += g_ui.scroll_offset;
    ui_draw_text(x, y, st->color_fg, text ? text : "");
}

ui_renderer* ui_renderer_create(const ui_renderer_desc* desc)
{
    ui_renderer* r;
    ui_renderer_desc local;

    r = (ui_renderer*)malloc(sizeof(ui_renderer));
    if (!r) {
        return NULL;
    }
    memset(&local, 0, sizeof(local));
    if (desc) {
        local = *desc;
    }
    r->width = local.width;
    r->height = local.height;
    r->dpi = local.dpi ? local.dpi : 96;
    r->viewports = local.viewports ? local.viewports : 1;
    r->theme.color_bg = ui_color(16, 16, 20, 255);
    r->theme.color_fg = ui_color(240, 240, 240, 255);
    r->theme.color_accent = ui_color(90, 160, 255, 255);
    r->theme.color_border = ui_color(64, 64, 80, 255);
    r->theme.radius = 4;
    r->theme.border_px = 1;
    r->theme.font_id = 0;
    r->theme.icon_sheet = 0;
    return r;
}

void ui_renderer_destroy(ui_renderer* r)
{
    if (r) {
        free(r);
    }
}

void ui_renderer_set_theme(ui_renderer* r, const ui_style* theme)
{
    if (!r || !theme) {
        return;
    }
    r->theme = *theme;
}

static void ui_renderer_draw_node(ui_renderer* r, ui_node* node, int depth)
{
    ui_style* st;
    ui_node* child;
    (void)depth;
    if (!r || !node) {
        return;
    }
    st = &r->theme;
    ui_draw_rect(node->box.x, node->box.y, node->box.w, node->box.h, st->color_bg);
    ui_draw_rect(node->box.x, node->box.y, node->box.w, st->border_px, st->color_border);
    ui_draw_rect(node->box.x, node->box.y + node->box.h - st->border_px, node->box.w, st->border_px, st->color_border);
    ui_draw_rect(node->box.x, node->box.y, st->border_px, node->box.h, st->color_border);
    ui_draw_rect(node->box.x + node->box.w - st->border_px, node->box.y, st->border_px, node->box.h, st->color_border);
    ui_draw_text(node->box.x + 4, node->box.y + 4, st->color_fg, node->id ? node->id : "");
    child = node->first_child;
    while (child) {
        ui_renderer_draw_node(r, child, depth + 1);
        child = child->next_sibling;
    }
}

void ui_renderer_draw(ui_renderer* r, ui_node* root)
{
    if (!r || !root) {
        return;
    }
    ui_renderer_draw_node(r, root, 0);
}

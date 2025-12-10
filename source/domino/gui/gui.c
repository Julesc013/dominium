#include "domino/gui/gui.h"
#include "domino/canvas.h"
#include "domino/input/input.h"
#include "domino/render/backend_detect.h"
#include "domino/render/pipeline.h"
#include "domino/system/dsys.h"
#include <stdlib.h>
#include <string.h>

#define DGUI_MAX_CHILDREN 16
#define DGUI_TEXT_MAX 128
#define DGUI_MAX_WIDGETS 128

struct dgui_widget {
    dgui_widget_type type;
    dgui_layout layout;
    char text[DGUI_TEXT_MAX];
    dgui_context* owner;
    dgui_widget* children[DGUI_MAX_CHILDREN];
    int child_count;
    int x, y, w, h;
    dgui_activate_fn on_activate;
    void* user;
};

struct dgui_context {
    dgui_widget* root;
    dgui_widget* focus[DGUI_MAX_WIDGETS];
    int focus_count;
    int focus_index;
    const dgui_style* style;
    int surface_w;
    int surface_h;
};

static void dgui_copy(char* dst, size_t cap, const char* src) {
    size_t len;
    if (!dst || cap == 0) return;
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = strlen(src);
    if (len >= cap) len = cap - 1u;
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static dgui_widget* dgui_alloc_widget(dgui_context* owner, dgui_widget_type type) {
    dgui_widget* w = (dgui_widget*)malloc(sizeof(dgui_widget));
    if (!w) return NULL;
    memset(w, 0, sizeof(*w));
    w->type = type;
    w->layout = DGUI_LAYOUT_VERTICAL;
    w->owner = owner;
    return w;
}

dgui_context* dgui_create(void) {
    dgui_context* ctx = (dgui_context*)malloc(sizeof(dgui_context));
    if (!ctx) return NULL;
    memset(ctx, 0, sizeof(*ctx));
    ctx->style = dgui_style_default();
    ctx->surface_w = 640;
    ctx->surface_h = 360;
    return ctx;
}

void dgui_destroy(dgui_context* ctx) {
    int i;
    if (!ctx) return;
    for (i = 0; i < ctx->focus_count; ++i) {
        free(ctx->focus[i]);
    }
    if (ctx->root) free(ctx->root);
    free(ctx);
}

void dgui_set_root(dgui_context* ctx, dgui_widget* root) {
    if (!ctx) return;
    ctx->root = root;
}

void dgui_set_style(dgui_context* ctx, const dgui_style* style) {
    if (!ctx) return;
    ctx->style = style ? style : dgui_style_default();
}

dgui_widget* dgui_panel(dgui_context* ctx, dgui_layout layout) {
    dgui_widget* w = dgui_alloc_widget(ctx, DGUI_WIDGET_PANEL);
    if (w) w->layout = layout;
    return w;
}

dgui_widget* dgui_label(dgui_context* ctx, const char* text) {
    dgui_widget* w = dgui_alloc_widget(ctx, DGUI_WIDGET_LABEL);
    if (w) dgui_copy(w->text, sizeof(w->text), text);
    return w;
}

dgui_widget* dgui_button(dgui_context* ctx, const char* text, dgui_activate_fn cb, void* user) {
    dgui_widget* w = dgui_alloc_widget(ctx, DGUI_WIDGET_BUTTON);
    if (w) {
        dgui_copy(w->text, sizeof(w->text), text);
        w->on_activate = cb;
        w->user = user;
    }
    return w;
}

dgui_widget* dgui_list(dgui_context* ctx, const char* const* items, int count) {
    (void)items;
    (void)count;
    return dgui_alloc_widget(ctx, DGUI_WIDGET_LIST);
}

int dgui_widget_add(dgui_widget* parent, dgui_widget* child) {
    if (!parent || !child) return 0;
    if (parent->child_count >= DGUI_MAX_CHILDREN) return 0;
    parent->children[parent->child_count++] = child;
    return 1;
}

static void dgui_collect_focus(dgui_context* ctx, dgui_widget* w) {
    int i;
    if (!ctx || !w) return;
    if (w->type == DGUI_WIDGET_BUTTON) {
        if (ctx->focus_count < DGUI_MAX_WIDGETS) {
            ctx->focus[ctx->focus_count++] = w;
        }
    }
    for (i = 0; i < w->child_count; ++i) {
        dgui_collect_focus(ctx, w->children[i]);
    }
}

static void dgui_layout_widget(dgui_widget* w, int x, int y, int w_px, int h_px) {
    int i;
    if (!w) return;
    w->x = x; w->y = y; w->w = w_px; w->h = h_px;
    if (w->type == DGUI_WIDGET_PANEL && w->child_count > 0) {
        if (w->layout == DGUI_LAYOUT_VERTICAL) {
            int slot = h_px / w->child_count;
            int extra = h_px - slot * w->child_count;
            int cy = y;
            for (i = 0; i < w->child_count; ++i) {
                int ch = slot + ((i == w->child_count - 1) ? extra : 0);
                dgui_layout_widget(w->children[i], x, cy, w_px, ch);
                cy += ch;
            }
        } else {
            int slot = w_px / w->child_count;
            int extra = w_px - slot * w->child_count;
            int cx = x;
            for (i = 0; i < w->child_count; ++i) {
                int cw = slot + ((i == w->child_count - 1) ? extra : 0);
                dgui_layout_widget(w->children[i], cx, y, cw, h_px);
                cx += cw;
            }
        }
    }
}

static void dgui_render_widget(const dgui_context* ctx, dgui_widget* w, struct dcvs_t* canvas) {
    int i;
    if (!w) return;
    if (w->type == DGUI_WIDGET_PANEL) {
        dgui_rect_prim rp;
        rp.rect.x = w->x; rp.rect.y = w->y; rp.rect.w = w->w; rp.rect.h = w->h;
        rp.fill = ctx->style->panel;
        rp.stroke = ctx->style->panel;
        rp.stroke_width = 0;
        rp.corner_radius = 0;
        dgui_draw_rect(canvas, &rp);
    } else if (w->type == DGUI_WIDGET_LABEL) {
        dgui_text_prim tp;
        tp.x = w->x + ctx->style->padding;
        tp.y = w->y + ctx->style->padding + 1;
        tp.color = ctx->style->text;
        tp.text = w->text;
        dgui_draw_text(canvas, &tp);
    } else if (w->type == DGUI_WIDGET_BUTTON) {
        dgui_rect_prim rp;
        dgui_text_prim tp;
        rp.rect.x = w->x + ctx->style->padding;
        rp.rect.y = w->y + ctx->style->padding;
        rp.rect.w = w->w - ctx->style->padding * 2;
        rp.rect.h = w->h - ctx->style->padding * 2;
        rp.fill = ctx->style->accent;
        rp.stroke = ctx->style->panel;
        rp.stroke_width = 0;
        rp.corner_radius = 2;
        dgui_draw_rect(canvas, &rp);
        tp.x = rp.rect.x + 1;
        tp.y = rp.rect.y + 1;
        tp.color = ctx->style->text;
        tp.text = w->text;
        dgui_draw_text(canvas, &tp);
    }
    for (i = 0; i < w->child_count; ++i) {
        dgui_render_widget(ctx, w->children[i], canvas);
    }
}

void dgui_render(dgui_context* ctx, struct dcvs_t* canvas) {
    int w;
    int h;
    if (!ctx || !ctx->root || !canvas) return;
    ctx->focus_count = 0;
    ctx->focus_index = 0;
    dgui_collect_focus(ctx, ctx->root);
    w = (ctx->surface_w > 0) ? ctx->surface_w : 640;
    h = (ctx->surface_h > 0) ? ctx->surface_h : 360;
    dgui_layout_widget(ctx->root, 0, 0, w, h);
    dgui_render_widget(ctx, ctx->root, canvas);
}

void dgui_handle_key(dgui_context* ctx, int keycode) {
    dgui_widget* focused;
    if (!ctx || ctx->focus_count == 0) return;
    focused = ctx->focus[ctx->focus_index];
    if (keycode == 1002 /* down */) {
        ctx->focus_index = (ctx->focus_index + 1) % ctx->focus_count;
    } else if (keycode == 1001 /* up */) {
        ctx->focus_index -= 1;
        if (ctx->focus_index < 0) ctx->focus_index = ctx->focus_count - 1;
    } else if (keycode == 10 && focused && focused->on_activate) {
        focused->on_activate(focused, focused->user);
    }
}

/*------------------------------------------------------------
 * Multi-window GUI host
 *------------------------------------------------------------*/
#define DGUI_MAX_IR_CMDS 256

struct d_gui_window {
    dsys_window*       window;
    d_gfx_pipeline*    pipeline;
    d_gfx_target*      target;
    d_gfx_pass*        pass;
    dgui_context*      gui;
    dgui_widget*       root;
    dcvs*              canvas;
    struct d_gui_window* next;
    d_gui_window_desc  desc;
    int                owns_pipeline;
};

static d_gui_window* g_gui_windows = NULL;
static d_gfx_pipeline* g_gui_shared_pipeline = NULL;

void d_gui_set_shared_pipeline(d_gfx_pipeline* pipe) {
    g_gui_shared_pipeline = pipe;
}

static uint32_t d_gui_pack_color(const dgui_color* c) {
    if (!c) {
        return 0xff202020u;
    }
    return ((uint32_t)c->a << 24) |
           ((uint32_t)c->r << 16) |
           ((uint32_t)c->g << 8)  |
           ((uint32_t)c->b);
}

static d_gfx_pipeline* d_gui_resolve_pipeline(int* owns_flag) {
    d_gfx_pipeline* pipe = NULL;
    d_gfx_backend_type backend;
    if (owns_flag) {
        *owns_flag = 0;
    }
    if (g_gui_shared_pipeline) {
        return g_gui_shared_pipeline;
    }
    backend = d_gfx_select_backend();
    pipe = d_gfx_pipeline_create(backend);
    if (!pipe && backend != D_GFX_BACKEND_SOFT) {
        backend = D_GFX_BACKEND_SOFT;
        pipe = d_gfx_pipeline_create(backend);
    }
    if (pipe && owns_flag) {
        *owns_flag = 1;
    }
    return pipe;
}

static void d_gui_window_list_add(d_gui_window* win) {
    if (!win) return;
    win->next = g_gui_windows;
    g_gui_windows = win;
}

static void d_gui_window_list_remove(d_gui_window* win) {
    d_gui_window** cur;
    cur = &g_gui_windows;
    while (*cur) {
        if (*cur == win) {
            *cur = win->next;
            return;
        }
        cur = &((*cur)->next);
    }
}

static u32 d_gui_decode_ir(const dgfx_cmd_buffer* buf, d_gfx_ir_command* out_cmds, u32 max_cmds) {
    u32 count = 0u;
    const uint8_t* ptr;
    const uint8_t* end;
    if (!buf || !buf->data || buf->size == 0u || !out_cmds || max_cmds == 0u) {
        return 0u;
    }
    ptr = buf->data;
    end = buf->data + buf->size;
    while (ptr + sizeof(dgfx_cmd_header) <= end && count < max_cmds) {
        const dgfx_cmd_header* hdr;
        const uint8_t* payload;
        uint32_t cmd_size;
        uint32_t payload_size;
        hdr = (const dgfx_cmd_header*)ptr;
        cmd_size = hdr->size;
        if (cmd_size < sizeof(dgfx_cmd_header)) {
            cmd_size = (uint32_t)sizeof(dgfx_cmd_header) + (uint32_t)hdr->payload_size;
        }
        if (ptr + cmd_size > end) {
            break;
        }
        payload = ptr + sizeof(dgfx_cmd_header);
        payload_size = cmd_size - (uint32_t)sizeof(dgfx_cmd_header);
        out_cmds[count].opcode = hdr->opcode;
        out_cmds[count].payload = payload;
        out_cmds[count].payload_size = payload_size;
        ++count;
        ptr += cmd_size;
    }
    return count;
}

d_gui_window* d_gui_window_create(const d_gui_window_desc* desc) {
    d_gui_window* win;
    d_gui_window_desc local;
    dsys_window_desc sdesc;
    int owns_pipeline = 0;

    win = (d_gui_window*)malloc(sizeof(d_gui_window));
    if (!win) return NULL;
    memset(win, 0, sizeof(*win));

    local.title = "Domino GUI";
    local.x = 0;
    local.y = 0;
    local.width = 640;
    local.height = 360;
    local.resizable = 1;
    if (desc) {
        local = *desc;
        if (!local.title) local.title = "Domino GUI";
        if (local.width <= 0) local.width = 640;
        if (local.height <= 0) local.height = 360;
    }
    win->desc = local;

    win->pipeline = d_gui_resolve_pipeline(&owns_pipeline);
    win->owns_pipeline = owns_pipeline;
    if (!win->pipeline) {
        free(win);
        return NULL;
    }

    win->target = d_gfx_target_create(win->pipeline, local.width, local.height);
    if (!win->target) {
        if (win->owns_pipeline) d_gfx_pipeline_destroy(win->pipeline);
        free(win);
        return NULL;
    }
    win->pass = d_gfx_pass_create(win->pipeline, win->target);
    if (!win->pass) {
        d_gfx_target_destroy(win->pipeline, win->target);
        if (win->owns_pipeline) d_gfx_pipeline_destroy(win->pipeline);
        free(win);
        return NULL;
    }
    win->canvas = dcvs_create(64u * 1024u);
    win->gui = dgui_create();
    if (!win->canvas || !win->gui) {
        if (win->canvas) dcvs_destroy(win->canvas);
        if (win->gui) dgui_destroy(win->gui);
        d_gfx_pass_destroy(win->pipeline, win->pass);
        d_gfx_target_destroy(win->pipeline, win->target);
        if (win->owns_pipeline) d_gfx_pipeline_destroy(win->pipeline);
        free(win);
        return NULL;
    }

    sdesc.x = local.x;
    sdesc.y = local.y;
    sdesc.width = local.width;
    sdesc.height = local.height;
    sdesc.mode = DWIN_MODE_WINDOWED;
    win->window = dsys_window_create(&sdesc);
    if (!win->window) {
        dcvs_destroy(win->canvas);
        dgui_destroy(win->gui);
        d_gfx_pass_destroy(win->pipeline, win->pass);
        d_gfx_target_destroy(win->pipeline, win->target);
        if (win->owns_pipeline) d_gfx_pipeline_destroy(win->pipeline);
        free(win);
        return NULL;
    }

    d_gui_window_list_add(win);
    return win;
}

void d_gui_window_destroy(d_gui_window* win) {
    if (!win) return;
    d_gui_window_list_remove(win);
    dsys_window_destroy(win->window);
    if (win->canvas) dcvs_destroy(win->canvas);
    if (win->gui) dgui_destroy(win->gui);
    if (win->pass) d_gfx_pass_destroy(win->pipeline, win->pass);
    if (win->target) d_gfx_target_destroy(win->pipeline, win->target);
    if (win->owns_pipeline && win->pipeline) {
        d_gfx_pipeline_destroy(win->pipeline);
    }
    free(win);
}

int d_gui_window_should_close(d_gui_window* win) {
    if (!win) return 1;
    return dsys_window_should_close(win->window);
}

void d_gui_window_set_root(d_gui_window* win, dgui_widget* root) {
    if (!win) return;
    win->root = root;
    if (win->gui) {
        win->gui->root = root;
        dgui_set_root(win->gui, root);
    }
}

d_gui_context* d_gui_window_get_gui(d_gui_window* win) {
    if (!win) return NULL;
    return win->gui;
}

void d_gui_window_frame(d_gui_window* win, float delta_time) {
    dgfx_viewport_t vp;
    const dgfx_cmd_buffer* buf;
    d_gfx_ir_command cmds[DGUI_MAX_IR_CMDS];
    u32 cmd_count;
    uint32_t clear_rgba;
    int32_t w = win ? (int32_t)win->desc.width : 0;
    int32_t h = win ? (int32_t)win->desc.height : 0;
    d_input_event iev;
    (void)delta_time;
    if (!win || !win->pass || !win->canvas || !win->gui) {
        return;
    }

    dsys_window_get_size(win->window, &w, &h);
    if (w <= 0) w = (int32_t)win->desc.width;
    if (h <= 0) h = (int32_t)win->desc.height;
    if (win->gui) {
        win->gui->surface_w = (int)w;
        win->gui->surface_h = (int)h;
    }

    d_input_begin_frame();
    while (d_input_poll(&iev)) {
        if (iev.type == D_INPUT_KEYDOWN || iev.type == D_INPUT_CHAR) {
            dgui_handle_key(win->gui, iev.param1);
        }
    }
    d_input_end_frame();

    dcvs_reset(win->canvas);
    vp.x = 0;
    vp.y = 0;
    vp.w = w;
    vp.h = h;
    dcvs_set_viewport(win->canvas, &vp);

    clear_rgba = d_gui_pack_color(win->gui->style ? &win->gui->style->bg : NULL);
    dcvs_clear(win->canvas, clear_rgba);
    if (win->root) {
        dgui_render(win->gui, win->canvas);
    }

    buf = dcvs_get_cmd_buffer(win->canvas);
    cmd_count = d_gui_decode_ir(buf, cmds, (u32)DGUI_MAX_IR_CMDS);

    d_gfx_pass_begin(win->pass);
    if (cmd_count > 0u) {
        d_gfx_pass_submit_ir(win->pass, cmds, cmd_count);
    }
    d_gfx_pass_end(win->pass);
    dsys_window_present(win->window);
}

d_gui_window* d_gui_window_get_first(void) {
    return g_gui_windows;
}

d_gui_window* d_gui_window_get_next(d_gui_window* current) {
    if (!current) return NULL;
    return current->next;
}

void d_gui_tick_all_windows(float delta_time) {
    d_gui_window* win = g_gui_windows;
    while (win) {
        if (!d_gui_window_should_close(win)) {
            d_gui_window_frame(win, delta_time);
        }
        win = win->next;
    }
}

int d_gui_any_window_alive(void) {
    d_gui_window* win = g_gui_windows;
    while (win) {
        if (!d_gui_window_should_close(win)) {
            return 1;
        }
        win = win->next;
    }
    return 0;
}

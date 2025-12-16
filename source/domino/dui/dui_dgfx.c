/*
FILE: source/domino/dui/dui_dgfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/dui_dgfx
RESPONSIBILITY: Implements the DUI DGFX backend (renders widgets via DGFX primitives; uses DSYS event pump).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, `source/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: Single-threaded UI driver expected.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Presentation-only; visuals driven by explicit inputs + integer frame counters.
VERSIONING / ABI / DATA FORMAT NOTES: `dui_api_v1` vtable; schema/state TLV are skip-unknown.
EXTENSION POINTS: Test/native handle extensions via query_interface.
*/
#include "dui/dui_api_v1.h"

#include <stdlib.h>
#include <string.h>

#include "dui_event_queue.h"
#include "dui_schema_parse.h"

#include "domino/gfx.h"
#include "domino/system/d_system.h"

/* Internal input event type (engine-private). */
#include "system/d_system_input.h"

typedef struct dui_context {
    dui_event_queue q;
    u32 quit_requested;
    u32 frame_counter;
} dui_context;

typedef struct dui_window {
    unsigned char* schema;
    u32 schema_len;
    unsigned char* state;
    u32 state_len;
    dui_schema_node* root;

    u32 focused_widget_id;
    u32 focused_is_valid;
} dui_window;

static dui_window* g_single_window = (dui_window*)0;

static dui_result dgfx_create_context(dui_context** out_ctx);
static void       dgfx_destroy_context(dui_context* ctx);
static dui_result dgfx_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win);
static void       dgfx_destroy_window(dui_window* win);
static dui_result dgfx_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len);
static dui_result dgfx_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len);
static dui_result dgfx_render(dui_window* win);
static dui_result dgfx_pump(dui_context* ctx);
static int        dgfx_poll_event(dui_context* ctx, dui_event_v1* out_ev);
static dui_result dgfx_request_quit(dui_context* ctx);

static dom_abi_result dgfx_query_interface(dom_iid iid, void** out_iface);

static const char* dgfx_backend_name(void) { return "dgfx"; }

static dui_caps dgfx_caps(void)
{
    return DUI_CAP_WINDOW |
           DUI_CAP_EVENT_PUMP |
           DUI_CAP_LABEL |
           DUI_CAP_BUTTON |
           DUI_CAP_CHECKBOX |
           DUI_CAP_LIST |
           DUI_CAP_TEXT_FIELD |
           DUI_CAP_PROGRESS |
           DUI_CAP_LAYOUT_ROW |
           DUI_CAP_LAYOUT_COLUMN |
           DUI_CAP_LAYOUT_STACK |
           DUI_CAP_FOCUS |
           DUI_CAP_KEYBOARD_NAV;
}

static dui_test_api_v1 g_test_api;
static dui_native_api_v1 g_native_api;

static dui_result dgfx_test_post_event(dui_context* ctx, const dui_event_v1* ev)
{
    if (!ctx || !ev) {
        return DUI_ERR_NULL;
    }
    if (dui_event_queue_push(&ctx->q, ev) != 0) {
        return DUI_ERR;
    }
    return DUI_OK;
}

static void* dgfx_get_native_window_handle(dui_window* win)
{
    (void)win;
    return d_system_get_native_window_handle();
}

static dom_abi_result dgfx_query_interface(dom_iid iid, void** out_iface)
{
    if (!out_iface) {
        return (dom_abi_result)DUI_ERR_NULL;
    }
    *out_iface = (void*)0;

    if (iid == DUI_IID_TEST_API_V1) {
        g_test_api.abi_version = DUI_API_ABI_VERSION;
        g_test_api.struct_size = (u32)sizeof(g_test_api);
        g_test_api.post_event = dgfx_test_post_event;
        *out_iface = (void*)&g_test_api;
        return 0;
    }
    if (iid == DUI_IID_NATIVE_API_V1) {
        g_native_api.abi_version = DUI_API_ABI_VERSION;
        g_native_api.struct_size = (u32)sizeof(g_native_api);
        g_native_api.get_native_window_handle = dgfx_get_native_window_handle;
        *out_iface = (void*)&g_native_api;
        return 0;
    }
    return (dom_abi_result)DUI_ERR_UNSUPPORTED;
}

static const dui_api_v1 g_dui_dgfx_api = {
    DOM_ABI_HEADER_INIT(DUI_API_ABI_VERSION, dui_api_v1),
    dgfx_query_interface,

    dgfx_backend_name,
    dgfx_caps,

    dgfx_create_context,
    dgfx_destroy_context,
    dgfx_create_window,
    dgfx_destroy_window,

    dgfx_set_schema_tlv,
    dgfx_set_state_tlv,

    dgfx_render,
    dgfx_pump,
    dgfx_poll_event,
    dgfx_request_quit
};

const void* dom_dui_dgfx_get_api(u32 requested_abi)
{
    if (requested_abi != DUI_API_ABI_VERSION) {
        return (const void*)0;
    }
    return (const void*)&g_dui_dgfx_api;
}

static int dgfx_node_visible(const dui_schema_node* n)
{
    if (!n) {
        return 0;
    }
    if (n->required_caps != 0u) {
        if ((dgfx_caps() & n->required_caps) != n->required_caps) {
            return 0;
        }
    }
    return 1;
}

static int dgfx_is_leaf_kind(u32 kind)
{
    switch ((dui_node_kind)kind) {
    case DUI_NODE_LABEL:
    case DUI_NODE_BUTTON:
    case DUI_NODE_CHECKBOX:
    case DUI_NODE_LIST:
    case DUI_NODE_TEXT_FIELD:
    case DUI_NODE_PROGRESS:
        return 1;
    default:
        break;
    }
    return 0;
}

static void dgfx_collect_focusables(const dui_schema_node* n, u32* out_ids, u32 cap, u32* io_count)
{
    const dui_schema_node* child;
    if (!n || !out_ids || !io_count) {
        return;
    }
    if (!dgfx_node_visible(n)) {
        return;
    }
    if (dgfx_is_leaf_kind(n->kind) && (n->flags & DUI_NODE_FLAG_FOCUSABLE)) {
        if (*io_count < cap) {
            out_ids[*io_count] = n->id;
            *io_count += 1u;
        }
    }
    child = n->first_child;
    while (child) {
        dgfx_collect_focusables(child, out_ids, cap, io_count);
        child = child->next_sibling;
    }
}

static u32 dgfx_next_focus_id(dui_window* win, int dir)
{
    u32 ids[64];
    u32 count;
    u32 i;
    if (!win || !win->root) {
        return 0u;
    }
    count = 0u;
    memset(ids, 0, sizeof(ids));
    dgfx_collect_focusables(win->root, ids, 64u, &count);
    if (count == 0u) {
        return 0u;
    }

    if (!win->focused_is_valid) {
        win->focused_is_valid = 1u;
        return ids[0];
    }
    for (i = 0u; i < count; ++i) {
        if (ids[i] == win->focused_widget_id) {
            if (dir >= 0) {
                return ids[(i + 1u) % count];
            }
            return ids[(i + count - 1u) % count];
        }
    }
    return ids[0];
}

static int dgfx_hit_test_leaf(const dui_schema_node* n, i32 px, i32 py, u32* out_id)
{
    const dui_schema_node* child;
    if (!n || !out_id) {
        return 0;
    }
    if (!dgfx_node_visible(n)) {
        return 0;
    }
    if (dgfx_is_leaf_kind(n->kind)) {
        if (px >= n->x && py >= n->y && px < (n->x + n->w) && py < (n->y + n->h)) {
            *out_id = n->id;
            return 1;
        }
    }
    child = n->first_child;
    while (child) {
        if (dgfx_hit_test_leaf(child, px, py, out_id)) {
            return 1;
        }
        child = child->next_sibling;
    }
    return 0;
}

static void dgfx_emit_quit(dui_context* ctx)
{
    dui_event_v1 ev;
    if (!ctx) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.abi_version = DUI_API_ABI_VERSION;
    ev.struct_size = (u32)sizeof(ev);
    ev.type = (u32)DUI_EVENT_QUIT;
    (void)dui_event_queue_push(&ctx->q, &ev);
}

static void dgfx_emit_action(dui_context* ctx, u32 widget_id, u32 action_id, u32 item_id)
{
    dui_event_v1 ev;
    if (!ctx) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.abi_version = DUI_API_ABI_VERSION;
    ev.struct_size = (u32)sizeof(ev);
    ev.type = (u32)DUI_EVENT_ACTION;
    ev.u.action.widget_id = widget_id;
    ev.u.action.action_id = action_id;
    ev.u.action.item_id = item_id;
    (void)dui_event_queue_push(&ctx->q, &ev);
}

static void dgfx_emit_value_text(dui_context* ctx, u32 widget_id, const char* text, u32 text_len)
{
    dui_event_v1 ev;
    u32 n;
    if (!ctx) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.abi_version = DUI_API_ABI_VERSION;
    ev.struct_size = (u32)sizeof(ev);
    ev.type = (u32)DUI_EVENT_VALUE_CHANGED;
    ev.u.value.widget_id = widget_id;
    ev.u.value.value_type = (u32)DUI_VALUE_TEXT;
    n = text_len;
    if (n > 255u) {
        n = 255u;
    }
    ev.u.value.text_len = n;
    if (n > 0u && text) {
        memcpy(ev.u.value.text, text, (size_t)n);
    }
    (void)dui_event_queue_push(&ctx->q, &ev);
}

static void dgfx_emit_value_u32(dui_context* ctx, u32 widget_id, u32 value_type, u32 v, u32 item_id)
{
    dui_event_v1 ev;
    if (!ctx) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.abi_version = DUI_API_ABI_VERSION;
    ev.struct_size = (u32)sizeof(ev);
    ev.type = (u32)DUI_EVENT_VALUE_CHANGED;
    ev.u.value.widget_id = widget_id;
    ev.u.value.value_type = value_type;
    ev.u.value.v_u32 = v;
    ev.u.value.item_id = item_id;
    (void)dui_event_queue_push(&ctx->q, &ev);
}

static int dgfx_state_get_widget_text(const dui_window* win, u32 bind_id, char* out_text, u32 out_cap, u32* out_len)
{
    if (!win || !win->state) {
        if (out_len) {
            *out_len = 0u;
        }
        if (out_text && out_cap > 0u) {
            out_text[0] = '\0';
        }
        return 0;
    }
    return dui_state_get_text(win->state, win->state_len, bind_id, out_text, out_cap, out_len);
}

static void dgfx_handle_key_text_field(dui_context* ctx, dui_window* win, const dui_schema_node* n, d_sys_key key)
{
    char buf[256];
    u32 len;
    char c;
    if (!ctx || !win || !n) {
        return;
    }
    buf[0] = '\0';
    len = 0u;
    (void)dgfx_state_get_widget_text(win, n->bind_id, buf, (u32)sizeof(buf), &len);

    if (key == D_SYS_KEY_BACKSPACE) {
        if (len > 0u) {
            len -= 1u;
            buf[len] = '\0';
        }
        dgfx_emit_value_text(ctx, n->id, buf, len);
        return;
    }

    c = '\0';
    switch (key) {
    case D_SYS_KEY_0: c = '0'; break;
    case D_SYS_KEY_1: c = '1'; break;
    case D_SYS_KEY_2: c = '2'; break;
    case D_SYS_KEY_3: c = '3'; break;
    case D_SYS_KEY_4: c = '4'; break;
    case D_SYS_KEY_5: c = '5'; break;
    case D_SYS_KEY_6: c = '6'; break;
    case D_SYS_KEY_7: c = '7'; break;
    case D_SYS_KEY_8: c = '8'; break;
    case D_SYS_KEY_9: c = '9'; break;
    case D_SYS_KEY_PERIOD: c = '.'; break;
    default:
        break;
    }
    if (c != '\0') {
        if (len < 255u) {
            buf[len++] = c;
            buf[len] = '\0';
        }
        dgfx_emit_value_text(ctx, n->id, buf, len);
    }
}

static int dgfx_find_list_index_by_item_id(const dui_window* win, u32 bind_id, u32 want_item_id, u32* out_index)
{
    u32 count;
    u32 i;
    if (!out_index) {
        return 0;
    }
    *out_index = 0u;
    if (!win || !win->state) {
        return 0;
    }
    if (!dui_state_get_list_item_count(win->state, win->state_len, bind_id, &count)) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        u32 item_id;
        char tmp[8];
        u32 tmp_len;
        if (dui_state_get_list_item_at(win->state, win->state_len, bind_id, i, &item_id, tmp, (u32)sizeof(tmp), &tmp_len)) {
            if (item_id == want_item_id) {
                *out_index = i;
                return 1;
            }
        }
    }
    return 0;
}

static void dgfx_handle_list_move(dui_context* ctx, dui_window* win, const dui_schema_node* n, int dir)
{
    u32 selected_id;
    u32 count;
    u32 idx;
    u32 next_idx;
    u32 next_id;
    char tmp[8];
    u32 tmp_len;

    if (!ctx || !win || !n || !win->state) {
        return;
    }
    selected_id = 0u;
    (void)dui_state_get_list_selected_item_id(win->state, win->state_len, n->bind_id, &selected_id);
    if (!dui_state_get_list_item_count(win->state, win->state_len, n->bind_id, &count) || count == 0u) {
        return;
    }
    idx = 0u;
    (void)dgfx_find_list_index_by_item_id(win, n->bind_id, selected_id, &idx);
    if (dir >= 0) {
        next_idx = (idx + 1u < count) ? (idx + 1u) : idx;
    } else {
        next_idx = (idx > 0u) ? (idx - 1u) : 0u;
    }
    next_id = 0u;
    if (dui_state_get_list_item_at(win->state, win->state_len, n->bind_id, next_idx, &next_id, tmp, (u32)sizeof(tmp), &tmp_len)) {
        dgfx_emit_value_u32(ctx, n->id, (u32)DUI_VALUE_LIST, next_idx, next_id);
    }
}

static void dgfx_handle_click(dui_context* ctx, dui_window* win, i32 x, i32 y)
{
    u32 hit_id;
    dui_schema_node* hit;
    if (!ctx || !win || !win->root) {
        return;
    }
    hit_id = 0u;
    if (!dgfx_hit_test_leaf(win->root, x, y, &hit_id)) {
        return;
    }
    hit = dui_schema_find_by_id(win->root, hit_id);
    if (!hit) {
        return;
    }
    win->focused_widget_id = hit->id;
    win->focused_is_valid = 1u;

    if (hit->kind == (u32)DUI_NODE_BUTTON) {
        dgfx_emit_action(ctx, hit->id, hit->action_id, 0u);
    } else if (hit->kind == (u32)DUI_NODE_CHECKBOX) {
        u32 v = 0u;
        (void)dui_state_get_u32(win->state, win->state_len, hit->bind_id, &v);
        v = (v == 0u) ? 1u : 0u;
        dgfx_emit_value_u32(ctx, hit->id, (u32)DUI_VALUE_BOOL, v, 0u);
    } else if (hit->kind == (u32)DUI_NODE_LIST) {
        const i32 pad = 6;
        const i32 item_h = 18;
        i32 rel_y = y - (hit->y + pad);
        u32 idx = 0u;
        u32 count = 0u;
        if (rel_y < 0) {
            rel_y = 0;
        }
        idx = (u32)(rel_y / item_h);
        if (dui_state_get_list_item_count(win->state, win->state_len, hit->bind_id, &count) && idx < count) {
            u32 item_id = 0u;
            char txt[8];
            u32 txt_len;
            if (dui_state_get_list_item_at(win->state, win->state_len, hit->bind_id, idx, &item_id, txt, (u32)sizeof(txt), &txt_len)) {
                dgfx_emit_value_u32(ctx, hit->id, (u32)DUI_VALUE_LIST, idx, item_id);
            }
        }
    }
}

static void dgfx_handle_key(dui_context* ctx, dui_window* win, d_sys_key key)
{
    dui_schema_node* n;
    if (!ctx || !win || !win->root) {
        return;
    }
    if (key == D_SYS_KEY_ESCAPE) {
        dgfx_emit_quit(ctx);
        return;
    }
    if (key == D_SYS_KEY_UP) {
        n = dui_schema_find_by_id(win->root, win->focused_widget_id);
        if (n && n->kind == (u32)DUI_NODE_LIST) {
            dgfx_handle_list_move(ctx, win, n, -1);
        } else {
            win->focused_widget_id = dgfx_next_focus_id(win, -1);
        }
        return;
    }
    if (key == D_SYS_KEY_DOWN) {
        n = dui_schema_find_by_id(win->root, win->focused_widget_id);
        if (n && n->kind == (u32)DUI_NODE_LIST) {
            dgfx_handle_list_move(ctx, win, n, +1);
        } else {
            win->focused_widget_id = dgfx_next_focus_id(win, +1);
        }
        return;
    }
    if (key == D_SYS_KEY_ENTER) {
        n = dui_schema_find_by_id(win->root, win->focused_widget_id);
        if (!n) {
            return;
        }
        if (n->kind == (u32)DUI_NODE_BUTTON) {
            dgfx_emit_action(ctx, n->id, n->action_id, 0u);
        } else if (n->kind == (u32)DUI_NODE_LIST) {
            u32 selected_id = 0u;
            (void)dui_state_get_list_selected_item_id(win->state, win->state_len, n->bind_id, &selected_id);
            dgfx_emit_action(ctx, n->id, n->action_id, selected_id);
        }
        return;
    }
    if (key == D_SYS_KEY_SPACE) {
        n = dui_schema_find_by_id(win->root, win->focused_widget_id);
        if (n && n->kind == (u32)DUI_NODE_CHECKBOX) {
            u32 v = 0u;
            (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
            v = (v == 0u) ? 1u : 0u;
            dgfx_emit_value_u32(ctx, n->id, (u32)DUI_VALUE_BOOL, v, 0u);
        }
        return;
    }

    n = dui_schema_find_by_id(win->root, win->focused_widget_id);
    if (n && n->kind == (u32)DUI_NODE_TEXT_FIELD) {
        dgfx_handle_key_text_field(ctx, win, n, key);
    }
}

static dui_result dgfx_create_context(dui_context** out_ctx)
{
    dui_context* ctx;
    if (!out_ctx) {
        return DUI_ERR_NULL;
    }
    *out_ctx = (dui_context*)0;

    ctx = (dui_context*)malloc(sizeof(dui_context));
    if (!ctx) {
        return DUI_ERR;
    }
    memset(ctx, 0, sizeof(*ctx));
    dui_event_queue_init(&ctx->q);
    ctx->quit_requested = 0u;
    ctx->frame_counter = 0u;
    *out_ctx = ctx;
    return DUI_OK;
}

static void dgfx_destroy_context(dui_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

static dui_result dgfx_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win)
{
    dui_window* win;
    const char* sys_backend;
    if (!ctx || !out_win) {
        return DUI_ERR_NULL;
    }
    *out_win = (dui_window*)0;

    if (g_single_window) {
        return DUI_ERR;
    }

    win = (dui_window*)malloc(sizeof(dui_window));
    if (!win) {
        return DUI_ERR;
    }
    memset(win, 0, sizeof(*win));

    sys_backend = "win32";
    if (desc && (desc->flags & DUI_WINDOW_FLAG_HEADLESS)) {
        sys_backend = "headless";
    }
    if (!d_system_init(sys_backend)) {
        free(win);
        return DUI_ERR_BACKEND_UNAVAILABLE;
    }
    if (!d_gfx_init("soft")) {
        d_system_shutdown();
        free(win);
        return DUI_ERR_BACKEND_UNAVAILABLE;
    }

    win->focused_widget_id = 0u;
    win->focused_is_valid = 0u;

    g_single_window = win;
    *out_win = win;
    return DUI_OK;
}

static void dgfx_destroy_window(dui_window* win)
{
    if (!win) {
        return;
    }

    if (win->schema) {
        free(win->schema);
        win->schema = (unsigned char*)0;
        win->schema_len = 0u;
    }
    if (win->state) {
        free(win->state);
        win->state = (unsigned char*)0;
        win->state_len = 0u;
    }
    if (win->root) {
        dui_schema_free(win->root);
        win->root = (dui_schema_node*)0;
    }

    d_gfx_shutdown();
    d_system_shutdown();

    g_single_window = (dui_window*)0;
    free(win);
}

static dui_result dgfx_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len)
{
    dui_result perr;
    unsigned char* copy;
    if (!win || (!schema_tlv && schema_len != 0u)) {
        return DUI_ERR_NULL;
    }
    if (win->schema) {
        free(win->schema);
        win->schema = (unsigned char*)0;
        win->schema_len = 0u;
    }
    if (win->root) {
        dui_schema_free(win->root);
        win->root = (dui_schema_node*)0;
    }
    if (!schema_tlv || schema_len == 0u) {
        return DUI_OK;
    }

    copy = (unsigned char*)malloc((size_t)schema_len);
    if (!copy) {
        return DUI_ERR;
    }
    memcpy(copy, schema_tlv, (size_t)schema_len);
    win->schema = copy;
    win->schema_len = schema_len;

    perr = DUI_OK;
    win->root = dui_schema_parse_first_form_root(copy, schema_len, &perr);
    return (win->root) ? DUI_OK : perr;
}

static dui_result dgfx_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len)
{
    unsigned char* copy;
    if (!win || (!state_tlv && state_len != 0u)) {
        return DUI_ERR_NULL;
    }
    if (win->state) {
        free(win->state);
        win->state = (unsigned char*)0;
        win->state_len = 0u;
    }
    if (!state_tlv || state_len == 0u) {
        return DUI_OK;
    }
    copy = (unsigned char*)malloc((size_t)state_len);
    if (!copy) {
        return DUI_ERR;
    }
    memcpy(copy, state_tlv, (size_t)state_len);
    win->state = copy;
    win->state_len = state_len;
    return DUI_OK;
}

static void dgfx_draw_rect(d_gfx_cmd_buffer* buf, i32 x, i32 y, i32 w, i32 h, d_gfx_color c)
{
    d_gfx_draw_rect_cmd r;
    r.x = x;
    r.y = y;
    r.w = w;
    r.h = h;
    r.color = c;
    d_gfx_cmd_draw_rect(buf, &r);
}

static void dgfx_draw_text(d_gfx_cmd_buffer* buf, i32 x, i32 y, const char* text, d_gfx_color c)
{
    d_gfx_draw_text_cmd t;
    t.x = x;
    t.y = y;
    t.text = text ? text : "";
    t.color = c;
    d_gfx_cmd_draw_text(buf, &t);
}

static void dgfx_render_leaf(const dui_window* win, const dui_schema_node* n, d_gfx_cmd_buffer* buf)
{
    d_gfx_color bg = { 0xffu, 0x22u, 0x22u, 0x22u };
    d_gfx_color panel = { 0xffu, 0x2au, 0x2au, 0x2au };
    d_gfx_color btn = { 0xffu, 0x3au, 0x6eu, 0xa5u };
    d_gfx_color hi = { 0xffu, 0xe8u, 0xc4u, 0x40u };
    d_gfx_color fg = { 0xffu, 0xffu, 0xffu, 0xffu };
    char text[256];
    u32 text_len;

    if (!win || !n || !buf) {
        return;
    }
    if (!dgfx_node_visible(n)) {
        return;
    }
    if (!dgfx_is_leaf_kind(n->kind)) {
        return;
    }

    text[0] = '\0';
    text_len = 0u;

    switch ((dui_node_kind)n->kind) {
    case DUI_NODE_LABEL:
        (void)dgfx_state_get_widget_text(win, n->bind_id, text, (u32)sizeof(text), &text_len);
        if (!text[0] && n->text) {
            strncpy(text, n->text, sizeof(text) - 1u);
            text[sizeof(text) - 1u] = '\0';
        }
        dgfx_draw_text(buf, n->x + 4, n->y + 4, text, fg);
        break;
    case DUI_NODE_BUTTON:
        dgfx_draw_rect(buf, n->x, n->y, n->w, n->h, btn);
        (void)dgfx_state_get_widget_text(win, n->bind_id, text, (u32)sizeof(text), &text_len);
        if (!text[0] && n->text) {
            strncpy(text, n->text, sizeof(text) - 1u);
            text[sizeof(text) - 1u] = '\0';
        }
        dgfx_draw_text(buf, n->x + 6, n->y + 6, text, fg);
        if (win->focused_is_valid && win->focused_widget_id == n->id) {
            dgfx_draw_rect(buf, n->x - 2, n->y - 2, n->w + 4, n->h + 4, hi);
        }
        break;
    case DUI_NODE_CHECKBOX: {
        u32 v = 0u;
        const i32 box = 14;
        (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
        dgfx_draw_rect(buf, n->x, n->y, n->w, n->h, panel);
        dgfx_draw_rect(buf, n->x + 6, n->y + 5, box, box, bg);
        if (v) {
            dgfx_draw_rect(buf, n->x + 9, n->y + 8, box - 6, box - 6, hi);
        }
        dgfx_draw_text(buf, n->x + 6 + box + 6, n->y + 6, n->text ? n->text : "", fg);
        if (win->focused_is_valid && win->focused_widget_id == n->id) {
            dgfx_draw_rect(buf, n->x - 2, n->y - 2, n->w + 4, n->h + 4, hi);
        }
        break;
    }
    case DUI_NODE_TEXT_FIELD:
        dgfx_draw_rect(buf, n->x, n->y, n->w, n->h, panel);
        (void)dgfx_state_get_widget_text(win, n->bind_id, text, (u32)sizeof(text), &text_len);
        dgfx_draw_text(buf, n->x + 6, n->y + 6, text, fg);
        if (win->focused_is_valid && win->focused_widget_id == n->id) {
            dgfx_draw_rect(buf, n->x - 2, n->y - 2, n->w + 4, n->h + 4, hi);
        }
        break;
    case DUI_NODE_PROGRESS: {
        u32 v = 0u;
        i32 fill_w;
        (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
        if (v > 1000u) v = 1000u;
        dgfx_draw_rect(buf, n->x, n->y, n->w, n->h, panel);
        fill_w = (i32)((u64)n->w * (u64)v / 1000u);
        dgfx_draw_rect(buf, n->x, n->y, fill_w, n->h, btn);
        break;
    }
    case DUI_NODE_LIST: {
        const i32 pad = 6;
        const i32 item_h = 18;
        u32 count = 0u;
        u32 selected_item_id = 0u;
        u32 i;
        i32 iy;

        dgfx_draw_rect(buf, n->x, n->y, n->w, n->h, panel);
        (void)dui_state_get_list_item_count(win->state, win->state_len, n->bind_id, &count);
        (void)dui_state_get_list_selected_item_id(win->state, win->state_len, n->bind_id, &selected_item_id);
        iy = n->y + pad;
        for (i = 0u; i < count; ++i) {
            u32 item_id = 0u;
            u32 item_len = 0u;
            char item_text[128];
            item_text[0] = '\0';
            if (!dui_state_get_list_item_at(win->state, win->state_len, n->bind_id, i, &item_id, item_text, (u32)sizeof(item_text), &item_len)) {
                continue;
            }
            if (item_id == selected_item_id) {
                dgfx_draw_rect(buf, n->x + 2, iy - 2, n->w - 4, item_h, btn);
            }
            dgfx_draw_text(buf, n->x + pad, iy, item_text, fg);
            iy += item_h;
            if (iy > n->y + n->h - item_h) {
                break;
            }
        }
        if (win->focused_is_valid && win->focused_widget_id == n->id) {
            dgfx_draw_rect(buf, n->x - 2, n->y - 2, n->w + 4, n->h + 4, hi);
        }
        break;
    }
    default:
        break;
    }
}

static void dgfx_render_tree(const dui_window* win, const dui_schema_node* n, d_gfx_cmd_buffer* buf)
{
    const dui_schema_node* child;
    if (!n || !buf) {
        return;
    }
    if (dgfx_is_leaf_kind(n->kind)) {
        dgfx_render_leaf(win, n, buf);
    }
    child = n->first_child;
    while (child) {
        dgfx_render_tree(win, child, buf);
        child = child->next_sibling;
    }
}

static dui_result dgfx_render(dui_window* win)
{
    d_gfx_cmd_buffer* buf;
    d_gfx_color clear = { 0xffu, 0x10u, 0x10u, 0x10u };
    i32 w = 800;
    i32 h = 600;
    if (!win) {
        return DUI_ERR_NULL;
    }
    if (!win->root) {
        return DUI_OK;
    }
    d_gfx_get_surface_size(&w, &h);
    if (w <= 0) w = 800;
    if (h <= 0) h = 600;

    dui_schema_layout(win->root, 0, 0, w, h);

    buf = d_gfx_cmd_buffer_begin();
    d_gfx_cmd_clear(buf, clear);
    dgfx_render_tree(win, win->root, buf);
    d_gfx_cmd_buffer_end(buf);
    d_gfx_submit(buf);
    d_gfx_present();
    return DUI_OK;
}

static dui_result dgfx_pump(dui_context* ctx)
{
    d_sys_event ev;
    if (!ctx) {
        return DUI_ERR_NULL;
    }
    if (ctx->quit_requested) {
        dgfx_emit_quit(ctx);
        ctx->quit_requested = 0u;
    }
    if (!g_single_window) {
        return DUI_OK;
    }
    if (d_system_pump_events() != 0) {
        dgfx_emit_quit(ctx);
        return DUI_OK;
    }
    while (d_system_poll_event(&ev) > 0) {
        if (ev.type == D_SYS_EVENT_QUIT) {
            dgfx_emit_quit(ctx);
            return DUI_OK;
        }
        if (ev.type == D_SYS_EVENT_MOUSE_BUTTON_DOWN) {
            if (ev.u.mouse.button == 1u) {
                dgfx_handle_click(ctx, g_single_window, ev.u.mouse.x, ev.u.mouse.y);
            }
        }
        if (ev.type == D_SYS_EVENT_KEY_DOWN) {
            dgfx_handle_key(ctx, g_single_window, ev.u.key.key);
        }
    }
    ctx->frame_counter += 1u;
    return DUI_OK;
}

static int dgfx_poll_event(dui_context* ctx, dui_event_v1* out_ev)
{
    if (!ctx || !out_ev) {
        return -1;
    }
    return dui_event_queue_pop(&ctx->q, out_ev);
}

static dui_result dgfx_request_quit(dui_context* ctx)
{
    if (!ctx) {
        return DUI_ERR_NULL;
    }
    ctx->quit_requested = 1u;
    return DUI_OK;
}

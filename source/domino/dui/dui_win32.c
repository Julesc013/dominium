/*
FILE: source/domino/dui/dui_win32.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/dui_win32
RESPONSIBILITY: Implements the DUI Win32 native backend (common controls; message pump; schema/state driven).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, `source/domino/**`, Win32 SDK headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: Single-threaded UI driver expected.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Presentation-only; UI does not influence deterministic simulation.
VERSIONING / ABI / DATA FORMAT NOTES: `dui_api_v1` vtable; schema/state TLV are skip-unknown.
EXTENSION POINTS: Test/native handle extensions via query_interface.
*/
#include "dui/dui_api_v1.h"
#include "dui/dui_win32.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commctrl.h>
#endif

#include "dui_event_queue.h"
#include "dui_schema_parse.h"

typedef struct dui_context {
    dui_event_queue q;
    u32 quit_requested;
    u32 quit_emitted;
    domui_action_fn action_dispatch;
    void* action_user_ctx;
    struct dui_window* primary_window;
} dui_context;

typedef struct dui_window {
#if defined(_WIN32)
    HWND hwnd;
    HFONT font;
#endif
    dui_context* ctx;
    unsigned char* schema;
    u32 schema_len;
    unsigned char* state;
    u32 state_len;
    dui_schema_node* root;
    u32 suppress_events;
    int relayout_pending;
    int pending_w;
    int pending_h;
} dui_window;

typedef struct dui_splitter_data {
#if defined(_WIN32)
    dui_window* win;
    dui_schema_node* node;
    int dragging;
    int drag_offset;
#else
    void* unused;
#endif
} dui_splitter_data;

typedef struct dui_scrollpanel_data {
#if defined(_WIN32)
    dui_window* win;
    dui_schema_node* node;
#else
    void* unused;
#endif
} dui_scrollpanel_data;

static dui_result win32_create_context(dui_context** out_ctx);
static void       win32_destroy_context(dui_context* ctx);
static dui_result win32_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win);
static void       win32_destroy_window(dui_window* win);
static dui_result win32_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len);
static dui_result win32_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len);
static dui_result win32_render(dui_window* win);
static dui_result win32_pump(dui_context* ctx);
static int        win32_poll_event(dui_context* ctx, dui_event_v1* out_ev);
static dui_result win32_request_quit(dui_context* ctx);
static void       win32_relayout(dui_window* win);
static int        win32_splitter_clamp_pos(const dui_schema_node* n, int axis_len, int pos);

static dom_abi_result win32_query_interface(dom_iid iid, void** out_iface);
static void win32_set_action_dispatch(dui_context* ctx, domui_action_fn fn, void* user_ctx);

static const char* win32_backend_name(void) { return "win32"; }

static dui_caps win32_caps(void)
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
           DUI_CAP_KEYBOARD_NAV |
           DUI_CAP_IME;
}

static dui_test_api_v1 g_test_api;
static dui_native_api_v1 g_native_api;
static dui_action_api_v1 g_action_api;

static dui_result win32_test_post_event(dui_context* ctx, const dui_event_v1* ev)
{
    if (!ctx || !ev) {
        return DUI_ERR_NULL;
    }
    if (dui_event_queue_push(&ctx->q, ev) != 0) {
        return DUI_ERR;
    }
    return DUI_OK;
}

static void* win32_get_native_window_handle(dui_window* win)
{
#if defined(_WIN32)
    return win ? (void*)win->hwnd : (void*)0;
#else
    (void)win;
    return (void*)0;
#endif
}

static void win32_set_action_dispatch(dui_context* ctx, domui_action_fn fn, void* user_ctx)
{
    if (!ctx) {
        return;
    }
    ctx->action_dispatch = fn;
    ctx->action_user_ctx = user_ctx;
}

static dom_abi_result win32_query_interface(dom_iid iid, void** out_iface)
{
    if (!out_iface) {
        return (dom_abi_result)DUI_ERR_NULL;
    }
    *out_iface = (void*)0;

    if (iid == DUI_IID_TEST_API_V1) {
        g_test_api.abi_version = DUI_API_ABI_VERSION;
        g_test_api.struct_size = (u32)sizeof(g_test_api);
        g_test_api.post_event = win32_test_post_event;
        *out_iface = (void*)&g_test_api;
        return 0;
    }
    if (iid == DUI_IID_NATIVE_API_V1) {
        g_native_api.abi_version = DUI_API_ABI_VERSION;
        g_native_api.struct_size = (u32)sizeof(g_native_api);
        g_native_api.get_native_window_handle = win32_get_native_window_handle;
        *out_iface = (void*)&g_native_api;
        return 0;
    }
    if (iid == DUI_IID_ACTION_API_V1) {
        g_action_api.abi_version = DUI_API_ABI_VERSION;
        g_action_api.struct_size = (u32)sizeof(g_action_api);
        g_action_api.set_action_dispatch = win32_set_action_dispatch;
        *out_iface = (void*)&g_action_api;
        return 0;
    }
    return (dom_abi_result)DUI_ERR_UNSUPPORTED;
}

static const dui_api_v1 g_dui_win32_api = {
    DOM_ABI_HEADER_INIT(DUI_API_ABI_VERSION, dui_api_v1),
    win32_query_interface,

    win32_backend_name,
    win32_caps,

    win32_create_context,
    win32_destroy_context,
    win32_create_window,
    win32_destroy_window,

    win32_set_schema_tlv,
    win32_set_state_tlv,

    win32_render,
    win32_pump,
    win32_poll_event,
    win32_request_quit
};

const void* dom_dui_win32_get_api(u32 requested_abi)
{
    if (requested_abi != DUI_API_ABI_VERSION) {
        return (const void*)0;
    }
    return (const void*)&g_dui_win32_api;
}

#if defined(_WIN32)

#if defined(_WIN64)
#define DUI_SET_WND_PTR(hwnd, ptr) SetWindowLongPtr((hwnd), GWLP_USERDATA, (LONG_PTR)(ptr))
#define DUI_GET_WND_PTR(hwnd) ((dui_window*)GetWindowLongPtr((hwnd), GWLP_USERDATA))
#else
#define DUI_SET_WND_PTR(hwnd, ptr) SetWindowLong((hwnd), GWL_USERDATA, (LONG)(ptr))
#define DUI_GET_WND_PTR(hwnd) ((dui_window*)GetWindowLong((hwnd), GWL_USERDATA))
#endif

#define DUI_WIN32_RELAYOUT_MSG (WM_APP + 42)

typedef struct dui_win32_batch_state {
    HWND hwnd;
    u32 depth;
    HDWP hdwp;
    struct dui_win32_batch_state* next;
} dui_win32_batch_state;

static dui_win32_batch_state* g_win32_batch_states = 0;

static dui_win32_batch_state* win32_batch_find(HWND hwnd)
{
    dui_win32_batch_state* it = g_win32_batch_states;
    while (it) {
        if (it->hwnd == hwnd) {
            return it;
        }
        it = it->next;
    }
    return 0;
}

static dui_win32_batch_state* win32_batch_get(HWND hwnd)
{
    dui_win32_batch_state* state = win32_batch_find(hwnd);
    if (state) {
        return state;
    }
    state = (dui_win32_batch_state*)malloc(sizeof(dui_win32_batch_state));
    if (!state) {
        return 0;
    }
    memset(state, 0, sizeof(*state));
    state->hwnd = hwnd;
    state->next = g_win32_batch_states;
    g_win32_batch_states = state;
    return state;
}

void dui_win32_begin_batch(HWND parent)
{
    dui_win32_batch_state* state;
    if (!parent) {
        return;
    }
    state = win32_batch_get(parent);
    if (!state) {
        return;
    }
    if (state->depth == 0u) {
        SendMessageA(parent, WM_SETREDRAW, (WPARAM)FALSE, 0);
        state->hdwp = BeginDeferWindowPos(64);
    }
    state->depth += 1u;
}

void dui_win32_end_batch(HWND parent)
{
    dui_win32_batch_state* state;
    if (!parent) {
        return;
    }
    state = win32_batch_find(parent);
    if (!state || state->depth == 0u) {
        return;
    }
    state->depth -= 1u;
    if (state->depth == 0u) {
        if (state->hdwp) {
            (void)EndDeferWindowPos(state->hdwp);
            state->hdwp = (HDWP)0;
        }
        SendMessageA(parent, WM_SETREDRAW, (WPARAM)TRUE, 0);
        RedrawWindow(parent, NULL, NULL, RDW_INVALIDATE | RDW_ALLCHILDREN);
    }
}

static const char* dui_win32_class_name(void)
{
    return "DominiumDUIWindow";
}

static const char* dui_win32_splitter_class_name(void)
{
    return "DominiumDUISplitter";
}

static const char* dui_win32_scrollpanel_class_name(void)
{
    return "DominiumDUIScrollPanel";
}

static void win32_emit_quit(dui_context* ctx)
{
    dui_event_v1 ev;
    if (!ctx) {
        return;
    }
    if (ctx->quit_emitted) {
        return;
    }
    ctx->quit_emitted = 1u;
    memset(&ev, 0, sizeof(ev));
    ev.abi_version = DUI_API_ABI_VERSION;
    ev.struct_size = (u32)sizeof(ev);
    ev.type = (u32)DUI_EVENT_QUIT;
    (void)dui_event_queue_push(&ctx->q, &ev);
}

static domui_value win32_domui_value_none(void)
{
    domui_value v;
    memset(&v, 0, sizeof(v));
    v.type = DOMUI_VALUE_NONE;
    return v;
}

static domui_value win32_domui_value_u32(domui_u32 v)
{
    domui_value out = win32_domui_value_none();
    out.type = DOMUI_VALUE_U32;
    out.u.v_u32 = v;
    return out;
}

static domui_value win32_domui_value_i32(int v)
{
    domui_value out = win32_domui_value_none();
    out.type = DOMUI_VALUE_I32;
    out.u.v_i32 = v;
    return out;
}

static domui_value win32_domui_value_bool(int v)
{
    domui_value out = win32_domui_value_none();
    out.type = DOMUI_VALUE_BOOL;
    out.u.v_bool = v ? 1 : 0;
    return out;
}

static domui_value win32_domui_value_str(const char* text, domui_u32 len)
{
    domui_value out = win32_domui_value_none();
    out.type = DOMUI_VALUE_STR;
    out.u.v_str.ptr = text;
    out.u.v_str.len = len;
    return out;
}

static void win32_dispatch_domui_event(dui_context* ctx,
                                       domui_action_id action_id,
                                       domui_widget_id widget_id,
                                       domui_event_type type,
                                       domui_value a,
                                       domui_value b,
                                       void* backend_ext)
{
    domui_event ev;
    if (!ctx || !ctx->action_dispatch || action_id == 0u) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.action_id = action_id;
    ev.widget_id = widget_id;
    ev.type = type;
    ev.modifiers = 0u;
    ev.a = a;
    ev.b = b;
    ev.backend_ext = backend_ext;
    ctx->action_dispatch(ctx->action_user_ctx, &ev);
}

static void win32_emit_action_event(dui_context* ctx,
                                    u32 widget_id,
                                    u32 action_id,
                                    domui_event_type type,
                                    u32 item_id,
                                    void* backend_ext)
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

    if (type != DOMUI_EVENT_CUSTOM) {
        domui_value a = win32_domui_value_none();
        domui_value b = win32_domui_value_none();
        if (item_id != 0u || type == DOMUI_EVENT_TAB_CHANGE) {
            a = win32_domui_value_u32(item_id);
        }
        win32_dispatch_domui_event(ctx, action_id, widget_id, type, a, b, backend_ext);
    }
}

static void win32_emit_value_u32(dui_context* ctx,
                                 u32 widget_id,
                                 u32 action_id,
                                 u32 value_type,
                                 u32 v,
                                 u32 item_id,
                                 void* backend_ext)
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

    {
        domui_value a = win32_domui_value_none();
        domui_value b = win32_domui_value_none();
        if (value_type == (u32)DUI_VALUE_BOOL) {
            a = win32_domui_value_bool(v ? 1 : 0);
        } else if (value_type == (u32)DUI_VALUE_LIST) {
            a = win32_domui_value_u32(v);
            b = win32_domui_value_u32(item_id);
        } else if (value_type == (u32)DUI_VALUE_I32) {
            a = win32_domui_value_i32((int)v);
        } else {
            a = win32_domui_value_u32(v);
        }
        win32_dispatch_domui_event(ctx, action_id, widget_id, DOMUI_EVENT_CHANGE, a, b, backend_ext);
    }
}

static void win32_emit_value_text(dui_context* ctx,
                                  u32 widget_id,
                                  u32 action_id,
                                  const char* text,
                                  u32 text_len,
                                  void* backend_ext)
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

    {
        domui_value a = win32_domui_value_str(text ? text : "", n);
        domui_value b = win32_domui_value_none();
        win32_dispatch_domui_event(ctx, action_id, widget_id, DOMUI_EVENT_CHANGE, a, b, backend_ext);
    }
}

static int win32_node_visible(const dui_window* win, const dui_schema_node* n)
{
    if (!n) {
        return 0;
    }
    if (n->required_caps != 0u) {
        if ((win32_caps() & n->required_caps) != n->required_caps) {
            return 0;
        }
    }
    if (n->visible_bind_id != 0u && win && win->state) {
        u32 v = 1u;
        if (dui_state_get_u32(win->state, win->state_len, n->visible_bind_id, &v)) {
            if (v == 0u) {
                return 0;
            }
        }
    }
    return 1;
}

static int win32_is_leaf_kind(u32 kind)
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

static void win32_destroy_child_controls(dui_schema_node* n)
{
    dui_schema_node* child;
    if (!n) {
        return;
    }
    if (n->native) {
        DestroyWindow((HWND)n->native);
        n->native = (void*)0;
    }
    if (n->native_aux) {
        DestroyWindow((HWND)n->native_aux);
        n->native_aux = (void*)0;
    }
    child = n->first_child;
    while (child) {
        win32_destroy_child_controls(child);
        child = child->next_sibling;
    }
}

static void win32_create_controls_for_tree(dui_window* win, HWND parent_hwnd, dui_schema_node* n)
{
    dui_schema_node* child;
    HWND child_parent;
    if (!win || !n) {
        return;
    }
    if (!win32_node_visible(win, n)) {
        return;
    }

    child_parent = parent_hwnd;

    if (n->kind == (u32)DUI_NODE_TABS) {
        DWORD style = WS_CHILD | WS_VISIBLE | WS_TABSTOP | WS_CLIPCHILDREN | WS_CLIPSIBLINGS;
        HWND h = CreateWindowExA(
            0,
            WC_TABCONTROLA,
            "",
            style,
            0, 0, 10, 10,
            parent_hwnd,
            (HMENU)(INT_PTR)n->id,
            GetModuleHandleA(NULL),
            NULL);
        if (h) {
            u32 page_count = 0u;
            int use_explicit_pages = 0;
            int index = 0;
            if (!win->font) {
                win->font = (HFONT)GetStockObject(DEFAULT_GUI_FONT);
            }
            SendMessageA(h, WM_SETFONT, (WPARAM)win->font, TRUE);
            child = n->first_child;
            while (child) {
                if (child->kind == (u32)DUI_NODE_TAB_PAGE) {
                    use_explicit_pages = 1;
                    break;
                }
                child = child->next_sibling;
            }
            child = n->first_child;
            while (child) {
                if (!use_explicit_pages || child->kind == (u32)DUI_NODE_TAB_PAGE) {
                    TCITEMA item;
                    char label[64];
                    const char* text = (child->text && child->text[0]) ? child->text : (const char*)0;
                    memset(&item, 0, sizeof(item));
                    item.mask = TCIF_TEXT;
                    if (!text) {
                        sprintf(label, "Tab %u", (unsigned int)(page_count + 1u));
                        item.pszText = label;
                    } else {
                        item.pszText = (LPSTR)text;
                    }
                    (void)TabCtrl_InsertItem(h, index, &item);
                    index += 1;
                    page_count += 1u;
                }
                child = child->next_sibling;
            }
            if (page_count > 0u) {
                if (n->tabs_selected >= page_count) {
                    n->tabs_selected = page_count - 1u;
                }
                (void)TabCtrl_SetCurSel(h, (int)n->tabs_selected);
            }
            n->native = (void*)h;
        }
    } else if (n->kind == (u32)DUI_NODE_SCROLL_PANEL) {
        DWORD style = WS_CHILD | WS_VISIBLE | WS_VSCROLL | WS_HSCROLL | WS_CLIPCHILDREN | WS_CLIPSIBLINGS;
        DWORD exstyle = WS_EX_CLIENTEDGE;
        dui_scrollpanel_data* data = (dui_scrollpanel_data*)malloc(sizeof(dui_scrollpanel_data));
        if (data) {
            memset(data, 0, sizeof(*data));
            data->win = win;
            data->node = n;
        }
        {
            HWND h = CreateWindowExA(
                exstyle,
                dui_win32_scrollpanel_class_name(),
                "",
                style,
                0, 0, 10, 10,
                parent_hwnd,
                (HMENU)(INT_PTR)n->id,
                GetModuleHandleA(NULL),
                data);
            if (h) {
                n->native = (void*)h;
                child_parent = h;
            } else if (data) {
                free(data);
            }
        }
    } else if (n->kind == (u32)DUI_NODE_SPLITTER) {
        DWORD style = WS_CHILD | WS_VISIBLE;
        dui_splitter_data* data = (dui_splitter_data*)malloc(sizeof(dui_splitter_data));
        if (data) {
            memset(data, 0, sizeof(*data));
            data->win = win;
            data->node = n;
        }
        {
            HWND h = CreateWindowExA(
                0,
                dui_win32_splitter_class_name(),
                "",
                style,
                0, 0, 10, 10,
                parent_hwnd,
                (HMENU)(INT_PTR)n->id,
                GetModuleHandleA(NULL),
                data);
            if (h) {
                n->native = (void*)h;
            } else if (data) {
                free(data);
            }
        }
    } else if (win32_is_leaf_kind(n->kind)) {
        DWORD style = WS_CHILD | WS_VISIBLE;
        DWORD exstyle = 0;
        const char* klass = "STATIC";
        const char* text = (n->text) ? n->text : "";
        HWND h = (HWND)0;

        if (n->kind == (u32)DUI_NODE_LABEL) {
            klass = "STATIC";
            style |= SS_LEFT;
        } else if (n->kind == (u32)DUI_NODE_BUTTON) {
            klass = "BUTTON";
            style |= BS_PUSHBUTTON | WS_TABSTOP;
            if ((n->flags & DUI_NODE_FLAG_FOCUSABLE) == 0u) {
                n->flags |= DUI_NODE_FLAG_FOCUSABLE;
            }
        } else if (n->kind == (u32)DUI_NODE_CHECKBOX) {
            klass = "BUTTON";
            style |= BS_AUTOCHECKBOX | WS_TABSTOP;
            if ((n->flags & DUI_NODE_FLAG_FOCUSABLE) == 0u) {
                n->flags |= DUI_NODE_FLAG_FOCUSABLE;
            }
        } else if (n->kind == (u32)DUI_NODE_TEXT_FIELD) {
            klass = "EDIT";
            exstyle |= WS_EX_CLIENTEDGE;
            style |= ES_LEFT | WS_TABSTOP;
            if ((n->flags & DUI_NODE_FLAG_FOCUSABLE) == 0u) {
                n->flags |= DUI_NODE_FLAG_FOCUSABLE;
            }
        } else if (n->kind == (u32)DUI_NODE_PROGRESS) {
            klass = PROGRESS_CLASSA;
            style |= 0;
        } else if (n->kind == (u32)DUI_NODE_LIST) {
            klass = "LISTBOX";
            style |= WS_TABSTOP | WS_VSCROLL | LBS_NOTIFY;
            if ((n->flags & DUI_NODE_FLAG_FOCUSABLE) == 0u) {
                n->flags |= DUI_NODE_FLAG_FOCUSABLE;
            }
            if ((n->flags & DUI_NODE_FLAG_FLEX) == 0u) {
                n->flags |= DUI_NODE_FLAG_FLEX;
            }
        }

        h = CreateWindowExA(
            exstyle,
            klass,
            text,
            style,
            0, 0, 10, 10,
            parent_hwnd,
            (HMENU)(INT_PTR)n->id,
            GetModuleHandleA(NULL),
            NULL);

        if (h) {
            if (!win->font) {
                win->font = (HFONT)GetStockObject(DEFAULT_GUI_FONT);
            }
            SendMessageA(h, WM_SETFONT, (WPARAM)win->font, TRUE);
            if (n->kind == (u32)DUI_NODE_PROGRESS) {
                SendMessageA(h, PBM_SETRANGE, 0, MAKELPARAM(0, 1000));
                SendMessageA(h, PBM_SETPOS, (WPARAM)0, 0);
            }
            n->native = (void*)h;
        }
    }

    child = n->first_child;
    while (child) {
        win32_create_controls_for_tree(win, child_parent, child);
        child = child->next_sibling;
    }
}

static u32 win32_count_native_controls(const dui_schema_node* n)
{
    u32 count;
    const dui_schema_node* child;
    if (!n) {
        return 0u;
    }
    count = 0u;
    if (n->native) {
        count += 1u;
    }
    child = n->first_child;
    while (child) {
        count += win32_count_native_controls(child);
        child = child->next_sibling;
    }
    return count;
}

static void win32_splitter_divider_rect(const dui_schema_node* n,
                                        int* out_x,
                                        int* out_y,
                                        int* out_w,
                                        int* out_h)
{
    int thickness;
    int axis_len;
    int pos;
    if (!n || !out_x || !out_y || !out_w || !out_h) {
        return;
    }
    thickness = (int)n->splitter_thickness;
    if (thickness < 1) {
        thickness = 1;
    }
    axis_len = (n->splitter_orient == (u32)DUI_SPLIT_HORIZONTAL) ? (int)n->h : (int)n->w;
    pos = win32_splitter_clamp_pos(n, axis_len, (int)n->splitter_pos);
    if (n->splitter_orient == (u32)DUI_SPLIT_HORIZONTAL) {
        *out_x = (int)n->x;
        *out_y = (int)n->y + pos;
        *out_w = (int)n->w;
        *out_h = thickness;
    } else {
        *out_x = (int)n->x + pos;
        *out_y = (int)n->y;
        *out_w = thickness;
        *out_h = (int)n->h;
    }
}

static void win32_scrollpanel_update(HWND hwnd, dui_schema_node* n)
{
    SCROLLINFO si;
    int view_w;
    int view_h;
    int content_w;
    int content_h;
    int max_x;
    int max_y;
    dui_schema_node* child;
    if (!hwnd || !n) {
        return;
    }
    view_w = (int)n->w;
    view_h = (int)n->h;
    if (view_w < 0) view_w = 0;
    if (view_h < 0) view_h = 0;
    content_w = view_w;
    content_h = view_h;
    child = n->first_child;
    if (child) {
        if ((int)child->w > content_w) content_w = (int)child->w;
        if ((int)child->h > content_h) content_h = (int)child->h;
    }
    max_x = content_w - view_w;
    max_y = content_h - view_h;
    if (max_x < 0) max_x = 0;
    if (max_y < 0) max_y = 0;
    if ((int)n->scroll_x > max_x) n->scroll_x = (u32)max_x;
    if ((int)n->scroll_y > max_y) n->scroll_y = (u32)max_y;

    memset(&si, 0, sizeof(si));
    si.cbSize = sizeof(si);
    si.fMask = SIF_RANGE | SIF_PAGE | SIF_POS;
    si.nMin = 0;
    si.nMax = (content_w > 0) ? (content_w - 1) : 0;
    si.nPage = (UINT)view_w;
    si.nPos = (int)n->scroll_x;
    SetScrollInfo(hwnd, SB_HORZ, &si, TRUE);

    memset(&si, 0, sizeof(si));
    si.cbSize = sizeof(si);
    si.fMask = SIF_RANGE | SIF_PAGE | SIF_POS;
    si.nMin = 0;
    si.nMax = (content_h > 0) ? (content_h - 1) : 0;
    si.nPage = (UINT)view_h;
    si.nPos = (int)n->scroll_y;
    SetScrollInfo(hwnd, SB_VERT, &si, TRUE);
}

static void win32_apply_layout_to_tree_fallback(dui_schema_node* n, int origin_x, int origin_y)
{
    dui_schema_node* child;
    int child_origin_x = origin_x;
    int child_origin_y = origin_y;
    if (!n) {
        return;
    }
    if (n->native) {
        int x = (int)n->x - origin_x;
        int y = (int)n->y - origin_y;
        int w = (int)n->w;
        int h = (int)n->h;
        if (n->kind == (u32)DUI_NODE_SPLITTER) {
            win32_splitter_divider_rect(n, &x, &y, &w, &h);
            x -= origin_x;
            y -= origin_y;
        }
        MoveWindow((HWND)n->native, x, y, w, h, FALSE);
        if (n->kind == (u32)DUI_NODE_SCROLL_PANEL) {
            win32_scrollpanel_update((HWND)n->native, n);
            child_origin_x = (int)n->x + (int)n->scroll_x;
            child_origin_y = (int)n->y + (int)n->scroll_y;
        }
    }
    child = n->first_child;
    while (child) {
        win32_apply_layout_to_tree_fallback(child, child_origin_x, child_origin_y);
        child = child->next_sibling;
    }
}

static HDWP win32_defer_layout_to_tree(HDWP hdwp, dui_schema_node* n, int origin_x, int origin_y)
{
    dui_schema_node* child;
    int child_origin_x = origin_x;
    int child_origin_y = origin_y;
    if (!hdwp || !n) {
        return hdwp;
    }
    if (n->native) {
        int x = (int)n->x - origin_x;
        int y = (int)n->y - origin_y;
        int w = (int)n->w;
        int h = (int)n->h;
        HWND insert_after = (HWND)0;
        UINT flags = SWP_NOACTIVATE | SWP_NOOWNERZORDER | SWP_NOCOPYBITS | SWP_NOREDRAW;
        if (n->kind == (u32)DUI_NODE_SPLITTER) {
            win32_splitter_divider_rect(n, &x, &y, &w, &h);
            x -= origin_x;
            y -= origin_y;
            insert_after = HWND_TOP;
        } else {
            flags |= SWP_NOZORDER;
        }
        hdwp = DeferWindowPos(hdwp,
                              (HWND)n->native,
                              insert_after,
                              x,
                              y,
                              w,
                              h,
                              flags);
        if (n->kind == (u32)DUI_NODE_SCROLL_PANEL) {
            win32_scrollpanel_update((HWND)n->native, n);
            child_origin_x = (int)n->x + (int)n->scroll_x;
            child_origin_y = (int)n->y + (int)n->scroll_y;
        }
    }
    child = n->first_child;
    while (child) {
        hdwp = win32_defer_layout_to_tree(hdwp, child, child_origin_x, child_origin_y);
        child = child->next_sibling;
    }
    return hdwp;
}

static void win32_apply_layout_to_tree(dui_window* win, dui_schema_node* root)
{
    u32 count;
    HDWP hdwp;
    dui_win32_batch_state* batch;
    if (!win || !root || !win->hwnd) {
        return;
    }
    count = win32_count_native_controls(root);
    if (count == 0u) {
        return;
    }
    batch = win32_batch_find(win->hwnd);
    if (batch && batch->depth > 0u && batch->hdwp) {
        batch->hdwp = win32_defer_layout_to_tree(batch->hdwp, root, 0, 0);
        if (!batch->hdwp) {
            win32_apply_layout_to_tree_fallback(root, 0, 0);
        }
        return;
    }
    hdwp = BeginDeferWindowPos((int)count);
    if (!hdwp) {
        win32_apply_layout_to_tree_fallback(root, 0, 0);
        return;
    }
    hdwp = win32_defer_layout_to_tree(hdwp, root, 0, 0);
    if (hdwp) {
        (void)EndDeferWindowPos(hdwp);
    }
}

static void win32_build_node_text(const dui_schema_node* n,
                                  const unsigned char* state,
                                  u32 state_len,
                                  char* out_text,
                                  u32 out_cap)
{
    u32 text_len;
    if (!out_text || out_cap == 0u) {
        return;
    }
    out_text[0] = '\0';
    text_len = 0u;
    if (n && n->bind_id != 0u && state) {
        (void)dui_state_get_text(state, state_len, n->bind_id, out_text, out_cap, &text_len);
    }
    if ((!out_text[0]) && n && n->text) {
        u32 i = 0u;
        while (i + 1u < out_cap && n->text[i]) {
            out_text[i] = n->text[i];
            i += 1u;
        }
        out_text[i] = '\0';
    }
}

static int win32_list_items_equal(u32 bind_id,
                                  const unsigned char* a_state,
                                  u32 a_state_len,
                                  const unsigned char* b_state,
                                  u32 b_state_len)
{
    u32 a_count;
    u32 b_count;
    u32 i;
    if (!bind_id || !a_state || !b_state) {
        return 0;
    }
    a_count = 0u;
    b_count = 0u;
    (void)dui_state_get_list_item_count(a_state, a_state_len, bind_id, &a_count);
    (void)dui_state_get_list_item_count(b_state, b_state_len, bind_id, &b_count);
    if (a_count != b_count) {
        return 0;
    }
    for (i = 0u; i < a_count; ++i) {
        u32 a_id = 0u;
        u32 b_id = 0u;
        char a_text[256];
        char b_text[256];
        u32 a_len = 0u;
        u32 b_len = 0u;
        a_text[0] = '\0';
        b_text[0] = '\0';
        if (!dui_state_get_list_item_at(a_state, a_state_len, bind_id, i, &a_id, a_text, (u32)sizeof(a_text), &a_len)) {
            return 0;
        }
        if (!dui_state_get_list_item_at(b_state, b_state_len, bind_id, i, &b_id, b_text, (u32)sizeof(b_text), &b_len)) {
            return 0;
        }
        if (a_id != b_id || a_len != b_len) {
            return 0;
        }
        if (a_len > 0u && memcmp(a_text, b_text, (size_t)a_len) != 0) {
            return 0;
        }
    }
    return 1;
}

static int win32_list_find_index_by_item_id(HWND h, u32 item_id)
{
    int count;
    int i;
    if (!h || item_id == 0u) {
        return -1;
    }
    count = (int)SendMessageA(h, LB_GETCOUNT, 0, 0);
    if (count <= 0) {
        return -1;
    }
    for (i = 0; i < count; ++i) {
        u32 id = (u32)SendMessageA(h, LB_GETITEMDATA, (WPARAM)i, 0);
        if (id == item_id) {
            return i;
        }
    }
    return -1;
}

static void win32_batch_set_visibility(const dui_window* win, HWND hwnd, int visible)
{
    dui_win32_batch_state* state;
    UINT flags;
    if (!win || !hwnd) {
        return;
    }
    state = win32_batch_find(win->hwnd);
    if (state && state->depth > 0u && state->hdwp) {
        flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE |
                (visible ? SWP_SHOWWINDOW : SWP_HIDEWINDOW);
        state->hdwp = DeferWindowPos(state->hdwp, hwnd, NULL, 0, 0, 0, 0, flags);
        if (!state->hdwp) {
            ShowWindow(hwnd, visible ? SW_SHOW : SW_HIDE);
        }
    } else {
        ShowWindow(hwnd, visible ? SW_SHOW : SW_HIDE);
    }
}

static void win32_update_control_values(dui_window* win,
                                       dui_schema_node* n,
                                       int parent_visible,
                                       const unsigned char* prev_state,
                                       u32 prev_state_len)
{
    dui_schema_node* child;
    char text[256];
    u32 text_len;
    char prev_text[256];
    int visible;
    if (!win || !n) {
        return;
    }
    visible = parent_visible && win32_node_visible(win, n);
    if (n->native) {
        HWND h = (HWND)n->native;
        const int cur_vis = IsWindowVisible(h) ? 1 : 0;
        const int cur_en = IsWindowEnabled(h) ? 1 : 0;
        if (cur_vis != (visible ? 1 : 0)) {
            win32_batch_set_visibility(win, h, visible);
        }
        if (cur_en != (visible ? 1 : 0)) {
            EnableWindow(h, visible ? TRUE : FALSE);
        }
    }

    if (!visible) {
        /* Still recurse to ensure hidden subtrees are hidden too. */
        child = n->first_child;
        while (child) {
            win32_update_control_values(win, child, visible, prev_state, prev_state_len);
            child = child->next_sibling;
        }
        return;
    }

    if (n->kind == (u32)DUI_NODE_TABS && n->native) {
        u32 page_count = 0u;
        u32 selected = n->tabs_selected;
        u32 page_index = 0u;
        int use_explicit_pages = 0;
        int cur_sel;
        u32 state_sel = 0u;
        child = n->first_child;
        while (child) {
            if (child->kind == (u32)DUI_NODE_TAB_PAGE) {
                use_explicit_pages = 1;
                break;
            }
            child = child->next_sibling;
        }
        child = n->first_child;
        while (child) {
            if (!use_explicit_pages || child->kind == (u32)DUI_NODE_TAB_PAGE) {
                page_count += 1u;
            }
            child = child->next_sibling;
        }
        if (n->bind_id != 0u && win->state) {
            if (dui_state_get_u32(win->state, win->state_len, n->bind_id, &state_sel)) {
                selected = state_sel;
            }
        }
        if (page_count > 0u && selected >= page_count) {
            selected = page_count - 1u;
        }
        n->tabs_selected = selected;
        cur_sel = TabCtrl_GetCurSel((HWND)n->native);
        if (page_count > 0u && cur_sel != (int)selected) {
            (void)TabCtrl_SetCurSel((HWND)n->native, (int)selected);
        }
        child = n->first_child;
        while (child) {
            int is_page = (!use_explicit_pages || child->kind == (u32)DUI_NODE_TAB_PAGE) ? 1 : 0;
            int child_visible = visible;
            if (is_page) {
                child_visible = (page_index == selected) ? 1 : 0;
                page_index += 1u;
            } else {
                child_visible = 0;
            }
            win32_update_control_values(win, child, child_visible, prev_state, prev_state_len);
            child = child->next_sibling;
        }
        return;
    }

    if (n->native && win32_is_leaf_kind(n->kind)) {
        HWND h = (HWND)n->native;
        if (n->kind == (u32)DUI_NODE_LABEL || n->kind == (u32)DUI_NODE_BUTTON) {
            if (n->bind_id != 0u) {
                win32_build_node_text(n, win->state, win->state_len, text, (u32)sizeof(text));
                win32_build_node_text(n, prev_state, prev_state_len, prev_text, (u32)sizeof(prev_text));
                if (strcmp(text, prev_text) != 0) {
                    SetWindowTextA(h, text);
                }
            }
        } else if (n->kind == (u32)DUI_NODE_CHECKBOX) {
            u32 v = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
            }
            {
                LRESULT st = SendMessageA(h, BM_GETCHECK, 0, 0);
                const u32 cur = (st == BST_CHECKED) ? 1u : 0u;
                if (cur != (v ? 1u : 0u)) {
                    SendMessageA(h, BM_SETCHECK, (WPARAM)(v ? BST_CHECKED : BST_UNCHECKED), 0);
                }
            }
        } else if (n->kind == (u32)DUI_NODE_TEXT_FIELD) {
            text[0] = '\0';
            text_len = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_text(win->state, win->state_len, n->bind_id, text, (u32)sizeof(text), &text_len);
            }
            {
                char cur_text[256];
                cur_text[0] = '\0';
                GetWindowTextA(h, cur_text, (int)sizeof(cur_text));
                if (strcmp(cur_text, text) != 0) {
                    SetWindowTextA(h, text);
                }
            }
        } else if (n->kind == (u32)DUI_NODE_PROGRESS) {
            u32 v = 0u;
            u32 prev_v = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
            }
            if (v > 1000u) v = 1000u;
            if (n->bind_id != 0u && prev_state) {
                (void)dui_state_get_u32(prev_state, prev_state_len, n->bind_id, &prev_v);
                if (prev_v > 1000u) prev_v = 1000u;
            }
            if (!prev_state || prev_v != v) {
                SendMessageA(h, PBM_SETPOS, (WPARAM)v, 0);
            }
        } else if (n->kind == (u32)DUI_NODE_LIST) {
            u32 count = 0u;
            u32 selected_id = 0u;
            u32 prev_selected_id = 0u;
            u32 i;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_list_item_count(win->state, win->state_len, n->bind_id, &count);
                (void)dui_state_get_list_selected_item_id(win->state, win->state_len, n->bind_id, &selected_id);
            }

            if (n->bind_id != 0u && prev_state) {
                (void)dui_state_get_list_selected_item_id(prev_state, prev_state_len, n->bind_id, &prev_selected_id);
            }

            if (!prev_state || !n->bind_id ||
                !win32_list_items_equal(n->bind_id, prev_state, prev_state_len, win->state, win->state_len)) {
                int top = (int)SendMessageA(h, LB_GETTOPINDEX, 0, 0);
                int found_sel = -1;
                dui_win32_begin_batch(h);
                SendMessageA(h, LB_RESETCONTENT, 0, 0);
                for (i = 0u; i < count; ++i) {
                    u32 item_id = 0u;
                    char item_text[256];
                    u32 item_len = 0u;
                    int idx;
                    item_text[0] = '\0';
                    if (!dui_state_get_list_item_at(win->state, win->state_len, n->bind_id, i, &item_id, item_text, (u32)sizeof(item_text), &item_len)) {
                        continue;
                    }
                    idx = (int)SendMessageA(h, LB_ADDSTRING, 0, (LPARAM)item_text);
                    if (idx >= 0) {
                        SendMessageA(h, LB_SETITEMDATA, (WPARAM)idx, (LPARAM)item_id);
                        if (item_id == selected_id) {
                            found_sel = idx;
                        }
                    }
                }
                SendMessageA(h, LB_SETCURSEL, (WPARAM)found_sel, 0);
                if (top >= 0 && (int)count > 0) {
                    if (top >= (int)count) {
                        top = (int)count - 1;
                    }
                    (void)SendMessageA(h, LB_SETTOPINDEX, (WPARAM)top, 0);
                }
                dui_win32_end_batch(h);
            } else if (prev_selected_id != selected_id) {
                int idx = -1;
                if (selected_id != 0u) {
                    idx = win32_list_find_index_by_item_id(h, selected_id);
                }
                SendMessageA(h, LB_SETCURSEL, (WPARAM)idx, 0);
            }
        }
    }

    child = n->first_child;
    while (child) {
        win32_update_control_values(win, child, visible, prev_state, prev_state_len);
        child = child->next_sibling;
    }
}

static void win32_relayout_with_size(dui_window* win, int width, int height, int use_size)
{
    RECT rc;
    int w;
    int h;
    if (!win || !win->hwnd || !win->root) {
        return;
    }
    if (!use_size) {
        GetClientRect(win->hwnd, &rc);
        w = (int)(rc.right - rc.left);
        h = (int)(rc.bottom - rc.top);
    } else {
        w = width;
        h = height;
    }
    if (w < 0) w = 0;
    if (h < 0) h = 0;
    dui_win32_begin_batch(win->hwnd);
    dui_schema_layout(win->root, 0, 0, (i32)w, (i32)h);
    win32_apply_layout_to_tree(win, win->root);
    dui_win32_end_batch(win->hwnd);
}

static void win32_relayout(dui_window* win)
{
    win32_relayout_with_size(win, 0, 0, 0);
}

static void win32_schedule_relayout(dui_window* win, int width, int height)
{
    if (!win || !win->hwnd) {
        return;
    }
    win->pending_w = width;
    win->pending_h = height;
    if (!win->relayout_pending) {
        win->relayout_pending = 1;
        PostMessageA(win->hwnd, DUI_WIN32_RELAYOUT_MSG, 0, 0);
    }
}

static int win32_splitter_clamp_pos(const dui_schema_node* n, int axis_len, int pos)
{
    int thickness;
    int avail_axis;
    int min_a;
    int min_b;

    if (!n) {
        return 0;
    }
    thickness = (int)n->splitter_thickness;
    if (thickness < 1) {
        thickness = 1;
    }
    avail_axis = axis_len - thickness;
    if (avail_axis < 0) {
        avail_axis = 0;
    }
    if (pos < 0) {
        pos = avail_axis / 2;
    }
    min_a = (int)n->splitter_min_a;
    min_b = (int)n->splitter_min_b;
    if (min_a < 0) min_a = 0;
    if (min_b < 0) min_b = 0;
    if (pos < min_a) {
        pos = min_a;
    }
    if (pos > (avail_axis - min_b)) {
        pos = avail_axis - min_b;
    }
    if (pos < 0) {
        pos = 0;
    }
    return pos;
}

static LRESULT CALLBACK win32_splitter_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    dui_splitter_data* data = (dui_splitter_data*)GetWindowLongPtr(hwnd, GWLP_USERDATA);

    if (msg == WM_CREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        if (cs && cs->lpCreateParams) {
            data = (dui_splitter_data*)cs->lpCreateParams;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)data);
        }
        return 0;
    }

    if (msg == WM_NCDESTROY) {
        if (data) {
            free(data);
            data = (dui_splitter_data*)0;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)0);
        }
        return 0;
    }

    if (!data || !data->win || !data->node) {
        return DefWindowProcA(hwnd, msg, wparam, lparam);
    }

    if (msg == WM_LBUTTONDOWN) {
        RECT rc;
        POINT pt;
        SetCapture(hwnd);
        data->dragging = 1;
        GetWindowRect(hwnd, &rc);
        GetCursorPos(&pt);
        {
            POINT win_pt = { rc.left, rc.top };
            ScreenToClient(data->win->hwnd, &win_pt);
            ScreenToClient(data->win->hwnd, &pt);
            if (data->node->splitter_orient == (u32)DUI_SPLIT_HORIZONTAL) {
                data->drag_offset = pt.y - win_pt.y;
            } else {
                data->drag_offset = pt.x - win_pt.x;
            }
        }
        return 0;
    }

    if (msg == WM_LBUTTONUP) {
        data->dragging = 0;
        ReleaseCapture();
        return 0;
    }

    if (msg == WM_MOUSEMOVE && data->dragging) {
        POINT pt;
        int pos;
        int axis_len = (data->node->splitter_orient == (u32)DUI_SPLIT_HORIZONTAL) ? (int)data->node->h : (int)data->node->w;
        GetCursorPos(&pt);
        ScreenToClient(data->win->hwnd, &pt);
        if (data->node->splitter_orient == (u32)DUI_SPLIT_HORIZONTAL) {
            pos = pt.y - (int)data->node->y - data->drag_offset;
        } else {
            pos = pt.x - (int)data->node->x - data->drag_offset;
        }
        pos = win32_splitter_clamp_pos(data->node, axis_len, pos);
        data->node->splitter_pos = (u32)pos;
        win32_relayout(data->win);
        if (!data->win->suppress_events && data->node->bind_id != 0u) {
            win32_emit_value_u32(data->win->ctx,
                                 data->node->id,
                                 data->node->action_id,
                                 (u32)DUI_VALUE_U32,
                                 (u32)pos,
                                 0u,
                                 hwnd);
        }
        return 0;
    }

    if (msg == WM_SETCURSOR) {
        if (data->node->splitter_orient == (u32)DUI_SPLIT_HORIZONTAL) {
            SetCursor(LoadCursor(NULL, IDC_SIZENS));
        } else {
            SetCursor(LoadCursor(NULL, IDC_SIZEWE));
        }
        return TRUE;
    }

    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

static LRESULT CALLBACK win32_scrollpanel_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    dui_scrollpanel_data* data = (dui_scrollpanel_data*)GetWindowLongPtr(hwnd, GWLP_USERDATA);

    if (msg == WM_CREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        if (cs && cs->lpCreateParams) {
            data = (dui_scrollpanel_data*)cs->lpCreateParams;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)data);
        }
        return 0;
    }

    if (msg == WM_NCDESTROY) {
        if (data) {
            free(data);
            data = (dui_scrollpanel_data*)0;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)0);
        }
        return 0;
    }

    if (!data || !data->win || !data->node) {
        return DefWindowProcA(hwnd, msg, wparam, lparam);
    }

    if (msg == WM_HSCROLL || msg == WM_VSCROLL) {
        SCROLLINFO si;
        int pos;
        int max_pos;
        int bar = (msg == WM_HSCROLL) ? SB_HORZ : SB_VERT;
        memset(&si, 0, sizeof(si));
        si.cbSize = sizeof(si);
        si.fMask = SIF_ALL;
        if (!GetScrollInfo(hwnd, bar, &si)) {
            return 0;
        }
        pos = si.nPos;
        switch (LOWORD(wparam)) {
        case SB_LINELEFT: pos -= 16; break;
        case SB_LINERIGHT: pos += 16; break;
        case SB_PAGELEFT: pos -= (int)si.nPage; break;
        case SB_PAGERIGHT: pos += (int)si.nPage; break;
        case SB_THUMBTRACK: pos = si.nTrackPos; break;
        case SB_THUMBPOSITION: pos = si.nTrackPos; break;
        default: break;
        }
        max_pos = si.nMax - (int)si.nPage + 1;
        if (max_pos < 0) {
            max_pos = 0;
        }
        if (pos < 0) {
            pos = 0;
        }
        if (pos > max_pos) {
            pos = max_pos;
        }
        if (msg == WM_HSCROLL) {
            if ((u32)pos != data->node->scroll_x) {
                data->node->scroll_x = (u32)pos;
                win32_relayout(data->win);
            }
        } else {
            if ((u32)pos != data->node->scroll_y) {
                data->node->scroll_y = (u32)pos;
                win32_relayout(data->win);
            }
        }
        return 0;
    }

    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

static LRESULT CALLBACK dui_win32_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    dui_window* win = DUI_GET_WND_PTR(hwnd);
    dui_context* ctx = (dui_context*)0;

    if (msg == WM_CREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        if (cs && cs->lpCreateParams) {
            win = (dui_window*)cs->lpCreateParams;
            DUI_SET_WND_PTR(hwnd, win);
            if (win) {
                win->hwnd = hwnd;
            }
        }
        return 0;
    }

    if (!win) {
        return DefWindowProcA(hwnd, msg, wparam, lparam);
    }
    ctx = win->ctx;


    if (msg == WM_COMMAND) {
        const int ctrl_id = (int)LOWORD(wparam);
        const int notify = (int)HIWORD(wparam);
        HWND ctrl = (HWND)lparam;
        dui_schema_node* n;

        if (!ctx || !win->root || win->suppress_events) {
            return 0;
        }
        n = dui_schema_find_by_id(win->root, (u32)ctrl_id);
        if (!n || !ctrl) {
            return 0;
        }
        if (n->kind == (u32)DUI_NODE_BUTTON) {
            if (notify == BN_CLICKED) {
                win32_emit_action_event(ctx, n->id, n->action_id, DOMUI_EVENT_CLICK, 0u, ctrl);
            }
            return 0;
        }
        if (n->kind == (u32)DUI_NODE_CHECKBOX) {
            if (notify == BN_CLICKED) {
                LRESULT st = SendMessageA(ctrl, BM_GETCHECK, 0, 0);
                u32 v = (st == BST_CHECKED) ? 1u : 0u;
                win32_emit_value_u32(ctx, n->id, n->action_id, (u32)DUI_VALUE_BOOL, v, 0u, ctrl);
            }
            return 0;
        }
        if (n->kind == (u32)DUI_NODE_TEXT_FIELD) {
            if (notify == EN_CHANGE) {
                char buf[256];
                int len = GetWindowTextA(ctrl, buf, (int)sizeof(buf));
                if (len < 0) {
                    len = 0;
                }
                win32_emit_value_text(ctx, n->id, n->action_id, buf, (u32)len, ctrl);
            }
            return 0;
        }
        if (n->kind == (u32)DUI_NODE_LIST) {
            if (notify == LBN_SELCHANGE || notify == LBN_DBLCLK) {
                int sel = (int)SendMessageA(ctrl, LB_GETCURSEL, 0, 0);
                u32 item_id = 0u;
                if (sel >= 0) {
                    item_id = (u32)SendMessageA(ctrl, LB_GETITEMDATA, (WPARAM)sel, 0);
                }
                if (notify == LBN_SELCHANGE) {
                    win32_emit_value_u32(ctx, n->id, n->action_id, (u32)DUI_VALUE_LIST, (u32)((sel >= 0) ? sel : 0), item_id, ctrl);
                } else if (notify == LBN_DBLCLK) {
                    win32_emit_action_event(ctx, n->id, n->action_id, DOMUI_EVENT_SUBMIT, item_id, ctrl);
                }
            }
            return 0;
        }
        return 0;
    }

    if (msg == WM_NOTIFY) {
        NMHDR* hdr = (NMHDR*)lparam;
        dui_schema_node* n;
        if (!ctx || !win->root || win->suppress_events) {
            return 0;
        }
        if (!hdr) {
            return 0;
        }
        if (hdr->code == TCN_SELCHANGE) {
            int sel = TabCtrl_GetCurSel(hdr->hwndFrom);
            if (sel < 0) {
                sel = 0;
            }
            n = dui_schema_find_by_id(win->root, (u32)hdr->idFrom);
            if (!n || n->kind != (u32)DUI_NODE_TABS) {
                return 0;
            }
            n->tabs_selected = (u32)sel;
            if (!win->suppress_events) {
                if (n->action_id != 0u) {
                    win32_emit_action_event(ctx, n->id, n->action_id, DOMUI_EVENT_TAB_CHANGE, (u32)sel, hdr->hwndFrom);
                }
                win32_emit_value_u32(ctx, n->id, n->action_id, (u32)DUI_VALUE_U32, (u32)sel, 0u, hdr->hwndFrom);
            }
            {
                u32 page_index = 0u;
                int use_explicit_pages = 0;
                dui_schema_node* child = n->first_child;
                while (child) {
                    if (child->kind == (u32)DUI_NODE_TAB_PAGE) {
                        use_explicit_pages = 1;
                        break;
                    }
                    child = child->next_sibling;
                }
                child = n->first_child;
                dui_win32_begin_batch(win->hwnd);
                while (child) {
                    int is_page = (!use_explicit_pages || child->kind == (u32)DUI_NODE_TAB_PAGE) ? 1 : 0;
                    int child_visible = 0;
                    if (is_page) {
                        child_visible = (page_index == (u32)sel) ? 1 : 0;
                        page_index += 1u;
                    }
                    win32_update_control_values(win, child, child_visible, win->state, win->state_len);
                    child = child->next_sibling;
                }
                dui_win32_end_batch(win->hwnd);
            }
            return 0;
        }
        return 0;
    }

    if (msg == DUI_WIN32_RELAYOUT_MSG) {
        win->relayout_pending = 0;
        win32_relayout_with_size(win, win->pending_w, win->pending_h, 1);
        return 0;
    }

    if (msg == WM_SIZE) {
        int w = (int)LOWORD(lparam);
        int h = (int)HIWORD(lparam);
        win32_schedule_relayout(win, w, h);
        return 0;
    }

    if (msg == WM_CLOSE) {
        /* Emit quit event; actual destruction is driven by caller via destroy_window. */
        /* Post a WM_DESTROY to keep the message pump progressing. */
        if (ctx) {
            win32_emit_quit(ctx);
        }
        DestroyWindow(hwnd);
        return 0;
    }

    if (msg == WM_DESTROY) {
        PostQuitMessage(0);
        return 0;
    }

    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

static int win32_register_class(void)
{
    static int s_registered = 0;
    WNDCLASSA wc;
    if (s_registered) {
        return 1;
    }
    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = dui_win32_wndproc;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = dui_win32_class_name();
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    if (!RegisterClassA(&wc)) {
        return 0;
    }

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = win32_splitter_wndproc;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = dui_win32_splitter_class_name();
    wc.hCursor = LoadCursor(NULL, IDC_SIZEWE);
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    if (!RegisterClassA(&wc)) {
        return 0;
    }

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = win32_scrollpanel_wndproc;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = dui_win32_scrollpanel_class_name();
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    if (!RegisterClassA(&wc)) {
        return 0;
    }

    s_registered = 1;
    return 1;
}

static void win32_init_common_controls(void)
{
    INITCOMMONCONTROLSEX icc;
    memset(&icc, 0, sizeof(icc));
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_PROGRESS_CLASS | ICC_TAB_CLASSES;
    InitCommonControlsEx(&icc);
}

#endif /* _WIN32 */

static dui_result win32_create_context(dui_context** out_ctx)
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
    ctx->quit_emitted = 0u;
    ctx->primary_window = (dui_window*)0;
    *out_ctx = ctx;
    return DUI_OK;
}

static void win32_destroy_context(dui_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

static dui_result win32_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win)
{
    dui_window* win;
#if defined(_WIN32)
    DWORD style;
    RECT rect;
    int w;
    int h;
    const char* title;
    HWND parent_hwnd;
    int is_child;
    int win_x;
    int win_y;
    int win_w;
    int win_h;
#endif

    if (!ctx || !out_win) {
        return DUI_ERR_NULL;
    }
    *out_win = (dui_window*)0;

    win = (dui_window*)malloc(sizeof(dui_window));
    if (!win) {
        return DUI_ERR;
    }
    memset(win, 0, sizeof(*win));
    win->ctx = ctx;

#if defined(_WIN32)
    win32_init_common_controls();
    if (!win32_register_class()) {
        free(win);
        return DUI_ERR_BACKEND_UNAVAILABLE;
    }

    title = (desc && desc->title) ? desc->title : "Dominium";
    w = (desc) ? (int)desc->width : 800;
    h = (desc) ? (int)desc->height : 600;
    if (w <= 0) w = 800;
    if (h <= 0) h = 600;
    parent_hwnd = NULL;
    is_child = 0;
    if (desc && (desc->flags & DUI_WINDOW_FLAG_CHILD)) {
        is_child = 1;
        if (desc->struct_size >= (u32)sizeof(dui_window_desc_v1)) {
            parent_hwnd = (HWND)desc->parent_hwnd;
        }
    }
    if (is_child && parent_hwnd) {
        style = WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN | WS_CLIPSIBLINGS;
        win_x = 0;
        win_y = 0;
        win_w = w;
        win_h = h;
    } else {
        style = WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN | WS_CLIPSIBLINGS;
        rect.left = 0;
        rect.top = 0;
        rect.right = w;
        rect.bottom = h;
        AdjustWindowRect(&rect, style, FALSE);
        win_x = CW_USEDEFAULT;
        win_y = CW_USEDEFAULT;
        win_w = rect.right - rect.left;
        win_h = rect.bottom - rect.top;
        parent_hwnd = NULL;
        is_child = 0;
    }

    win->hwnd = CreateWindowExA(
        0,
        dui_win32_class_name(),
        title,
        style,
        win_x,
        win_y,
        win_w,
        win_h,
        parent_hwnd,
        NULL,
        GetModuleHandleA(NULL),
        win);

    if (!win->hwnd) {
        free(win);
        return DUI_ERR_BACKEND_UNAVAILABLE;
    }
    ShowWindow(win->hwnd, SW_SHOW);
    UpdateWindow(win->hwnd);

    if (!is_child) {
        ctx->primary_window = win;
    }
#else
    (void)desc;
    free(win);
    return DUI_ERR_UNSUPPORTED;
#endif

    *out_win = win;
    return DUI_OK;
}

static void win32_destroy_window(dui_window* win)
{
    if (!win) {
        return;
    }

#if defined(_WIN32)
    if (win->root) {
        win32_destroy_child_controls(win->root);
    }
    if (win->hwnd) {
        DestroyWindow(win->hwnd);
        win->hwnd = (HWND)0;
    }
#endif

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
    free(win);
}

static dui_result win32_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len)
{
    unsigned char* copy;
    dui_result perr;
    if (!win || (!schema_tlv && schema_len != 0u)) {
        return DUI_ERR_NULL;
    }

#if defined(_WIN32)
    if (win->root) {
        win32_destroy_child_controls(win->root);
    }
#endif

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
    if (!win->root) {
        return perr;
    }

#if defined(_WIN32)
    dui_win32_begin_batch(win->hwnd);
    win32_create_controls_for_tree(win, win->hwnd, win->root);
    win32_relayout(win);
    win->suppress_events = 1u;
    win32_update_control_values(win, win->root, 1, (const unsigned char*)0, 0u);
    win->suppress_events = 0u;
    dui_win32_end_batch(win->hwnd);
#endif
    return DUI_OK;
}

static dui_result win32_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len)
{
    unsigned char* copy;
    unsigned char* prev_state;
    u32 prev_state_len;
    if (!win || (!state_tlv && state_len != 0u)) {
        return DUI_ERR_NULL;
    }

    if (win->state && state_tlv && state_len == win->state_len && state_len != 0u) {
        if (memcmp(win->state, state_tlv, (size_t)state_len) == 0) {
            return DUI_OK;
        }
    }

    prev_state = win->state;
    prev_state_len = win->state_len;
    win->state = (unsigned char*)0;
    win->state_len = 0u;

    if (!state_tlv || state_len == 0u) {
        if (prev_state) {
            free(prev_state);
        }
        return DUI_OK;
    }
    copy = (unsigned char*)malloc((size_t)state_len);
    if (!copy) {
        win->state = prev_state;
        win->state_len = prev_state_len;
        return DUI_ERR;
    }
    memcpy(copy, state_tlv, (size_t)state_len);
    win->state = copy;
    win->state_len = state_len;

#if defined(_WIN32)
    if (win->root) {
        dui_win32_begin_batch(win->hwnd);
        win->suppress_events = 1u;
        win32_update_control_values(win, win->root, 1, prev_state, prev_state_len);
        win->suppress_events = 0u;
        dui_win32_end_batch(win->hwnd);
    }
#endif
    if (prev_state) {
        free(prev_state);
    }
    return DUI_OK;
}

static dui_result win32_render(dui_window* win)
{
    (void)win;
    return DUI_OK;
}

static dui_result win32_pump(dui_context* ctx)
{
#if defined(_WIN32)
    MSG msg;
#endif
    if (!ctx) {
        return DUI_ERR_NULL;
    }

    if (ctx->quit_requested) {
        if (ctx->primary_window && ctx->primary_window->hwnd) {
#if defined(_WIN32)
            PostMessageA(ctx->primary_window->hwnd, WM_CLOSE, 0, 0);
#endif
        } else {
            win32_emit_quit(ctx);
        }
        ctx->quit_requested = 0u;
    }

#if defined(_WIN32)
    while (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) {
            win32_emit_quit(ctx);
            break;
        }
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
#endif
    return DUI_OK;
}

static int win32_poll_event(dui_context* ctx, dui_event_v1* out_ev)
{
    if (!ctx || !out_ev) {
        return -1;
    }
    return dui_event_queue_pop(&ctx->q, out_ev);
}

static dui_result win32_request_quit(dui_context* ctx)
{
    if (!ctx) {
        return DUI_ERR_NULL;
    }
    ctx->quit_requested = 1u;
    return DUI_OK;
}

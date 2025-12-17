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

#include <stdlib.h>
#include <string.h>

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
} dui_window;

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

static dom_abi_result win32_query_interface(dom_iid iid, void** out_iface);

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

static const char* dui_win32_class_name(void)
{
    return "DominiumDUIWindow";
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

static void win32_emit_action(dui_context* ctx, u32 widget_id, u32 action_id, u32 item_id)
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

static void win32_emit_value_u32(dui_context* ctx, u32 widget_id, u32 value_type, u32 v, u32 item_id)
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

static void win32_emit_value_text(dui_context* ctx, u32 widget_id, const char* text, u32 text_len)
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
    child = n->first_child;
    while (child) {
        win32_destroy_child_controls(child);
        child = child->next_sibling;
    }
}

static void win32_create_controls_for_tree(dui_window* win, HWND parent_hwnd, dui_schema_node* n)
{
    dui_schema_node* child;
    if (!win || !n) {
        return;
    }
    if (!win32_node_visible(win, n)) {
        return;
    }

    if (win32_is_leaf_kind(n->kind)) {
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
            n->native = (void*)h;
        }
    }

    child = n->first_child;
    while (child) {
        win32_create_controls_for_tree(win, parent_hwnd, child);
        child = child->next_sibling;
    }
}

static void win32_apply_layout_to_tree(dui_schema_node* n)
{
    dui_schema_node* child;
    if (!n) {
        return;
    }
    if (n->native && win32_is_leaf_kind(n->kind)) {
        MoveWindow((HWND)n->native, n->x, n->y, n->w, n->h, TRUE);
    }
    child = n->first_child;
    while (child) {
        win32_apply_layout_to_tree(child);
        child = child->next_sibling;
    }
}

static void win32_update_control_values(dui_window* win, dui_schema_node* n, int parent_visible)
{
    dui_schema_node* child;
    char text[256];
    u32 text_len;
    int visible;
    if (!win || !n) {
        return;
    }
    visible = parent_visible && win32_node_visible(win, n);
    if (n->native && win32_is_leaf_kind(n->kind)) {
        HWND h = (HWND)n->native;
        ShowWindow(h, visible ? SW_SHOW : SW_HIDE);
        EnableWindow(h, visible ? TRUE : FALSE);
        if (!visible) {
            /* Still recurse to ensure hidden subtrees are hidden too. */
            child = n->first_child;
            while (child) {
                win32_update_control_values(win, child, visible);
                child = child->next_sibling;
            }
            return;
        }
        if (n->kind == (u32)DUI_NODE_LABEL || n->kind == (u32)DUI_NODE_BUTTON) {
            text[0] = '\0';
            text_len = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_text(win->state, win->state_len, n->bind_id, text, (u32)sizeof(text), &text_len);
            }
            if (!text[0] && n->text) {
                strncpy(text, n->text, sizeof(text) - 1u);
                text[sizeof(text) - 1u] = '\0';
            }
            SetWindowTextA(h, text);
        } else if (n->kind == (u32)DUI_NODE_CHECKBOX) {
            u32 v = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
            }
            SendMessageA(h, BM_SETCHECK, (WPARAM)(v ? BST_CHECKED : BST_UNCHECKED), 0);
        } else if (n->kind == (u32)DUI_NODE_TEXT_FIELD) {
            text[0] = '\0';
            text_len = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_text(win->state, win->state_len, n->bind_id, text, (u32)sizeof(text), &text_len);
            }
            SetWindowTextA(h, text);
        } else if (n->kind == (u32)DUI_NODE_PROGRESS) {
            u32 v = 0u;
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_u32(win->state, win->state_len, n->bind_id, &v);
            }
            if (v > 1000u) v = 1000u;
            SendMessageA(h, PBM_SETRANGE, 0, MAKELPARAM(0, 1000));
            SendMessageA(h, PBM_SETPOS, (WPARAM)v, 0);
        } else if (n->kind == (u32)DUI_NODE_LIST) {
            u32 count = 0u;
            u32 selected_id = 0u;
            u32 i;
            win->suppress_events = 1u;
            SendMessageA(h, LB_RESETCONTENT, 0, 0);
            if (n->bind_id != 0u && win->state) {
                (void)dui_state_get_list_item_count(win->state, win->state_len, n->bind_id, &count);
                (void)dui_state_get_list_selected_item_id(win->state, win->state_len, n->bind_id, &selected_id);
            }
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
                        SendMessageA(h, LB_SETCURSEL, (WPARAM)idx, 0);
                    }
                }
            }
            win->suppress_events = 0u;
        }
    }

    child = n->first_child;
    while (child) {
        win32_update_control_values(win, child, visible);
        child = child->next_sibling;
    }
}

static void win32_relayout(dui_window* win)
{
    RECT rc;
    if (!win || !win->hwnd || !win->root) {
        return;
    }
    GetClientRect(win->hwnd, &rc);
    dui_schema_layout(win->root, 0, 0, (i32)(rc.right - rc.left), (i32)(rc.bottom - rc.top));
    win32_apply_layout_to_tree(win->root);
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
                win32_emit_action(ctx, n->id, n->action_id, 0u);
            }
            return 0;
        }
        if (n->kind == (u32)DUI_NODE_CHECKBOX) {
            if (notify == BN_CLICKED) {
                LRESULT st = SendMessageA(ctrl, BM_GETCHECK, 0, 0);
                u32 v = (st == BST_CHECKED) ? 1u : 0u;
                win32_emit_value_u32(ctx, n->id, (u32)DUI_VALUE_BOOL, v, 0u);
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
                win32_emit_value_text(ctx, n->id, buf, (u32)len);
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
                    win32_emit_value_u32(ctx, n->id, (u32)DUI_VALUE_LIST, (u32)((sel >= 0) ? sel : 0), item_id);
                } else if (notify == LBN_DBLCLK) {
                    win32_emit_action(ctx, n->id, n->action_id, item_id);
                }
            }
            return 0;
        }
        return 0;
    }

    if (msg == WM_SIZE) {
        win32_relayout(win);
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
    s_registered = 1;
    return 1;
}

static void win32_init_common_controls(void)
{
    INITCOMMONCONTROLSEX icc;
    memset(&icc, 0, sizeof(icc));
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_PROGRESS_CLASS;
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
    style = WS_OVERLAPPEDWINDOW;
    rect.left = 0;
    rect.top = 0;
    rect.right = w;
    rect.bottom = h;
    AdjustWindowRect(&rect, style, FALSE);

    win->hwnd = CreateWindowExA(
        0,
        dui_win32_class_name(),
        title,
        style,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        rect.right - rect.left,
        rect.bottom - rect.top,
        NULL,
        NULL,
        GetModuleHandleA(NULL),
        win);

    if (!win->hwnd) {
        free(win);
        return DUI_ERR_BACKEND_UNAVAILABLE;
    }
    ShowWindow(win->hwnd, SW_SHOW);
    UpdateWindow(win->hwnd);

    ctx->primary_window = win;
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
    win32_create_controls_for_tree(win, win->hwnd, win->root);
    win32_relayout(win);
#endif
    return DUI_OK;
}

static dui_result win32_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len)
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

#if defined(_WIN32)
    if (win->root) {
        win->suppress_events = 1u;
        win32_update_control_values(win, win->root, 1);
        win->suppress_events = 0u;
    }
#endif
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

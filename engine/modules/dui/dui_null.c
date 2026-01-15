/*
FILE: source/domino/dui/dui_null.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/dui_null
RESPONSIBILITY: Implements the DUI null/headless backend (no window; programmatic event queue).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, `source/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: Single-threaded UI driver expected.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Presentation-only; no simulation-affecting state.
VERSIONING / ABI / DATA FORMAT NOTES: `dui_api_v1` vtable; schema/state TLV are skip-unknown.
EXTENSION POINTS: Test/native handle extensions via query_interface.
*/
#include "dui/dui_api_v1.h"

#include <stdlib.h>
#include <string.h>

#include "dui_event_queue.h"
#include "dui_schema_parse.h"

typedef struct dui_context {
    dui_event_queue q;
    u32 quit_requested;
    domui_action_fn action_dispatch;
    void* action_user_ctx;
} dui_context;

typedef struct dui_window {
    unsigned char* schema;
    u32 schema_len;
    unsigned char* state;
    u32 state_len;
    dui_schema_node* root;
} dui_window;

static dui_result null_create_context(dui_context** out_ctx);
static void       null_destroy_context(dui_context* ctx);
static dui_result null_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win);
static void       null_destroy_window(dui_window* win);
static dui_result null_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len);
static dui_result null_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len);
static dui_result null_render(dui_window* win);
static dui_result null_pump(dui_context* ctx);
static int        null_poll_event(dui_context* ctx, dui_event_v1* out_ev);
static dui_result null_request_quit(dui_context* ctx);

static dom_abi_result null_query_interface(dom_iid iid, void** out_iface);
static void null_set_action_dispatch(dui_context* ctx, domui_action_fn fn, void* user_ctx);

static const char* null_backend_name(void) { return "null"; }

static dui_caps null_caps(void)
{
    /* Null backend parses schema/state and participates in the event flow,
     * but does not render to a real window. Cap bits are reported as supported
     * to avoid schema gating for headless tests.
     */
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
static dui_action_api_v1 g_action_api;

static dui_result null_test_post_event(dui_context* ctx, const dui_event_v1* ev)
{
    if (!ctx || !ev) {
        return DUI_ERR_NULL;
    }
    if (dui_event_queue_push(&ctx->q, ev) != 0) {
        return DUI_ERR;
    }
    if (ctx->action_dispatch && ev->type == (u32)DUI_EVENT_ACTION) {
        domui_event out_ev;
        memset(&out_ev, 0, sizeof(out_ev));
        out_ev.action_id = ev->u.action.action_id;
        out_ev.widget_id = ev->u.action.widget_id;
        out_ev.type = DOMUI_EVENT_CLICK;
        out_ev.modifiers = 0u;
        out_ev.backend_ext = (void*)0;
        if (ev->u.action.item_id != 0u) {
            out_ev.a.type = DOMUI_VALUE_U32;
            out_ev.a.u.v_u32 = ev->u.action.item_id;
        }
        ctx->action_dispatch(ctx->action_user_ctx, &out_ev);
    }
    return DUI_OK;
}

static void* null_get_native_window_handle(dui_window* win)
{
    (void)win;
    return (void*)0;
}

static void null_set_action_dispatch(dui_context* ctx, domui_action_fn fn, void* user_ctx)
{
    if (!ctx) {
        return;
    }
    ctx->action_dispatch = fn;
    ctx->action_user_ctx = user_ctx;
}

static dom_abi_result null_query_interface(dom_iid iid, void** out_iface)
{
    if (!out_iface) {
        return (dom_abi_result)DUI_ERR_NULL;
    }
    *out_iface = (void*)0;

    if (iid == DUI_IID_TEST_API_V1) {
        g_test_api.abi_version = DUI_API_ABI_VERSION;
        g_test_api.struct_size = (u32)sizeof(g_test_api);
        g_test_api.post_event = null_test_post_event;
        *out_iface = (void*)&g_test_api;
        return 0;
    }
    if (iid == DUI_IID_NATIVE_API_V1) {
        g_native_api.abi_version = DUI_API_ABI_VERSION;
        g_native_api.struct_size = (u32)sizeof(g_native_api);
        g_native_api.get_native_window_handle = null_get_native_window_handle;
        *out_iface = (void*)&g_native_api;
        return 0;
    }
    if (iid == DUI_IID_ACTION_API_V1) {
        g_action_api.abi_version = DUI_API_ABI_VERSION;
        g_action_api.struct_size = (u32)sizeof(g_action_api);
        g_action_api.set_action_dispatch = null_set_action_dispatch;
        *out_iface = (void*)&g_action_api;
        return 0;
    }
    return (dom_abi_result)DUI_ERR_UNSUPPORTED;
}

static const dui_api_v1 g_dui_null_api = {
    DOM_ABI_HEADER_INIT(DUI_API_ABI_VERSION, dui_api_v1),
    null_query_interface,

    null_backend_name,
    null_caps,

    null_create_context,
    null_destroy_context,
    null_create_window,
    null_destroy_window,

    null_set_schema_tlv,
    null_set_state_tlv,

    null_render,
    null_pump,
    null_poll_event,
    null_request_quit
};

const void* dom_dui_null_get_api(u32 requested_abi)
{
    if (requested_abi != DUI_API_ABI_VERSION) {
        return (const void*)0;
    }
    return (const void*)&g_dui_null_api;
}

static dui_result null_create_context(dui_context** out_ctx)
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
    *out_ctx = ctx;
    return DUI_OK;
}

static void null_destroy_context(dui_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

static dui_result null_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win)
{
    dui_window* win;
    (void)ctx;
    (void)desc;
    if (!out_win) {
        return DUI_ERR_NULL;
    }
    *out_win = (dui_window*)0;

    win = (dui_window*)malloc(sizeof(dui_window));
    if (!win) {
        return DUI_ERR;
    }
    memset(win, 0, sizeof(*win));
    *out_win = win;
    return DUI_OK;
}

static void null_destroy_window(dui_window* win)
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
    free(win);
}

static dui_result null_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len)
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

static dui_result null_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len)
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

static dui_result null_render(dui_window* win)
{
    (void)win;
    return DUI_OK;
}

static dui_result null_pump(dui_context* ctx)
{
    if (!ctx) {
        return DUI_ERR_NULL;
    }
    if (ctx->quit_requested) {
        dui_event_v1 ev;
        memset(&ev, 0, sizeof(ev));
        ev.abi_version = DUI_API_ABI_VERSION;
        ev.struct_size = (u32)sizeof(ev);
        ev.type = (u32)DUI_EVENT_QUIT;
        (void)dui_event_queue_push(&ctx->q, &ev);
        ctx->quit_requested = 0u;
    }
    return DUI_OK;
}

static int null_poll_event(dui_context* ctx, dui_event_v1* out_ev)
{
    if (!ctx || !out_ev) {
        return -1;
    }
    return dui_event_queue_pop(&ctx->q, out_ev);
}

static dui_result null_request_quit(dui_context* ctx)
{
    if (!ctx) {
        return DUI_ERR_NULL;
    }
    ctx->quit_requested = 1u;
    return DUI_OK;
}

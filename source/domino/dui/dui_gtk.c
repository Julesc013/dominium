/*
FILE: source/domino/dui/dui_gtk.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dui/dui_gtk
RESPONSIBILITY: GTK native backend placeholder (registered only when enabled on UNIX hosts).
ALLOWED DEPENDENCIES: `include/dui/**`, `include/domino/**`, `source/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: Single-threaded UI driver expected.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Presentation-only.
VERSIONING / ABI / DATA FORMAT NOTES: `dui_api_v1` vtable.
EXTENSION POINTS: Replace placeholder with real GTK2/GTK3 implementation.
*/
#include "dui/dui_api_v1.h"

#include <stdlib.h>
#include <string.h>

#include "dui_event_queue.h"

typedef struct dui_context {
    dui_event_queue q;
} dui_context;

typedef struct dui_window {
    int unused;
} dui_window;

static dui_result gtk_create_context(dui_context** out_ctx);
static void       gtk_destroy_context(dui_context* ctx);
static dui_result gtk_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win);
static void       gtk_destroy_window(dui_window* win);
static dui_result gtk_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len);
static dui_result gtk_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len);
static dui_result gtk_render(dui_window* win);
static dui_result gtk_pump(dui_context* ctx);
static int        gtk_poll_event(dui_context* ctx, dui_event_v1* out_ev);
static dui_result gtk_request_quit(dui_context* ctx);

static dom_abi_result gtk_query_interface(dom_iid iid, void** out_iface);

static const char* gtk_backend_name(void) { return "gtk"; }

static dui_caps gtk_caps(void)
{
    /* Placeholder reports core widget bits but create_window returns unavailable
     * until the GTK implementation is wired in.
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

static dui_result gtk_test_post_event(dui_context* ctx, const dui_event_v1* ev)
{
    if (!ctx || !ev) {
        return DUI_ERR_NULL;
    }
    if (dui_event_queue_push(&ctx->q, ev) != 0) {
        return DUI_ERR;
    }
    return DUI_OK;
}

static void* gtk_get_native_window_handle(dui_window* win)
{
    (void)win;
    return (void*)0;
}

static dom_abi_result gtk_query_interface(dom_iid iid, void** out_iface)
{
    if (!out_iface) {
        return (dom_abi_result)DUI_ERR_NULL;
    }
    *out_iface = (void*)0;

    if (iid == DUI_IID_TEST_API_V1) {
        g_test_api.abi_version = DUI_API_ABI_VERSION;
        g_test_api.struct_size = (u32)sizeof(g_test_api);
        g_test_api.post_event = gtk_test_post_event;
        *out_iface = (void*)&g_test_api;
        return 0;
    }
    if (iid == DUI_IID_NATIVE_API_V1) {
        g_native_api.abi_version = DUI_API_ABI_VERSION;
        g_native_api.struct_size = (u32)sizeof(g_native_api);
        g_native_api.get_native_window_handle = gtk_get_native_window_handle;
        *out_iface = (void*)&g_native_api;
        return 0;
    }
    return (dom_abi_result)DUI_ERR_UNSUPPORTED;
}

static const dui_api_v1 g_dui_gtk_api = {
    DOM_ABI_HEADER_INIT(DUI_API_ABI_VERSION, dui_api_v1),
    gtk_query_interface,

    gtk_backend_name,
    gtk_caps,

    gtk_create_context,
    gtk_destroy_context,
    gtk_create_window,
    gtk_destroy_window,

    gtk_set_schema_tlv,
    gtk_set_state_tlv,

    gtk_render,
    gtk_pump,
    gtk_poll_event,
    gtk_request_quit
};

const void* dom_dui_gtk_get_api(u32 requested_abi)
{
    if (requested_abi != DUI_API_ABI_VERSION) {
        return (const void*)0;
    }
    return (const void*)&g_dui_gtk_api;
}

static dui_result gtk_create_context(dui_context** out_ctx)
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
    *out_ctx = ctx;
    return DUI_OK;
}

static void gtk_destroy_context(dui_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

static dui_result gtk_create_window(dui_context* ctx, const dui_window_desc_v1* desc, dui_window** out_win)
{
    (void)ctx;
    (void)desc;
    if (!out_win) {
        return DUI_ERR_NULL;
    }
    *out_win = (dui_window*)0;
    return DUI_ERR_BACKEND_UNAVAILABLE;
}

static void gtk_destroy_window(dui_window* win)
{
    (void)win;
}

static dui_result gtk_set_schema_tlv(dui_window* win, const void* schema_tlv, u32 schema_len)
{
    (void)win;
    (void)schema_tlv;
    (void)schema_len;
    return DUI_OK;
}

static dui_result gtk_set_state_tlv(dui_window* win, const void* state_tlv, u32 state_len)
{
    (void)win;
    (void)state_tlv;
    (void)state_len;
    return DUI_OK;
}

static dui_result gtk_render(dui_window* win)
{
    (void)win;
    return DUI_OK;
}

static dui_result gtk_pump(dui_context* ctx)
{
    (void)ctx;
    return DUI_OK;
}

static int gtk_poll_event(dui_context* ctx, dui_event_v1* out_ev)
{
    if (!ctx || !out_ev) {
        return -1;
    }
    return dui_event_queue_pop(&ctx->q, out_ev);
}

static dui_result gtk_request_quit(dui_context* ctx)
{
    (void)ctx;
    return DUI_OK;
}


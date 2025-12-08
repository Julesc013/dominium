#include "domino/ui.h"

#include <stdlib.h>
#include <string.h>

struct dom_ui_context {
    dom_ui_desc desc;
    int         running;
};

struct dom_ui_window {
    int placeholder;
};

int dom_ui_create(const dom_ui_desc* desc, dom_ui_context** out_ctx)
{
    dom_ui_context* ctx;
    dom_ui_desc local_desc;

    if (!out_ctx) {
        return -1;
    }
    *out_ctx = NULL;

    ctx = (dom_ui_context*)malloc(sizeof(dom_ui_context));
    if (!ctx) {
        return -1;
    }
    memset(ctx, 0, sizeof(*ctx));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }

    ctx->desc = local_desc;
    ctx->desc.struct_size = sizeof(dom_ui_desc);
    ctx->desc.struct_version = local_desc.struct_version;
    ctx->running = 0;

    *out_ctx = ctx;
    return 0;
}

void dom_ui_destroy(dom_ui_context* ctx)
{
    if (!ctx) {
        return;
    }
    free(ctx);
}

int dom_ui_run(dom_ui_context* ctx)
{
    if (!ctx) {
        return -1;
    }
    ctx->running = 1;
    return 0;
}

int dom_ui_open_window(dom_ui_context* ctx, dom_ui_window** out_window)
{
    dom_ui_window* win;

    (void)ctx;
    if (!out_window) {
        return -1;
    }
    *out_window = NULL;

    win = (dom_ui_window*)malloc(sizeof(dom_ui_window));
    if (!win) {
        return -1;
    }
    memset(win, 0, sizeof(*win));
    *out_window = win;
    return 0;
}

int dom_ui_close_window(dom_ui_window* win)
{
    if (!win) {
        return -1;
    }
    free(win);
    return 0;
}

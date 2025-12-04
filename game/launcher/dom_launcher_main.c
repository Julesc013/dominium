#include <stdio.h>
#include <string.h>

#include "dom_core_err.h"
#include "dom_core_types.h"
#include "dom_platform_win32.h"
#include "dom_render_api.h"
#include "dom_render_debug.h"

static void dom_launcher_log_err(const char *msg, dom_err_t err)
{
    printf("%s (err=%d)\n", msg, (int)err);
}

int main(void)
{
    DomPlatformWin32Window *win = 0;
    DomRenderer renderer;
    dom_render_config render_cfg;
    dom_render_caps render_caps;
    dom_err_t err;
    dom_u32 win_w = 1280;
    dom_u32 win_h = 720;
    dom_u32 cur_w;
    dom_u32 cur_h;
    DomColor clear = 0xFF1E1E1E;

    memset(&renderer, 0, sizeof(renderer));
    memset(&render_cfg, 0, sizeof(render_cfg));
    memset(&render_caps, 0, sizeof(render_caps));

    err = dom_platform_win32_create_window("Dominium MVP", win_w, win_h, 0, &win);
    if (err != DOM_OK) {
        dom_launcher_log_err("Failed to create window", err);
        return 1;
    }

    render_cfg.backend = DOM_RENDER_BACKEND_SOFTWARE;
    render_cfg.mode = DOM_RENDER_MODE_VECTOR_ONLY;
    render_cfg.width = win_w;
    render_cfg.height = win_h;
    render_cfg.platform_window = dom_platform_win32_native_handle(win);

    err = dom_render_create(&renderer,
                            render_cfg.backend,
                            &render_cfg,
                            &render_caps);
    if (err != DOM_OK) {
        dom_launcher_log_err("Failed to create renderer", err);
        dom_platform_win32_destroy_window(win);
        return 1;
    }

    while (!dom_platform_win32_should_close(win)) {
        dom_platform_win32_pump_messages(win);
        dom_platform_win32_get_size(win, &cur_w, &cur_h);
        if (cur_w != renderer.width || cur_h != renderer.height) {
            dom_render_resize(&renderer, cur_w, cur_h);
        }

        dom_render_begin(&renderer, clear);
        dom_render_debug_draw_grid(&renderer, 64, 0xFF303040);
        dom_render_debug_draw_crosshair(&renderer, 0xFFFFAA00);
        dom_render_submit(&renderer, 0, 0);
        dom_render_present(&renderer);
    }

    dom_render_destroy(&renderer);
    dom_platform_win32_destroy_window(win);
    return 0;
}

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
    dom_err_t err;
    dom_u32 win_w = 1280;
    dom_u32 win_h = 720;
    dom_u32 cur_w;
    dom_u32 cur_h;
    DomColor clear = 0xFF1E1E1E;

    memset(&renderer, 0, sizeof(renderer));

    err = dom_platform_win32_create_window("Dominium MVP", win_w, win_h, 0, &win);
    if (err != DOM_OK) {
        dom_launcher_log_err("Failed to create window", err);
        return 1;
    }

    err = dom_render_create(&renderer,
                            DOM_RENDER_BACKEND_DX9,
                            win_w,
                            win_h,
                            dom_platform_win32_native_handle(win));
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
        dom_render_submit(&renderer);
        dom_render_present(&renderer);
    }

    dom_render_destroy(&renderer);
    dom_platform_win32_destroy_window(win);
    return 0;
}

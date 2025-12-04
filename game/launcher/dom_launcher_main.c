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

static void dom_launcher_draw_ui(DomRenderer *r, dom_u32 w, dom_u32 h)
{
    DomRect rect;
    DomColor bg = 0xFF0F0F0F;
    DomColor chrome = 0xFF2B2B2B;
    DomColor tab_bar = 0xFF1E1E1E;
    DomColor tab_active = 0xFF3A3A3A;
    DomColor tab_inactive = 0xFF2A2A2A;
    DomColor content_bg = 0xFF151515;
    DomColor sidebar = 0xFF1C1C1C;
    DomColor footer = 0xFF101010;
    DomColor accent = 0xFF4AA3FF;
    DomColor border = 0xFF444444;
    DomColor button = 0xFF2D2D2D;
    DomColor button_border = 0xFF505050;

    /* Background */
    rect.x = 0; rect.y = 0; rect.w = (dom_i32)w; rect.h = (dom_i32)h;
    dom_render_rect(r, &rect, bg);

    /* Top chrome bar */
    rect.x = 0; rect.y = 0; rect.w = (dom_i32)w; rect.h = 28;
    dom_render_rect(r, &rect, chrome);

    /* Tab bar */
    rect.x = 0; rect.y = 28; rect.w = (dom_i32)w; rect.h = 28;
    dom_render_rect(r, &rect, tab_bar);

    /* Tabs */
    {
        dom_i32 tx = 8;
        dom_i32 ty = 28;
        dom_i32 th = 28;
        dom_i32 tw = 120;
        int i;
        for (i = 0; i < 3; ++i) {
            rect.x = tx + i * (tw + 4);
            rect.y = ty;
            rect.w = tw;
            rect.h = th;
            dom_render_rect(r, &rect, (i == 0) ? tab_active : tab_inactive);
            /* tab underline for active */
            if (i == 0) {
                DomRect u;
                u.x = rect.x;
                u.y = rect.y + th - 3;
                u.w = rect.w;
                u.h = 3;
                dom_render_rect(r, &u, accent);
            }
        }
    }

    /* Content area */
    rect.x = 0; rect.y = 56; rect.w = (dom_i32)w; rect.h = (dom_i32)(h - 128);
    dom_render_rect(r, &rect, content_bg);

    /* Sidebar (links) */
    rect.x = (dom_i32)(w - 240);
    rect.y = 64;
    rect.w = 224;
    rect.h = (dom_i32)(h - 144);
    dom_render_rect(r, &rect, sidebar);

    /* Sidebar link slots */
    {
        dom_i32 sx = rect.x + 12;
        dom_i32 sy = rect.y + 12;
        dom_i32 sw = rect.w - 24;
        dom_i32 sh = 26;
        int i;
        for (i = 0; i < 10; ++i) {
            DomRect slot;
            DomRect underline;
            slot.x = sx;
            slot.y = sy + i * (sh + 6);
            slot.w = sw;
            slot.h = sh;
            dom_render_rect(r, &slot, 0xFF232323);
            underline.x = slot.x;
            underline.y = slot.y + sh - 2;
            underline.w = slot.w;
            underline.h = 2;
            dom_render_rect(r, &underline, border);
        }
    }

    /* Main content block */
    rect.x = 12;
    rect.y = 64;
    rect.w = (dom_i32)(w - 264);
    rect.h = (dom_i32)(h - 144);
    dom_render_rect(r, &rect, 0xFF181818);

    /* Content headline block */
    {
        DomRect hero;
        DomRect underline;
        hero.x = rect.x + 12;
        hero.y = rect.y + 12;
        hero.w = rect.w - 24;
        hero.h = 80;
        dom_render_rect(r, &hero, 0xFF202020);
        underline.x = hero.x;
        underline.y = hero.y + 76;
        underline.w = hero.w;
        underline.h = 4;
        dom_render_rect(r, &underline, accent);
    }

    /* Content paragraphs (placeholder bars) */
    {
        dom_i32 px = rect.x + 12;
        dom_i32 py = rect.y + 108;
        dom_i32 pw = rect.w - 24;
        int i;
        for (i = 0; i < 5; ++i) {
            DomRect line;
            line.x = px;
            line.y = py + i * 26;
            line.w = pw;
            line.h = 18;
            dom_render_rect(r, &line, 0xFF1F1F1F);
        }
    }

    /* Footer */
    rect.x = 0; rect.y = (dom_i32)(h - 72); rect.w = (dom_i32)w; rect.h = 72;
    dom_render_rect(r, &rect, footer);

    /* Footer profile dropdown stub */
    {
        DomRect ddl;
        ddl.x = 12;
        ddl.y = (dom_i32)(h - 60);
        ddl.w = 200;
        ddl.h = 32;
        dom_render_rect(r, &ddl, button_border);
        ddl.x += 2; ddl.y += 2; ddl.w -= 4; ddl.h -= 4;
        dom_render_rect(r, &ddl, button);
    }

    /* Footer buttons */
    {
        DomRect btn1;
        DomRect btn2;
        btn1.x = 220; btn1.y = (dom_i32)(h - 60); btn1.w = 120; btn1.h = 32;
        btn2.x = 348; btn2.y = (dom_i32)(h - 60); btn2.w = 120; btn2.h = 32;
        dom_render_rect(r, &btn1, button_border);
        dom_render_rect(r, &btn2, button_border);
        btn1.x += 2; btn1.y += 2; btn1.w -= 4; btn1.h -= 4;
        btn2.x += 2; btn2.y += 2; btn2.w -= 4; btn2.h -= 4;
        dom_render_rect(r, &btn1, button);
        dom_render_rect(r, &btn2, button);
    }

    /* Play button */
    {
        DomRect play;
        play.x = (dom_i32)(w / 2 - 100);
        play.y = (dom_i32)(h - 64);
        play.w = 200;
        play.h = 48;
        dom_render_rect(r, &play, button_border);
        play.x += 2; play.y += 2; play.w -= 4; play.h -= 4;
        dom_render_rect(r, &play, accent);
    }

    /* Status area right */
    {
        DomRect status;
        status.x = (dom_i32)(w - 240);
        status.y = (dom_i32)(h - 60);
        status.w = 220;
        status.h = 32;
        dom_render_rect(r, &status, button_border);
        status.x += 2; status.y += 2; status.w -= 4; status.h -= 4;
        dom_render_rect(r, &status, button);
    }
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
        dom_launcher_draw_ui(&renderer, renderer.width, renderer.height);
        dom_render_submit(&renderer, 0, 0);
        dom_render_present(&renderer);
    }

    dom_render_destroy(&renderer);
    dom_platform_win32_destroy_window(win);
    return 0;
}

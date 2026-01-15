/*
FILE: source/dominium/launcher/gui/launch_gui.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/gui/launch_gui
RESPONSIBILITY: Implements `launch_gui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "domino/sys.h"
#include "domino/gfx.h"
#include "domino/core.h"
#include "domino/view.h"
#include "domino/model_table.h"
#include "domino/canvas.h"
#include "domino/inst.h"
#include "dominium/launch_api.h"

typedef struct gui_tab {
    const char* id;
    const char* title;
    const char* view_id;
} gui_tab;

static gui_tab g_tabs[] = {
    { "tab_instances", "Instances", "view_instances" },
    { "tab_packages",  "Packages",  "view_packages"  },
    { "tab_mods",      "Mods",      "view_mods"      },
    { "tab_world",     "World",     "view_world_surface" }
};

#define GUI_TAB_COUNT ((uint32_t)(sizeof(g_tabs) / sizeof(g_tabs[0])))

static uint32_t rgba(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
{
    return ((uint32_t)a << 24) | ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
}

static void gui_draw_rect(dcvs* c, int x, int y, int w, int h, uint32_t color)
{
    dgfx_sprite_t spr;
    spr.x = x;
    spr.y = y;
    spr.w = w;
    spr.h = h;
    spr.color_rgba = color;
    dcvs_draw_sprite(c, &spr);
}

static void gui_draw_tab_bar(dcvs* c, int width, int height, uint32_t active_idx)
{
    uint32_t i;
    int tab_w = (GUI_TAB_COUNT > 0u) ? width / (int)GUI_TAB_COUNT : width;
    gui_draw_rect(c, 0, 0, width, 32, rgba(30, 30, 30, 255));
    for (i = 0u; i < GUI_TAB_COUNT; ++i) {
        int x = (int)(i * tab_w);
        uint32_t color = (i == active_idx) ? rgba(60, 90, 140, 255) : rgba(50, 50, 50, 255);
        gui_draw_rect(c, x, 0, tab_w - 1, 30, color);
        /* Minimal text; placeholder rectangles act as tabs */
    }
}

static void gui_draw_status(dcvs* c, int width, int height, const char* text)
{
    int y = height - 24;
    gui_draw_rect(c, 0, y, width, 24, rgba(25, 25, 25, 255));
    (void)text; /* Text rendering would go here when a font backend is wired */
}

static uint32_t gui_tab_from_view(const char* view_id)
{
    uint32_t i;
    if (!view_id) return 0u;
    for (i = 0u; i < GUI_TAB_COUNT; ++i) {
        if (g_tabs[i].view_id && strcmp(g_tabs[i].view_id, view_id) == 0) {
            return i;
        }
    }
    return 0u;
}

static void gui_render_table(dcvs* c, dom_core* core, const char* table_id, int x, int y, int w, int h)
{
    dom_table_meta meta;
    uint32_t row;
    uint32_t col;
    int line = 0;
    char cell[256];

    gui_draw_rect(c, x, y, w, h, rgba(15, 15, 15, 255));
    if (!dom_table_get_meta(core, table_id, &meta)) {
        return;
    }

    for (row = 0u; row < meta.row_count && y + 4 + line * 18 < y + h; ++row) {
        for (col = 0u; col < meta.col_count && col < 4u; ++col) {
            if (!dom_table_get_cell(core, table_id, row, col, cell, sizeof(cell))) {
                cell[0] = '\0';
            }
            /* Placeholder: draw tiny rects per cell */
            gui_draw_rect(c, x + (int)col * (w / 4), y + 4 + line * 18, (w / 4) - 2, 16, rgba(40, 40, 40, 255));
            (void)cell; /* text rendering omitted in stub */
        }
        line += 1;
    }
}

static bool gui_build_world(dom_core* core, dom_launch_snapshot* snap, dom_gfx_buffer* out)
{
    if (!out) {
        return false;
    }
    memset(out, 0, sizeof(*out));

    if (!dom_canvas_build(core, snap->current_instance, "world_surface", out)) {
        return false;
    }
    return true;
}

int main(int argc, char** argv)
{
    dsys_result     dres;
    dom_core_desc   core_desc;
    dom_core*       core;
    dom_launch_desc ldesc;
    dom_launch_ctx* ctx;
    dsys_window_desc wdesc;
    dsys_window*    win;
    dgfx_desc       gdesc;
    int             running = 1;

    (void)argc;
    (void)argv;

    dres = dsys_init();
    if (dres != DSYS_OK) {
        fprintf(stderr, "dsys_init failed (%d)\n", (int)dres);
        return 1;
    }

    memset(&core_desc, 0, sizeof(core_desc));
    core_desc.api_version = 1;
    core = dom_core_create(&core_desc);
    if (!core) {
        fprintf(stderr, "Failed to create dom_core\n");
        dsys_shutdown();
        return 1;
    }

    memset(&wdesc, 0, sizeof(wdesc));
    wdesc.width = 1280;
    wdesc.height = 720;
    wdesc.mode = DWIN_MODE_WINDOWED;
    win = dsys_window_create(&wdesc);
    if (!win) {
        fprintf(stderr, "Failed to create window\n");
        dom_core_destroy(core);
        dsys_shutdown();
        return 1;
    }

    memset(&gdesc, 0, sizeof(gdesc));
    gdesc.backend = DGFX_BACKEND_SOFT;
    gdesc.window = win;
    gdesc.width = wdesc.width;
    gdesc.height = wdesc.height;
    if (!dgfx_init(&gdesc)) {
        fprintf(stderr, "dgfx_init failed\n");
        dsys_window_destroy(win);
        dom_core_destroy(core);
        dsys_shutdown();
        return 1;
    }

    memset(&ldesc, 0, sizeof(ldesc));
    ldesc.struct_size = sizeof(ldesc);
    ldesc.struct_version = 1;
    ldesc.core = core;
    ldesc.ui_mode = DOM_UI_MODE_GUI;
    ldesc.product_id = "dominium";
    ldesc.version = "0.0.0";
    ctx = dom_launch_create(&ldesc);
    if (!ctx) {
        fprintf(stderr, "Failed to create launcher ctx\n");
        dgfx_shutdown();
        dsys_window_destroy(win);
        dom_core_destroy(core);
        dsys_shutdown();
        return 1;
    }

    while (running) {
        dsys_event ev;
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                running = 0;
            } else if (ev.type == DSYS_EVENT_WINDOW_RESIZED) {
                gdesc.width = ev.payload.window.width;
                gdesc.height = ev.payload.window.height;
                dgfx_resize(gdesc.width, gdesc.height);
            } else if (ev.type == DSYS_EVENT_KEY_DOWN) {
                int key = ev.payload.key.key;
                switch (key) {
                case 282: /* F1 */ dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_INSTANCES, 0u, NULL); break;
                case 283: /* F2 */ dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_PACKAGES, 0u, NULL); break;
                case 284: /* F3 */ dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_PACKAGES, 0u, NULL); break;
                case 285: /* F4 */ dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_VIEW_WORLD, 0u, "view_world_surface"); break;
                case 286: /* F5 */ dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LAUNCH_INSTANCE, 0u, NULL); break;
                case 27:  /* ESC */ running = 0; break;
                default:
                    break;
                }
            }
        }

        {
            dom_launch_snapshot snap;
            dcvs*               canvas;
            int                 width = gdesc.width;
            int                 height = gdesc.height;
            uint32_t            active_tab;
            dom_gfx_buffer      world_buf;
            int                 have_world = 0;

            memset(&snap, 0, sizeof(snap));
            snap.struct_size = sizeof(snap);
            snap.struct_version = 1;
            dom_launch_get_snapshot(ctx, &snap);
            active_tab = gui_tab_from_view(snap.current_view_id);
            memset(&world_buf, 0, sizeof(world_buf));

            canvas = dgfx_get_frame_canvas();
            dcvs_reset(canvas);

            gui_draw_rect(canvas, 0, 0, width, height, rgba(20, 20, 25, 255));
            gui_draw_tab_bar(canvas, width, height, active_tab);

            /* Content area */
            if (active_tab == 0u) {
                gui_render_table(canvas, core, "instances_table", 8, 40, width - 16, height - 80);
            } else if (active_tab == 1u) {
                gui_render_table(canvas, core, "packages_table", 8, 40, width - 16, height - 80);
            } else if (active_tab == 2u) {
                gui_render_table(canvas, core, "mods_table", 8, 40, width - 16, height - 80);
            } else if (active_tab == 3u) {
                have_world = gui_build_world(core, &snap, &world_buf) ? 1 : 0;
            }

            gui_draw_status(canvas, width, height, "F1-4 tabs, F5 launch, ESC quit");

            dgfx_begin_frame();
            if (have_world && world_buf.data && world_buf.size > 0) {
                dgfx_cmd_buffer cb;
                cb.data = world_buf.data;
                cb.size = (uint32_t)world_buf.size;
                cb.capacity = (uint32_t)world_buf.capacity;
                dgfx_execute(&cb);
            }
            dgfx_execute(dcvs_get_cmd_buffer(canvas));
            dgfx_end_frame();

            if (have_world && world_buf.data) {
                free(world_buf.data);
            }
        }
    }

    dom_launch_destroy(ctx);
    dgfx_shutdown();
    dsys_window_destroy(win);
    dom_core_destroy(core);
    dsys_shutdown();
    return 0;
}

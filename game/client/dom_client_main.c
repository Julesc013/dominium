#include "dom_client_main.h"

#include <stdio.h>
#include <string.h>

#include "core/dom_core_err.h"
#include "core/dom_core_types.h"
#include "platform/win32/dom_platform_win32.h"
#include "render/dom_render_api.h"
#include "render/dom_render_debug.h"
#include "sim/dom_sim_world.h"

#define DOM_KEY_ESC     0x1B
#define DOM_KEY_UP      0x26
#define DOM_KEY_DOWN    0x28
#define DOM_KEY_LEFT    0x25
#define DOM_KEY_RIGHT   0x27

/* ------------------------------------------------------------
 * Simple camera state (2D + stub 3D)
 * ------------------------------------------------------------ */
typedef struct DomClientCamera2D {
    dom_i64 x;
    dom_i64 y;
    dom_i32 zoom; /* integer zoom level, >=1 */
} DomClientCamera2D;

typedef struct DomClientCamera3D {
    dom_i64 x;
    dom_i64 y;
    dom_i64 z;
    dom_i32 yaw_deg;
    dom_i32 pitch_deg;
} DomClientCamera3D;

typedef struct DomClientState {
    DomClientCamera2D cam2d;
    DomClientCamera3D cam3d;
    dom_bool8 use_3d;
    dom_bool8 toggle_pressed;
} DomClientState;

static void dom_client_state_init(DomClientState *st)
{
    if (!st) return;
    memset(st, 0, sizeof(*st));
    st->cam2d.zoom = 1;
    st->cam3d.z = 10;
    st->cam3d.yaw_deg = 0;
    st->cam3d.pitch_deg = 0;
}

/* ------------------------------------------------------------
 * Input handling
 * ------------------------------------------------------------ */
static void dom_client_handle_input(DomClientState *st,
                                    const DomPlatformInputFrame *in)
{
    const dom_i32 pan_speed = 32;
    const dom_i32 zoom_min = 1;
    const dom_i32 zoom_max = 8;

    if (!st || !in) return;

    if (in->key_down['W'] || in->key_down[DOM_KEY_UP]) {
        st->cam2d.y -= pan_speed;
    }
    if (in->key_down['S'] || in->key_down[DOM_KEY_DOWN]) {
        st->cam2d.y += pan_speed;
    }
    if (in->key_down['A'] || in->key_down[DOM_KEY_LEFT]) {
        st->cam2d.x -= pan_speed;
    }
    if (in->key_down['D'] || in->key_down[DOM_KEY_RIGHT]) {
        st->cam2d.x += pan_speed;
    }

    if (in->key_down['Q']) {
        if (st->cam2d.zoom > zoom_min) {
            st->cam2d.zoom -= 1;
        }
    }
    if (in->key_down['E']) {
        if (st->cam2d.zoom < zoom_max) {
            st->cam2d.zoom += 1;
        }
    }

    /* Toggle 3D mode on T press (edge) */
    if (in->key_down['T']) {
        if (!st->toggle_pressed) {
            st->use_3d = st->use_3d ? 0 : 1;
            st->toggle_pressed = 1;
        }
    } else {
        st->toggle_pressed = 0;
    }

    /* Simple 3D camera motion */
    if (st->use_3d) {
        if (in->key_down['W']) st->cam3d.z += 1;
        if (in->key_down['S']) st->cam3d.z -= 1;
        if (in->key_down['A']) st->cam3d.x -= 1;
        if (in->key_down['D']) st->cam3d.x += 1;
        if (in->key_down['R']) st->cam3d.y += 1;
        if (in->key_down['F']) st->cam3d.y -= 1;
    }
}

/* ------------------------------------------------------------
 * Rendering helpers
 * ------------------------------------------------------------ */
static void dom_client_draw_scene(DomRenderer *renderer,
                                  const DomClientState *st)
{
    dom_i32 spacing;
    if (!renderer || !st) return;

    /* Simple grid spacing scales with zoom */
    spacing = 64;
    if (st->cam2d.zoom > 1) {
        spacing = spacing / st->cam2d.zoom;
        if (spacing < 4) spacing = 4;
    }

    dom_render_debug_draw_grid(renderer, spacing, 0xFF2A2A2A);
    dom_render_debug_draw_crosshair(renderer, st->use_3d ? 0xFF00AAFF : 0xFFFFAA00);
}

/* ------------------------------------------------------------
 * Main loop
 * ------------------------------------------------------------ */
int dom_client_run(void)
{
    DomPlatformWin32Window *win = 0;
    DomRenderer renderer;
    DomSimWorld *world = 0;
    DomSimConfig sim_cfg;
    DomPlatformInputFrame input;
    DomClientState client;
    dom_err_t err;
    dom_u64 last_time;
    dom_u64 now;
    dom_u64 accum_ms;
    const dom_u32 tick_ms = 1000 / 60; /* 60 UPS */
    dom_bool8 running = 1;

    dom_client_state_init(&client);
    memset(&renderer, 0, sizeof(renderer));
    memset(&sim_cfg, 0, sizeof(sim_cfg));
    memset(&input, 0, sizeof(input));

    sim_cfg.target_ups = 60;
    sim_cfg.num_lanes = 1;

    err = dom_platform_win32_create_window("Dominium Client MVP", 1280, 720, 0, &win);
    if (err != DOM_OK) {
        printf("Platform init failed (%d)\n", (int)err);
        return 1;
    }

    err = dom_render_create(&renderer,
                            DOM_RENDER_BACKEND_DX9,
                            1280,
                            720,
                            dom_platform_win32_native_handle(win));
    if (err != DOM_OK) {
        /* Fallback to null renderer for headless validation */
        err = dom_render_create(&renderer,
                                DOM_RENDER_BACKEND_NULL,
                                1280,
                                720,
                                dom_platform_win32_native_handle(win));
        if (err != DOM_OK) {
            printf("Renderer init failed (%d)\n", (int)err);
            dom_platform_win32_destroy_window(win);
            return 1;
        }
    }

    err = dom_sim_world_create(&sim_cfg, &world);
    if (err != DOM_OK) {
        printf("Sim world init failed (%d)\n", (int)err);
        dom_render_destroy(&renderer);
        dom_platform_win32_destroy_window(win);
        return 1;
    }

    last_time = dom_platform_win32_now_msec();
    accum_ms = 0;

    while (running && !dom_platform_win32_should_close(win)) {
        dom_platform_win32_pump_messages(win);
        dom_platform_win32_poll_input(win, &input);

        if (input.key_down[DOM_KEY_ESC]) {
            running = 0;
            break;
        }

        now = dom_platform_win32_now_msec();
        accum_ms += (now - last_time);
        last_time = now;

        while (accum_ms >= tick_ms) {
            dom_client_handle_input(&client, &input);
            dom_sim_world_step(world);
            accum_ms -= tick_ms;
        }

        dom_render_begin(&renderer, 0xFF101010);
        dom_client_draw_scene(&renderer, &client);
        dom_render_submit(&renderer);
        dom_render_present(&renderer);
        dom_platform_win32_sleep_msec(1);
    }

    dom_sim_world_destroy(world);
    dom_render_destroy(&renderer);
    dom_platform_win32_destroy_window(win);
    return 0;
}

int main(void)
{
    return dom_client_run();
}

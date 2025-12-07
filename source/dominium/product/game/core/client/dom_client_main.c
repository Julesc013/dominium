#include "dom_client_main.h"

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "dom_core/dom_core_err.h"
#include "dom_core/dom_core_types.h"
#include "dom_core/dom_core_version.h"
#include "dom_priv/dom_keys.h"
#include "dominium/dom_rend.h"
#include "dom_render_debug.h"
#include "sim/dom_sim_world.h"
#include "input/dom_input_actions.h"
#include "input/dom_input_mapping.h"

/* Platform stubs (Win32-specific functions not wired through dom_plat yet). */
typedef struct DomPlatformWin32Window {
    int stub;
} DomPlatformWin32Window;

typedef struct DomPlatformInputFrame {
    dom_bool8 key_down[DOM_KEYCODE_MAX];
    dom_bool8 mouse_down[3];
    int wheel_delta;
    int mouse_x;
    int mouse_y;
} DomPlatformInputFrame;

static dom_err_t dom_platform_win32_create_window(const char *title, int w, int h, int fullscreen, DomPlatformWin32Window **out_win)
{
    (void)title; (void)w; (void)h; (void)fullscreen;
    if (out_win) *out_win = 0;
    return DOM_ERR_NOT_IMPLEMENTED;
}

static void dom_platform_win32_destroy_window(DomPlatformWin32Window *win) { (void)win; }
static void *dom_platform_win32_native_handle(DomPlatformWin32Window *win) { (void)win; return 0; }
static void dom_platform_win32_set_title(DomPlatformWin32Window *win, const char *title) { (void)win; (void)title; }
static dom_u64 dom_platform_win32_now_msec(void) { return 0; }
static int dom_platform_win32_should_close(DomPlatformWin32Window *win) { (void)win; return 1; }
static void dom_platform_win32_pump_messages(DomPlatformWin32Window *win) { (void)win; }
static void dom_platform_win32_poll_input(DomPlatformWin32Window *win, DomPlatformInputFrame *out) { (void)win; if (out) memset(out, 0, sizeof(*out)); }
static void dom_platform_win32_sleep_msec(dom_u32 ms) { (void)ms; }

#define DOM_CLAMP(v, lo, hi) (((v) < (lo)) ? (lo) : (((v) > (hi)) ? (hi) : (v)))
#define DOM_COLOR_TEXT 0xFFFFFFFFu
#define DOM_COLOR_ACCENT 0xFFFFAA00u
#define DOM_COLOR_ACCENT_ALT 0xFF00AAFFu
#define DOM_COLOR_GRID 0xFF2A2A2Au
#define DOM_COLOR_GRID_DENSE 0xFF1A1A1Au
#define DOM_COLOR_BG 0xFF101010u

typedef enum DomClientDebugMode {
    DOM_DEBUG_OFF = 0,
    DOM_DEBUG_BASIC = 1,
    DOM_DEBUG_FULL = 2
} DomClientDebugMode;

typedef enum DomClientViewKind {
    DOM_VIEW_KIND_TOPDOWN = 0,
    DOM_VIEW_KIND_FIRST_PERSON = 1
} DomClientViewKind;

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

typedef struct DomClientStats {
    dom_u64 tick_count;
    dom_u64 frame_count;
    dom_u32 fps;
    dom_u32 ups;
    dom_u32 frame_accum;
    dom_u32 tick_accum;
    dom_u64 last_stats_ms;
    dom_u64 start_ms;
} DomClientStats;

typedef struct DomClientSelection {
    dom_bool8 has_selection;
    dom_i32 world_x;
    dom_i32 world_y;
    dom_i32 layer;
    dom_i32 quickbar_slot;
} DomClientSelection;

typedef struct DomClientState {
    DomClientCamera2D cam2d;
    DomClientCamera3D cam3d;
    dom_bool8 use_3d;
    dom_render_mode render_mode;
    DomClientDebugMode debug_mode;
    dom_bool8 show_help;
    dom_bool8 show_replay;
    dom_bool8 show_tools;
    dom_bool8 show_map;
    dom_bool8 show_settings;
    dom_bool8 show_dev_console;
    dom_bool8 show_profiler;
    dom_bool8 highlight_interactive;
    DomClientViewKind view_kind;
    DomClientStats stats;
    DomClientSelection selection;
    char status_line[128];
    dom_u64 status_until_ms;
} DomClientState;

static const char *dom_client_backend_name(dom_render_backend b)
{
    switch (b) {
    case DOM_RENDER_BACKEND_DX9: return "DX9";
    case DOM_RENDER_BACKEND_DX11: return "DX11";
    case DOM_RENDER_BACKEND_DX12: return "DX12";
    case DOM_RENDER_BACKEND_GL1: return "GL1";
    case DOM_RENDER_BACKEND_GL2: return "GL2";
    case DOM_RENDER_BACKEND_VK1: return "VK1";
    case DOM_RENDER_BACKEND_SOFTWARE: return "software";
    default: return "unknown";
    }
}

static const char *dom_client_platform_name(void)
{
#if defined(DOM_PLATFORM_WIN32)
    return "win32";
#elif defined(DOM_PLATFORM_LINUX)
    return "linux";
#elif defined(DOM_PLATFORM_MACOS)
    return "macos";
#else
    return "platform";
#endif
}

static const char *dom_client_mode_name(dom_render_mode m)
{
    return (m == DOM_RENDER_MODE_FULL) ? "graphics" : "vector";
}

static void dom_client_set_status(DomClientState *st, const char *msg, dom_u64 now_ms, dom_u32 duration_ms)
{
    if (!st || !msg) return;
    snprintf(st->status_line, sizeof(st->status_line), "%s", msg);
    st->status_until_ms = now_ms + duration_ms;
}

static void dom_client_update_title(DomPlatformWin32Window *win,
                                    DomRenderer *renderer,
                                    const DomClientState *st)
{
    char title[256];
    unsigned build = (unsigned)dom_version_build_number();
    const char *ver = dom_version_full();
    const char *platform = dom_client_platform_name();
    const char *backend = renderer ? dom_client_backend_name(renderer->backend) : "renderer";
    const char *mode = st ? dom_client_mode_name(st->render_mode) : "vector";
    snprintf(title, sizeof(title), "Dominium %s (build %u) (%s %s %s)",
             ver ? ver : "v0.0.0",
             build,
             platform,
             backend,
             mode);
    dom_platform_win32_set_title(win, title);
}

static void dom_client_state_init(DomClientState *st)
{
    if (!st) return;
    memset(st, 0, sizeof(*st));
    st->cam2d.zoom = 1;
    st->cam3d.z = 10;
    st->cam3d.yaw_deg = 0;
    st->cam3d.pitch_deg = 0;
    st->render_mode = DOM_RENDER_MODE_VECTOR_ONLY;
    st->debug_mode = DOM_DEBUG_OFF;
    st->view_kind = DOM_VIEW_KIND_TOPDOWN;
    st->selection.layer = 0;
}

/* ------------------------------------------------------------
 * Input handling
 * ------------------------------------------------------------ */
static dom_bool8 dom_client_world_from_screen(const DomClientState *st,
                                              const DomRenderer *renderer,
                                              dom_i32 sx,
                                              dom_i32 sy,
                                              dom_i32 *out_x,
                                              dom_i32 *out_y)
{
    dom_i32 cx;
    dom_i32 cy;
    if (!st || !renderer || !out_x || !out_y) {
        return 0;
    }
    cx = (dom_i32)(renderer->width / 2u);
    cy = (dom_i32)(renderer->height / 2u);
    *out_x = st->cam2d.x + (sx - cx);
    *out_y = st->cam2d.y + (sy - cy);
    return 1;
}

static void dom_client_set_render_mode(DomClientState *st,
                                       DomRenderer *renderer,
                                       dom_render_mode mode)
{
    if (!st || !renderer) return;
    st->render_mode = mode;
    renderer->mode = mode;
    renderer->config.mode = mode;
}

static void dom_client_apply_frame_actions(DomClientState *st,
                                           DomRenderer *renderer,
                                           DomPlatformWin32Window *win,
                                           const DomPlatformInputFrame *in,
                                           const dom_render_caps *caps,
                                           dom_u64 now_ms)
{
    if (!st) return;

    st->highlight_interactive = dom_input_action_is_down(ACTION_HIGHLIGHT_INTERACTIVES) ? 1 : 0;

    if (dom_input_action_was_triggered(ACTION_HELP_OVERLAY)) {
        st->show_help = st->show_help ? 0 : 1;
    }
    if (dom_input_action_was_triggered(ACTION_DEBUG_OVERLAY_CYCLE)) {
        st->debug_mode = (DomClientDebugMode)(((int)st->debug_mode + 1) % 3);
    }
    if (dom_input_action_was_triggered(ACTION_VIEW_DIMENSION_TOGGLE)) {
        st->use_3d = st->use_3d ? 0 : 1;
        st->view_kind = st->use_3d ? DOM_VIEW_KIND_FIRST_PERSON : DOM_VIEW_KIND_TOPDOWN;
    }
    if (dom_input_action_was_triggered(ACTION_VIEW_RENDER_MODE_CYCLE)) {
        dom_render_mode next = st->render_mode;
        if (st->render_mode == DOM_RENDER_MODE_VECTOR_ONLY && caps && caps->supports_textures) {
            next = DOM_RENDER_MODE_FULL;
        } else {
            next = DOM_RENDER_MODE_VECTOR_ONLY;
        }
        dom_client_set_render_mode(st, renderer, next);
        dom_client_update_title(win, renderer, st);
        dom_client_set_status(st,
                              (next == DOM_RENDER_MODE_FULL) ? "Render: graphics" : "Render: vector",
                              now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_QUICK_SAVE)) {
        dom_client_set_status(st, "Quick save (stub)", now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_QUICK_LOAD)) {
        dom_client_set_status(st, "Quick load (disabled in demo)", now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_REPLAY_PANEL)) {
        st->show_replay = st->show_replay ? 0 : 1;
        dom_client_set_status(st, st->show_replay ? "Replay panel open" : "Replay panel closed", now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_TOOLS_PANEL)) {
        st->show_tools = st->show_tools ? 0 : 1;
        dom_client_set_status(st, st->show_tools ? "Tools panel open" : "Tools panel closed", now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_WORLD_MAP)) {
        st->show_map = st->show_map ? 0 : 1;
        if (st->show_map) {
            st->use_3d = 0;
            st->view_kind = DOM_VIEW_KIND_TOPDOWN;
            st->cam2d.zoom = 1;
        }
        dom_client_set_status(st, st->show_map ? "Map view" : "World view", now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_SETTINGS_MENU)) {
        st->show_settings = st->show_settings ? 0 : 1;
        dom_client_set_status(st, st->show_settings ? "Settings open" : "Settings closed", now_ms, 1200);
    }
    if (dom_input_action_was_triggered(ACTION_FULLSCREEN_TOGGLE)) {
        dom_client_set_status(st, "Fullscreen toggle (not implemented in MVP)", now_ms, 1800);
    }
    if (dom_input_action_was_triggered(ACTION_DEV_CONSOLE)) {
        st->show_dev_console = st->show_dev_console ? 0 : 1;
        dom_client_set_status(st, st->show_dev_console ? "Dev console open" : "Dev console closed", now_ms, 1500);
    }
    if (dom_input_action_was_triggered(ACTION_SCREENSHOT_CAPTURE)) {
        dom_client_set_status(st, "Screenshot captured (stub)", now_ms, 1200);
    }
    if (dom_input_action_was_triggered(ACTION_PROFILER_OVERLAY)) {
        st->show_profiler = st->show_profiler ? 0 : 1;
    }
    if (dom_input_action_was_triggered(ACTION_LAYER_CYCLE)) {
        st->selection.layer = (st->selection.layer + 1) % 4;
        dom_client_set_status(st, "Layer cycled", now_ms, 800);
    }
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_1)) st->selection.quickbar_slot = 1;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_2)) st->selection.quickbar_slot = 2;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_3)) st->selection.quickbar_slot = 3;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_4)) st->selection.quickbar_slot = 4;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_5)) st->selection.quickbar_slot = 5;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_6)) st->selection.quickbar_slot = 6;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_7)) st->selection.quickbar_slot = 7;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_8)) st->selection.quickbar_slot = 8;
    if (dom_input_action_was_triggered(ACTION_QUICKBAR_SLOT_9)) st->selection.quickbar_slot = 9;

    if (dom_input_action_was_triggered(ACTION_PRIMARY_SELECT) && in && renderer) {
        dom_i32 wx, wy;
        if (dom_client_world_from_screen(st, renderer, in->mouse_x, in->mouse_y, &wx, &wy)) {
            st->selection.has_selection = 1;
            st->selection.world_x = wx;
            st->selection.world_y = wy;
            dom_client_set_status(st, "Primary select", now_ms, 800);
        }
    }
    if (dom_input_action_was_triggered(ACTION_SECONDARY_SELECT)) {
        st->selection.has_selection = 0;
        dom_client_set_status(st, "Secondary / cancel", now_ms, 600);
    }
}

static void dom_client_step_tick(DomClientState *st, const DomPlatformInputFrame *in)
{
    dom_i32 pan_speed = 32;
    const dom_i32 zoom_min = 1;
    const dom_i32 zoom_max = 8;

    if (!st) return;

    if (in && in->key_down[DOM_KEY_SHIFT]) {
        pan_speed = 64;
    }

    if (dom_input_action_is_down(ACTION_MOVE_FORWARD)) {
        st->cam2d.y -= pan_speed;
    }
    if (dom_input_action_is_down(ACTION_MOVE_BACKWARD)) {
        st->cam2d.y += pan_speed;
    }
    if (dom_input_action_is_down(ACTION_MOVE_LEFT)) {
        st->cam2d.x -= pan_speed;
    }
    if (dom_input_action_is_down(ACTION_MOVE_RIGHT)) {
        st->cam2d.x += pan_speed;
    }

    if (!st->use_3d) {
        if (dom_input_action_is_down(ACTION_CAMERA_ALT_UP) && st->cam2d.zoom > zoom_min) {
            st->cam2d.zoom -= 1;
        }
        if (dom_input_action_is_down(ACTION_CAMERA_ALT_DOWN) && st->cam2d.zoom < zoom_max) {
            st->cam2d.zoom += 1;
        }
    } else {
        if (dom_input_action_is_down(ACTION_CAMERA_ALT_UP)) {
            st->cam3d.y += 1;
        }
        if (dom_input_action_is_down(ACTION_CAMERA_ALT_DOWN)) {
            st->cam3d.y -= 1;
        }
    }

    if (st->use_3d) {
        if (dom_input_action_is_down(ACTION_MOVE_FORWARD)) st->cam3d.z += 1;
        if (dom_input_action_is_down(ACTION_MOVE_BACKWARD)) st->cam3d.z -= 1;
        if (dom_input_action_is_down(ACTION_MOVE_LEFT)) st->cam3d.x -= 1;
        if (dom_input_action_is_down(ACTION_MOVE_RIGHT)) st->cam3d.x += 1;
        if (dom_input_action_is_down(ACTION_CAMERA_ROTATE_CCW)) st->cam3d.yaw_deg -= 2;
        if (dom_input_action_is_down(ACTION_CAMERA_ROTATE_CW)) st->cam3d.yaw_deg += 2;
        st->cam3d.yaw_deg %= 360;
    }
}

/* ------------------------------------------------------------
 * Rendering helpers
 * ------------------------------------------------------------ */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static dom_bool8 dom_client_project_point(const DomClientState *st,
                                          const DomRenderer *renderer,
                                          float wx, float wy, float wz,
                                          dom_i32 *out_x,
                                          dom_i32 *out_y)
{
    float dx, dy, dz;
    float cy, sy, cp, sp;
    float rx, ry, rz;
    float ry2, rz2;
    float fov_rad;
    float focal;

    if (!st || !renderer || !out_x || !out_y) return 0;

    dx = wx - (float)st->cam3d.x;
    dy = wy - (float)st->cam3d.y;
    dz = wz - (float)st->cam3d.z;

    cy = (float)cos((double)st->cam3d.yaw_deg * M_PI / 180.0);
    sy = (float)sin((double)st->cam3d.yaw_deg * M_PI / 180.0);
    cp = (float)cos((double)st->cam3d.pitch_deg * M_PI / 180.0);
    sp = (float)sin((double)st->cam3d.pitch_deg * M_PI / 180.0);

    rx = cy * dx - sy * dz;
    rz = sy * dx + cy * dz;
    ry = dy;

    ry2 = cp * ry - sp * rz;
    rz2 = sp * ry + cp * rz;

    if (rz2 <= 0.1f) {
        return 0;
    }

    fov_rad = 70.0f * (float)M_PI / 180.0f;
    focal = (float)renderer->width / (2.0f * (float)tan((double)(fov_rad * 0.5f)));

    *out_x = (dom_i32)(renderer->width * 0.5f + (rx * focal) / rz2);
    *out_y = (dom_i32)(renderer->height * 0.5f - (ry2 * focal) / rz2);
    return 1;
}

static void dom_client_draw_world_2d(DomRenderer *renderer, const DomClientState *st)
{
    dom_i32 spacing = 64;
    dom_i32 start_x;
    dom_i32 start_y;
    dom_i32 camx_mod;
    dom_i32 camy_mod;
    dom_i32 origin_x;
    dom_i32 origin_y;
    dom_i32 x;
    dom_i32 y;
    dom_i32 marker_size = 6;
    dom_i32 moving_x;
    dom_i32 moving_y;

    if (!renderer || !st) return;

    if (st->cam2d.zoom > 1) {
        spacing = spacing / st->cam2d.zoom;
        if (spacing < 4) spacing = 4;
    }

    camx_mod = (dom_i32)(st->cam2d.x % spacing);
    camy_mod = (dom_i32)(st->cam2d.y % spacing);
    if (camx_mod < 0) camx_mod += spacing;
    if (camy_mod < 0) camy_mod += spacing;
    start_x = -camx_mod;
    start_y = -camy_mod;

    for (x = start_x; x < (dom_i32)renderer->width; x += spacing) {
        dom_render_line(renderer, x, 0, x, (dom_i32)renderer->height, DOM_COLOR_GRID);
    }
    for (y = start_y; y < (dom_i32)renderer->height; y += spacing) {
        dom_render_line(renderer, 0, y, (dom_i32)renderer->width, y, DOM_COLOR_GRID);
    }

    origin_x = (dom_i32)(renderer->width / 2u - st->cam2d.x);
    origin_y = (dom_i32)(renderer->height / 2u - st->cam2d.y);
    dom_render_line(renderer, origin_x, 0, origin_x, (dom_i32)renderer->height, DOM_COLOR_ACCENT);
    dom_render_line(renderer, 0, origin_y, (dom_i32)renderer->width, origin_y, DOM_COLOR_ACCENT);

    /* Moving marker to show updates */
    moving_x = (dom_i32)((st->stats.tick_count % 400u) - 200);
    moving_y = (dom_i32)(sin((double)(st->stats.tick_count % 360) * M_PI / 180.0) * 80.0);
    moving_x = origin_x + moving_x;
    moving_y = origin_y + moving_y;
    {
        DomRect rc;
        rc.x = moving_x - marker_size;
        rc.y = moving_y - marker_size;
        rc.w = marker_size * 2;
        rc.h = marker_size * 2;
        dom_render_rect(renderer, &rc, DOM_COLOR_ACCENT_ALT);
    }

    if (st->selection.has_selection) {
        dom_i32 sx = origin_x + (st->selection.world_x - st->cam2d.x);
        dom_i32 sy = origin_y + (st->selection.world_y - st->cam2d.y);
        dom_render_line(renderer, sx - 6, sy, sx + 6, sy, DOM_COLOR_ACCENT_ALT);
        dom_render_line(renderer, sx, sy - 6, sx, sy + 6, DOM_COLOR_ACCENT_ALT);
    }
}

static void dom_client_draw_world_3d(DomRenderer *renderer, const DomClientState *st)
{
    int i;
    int j;
    float grid_range = 40.0f;
    float step = 4.0f;
    if (!renderer || !st) return;

    /* Ground grid */
    for (i = -10; i <= 10; ++i) {
        float x = (float)(i * (int)step);
        dom_i32 sx0, sy0, sx1, sy1;
        if (dom_client_project_point(st, renderer, x, 0.0f, 2.0f, &sx0, &sy0) &&
            dom_client_project_point(st, renderer, x, 0.0f, grid_range, &sx1, &sy1)) {
            dom_render_line(renderer, sx0, sy0, sx1, sy1, DOM_COLOR_GRID_DENSE);
        }
    }
    for (j = 0; j <= 10; ++j) {
        float z = (float)(j * step);
        dom_i32 sx0, sy0, sx1, sy1;
        if (dom_client_project_point(st, renderer, -grid_range, 0.0f, z, &sx0, &sy0) &&
            dom_client_project_point(st, renderer, grid_range, 0.0f, z, &sx1, &sy1)) {
            dom_render_line(renderer, sx0, sy0, sx1, sy1, DOM_COLOR_GRID);
        }
    }

    /* Horizon / forward vector */
    {
        dom_i32 sx, sy;
        if (dom_client_project_point(st, renderer,
                                     st->cam3d.x + (dom_i64)(cos((double)st->cam3d.yaw_deg * M_PI / 180.0) * 10.0),
                                     st->cam3d.y,
                                     st->cam3d.z + (dom_i64)(sin((double)st->cam3d.yaw_deg * M_PI / 180.0) * 10.0),
                                     &sx, &sy)) {
            dom_render_line(renderer,
                            (dom_i32)(renderer->width / 2u),
                            (dom_i32)(renderer->height / 2u),
                            sx, sy,
                            DOM_COLOR_ACCENT);
        }
    }
}

static void dom_client_draw_overlay(DomRenderer *renderer,
                                    const DomClientState *st,
                                    dom_u64 now_ms)
{
    char line[256];
    dom_i32 x;
    dom_i32 y;
    dom_u64 elapsed_ms;
    dom_u32 seconds;
    dom_u32 minutes;
    if (!renderer || !st) return;

    x = (dom_i32)renderer->width - 240;
    y = 8;

    if (st->debug_mode != DOM_DEBUG_OFF) {
        elapsed_ms = now_ms - st->stats.start_ms;
        seconds = (dom_u32)((elapsed_ms / 1000u) % 60u);
        minutes = (dom_u32)(elapsed_ms / 60000u);
        snprintf(line, sizeof(line), "UPS %u | FPS %u | Tick %lu", st->stats.ups, st->stats.fps, (unsigned long)st->stats.tick_count);
        dom_render_text(renderer, 0, DOM_COLOR_TEXT, line, x, y); y += 14;
        snprintf(line, sizeof(line), "Time %lu:%02lu | Mode %s | View %s",
                 (unsigned long)minutes,
                 (unsigned long)seconds,
                 dom_client_mode_name(st->render_mode),
                 st->use_3d ? "3D FP" : "2D topdown");
        dom_render_text(renderer, 0, DOM_COLOR_TEXT, line, x, y); y += 14;
        if (st->debug_mode == DOM_DEBUG_FULL) {
            snprintf(line, sizeof(line), "Cam2D (%ld,%ld) zoom %d",
                     (long)st->cam2d.x, (long)st->cam2d.y, (int)st->cam2d.zoom);
            dom_render_text(renderer, 0, DOM_COLOR_TEXT, line, x, y); y += 14;
            snprintf(line, sizeof(line), "Cam3D (%ld,%ld,%ld) yaw %d pitch %d",
                     (long)st->cam3d.x, (long)st->cam3d.y, (long)st->cam3d.z,
                     (int)st->cam3d.yaw_deg, (int)st->cam3d.pitch_deg);
            dom_render_text(renderer, 0, DOM_COLOR_TEXT, line, x, y); y += 14;
            snprintf(line, sizeof(line), "Flags: replay:%d tools:%d map:%d settings:%d console:%d",
                     st->show_replay, st->show_tools, st->show_map, st->show_settings, st->show_dev_console);
            dom_render_text(renderer, 0, DOM_COLOR_TEXT, line, x, y); y += 14;
        }
    }

    if (st->show_help) {
        dom_render_text(renderer, 0, DOM_COLOR_TEXT, "F1 Help | F3 Debug | F4 2D/3D | Shift+F4 Render mode", 12, 12);
        dom_render_text(renderer, 0, DOM_COLOR_TEXT, "WASD move, QE rotate, RF altitude/zoom, Esc quit", 12, 26);
        dom_render_text(renderer, 0, DOM_COLOR_TEXT, "F5 save, F6 load, F7 replay, F8 tools, F9 map, F10 settings, F12 console", 12, 40);
    }

    if (st->highlight_interactive) {
        dom_render_text(renderer, 0, DOM_COLOR_ACCENT_ALT, "Highlighting interactives", 12, 56);
    }

    if (st->status_line[0] && now_ms < st->status_until_ms) {
        dom_render_text(renderer, 0, DOM_COLOR_ACCENT, st->status_line, 12, (dom_i32)renderer->height - 24);
    }

    if (st->selection.has_selection && st->debug_mode == DOM_DEBUG_FULL) {
        snprintf(line, sizeof(line), "Selection (%d,%d) layer %d slot %d",
                 st->selection.world_x, st->selection.world_y, st->selection.layer, st->selection.quickbar_slot);
        dom_render_text(renderer, 0, DOM_COLOR_TEXT, line, 12, (dom_i32)renderer->height - 40);
    }
}

static void dom_client_draw_scene(DomRenderer *renderer,
                                  const DomClientState *st,
                                  dom_u64 now_ms)
{
    if (!renderer || !st) return;

    if (st->use_3d) {
        dom_client_draw_world_3d(renderer, st);
    } else {
        dom_client_draw_world_2d(renderer, st);
    }
    dom_render_debug_draw_crosshair(renderer, st->use_3d ? DOM_COLOR_ACCENT_ALT : DOM_COLOR_ACCENT);
    dom_client_draw_overlay(renderer, st, now_ms);
}

static void dom_client_log_bindings(void)
{
    dom_input_mapping_debug_dump_binding(ACTION_HELP_OVERLAY);
    dom_input_mapping_debug_dump_binding(ACTION_DEBUG_OVERLAY_CYCLE);
    dom_input_mapping_debug_dump_binding(ACTION_VIEW_DIMENSION_TOGGLE);
    dom_input_mapping_debug_dump_binding(ACTION_VIEW_RENDER_MODE_CYCLE);
    dom_input_mapping_debug_dump_binding(ACTION_QUICK_SAVE);
    dom_input_mapping_debug_dump_binding(ACTION_QUICK_LOAD);
    dom_input_mapping_debug_dump_binding(ACTION_FULLSCREEN_TOGGLE);
    dom_input_mapping_debug_dump_binding(ACTION_DEV_CONSOLE);
}

static void dom_client_update_stats(DomClientState *st, dom_u64 now_ms)
{
    dom_u64 delta;
    if (!st) return;
    st->stats.frame_count += 1;
    st->stats.frame_accum += 1;
    if (st->stats.last_stats_ms == 0) {
        st->stats.last_stats_ms = now_ms;
    }
    delta = now_ms - st->stats.last_stats_ms;
    if (delta >= 1000u) {
        st->stats.fps = (dom_u32)((st->stats.frame_accum * 1000u) / delta);
        st->stats.ups = (dom_u32)((st->stats.tick_accum * 1000u) / delta);
        st->stats.frame_accum = 0;
        st->stats.tick_accum = 0;
        st->stats.last_stats_ms = now_ms;
    }
}

static void dom_client_load_default_bindings(void)
{
    const char *candidates[] = {
        "game/client/input/default_bindings.json",
        "../game/client/input/default_bindings.json",
        "../../game/client/input/default_bindings.json",
        "input/default_bindings.json",
        0
    };
    int i;
    int loaded = -1;

    for (i = 0; candidates[i]; ++i) {
        if (dom_input_mapping_load_defaults(candidates[i]) == 0) {
            printf("Loaded input bindings from %s\n", candidates[i]);
            loaded = 0;
            break;
        }
    }

    if (loaded != 0) {
        dom_input_mapping_load_defaults(NULL);
        printf("Loaded built-in input bindings\n");
    }

    dom_client_log_bindings();
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
    dom_render_config render_cfg;
    dom_render_caps render_caps;
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
    memset(&render_cfg, 0, sizeof(render_cfg));
    memset(&render_caps, 0, sizeof(render_caps));

    sim_cfg.target_ups = 60;
    sim_cfg.num_lanes = 1;

    dom_input_mapping_init();
    dom_client_load_default_bindings();

    printf("Dominium %s (build %u)\n",
           dom_version_full(),
           (unsigned)dom_version_build_number());

    err = dom_platform_win32_create_window("Dominium Client MVP", 1280, 720, 0, &win);
    if (err != DOM_OK) {
        printf("Platform init failed (%d)\n", (int)err);
        return 1;
    }

    render_cfg.mode = DOM_RENDER_MODE_VECTOR_ONLY;
    render_cfg.backend = DOM_RENDER_BACKEND_DX9;
    render_cfg.width = 1280;
    render_cfg.height = 720;
    render_cfg.fullscreen = 0;
    render_cfg.platform_window = dom_platform_win32_native_handle(win);

    err = dom_render_create(&renderer,
                            render_cfg.backend,
                            &render_cfg,
                            &render_caps);
    if (err != DOM_OK) {
        /* Fallback to null renderer for headless validation */
        render_cfg.backend = DOM_RENDER_BACKEND_SOFTWARE;
        render_cfg.mode = DOM_RENDER_MODE_VECTOR_ONLY;
        err = dom_render_create(&renderer,
                                DOM_RENDER_BACKEND_SOFTWARE,
                                &render_cfg,
                                &render_caps);
        if (err != DOM_OK) {
            printf("Renderer init failed (%d)\n", (int)err);
            dom_platform_win32_destroy_window(win);
            return 1;
        }
    }
    client.render_mode = render_cfg.mode;
    dom_client_update_title(win, &renderer, &client);

    err = dom_sim_world_create(&sim_cfg, &world);
    if (err != DOM_OK) {
        printf("Sim world init failed (%d)\n", (int)err);
        dom_render_destroy(&renderer);
        dom_platform_win32_destroy_window(win);
        return 1;
    }

    last_time = dom_platform_win32_now_msec();
    accum_ms = 0;
    client.stats.start_ms = last_time;
    client.stats.last_stats_ms = last_time;

    while (running && !dom_platform_win32_should_close(win)) {
        dom_input_mapping_begin_frame();
        dom_platform_win32_pump_messages(win);
        dom_platform_win32_poll_input(win, &input);
        dom_input_mapping_apply_frame(&input);

        if (dom_input_action_was_triggered(ACTION_UI_BACK)) {
            running = 0;
            break;
        }

        now = dom_platform_win32_now_msec();
        accum_ms += (now - last_time);
        last_time = now;

        dom_client_apply_frame_actions(&client, &renderer, win, &input, &render_caps, now);

        while (accum_ms >= tick_ms) {
            dom_client_step_tick(&client, &input);
            dom_sim_world_step(world);
            accum_ms -= tick_ms;
            client.stats.tick_count += 1;
            client.stats.tick_accum += 1;
        }

        dom_client_update_stats(&client, now);

        dom_render_begin(&renderer, DOM_COLOR_BG);
        dom_client_draw_scene(&renderer, &client, now);
        dom_render_submit(&renderer, 0, 0);
        dom_render_present(&renderer);
        dom_platform_win32_sleep_msec(1);
    }

    dom_sim_world_destroy(world);
    dom_render_destroy(&renderer);
    dom_platform_win32_destroy_window(win);
    dom_input_mapping_shutdown();
    return 0;
}

int main(void)
{
    return dom_client_run();
}

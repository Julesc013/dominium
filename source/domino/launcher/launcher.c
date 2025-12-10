#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "domino/launcher.h"
#include "domino/launcher_config.h"
#include "domino/launcher_profile.h"
#include "domino/launcher_mods.h"
#include "domino/launcher_process.h"
#include "domino/ui_widget.h"
#include "domino/ui_layout.h"
#include "domino/ui_renderer.h"
#include "domino/gfx.h"
#include "domino/canvas.h"
#include "domino/sys.h"

#define LAUNCHER_UI_MAX_ITEMS 64

typedef struct launcher_state {
    launcher_config config;
    dsys_window*    window;
    int             running;
    int             selected_profile;
    launcher_proc   active_proc;
} launcher_state;

static launcher_state g_launcher;
static int g_pointer_x = 0;
static int g_pointer_y = 0;
static int g_pointer_down = 0;

static void launcher_build_profile_names(const char** out_names, int cap, int* out_count)
{
    int count;
    int i;
    count = launcher_profile_count();
    if (count > cap) {
        count = cap;
    }
    for (i = 0; i < count; ++i) {
        const launcher_profile* p;
        p = launcher_profile_get(i);
        if (p && p->name[0] != '\0') {
            out_names[i] = p->name;
        } else if (p) {
            out_names[i] = p->id;
        } else {
            out_names[i] = "";
        }
    }
    if (out_count) {
        *out_count = count;
    }
}

static void launcher_handle_event(const dsys_event* ev)
{
    ui_event uie;
    if (!ev) {
        return;
    }
    memset(&uie, 0, sizeof(uie));
    switch (ev->type) {
    case DSYS_EVENT_QUIT:
        g_launcher.running = 0;
        break;
    case DSYS_EVENT_MOUSE_MOVE:
        uie.type = UI_EVT_MOUSE;
        uie.data.mouse.x = ev->payload.mouse_move.x;
        uie.data.mouse.y = ev->payload.mouse_move.y;
        uie.data.mouse.dx = ev->payload.mouse_move.dx;
        uie.data.mouse.dy = ev->payload.mouse_move.dy;
        g_pointer_x = ev->payload.mouse_move.x;
        g_pointer_y = ev->payload.mouse_move.y;
        uie.data.mouse.pressed = g_pointer_down;
        uie.data.mouse.button = 0;
        ui_input_event(&uie);
        break;
    case DSYS_EVENT_MOUSE_BUTTON:
        uie.type = UI_EVT_MOUSE;
        g_pointer_down = ev->payload.mouse_button.pressed ? 1 : 0;
        uie.data.mouse.x = g_pointer_x;
        uie.data.mouse.y = g_pointer_y;
        uie.data.mouse.button = ev->payload.mouse_button.button;
        uie.data.mouse.pressed = g_pointer_down;
        ui_input_event(&uie);
        break;
    case DSYS_EVENT_MOUSE_WHEEL:
        uie.type = UI_EVT_MOUSE;
        uie.data.mouse.wheel = ev->payload.mouse_wheel.delta_y;
        uie.data.mouse.x = g_pointer_x;
        uie.data.mouse.y = g_pointer_y;
        ui_input_event(&uie);
        break;
    case DSYS_EVENT_KEY_DOWN:
    case DSYS_EVENT_KEY_UP:
        uie.type = UI_EVT_KEY;
        uie.data.key.code = ev->payload.key.key;
        uie.data.key.mods = 0;
        uie.data.key.pressed = ev->type == DSYS_EVENT_KEY_DOWN ? 1 : 0;
        ui_input_event(&uie);
        break;
    case DSYS_EVENT_TEXT_INPUT:
        uie.type = UI_EVT_TEXT;
        strncpy(uie.data.text, ev->payload.text.text, sizeof(uie.data.text) - 1u);
        uie.data.text[sizeof(uie.data.text) - 1u] = '\0';
        ui_input_event(&uie);
        break;
    default:
        break;
    }
}

static void launcher_draw_ui(dcvs* canvas, int width, int height)
{
    ui_style style;
    const char* names[LAUNCHER_UI_MAX_ITEMS];
    int name_count;
    int selected;
    int launch_clicked;
    int quit_clicked;
    launcher_profile const* p;

    (void)canvas;
    style.color_bg = 0x181820ffu;
    style.color_fg = 0xf0f0f0ffu;
    style.color_accent = 0x508cffffu;
    style.color_border = 0x3c3c46ffu;
    style.radius = 4;
    style.border_px = 1;
    style.font_id = 0;
    style.icon_sheet = 0;

    ui_begin_frame(canvas, width, height, (int)(dsys_time_now_us() / 1000u));
    ui_label("title", "Dominium Launcher", &style);

    launcher_build_profile_names(names, LAUNCHER_UI_MAX_ITEMS, &name_count);
    selected = g_launcher.selected_profile;
    if (name_count > 0) {
        int res;
        ui_label("profiles_label", "Profiles", &style);
        res = ui_list("profiles_list", names, name_count, &selected, &style);
        if (res >= 0) {
            g_launcher.selected_profile = selected;
        }
    } else {
        ui_label("profiles_empty", "No profiles found.", &style);
    }

    launch_clicked = ui_button("btn_launch", "Launch", &style);
    quit_clicked = ui_button("btn_quit", "Quit", &style);

    p = launcher_profile_get(g_launcher.selected_profile);
    if (p) {
        ui_label("active_profile", p->install_path, &style);
    }

    if (g_launcher.active_proc.running) {
        ui_label("proc_running", "Process: running", &style);
    } else if (g_launcher.active_proc.exit_code != 0) {
        char status[64];
        sprintf(status, "Process exited: %d", g_launcher.active_proc.exit_code);
        ui_label("proc_exit", status, &style);
    }

    if (launch_clicked && p && p->install_path[0] != '\0') {
        char args[4];
        args[0] = '\0';
        (void)launcher_process_spawn(&g_launcher.active_proc, p->install_path, args, NULL);
    }
    if (quit_clicked) {
        g_launcher.running = 0;
    }
    ui_end_frame();
}

int launcher_init(const launcher_config* cfg)
{
    launcher_config local_cfg;
    dsys_window_desc wdesc;
    dgfx_desc gdesc;

    memset(&g_launcher, 0, sizeof(g_launcher));

    if (cfg) {
        local_cfg = *cfg;
    } else {
        launcher_config_load(&local_cfg);
    }
    g_launcher.config = local_cfg;
    g_launcher.selected_profile = launcher_profile_get_active();
    if (g_launcher.selected_profile < 0) {
        g_launcher.selected_profile = 0;
    }

    if (dsys_init() != DSYS_OK) {
        return -1;
    }

    memset(&wdesc, 0, sizeof(wdesc));
    wdesc.width = local_cfg.width;
    wdesc.height = local_cfg.height;
    wdesc.mode = DWIN_MODE_WINDOWED;
    g_launcher.window = dsys_window_create(&wdesc);
    if (!g_launcher.window) {
        dsys_shutdown();
        return -1;
    }

    memset(&gdesc, 0, sizeof(gdesc));
    gdesc.backend = DGFX_BACKEND_SOFT;
    gdesc.window = g_launcher.window;
    gdesc.native_window = dsys_window_get_native_handle(g_launcher.window);
    gdesc.width = local_cfg.width;
    gdesc.height = local_cfg.height;
    gdesc.fullscreen = 0;
    gdesc.vsync = 0;

    if (!dgfx_init(&gdesc)) {
        dsys_window_destroy(g_launcher.window);
        dsys_shutdown();
        return -1;
    }

    launcher_profile_load_all();
    launcher_mods_scan(NULL);
    {
        int count;
        count = launcher_profile_count();
        if (count == 0) {
            g_launcher.selected_profile = 0;
        } else if (g_launcher.selected_profile >= count) {
            g_launcher.selected_profile = count - 1;
        }
    }
    ui_input_reset();

    g_launcher.running = 1;
    return 0;
}

int launcher_run(void)
{
    dsys_event ev;
    int width;
    int height;
    dcvs* canvas;

    while (g_launcher.running) {
        while (dsys_poll_event(&ev)) {
            launcher_handle_event(&ev);
        }
        if (g_launcher.active_proc.running) {
            launcher_process_poll(&g_launcher.active_proc);
        }
        dsys_window_get_size(g_launcher.window, &width, &height);

        canvas = dgfx_get_frame_canvas();
        dgfx_begin_frame();
        if (canvas) {
            dcvs_reset(canvas);
            dcvs_clear(canvas, 0x101014ffu);
            launcher_draw_ui(canvas, width, height);
            dgfx_execute(dcvs_get_cmd_buffer(canvas));
        }
        dgfx_end_frame();
        dsys_sleep_ms(16u);
    }
    return 0;
}

void launcher_shutdown(void)
{
    if (g_launcher.active_proc.running) {
        launcher_process_kill(&g_launcher.active_proc);
    }
    dgfx_shutdown();
    if (g_launcher.window) {
        dsys_window_destroy(g_launcher.window);
        g_launcher.window = NULL;
    }
    dsys_shutdown();
}

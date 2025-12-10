#include "domino/sys.h"
#include "domino/mod.h"
#include "domino/gfx.h"
#include "dominium/game_api.h"
#include "dominium/version.h"
#include "g_modes.h"
#include "g_runtime.h"

#include <string.h>

int dominium_game_run(const domino_instance_desc* inst)
{
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    domino_package_registry* reg = NULL;
    domino_sys_paths paths;
    const char* roots[2];
    domino_resolve_error err;
    domino_gfx_device* gfx = NULL;
    domino_gfx_desc gdesc;
    domino_instance_desc local_inst;
    int i;
    const DmnGameLaunchOptions* opts;
    DmnGameMode selected_mode;

    opts = dmn_game_get_launch_options();
    selected_mode = (opts ? opts->mode : DMN_GAME_MODE_GUI);
    if (opts && opts->server_mode == DMN_GAME_SERVER_DEDICATED) {
        selected_mode = DMN_GAME_MODE_HEADLESS;
    }

    memset(&sdesc, 0, sizeof(sdesc));
    sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
    if (domino_sys_init(&sdesc, &sys) != 0) {
        return 1;
    }

    reg = domino_package_registry_create();
    if (!reg) {
        domino_sys_shutdown(sys);
        return 1;
    }
    domino_package_registry_set_sys(reg, sys);

    domino_sys_get_paths(sys, &paths);
    roots[0] = paths.data_root;
    roots[1] = paths.user_root;
    domino_package_registry_scan_roots(reg, roots, 2);

    if (inst) {
        err.message[0] = '\0';
        if (domino_instance_resolve(reg, inst, &err) != 0) {
            if (err.message[0]) {
                domino_sys_log(sys, DOMINO_LOG_ERROR, "game", err.message);
            }
            domino_package_registry_destroy(reg);
            domino_sys_shutdown(sys);
            return 1;
        }
    } else {
        memset(&local_inst, 0, sizeof(local_inst));
        strncpy(local_inst.id, "default", sizeof(local_inst.id) - 1);
        strncpy(local_inst.product_id, DOMINIUM_GAME_ID, sizeof(local_inst.product_id) - 1);
        dominium_game_get_version(&local_inst.product_version);
        inst = &local_inst;
    }

    memset(&gdesc, 0, sizeof(gdesc));
    gdesc.backend         = DOMINO_GFX_BACKEND_AUTO;
    gdesc.profile_hint    = DOMINO_GFX_PROFILE_FIXED;
    gdesc.width           = 640;
    gdesc.height          = 360;
    gdesc.fullscreen      = 0;
    gdesc.vsync           = 0;
    gdesc.framebuffer_fmt = DOMINO_PIXFMT_A8R8G8B8;

    domino_sys_log(sys, DOMINO_LOG_INFO, "game",
                   selected_mode == DMN_GAME_MODE_GUI ? "Starting game (GUI mode)" :
                   (selected_mode == DMN_GAME_MODE_TUI ? "Starting game (TUI mode)" :
                                                         "Starting game (headless mode)"));
    if (opts && opts->demo_mode) {
        domino_sys_log(sys, DOMINO_LOG_INFO, "game", "Demo mode enabled");
    }
    if (opts && opts->server_mode != DMN_GAME_SERVER_OFF) {
        const char* server_str = dmn_game_server_mode_to_string(opts->server_mode);
        domino_sys_log(sys, DOMINO_LOG_INFO, "game", server_str ? server_str : "server");
    }

    if (selected_mode != DMN_GAME_MODE_GUI) {
        /* Stub paths for TUI/headless for now; server/client wiring to follow. */
        domino_package_registry_destroy(reg);
        domino_sys_shutdown(sys);
        return 0;
    }

    if (domino_gfx_create_device(sys, &gdesc, &gfx) != 0) {
        domino_package_registry_destroy(reg);
        domino_sys_shutdown(sys);
        return 1;
    }

    for (i = 0; i < 60; ++i) {
        domino_gfx_begin_frame(gfx);
        domino_gfx_clear(gfx, 0.0f, 0.0f, 0.2f, 1.0f);
        domino_gfx_end_frame(gfx);
    }

    domino_gfx_destroy_device(gfx);
    domino_package_registry_destroy(reg);
    domino_sys_shutdown(sys);
    return 0;
}

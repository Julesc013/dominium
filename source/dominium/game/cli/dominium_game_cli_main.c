#include <stdio.h>
#include <string.h>

#include "domino/mod.h"
#include "dominium/game_api.h"
#include "dominium/product_info.h"
#include "dominium/version.h"
#include "g_modes.h"
#include "g_runtime.h"

static int dom_parse_arg(const char* arg, const char* prefix, char* out, size_t cap)
{
    size_t len;
    if (!arg || !prefix || !out || cap == 0) return 0;
    len = strlen(prefix);
    if (strncmp(arg, prefix, len) != 0) return 0;
    strncpy(out, arg + len, cap - 1);
    out[cap - 1] = '\0';
    return 1;
}

int main(int argc, char** argv)
{
    domino_instance_desc inst;
    int i;
    char instance_path[260];
    int has_path = 0;
    char mode_value[32];
    char server_value[32];
    DmnGameLaunchOptions launch_opts;

    memset(&inst, 0, sizeof(inst));
    strncpy(inst.id, "default", sizeof(inst.id) - 1);
    strncpy(inst.label, "Default Instance", sizeof(inst.label) - 1);
    strncpy(inst.product_id, DOMINIUM_GAME_ID, sizeof(inst.product_id) - 1);
    dominium_game_get_version(&inst.product_version);
    dmn_game_default_options(&launch_opts);
    mode_value[0] = '\0';
    server_value[0] = '\0';

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--introspect-json") == 0) {
            dominium_print_product_info_json(dom_get_product_info_game(), stdout);
            return 0;
        }
        if (dom_parse_arg(argv[i], "--instance=", instance_path, sizeof(instance_path))) {
            has_path = 1;
        } else if (dom_parse_arg(argv[i], "--mode=", mode_value, sizeof(mode_value))) {
            if (!dmn_game_mode_from_string(mode_value, &launch_opts.mode)) {
                fprintf(stderr, "Unknown --mode value '%s'\n", mode_value);
                return 1;
            }
        } else if (dom_parse_arg(argv[i], "--server=", server_value, sizeof(server_value))) {
            if (!dmn_game_server_mode_from_string(server_value, &launch_opts.server_mode)) {
                fprintf(stderr, "Unknown --server value '%s'\n", server_value);
                return 1;
            }
        } else if (strcmp(argv[i], "--demo") == 0) {
            launch_opts.demo_mode = 1;
        }
    }

    if (has_path) {
        if (domino_instance_load(instance_path, &inst) != 0) {
            printf("Failed to load instance: %s\n", instance_path);
            return 1;
        }
    }

    /* Dedicated server should always run headless. */
    if (launch_opts.server_mode == DMN_GAME_SERVER_DEDICATED) {
        launch_opts.mode = DMN_GAME_MODE_HEADLESS;
    }
    dmn_game_set_launch_options(&launch_opts);

    return dominium_game_run(&inst);
}

#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "domino/sys.h"
#include "domino/gfx.h"
#include "dominium/launch_api.h"
#include "dominium/product_info.h"

static void dom_launcher_print_usage(void)
{
    printf("Usage: dominium_launcher_cli [--introspect-json] [--platform=<backend>] [--renderer=<backend>]\n");
}

int main(int argc, char** argv)
{
    char platform_value[32];
    char renderer_value[32];
    int i;

    platform_value[0] = '\0';
    renderer_value[0] = '\0';
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--introspect-json") == 0) {
            dominium_print_product_info_json(dom_get_product_info_launcher(), stdout);
            return 0;
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            dom_launcher_print_usage();
            return 0;
        } else if (strncmp(argv[i], "--platform=", 11) == 0) {
            strncpy(platform_value, argv[i] + 11, sizeof(platform_value) - 1);
            platform_value[sizeof(platform_value) - 1] = '\0';
        } else if (strncmp(argv[i], "--renderer=", 11) == 0) {
            strncpy(renderer_value, argv[i] + 11, sizeof(renderer_value) - 1);
            renderer_value[sizeof(renderer_value) - 1] = '\0';
        }
    }
    if (platform_value[0]) {
        if (dom_sys_select_backend(platform_value) != 0) {
            fprintf(stderr, "Unsupported platform backend '%s'\n", platform_value);
            return 1;
        }
    }
    if (renderer_value[0]) {
        if (dom_gfx_select_backend(renderer_value) != 0) {
            fprintf(stderr, "Unsupported renderer backend '%s'\n", renderer_value);
            return 1;
        }
    }
    /* Later: parse args for specific view/instance actions. */
    return dominium_launcher_run(NULL);
}

#include <stdio.h>
#include <string.h>
#include "domino/sys.h"
#include "domino/gfx.h"
#include "dominium/tool_api.h"
#include "dominium/product_info.h"

static void print_usage(void)
{
    const dom_tool_desc *tools = NULL;
    uint32_t count = dom_tool_list(&tools);
    uint32_t i;

    printf("Usage: dominium-tools [--platform=<backend>] [--renderer=<backend>] [--introspect-json] <tool> [args]\n");
    printf("Available tools:\n");
    for (i = 0; i < count; ++i) {
        const char *id   = tools[i].id ? tools[i].id : "(unknown)";
        const char *desc = tools[i].description ? tools[i].description : "";
        printf("  %-12s %s\n", id, desc);
    }
}

int main(int argc, char **argv)
{
    dom_tool_env env;
    int rc;
    int i;
    int tool_index = -1;
    char platform_value[32];
    char renderer_value[32];

    platform_value[0] = '\0';
    renderer_value[0] = '\0';

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--introspect-json") == 0) {
            dominium_print_product_info_json(dom_get_product_info_tools(), stdout);
            return 0;
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            print_usage();
            return 0;
        } else if (strncmp(argv[i], "--platform=", 11) == 0) {
            strncpy(platform_value, argv[i] + 11, sizeof(platform_value) - 1);
            platform_value[sizeof(platform_value) - 1] = '\0';
        } else if (strncmp(argv[i], "--renderer=", 11) == 0) {
            strncpy(renderer_value, argv[i] + 11, sizeof(renderer_value) - 1);
            renderer_value[sizeof(renderer_value) - 1] = '\0';
        } else if (tool_index == -1) {
            tool_index = i;
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

    if (tool_index == -1) {
        print_usage();
        return 1;
    }

    memset(&env, 0, sizeof(env));
    env.struct_size = sizeof(env);
    env.struct_version = 1;
    env.write_stdout = NULL;
    env.write_stderr = NULL;
    env.io_user = NULL;
    env.core = NULL; /* could be set to a dom_core instance when available */

    rc = dom_tool_run(argv[tool_index], &env, argc - tool_index, argv + tool_index);
    if (rc == -1) {
        fprintf(stderr, "Unknown tool '%s'\n", argv[tool_index]);
        print_usage();
    }
    return rc;
}

#include <stdio.h>
#include <string.h>
#include "dominium/tool_api.h"

static void print_usage(void)
{
    const dom_tool_desc *tools = NULL;
    uint32_t count = dom_tool_list(&tools);
    uint32_t i;

    printf("Usage: dominium-tools <tool> [args]\n");
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

    if (argc < 2) {
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

    rc = dom_tool_run(argv[1], &env, argc - 1, argv + 1);
    if (rc == -1) {
        fprintf(stderr, "Unknown tool '%s'\n", argv[1]);
        print_usage();
    }
    return rc;
}

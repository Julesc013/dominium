/*
FILE: source/dominium/tools/core/tool_host_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/core/tool_host_cli
RESPONSIBILITY: Implements `tool_host_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include "domino/sys.h"
#include "domino/gfx.h"
#include "domino/input/input.h"
#include "domino/input/ime.h"
#include "domino/state/state.h"
#include "dominium/tool_api.h"
#include "dominium/product_info.h"

typedef enum tool_state {
    TOOL_STATE_MENU = 0,
    TOOL_STATE_VERIFY_MOD,
    TOOL_STATE_VERIFY_PACK,
    TOOL_STATE_MAX
} tool_state;

typedef struct tool_state_ctx {
    const char*   tool_id;
    dom_tool_env* env;
    int           argc;
    char**        argv;
    int           running;
    int           result;
} tool_state_ctx;

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

static void tool_state_stop(void* userdata)
{
    tool_state_ctx* ctx = (tool_state_ctx*)userdata;
    if (ctx) {
        ctx->running = 0;
    }
}

static void tool_state_enter_run(void* userdata)
{
    tool_state_ctx* ctx = (tool_state_ctx*)userdata;
    if (!ctx || !ctx->tool_id) {
        return;
    }
    ctx->result = dom_tool_run(ctx->tool_id, ctx->env, ctx->argc, (const char**)ctx->argv);
    ctx->running = 0;
}

int dom_tools_entry_cli(int argc, char **argv)
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

    d_input_init();
    d_ime_init();
    d_ime_enable();

    if (tool_index == -1) {
        print_usage();
        d_ime_shutdown();
        d_input_shutdown();
        return 1;
    }

    memset(&env, 0, sizeof(env));
    env.struct_size = sizeof(env);
    env.struct_version = 1;
    env.write_stdout = NULL;
    env.write_stderr = NULL;
    env.io_user = NULL;
    env.core = NULL; /* could be set to a dom_core instance when available */

    {
        d_state states[TOOL_STATE_MAX];
        d_state_machine sm;
        tool_state_ctx tctx;
        tool_state start = TOOL_STATE_MENU;
        u32 s;

        for (s = 0u; s < TOOL_STATE_MAX; ++s) {
            states[s].on_enter = NULL;
            states[s].on_update = tool_state_stop;
            states[s].on_exit = NULL;
        }
        states[TOOL_STATE_MENU].on_enter = tool_state_enter_run;
        states[TOOL_STATE_VERIFY_MOD].on_enter = tool_state_enter_run;
        states[TOOL_STATE_VERIFY_PACK].on_enter = tool_state_enter_run;

        tctx.tool_id = argv[tool_index];
        tctx.env = &env;
        tctx.argc = argc - tool_index;
        tctx.argv = argv + tool_index;
        tctx.running = 1;
        tctx.result = 0;

        if (strcmp(tctx.tool_id, "verify_mod") == 0) {
            start = TOOL_STATE_VERIFY_MOD;
        } else if (strcmp(tctx.tool_id, "verify_pack") == 0) {
            start = TOOL_STATE_VERIFY_PACK;
        } else {
            start = TOOL_STATE_MENU;
        }

        d_state_machine_init(&sm, states, TOOL_STATE_MAX, &tctx);
        d_state_machine_set(&sm, start);
        while (tctx.running) {
            d_input_begin_frame();
            d_state_machine_update(&sm);
            d_input_end_frame();
        }
        rc = tctx.result;
    }

    if (rc == -1) {
        fprintf(stderr, "Unknown tool '%s'\n", argv[tool_index]);
        print_usage();
    }

    d_ime_shutdown();
    d_input_shutdown();
    return rc;
}

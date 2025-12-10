#include <stdio.h>
#include <string.h>
#include "dominium/tool_api.h"
#include "dominium/game_edit_api.h"
#include "domino/sys.h"

static void tool_log(dom_tool_ctx *ctx, const char *msg)
{
    if (ctx && ctx->env.write_stdout) {
        ctx->env.write_stdout(msg, ctx->env.io_user);
    } else {
        printf("%s", msg);
    }
}

static void tool_err(dom_tool_ctx *ctx, const char *msg)
{
    if (ctx && ctx->env.write_stderr) {
        ctx->env.write_stderr(msg, ctx->env.io_user);
    } else {
        fprintf(stderr, "%s", msg);
    }
}

static void usage(void)
{
    printf("Usage: game_edit --def-root <path> [--list <kind>] [--get <kind> <id>] [--set <kind> <id> <json>]\n");
}

int dom_tool_game_edit_main(dom_tool_ctx *ctx, int argc, char **argv)
{
    const char *root = NULL;
    const char *list_kind = NULL;
    const char *get_kind = NULL;
    const char *get_id = NULL;
    const char *set_kind = NULL;
    const char *set_id = NULL;
    const char *set_json = NULL;
    int i;
    dom_game_edit_desc desc;
    dom_game_edit_ctx *gctx;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--def-root") == 0 && i + 1 < argc) {
            root = argv[++i];
        } else if (strcmp(argv[i], "--list") == 0 && i + 1 < argc) {
            list_kind = argv[++i];
        } else if (strcmp(argv[i], "--get") == 0 && i + 2 < argc) {
            get_kind = argv[++i];
            get_id = argv[++i];
        } else if (strcmp(argv[i], "--set") == 0 && i + 3 < argc) {
            set_kind = argv[++i];
            set_id = argv[++i];
            set_json = argv[++i];
        } else {
            usage();
            return 1;
        }
    }

    if (dsys_init() != DSYS_OK) {
        tool_err(ctx, "Failed to initialize dsys\n");
        return 1;
    }

    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.def_root = root;

    gctx = dom_game_edit_open(&desc);
    if (!gctx) {
        tool_err(ctx, "Failed to open game definitions\n");
        dsys_shutdown();
        return 1;
    }

    if (list_kind) {
        char buf[1024];
        int n = dom_game_edit_list_entities(gctx, list_kind, buf, sizeof(buf));
        if (n >= 0) {
            tool_log(ctx, buf);
        } else {
            tool_err(ctx, "List failed\n");
        }
    }

    if (get_kind && get_id) {
        char buf[512];
        if (dom_game_edit_get_entity_json(gctx, get_kind, get_id, buf, sizeof(buf)) == 0) {
            tool_log(ctx, buf);
            tool_log(ctx, "\n");
        } else {
            tool_err(ctx, "Get failed\n");
        }
    }

    if (set_kind && set_id && set_json) {
        if (dom_game_edit_set_entity_json(gctx, set_kind, set_id, set_json) == 0) {
            tool_log(ctx, "Entity updated\n");
            dom_game_edit_save(gctx);
        } else {
            tool_err(ctx, "Set failed\n");
        }
    }

    dom_game_edit_close(gctx);
    dsys_shutdown();
    return 0;
}

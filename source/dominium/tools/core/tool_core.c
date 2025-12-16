/*
FILE: source/dominium/tools/core/tool_core.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/core/tool_core
RESPONSIBILITY: Implements `tool_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include <stdio.h>
#include "dominium/tool_api.h"

typedef struct {
    dom_tool_desc desc;
} dom_tool_reg_entry;

/* forward declarations of built-in tools; will be added later: */
int dom_tool_assetc_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_pack_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_replay_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_test_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_world_edit_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_save_edit_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_game_edit_main(dom_tool_ctx *ctx, int argc, char **argv);
int dom_tool_launcher_edit_main(dom_tool_ctx *ctx, int argc, char **argv);
/* world_edit, save_edit, game_edit, launcher_edit will be added later */

static dom_tool_reg_entry g_tools[] = {
    { { sizeof(dom_tool_desc), 1, "assetc", "Asset Compiler", "Compile raw assets into packs", DOM_TOOL_KIND_BUILD,     dom_tool_assetc_main } },
    { { sizeof(dom_tool_desc), 1, "pack",   "Pack Builder",   "Assemble packs and versions",  DOM_TOOL_KIND_BUILD,     dom_tool_pack_main   } },
    { { sizeof(dom_tool_desc), 1, "replay", "Replay Inspector","Inspect and dump replay files", DOM_TOOL_KIND_ANALYSIS, dom_tool_replay_main } },
    { { sizeof(dom_tool_desc), 1, "test",   "Test Runner",     "Run deterministic engine tests", DOM_TOOL_KIND_ANALYSIS, dom_tool_test_main   } },
    { { sizeof(dom_tool_desc), 1, "world_edit",    "World Editor",    "Edit world chunks/regions",       DOM_TOOL_KIND_EDITOR,  dom_tool_world_edit_main    } },
    { { sizeof(dom_tool_desc), 1, "save_edit",     "Save Editor",     "Inspect and edit save games",     DOM_TOOL_KIND_EDITOR,  dom_tool_save_edit_main     } },
    { { sizeof(dom_tool_desc), 1, "game_edit",     "Game Def Editor", "Edit game definition data",       DOM_TOOL_KIND_EDITOR,  dom_tool_game_edit_main     } },
    { { sizeof(dom_tool_desc), 1, "launcher_edit", "Launcher Editor", "Edit launcher layout/config",     DOM_TOOL_KIND_EDITOR,  dom_tool_launcher_edit_main } },
};

uint32_t dom_tool_list(const dom_tool_desc **out_array)
{
    if (out_array) {
        *out_array = &g_tools[0].desc;
    }
    return (uint32_t)(sizeof(g_tools) / sizeof(g_tools[0]));
}

int dom_tool_run(const char *id, dom_tool_env *env, int argc, char **argv)
{
    uint32_t i;
    for (i = 0; i < sizeof(g_tools)/sizeof(g_tools[0]); ++i) {
        if (g_tools[i].desc.id && id && strcmp(g_tools[i].desc.id, id) == 0) {
            dom_tool_ctx ctx;
            memset(&ctx, 0, sizeof(ctx));
            if (env) ctx.env = *env;
            return g_tools[i].desc.entry(&ctx, argc, argv);
        }
    }
    return -1; /* not found */
}

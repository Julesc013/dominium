#include "dominium/game/game_app.hpp"
#include "domino/cli/cli.h"
#include "domino/sim/sim.h"
#include "domino/system/dsys.h"
#include "dominium/version.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>

struct GameCliContext {
    GameApp* app;
};

static int game_parse_u32(const char* text, u32* out_val) {
    char* endp;
    unsigned long v;
    if (!text || !out_val) {
        return 0;
    }
    v = std::strtoul(text, &endp, 10);
    if (text == endp) {
        return 0;
    }
    *out_val = (u32)v;
    return 1;
}

static int game_cmd_run_headless(int argc, const char** argv, void* userdata) {
    GameCliContext* ctx = (GameCliContext*)userdata;
    d_cli_args args;
    const d_cli_token* tok;
    u32 seed = 12345u;
    u32 ticks = 100u;
    u32 width = 64u;
    u32 height = 64u;
    int rc;
    int i;

    if (!ctx || !ctx->app) {
        return D_CLI_ERR_STATE;
    }

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    tok = d_cli_find_option(&args, "seed");
    if (tok && tok->has_value && tok->value) {
        if (!game_parse_u32(tok->value, &seed)) {
            d_cli_args_dispose(&args);
            std::printf("Game: invalid seed value\n");
            return D_CLI_BAD_USAGE;
        }
    }
    tok = d_cli_find_option(&args, "ticks");
    if (tok && tok->has_value && tok->value) {
        if (!game_parse_u32(tok->value, &ticks)) {
            d_cli_args_dispose(&args);
            std::printf("Game: invalid ticks value\n");
            return D_CLI_BAD_USAGE;
        }
    }
    tok = d_cli_find_option(&args, "width");
    if (tok && tok->has_value && tok->value) {
        if (!game_parse_u32(tok->value, &width)) {
            d_cli_args_dispose(&args);
            std::printf("Game: invalid width value\n");
            return D_CLI_BAD_USAGE;
        }
    }
    tok = d_cli_find_option(&args, "height");
    if (tok && tok->has_value && tok->value) {
        if (!game_parse_u32(tok->value, &height)) {
            d_cli_args_dispose(&args);
            std::printf("Game: invalid height value\n");
            return D_CLI_BAD_USAGE;
        }
    }

    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            d_cli_args_dispose(&args);
            std::printf("Game: unexpected positional argument '%s'\n",
                        t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "seed") ||
            d_cli_match_key(t, "ticks") ||
            d_cli_match_key(t, "width") ||
            d_cli_match_key(t, "height") ||
            d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Game: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->run_headless(seed, ticks, width, height);
    d_cli_args_dispose(&args);
    return rc;
}

static int game_cmd_run_tui(int argc, const char** argv, void* userdata) {
    (void)argc;
    (void)argv;
    (void)userdata;
    std::printf("Game: TUI mode is not implemented.\n");
    return D_CLI_BAD_USAGE;
}

static int game_cmd_run_gui(int argc, const char** argv, void* userdata) {
    (void)argc;
    (void)argv;
    (void)userdata;
    std::printf("Game: GUI mode is not implemented.\n");
    return D_CLI_BAD_USAGE;
}

static int game_cmd_world_checksum(int argc, const char** argv, void* userdata) {
    GameCliContext* ctx = (GameCliContext*)userdata;
    d_cli_args args;
    const d_cli_token* tok;
    const char* path = "world.tlv";
    u32 checksum = 0u;
    int rc;
    int i;

    if (!ctx || !ctx->app) {
        return D_CLI_ERR_STATE;
    }

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    tok = d_cli_find_option(&args, "path");
    if (tok && tok->has_value && tok->value) {
        path = tok->value;
    } else {
        const d_cli_token* pos = d_cli_get_positional(&args, 0);
        if (pos && pos->value) {
            path = pos->value;
        }
    }

    if (d_cli_count_positionals(&args) > 1) {
        d_cli_args_dispose(&args);
        std::printf("Game: too many positional arguments\n");
        return D_CLI_BAD_USAGE;
    }

    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            continue;
        }
        if (d_cli_match_key(t, "path") || d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Game: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->load_world_checksum(path, &checksum);
    if (rc == 0) {
        std::printf("World checksum for %s: %08X\n", path, (unsigned)checksum);
    }
    d_cli_args_dispose(&args);
    return rc;
}

static int game_cmd_world_load(int argc, const char** argv, void* userdata) {
    GameCliContext* ctx = (GameCliContext*)userdata;
    d_cli_args args;
    const d_cli_token* tok;
    const char* path = "world.tlv";
    u32 checksum = 0u;
    int rc;
    int i;

    if (!ctx || !ctx->app) {
        return D_CLI_ERR_STATE;
    }

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    tok = d_cli_find_option(&args, "path");
    if (tok && tok->has_value && tok->value) {
        path = tok->value;
    } else {
        const d_cli_token* pos = d_cli_get_positional(&args, 0);
        if (pos && pos->value) {
            path = pos->value;
        }
    }

    if (d_cli_count_positionals(&args) > 1) {
        d_cli_args_dispose(&args);
        std::printf("Game: too many positional arguments\n");
        return D_CLI_BAD_USAGE;
    }

    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            continue;
        }
        if (d_cli_match_key(t, "path") || d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Game: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->load_world_checksum(path, &checksum);
    if (rc == 0) {
        std::printf("World load OK: %s (checksum %08X)\n",
                    path, (unsigned)checksum);
    }
    d_cli_args_dispose(&args);
    return rc;
}

GameApp::GameApp() {
}

GameApp::~GameApp() {
}

int GameApp::run(int argc, char** argv) {
    d_cli cli;
    GameCliContext ctx;
    int rc;

    ctx.app = this;
    d_cli_init(&cli, (argc > 0) ? argv[0] : "dominium_game",
               DOMINIUM_GAME_VERSION);

    rc = d_cli_register(&cli, "run-headless",
                        "Run deterministic headless simulation",
                        game_cmd_run_headless, &ctx);
    if (rc != D_CLI_OK) {
        return rc;
    }
    rc = d_cli_register(&cli, "run-tui", "Launch text UI (stub)",
                        game_cmd_run_tui, &ctx);
    if (rc != D_CLI_OK) {
        return rc;
    }
    rc = d_cli_register(&cli, "run-gui", "Launch graphical UI (stub)",
                        game_cmd_run_gui, &ctx);
    if (rc != D_CLI_OK) {
        return rc;
    }
    rc = d_cli_register(&cli, "world-checksum",
                        "Load a world file and print its checksum",
                        game_cmd_world_checksum, &ctx);
    if (rc != D_CLI_OK) {
        return rc;
    }
    rc = d_cli_register(&cli, "world-load",
                        "Load a world file to verify format integrity",
                        game_cmd_world_load, &ctx);
    if (rc != D_CLI_OK) {
        return rc;
    }

    rc = d_cli_dispatch(&cli, argc, (const char**)argv);
    d_cli_shutdown(&cli);
    return rc;
}

int GameApp::run_headless(u32 seed, u32 ticks, u32 width, u32 height) {
    d_world_config cfg;
    d_world* world;
    u32 t;
    u32 checksum;

    cfg.seed = seed;
    cfg.width = width;
    cfg.height = height;

    if (dsys_init() != DSYS_OK) {
        std::printf("Game: dsys_init failed.\n");
        return 1;
    }

    world = d_world_create(&cfg);
    if (!world) {
        std::printf("Game: d_world_create failed.\n");
        dsys_shutdown();
        return 1;
    }

    for (t = 0; t < ticks; ++t) {
        d_world_tick(world);
    }

    checksum = d_world_checksum(world);

    std::printf("Game headless result:\n");
    std::printf("  seed      = %u\n", (unsigned)seed);
    std::printf("  ticks     = %u\n", (unsigned)ticks);
    std::printf("  width     = %u\n", (unsigned)width);
    std::printf("  height    = %u\n", (unsigned)height);
    std::printf("  checksum  = %08X\n", (unsigned)checksum);

    {
        const char* path = "world.tlv";
        if (!d_world_save_tlv(world, path)) {
            std::printf("  save_tlv  = FAILED (%s)\n", path);
        } else {
            std::printf("  save_tlv  = OK (%s)\n", path);
        }
    }

    d_world_destroy(world);
    dsys_shutdown();
    return 0;
}

int GameApp::load_world_checksum(const char* path, u32* checksum_out) {
    d_world* world;
    u32 checksum;

    if (!path) {
        return 1;
    }

    world = d_world_load_tlv(path);
    if (!world) {
        std::printf("Game: failed to load world '%s'\n", path);
        return 1;
    }

    checksum = d_world_checksum(world);
    if (checksum_out) {
        *checksum_out = checksum;
    }
    d_world_destroy(world);
    return 0;
}

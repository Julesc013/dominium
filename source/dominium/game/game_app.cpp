#include "dominium/game/game_app.hpp"
#include "domino/cli/cli.h"
#include "domino/gui/gui.h"
#include "domino/sim/sim.h"
#include "domino/system/dsys.h"
#include "domino/tui/tui.h"
#include "domino/render/backend_detect.h"
#include "domino/render/pipeline.h"
#include "domino/input/input.h"
#include "domino/input/ime.h"
#include "domino/state/state.h"
#include "domino/app/startup.h"
#include "dominium/version.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>

struct GameCliContext {
    GameApp* app;
};

enum GameState {
    GAME_STATE_MENU = 0,
    GAME_STATE_RUNNING_HEADLESS,
    GAME_STATE_RUNNING_TUI,
    GAME_STATE_RUNNING_GUI,
    GAME_STATE_MAX
};

struct GameStateContext {
    GameApp* app;
    u32      seed;
    u32      ticks;
    u32      width;
    u32      height;
    int      running;
    int      result;
};

static int  game_run_headless_impl(GameApp* app, u32 seed, u32 ticks, u32 width, u32 height);
static int  game_run_tui_impl(GameApp* app);
static int  game_run_gui_impl(GameApp* app);
static void game_state_stop(void* userdata);
static void game_state_enter_headless(void* userdata);
static void game_state_enter_tui(void* userdata);
static void game_state_enter_gui(void* userdata);

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
    GameCliContext* ctx = (GameCliContext*)userdata;
    d_cli_args args;
    int rc;
    int i;

    if (!ctx || !ctx->app) {
        return D_CLI_ERR_STATE;
    }

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }
    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            d_cli_args_dispose(&args);
            std::printf("Game: unexpected positional argument '%s'\n",
                        t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Game: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    d_cli_args_dispose(&args);
    return ctx->app->run_tui_mode();
}

static int game_cmd_run_gui(int argc, const char** argv, void* userdata) {
    GameCliContext* ctx = (GameCliContext*)userdata;
    d_cli_args args;
    int rc;
    int i;

    if (!ctx || !ctx->app) {
        return D_CLI_ERR_STATE;
    }
    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) return rc;
    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            d_cli_args_dispose(&args);
            std::printf("Game: unexpected positional '%s'\n", t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) continue;
        d_cli_args_dispose(&args);
        std::printf("Game: unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    d_cli_args_dispose(&args);
    return ctx->app->run_gui_mode();
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

struct GameTuiState {
    d_tui_widget* status;
    int*          running_flag;
};

static void game_tui_set_status(GameTuiState* state, const char* text) {
    if (!state || !state->status) return;
    d_tui_widget_set_text(state->status, text);
}

static void game_tui_on_run_headless(d_tui_widget* self, void* user) {
    (void)self;
    game_tui_set_status((GameTuiState*)user, "Run headless (stub)");
}

static void game_tui_on_step(d_tui_widget* self, void* user) {
    (void)self;
    game_tui_set_status((GameTuiState*)user, "Step world (stub)");
}

static void game_tui_on_checksum(d_tui_widget* self, void* user) {
    (void)self;
    game_tui_set_status((GameTuiState*)user, "Checksum (stub)");
}

static void game_tui_on_exit(d_tui_widget* self, void* user) {
    GameTuiState* st = (GameTuiState*)user;
    (void)self;
    if (st && st->running_flag) {
        *(st->running_flag) = 0;
    }
}

static void game_state_stop(void* userdata) {
    GameStateContext* ctx = (GameStateContext*)userdata;
    if (ctx) {
        ctx->running = 0;
    }
}

static int game_run_headless_impl(GameApp* app, u32 seed, u32 ticks, u32 width, u32 height) {
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
        d_input_begin_frame();
        d_world_tick(world);
        d_input_end_frame();
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

static int game_run_tui_impl(GameApp* app) {
    d_tui_context* tui;
    d_tui_widget* root;
    d_tui_widget* header;
    d_tui_widget* status;
    d_tui_widget* actions;
    int running = 1;
    GameTuiState state;

    (void)app;

    if (!dsys_terminal_init()) {
        std::printf("Game: terminal init failed.\n");
        return D_APP_ERR_TUI_UNSUPPORTED;
    }

    tui = d_tui_create();
    if (!tui) {
        dsys_terminal_shutdown();
        return D_APP_ERR_TUI_UNSUPPORTED;
    }

    root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    header = d_tui_label(tui, "Dominium Game TUI");
    actions = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    status = d_tui_label(tui, "Ready");

    d_tui_widget_add(root, header);
    d_tui_widget_add(root, actions);
    d_tui_widget_add(root, status);

    state.status = status;
    state.running_flag = &running;

    d_tui_widget_add(actions, d_tui_button(tui, "Run headless", game_tui_on_run_headless, &state));
    d_tui_widget_add(actions, d_tui_button(tui, "Step world", game_tui_on_step, &state));
    d_tui_widget_add(actions, d_tui_button(tui, "Checksum", game_tui_on_checksum, &state));
    d_tui_widget_add(actions, d_tui_button(tui, "Exit", game_tui_on_exit, &state));

    d_tui_set_root(tui, root);

    while (running) {
        d_input_event ev;
        d_input_begin_frame();
        while (d_input_poll(&ev)) {
            if (ev.type == D_INPUT_KEYDOWN) {
                int key = ev.param1;
                if (key == 'q' || key == 'Q' || key == 27) {
                    running = 0;
                    break;
                }
                d_tui_handle_key(tui, key);
            } else if (ev.type == D_INPUT_CHAR) {
                int key = ev.param1;
                d_tui_handle_key(tui, key);
            }
        }
        d_tui_render(tui);
        d_input_end_frame();
    }

    d_tui_destroy(tui);
    dsys_terminal_shutdown();
    return 0;
}

static int game_run_gui_impl(GameApp* app) {
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    d_gfx_backend_type backend;
    d_gfx_pipeline* pipeline = NULL;
    d_gui_window* main_win = NULL;
    d_gui_window* log_win = NULL;
    dgui_context* gui;
    const float dt = 1.0f / 60.0f;
    int frames = 0;
    int rc = 1;

    (void)app;
    std::memset(infos, 0, sizeof(infos));

    if (dsys_init() != DSYS_OK) {
        std::printf("Game: dsys_init failed.\n");
        return D_APP_ERR_GUI_UNSUPPORTED;
    }

    d_gfx_detect_backends(infos, D_GFX_BACKEND_MAX);
    backend = d_gfx_select_backend();
    pipeline = d_gfx_pipeline_create(backend);
    if (!pipeline && backend != D_GFX_BACKEND_SOFT) {
        pipeline = d_gfx_pipeline_create(D_GFX_BACKEND_SOFT);
    }
    if (!pipeline) {
        std::printf("Game: GUI not supported on this platform.\n");
        dsys_shutdown();
        return D_APP_ERR_GUI_UNSUPPORTED;
    }
    d_gui_set_shared_pipeline(pipeline);

    {
        d_gui_window_desc wdesc;
        wdesc.title = "Dominium Game";
        wdesc.x = 120;
        wdesc.y = 120;
        wdesc.width = 800;
        wdesc.height = 480;
        wdesc.resizable = 1;
        main_win = d_gui_window_create(&wdesc);
    }
    if (main_win) {
        dgui_widget* root;
        dgui_widget* header;
        dgui_widget* actions;
        dgui_widget* status;
        gui = d_gui_window_get_gui(main_win);
        root = dgui_panel(gui, DGUI_LAYOUT_VERTICAL);
        header = dgui_label(gui, "Dominium Game GUI");
        actions = dgui_panel(gui, DGUI_LAYOUT_VERTICAL);
        status = dgui_label(gui, "Simulation ready");
        dgui_widget_add(root, header);
        dgui_widget_add(root, actions);
        dgui_widget_add(root, status);
        dgui_widget_add(actions, dgui_button(gui, "Run", NULL, NULL));
        dgui_widget_add(actions, dgui_button(gui, "Step", NULL, NULL));
        dgui_widget_add(actions, dgui_button(gui, "Checksum", NULL, NULL));
        dgui_widget_add(actions, dgui_button(gui, "Exit", NULL, NULL));
        d_gui_window_set_root(main_win, root);
    }

    {
        d_gui_window_desc ldesc;
        ldesc.title = "Log / Inspector";
        ldesc.x = 940;
        ldesc.y = 140;
        ldesc.width = 360;
        ldesc.height = 260;
        ldesc.resizable = 0;
        log_win = d_gui_window_create(&ldesc);
    }
    if (log_win) {
        dgui_context* lctx = d_gui_window_get_gui(log_win);
        dgui_widget* root = dgui_panel(lctx, DGUI_LAYOUT_VERTICAL);
        dgui_widget* header = dgui_label(lctx, "Backends");
        dgui_widget* list = dgui_panel(lctx, DGUI_LAYOUT_VERTICAL);
        u32 i;
        dgui_widget_add(root, header);
        dgui_widget_add(root, list);
        for (i = 0; i < D_GFX_BACKEND_MAX; ++i) {
            if (infos[i].name[0] == '\0') continue;
            dgui_widget_add(list, dgui_label(lctx, infos[i].name));
        }
        d_gui_window_set_root(log_win, root);
    }

    while (d_gui_any_window_alive() && frames < 3) {
        d_gui_tick_all_windows(dt);
        ++frames;
    }

    if (log_win) d_gui_window_destroy(log_win);
    if (main_win) d_gui_window_destroy(main_win);
    d_gui_set_shared_pipeline(NULL);
    d_gfx_pipeline_destroy(pipeline);
    dsys_shutdown();
    rc = 0;
    return rc;
}

static void game_state_enter_headless(void* userdata) {
    GameStateContext* ctx = (GameStateContext*)userdata;
    if (!ctx || !ctx->app) {
        return;
    }
    ctx->result = game_run_headless_impl(ctx->app, ctx->seed, ctx->ticks, ctx->width, ctx->height);
    ctx->running = 0;
}

static void game_state_enter_tui(void* userdata) {
    GameStateContext* ctx = (GameStateContext*)userdata;
    if (!ctx || !ctx->app) {
        return;
    }
    ctx->result = game_run_tui_impl(ctx->app);
    ctx->running = 0;
}

static void game_state_enter_gui(void* userdata) {
    GameStateContext* ctx = (GameStateContext*)userdata;
    if (!ctx || !ctx->app) {
        return;
    }
    ctx->result = game_run_gui_impl(ctx->app);
    ctx->running = 0;
}

GameApp::GameApp() {
}

GameApp::~GameApp() {
}

int GameApp::run(int argc, char** argv) {
    d_cli cli;
    GameCliContext ctx;
    int rc = 0;
    int i;
    int cli_initialized = 0;
    int input_initialized = 0;

    d_input_init();
    d_ime_init();
    d_ime_enable();
    input_initialized = 1;

    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--mode=tui") == 0) {
            rc = run_tui_mode();
            goto cleanup;
        }
        if (std::strcmp(argv[i], "--mode=headless") == 0) {
            rc = run_headless(12345u, 100u, 64u, 64u);
            goto cleanup;
        }
    }

    ctx.app = this;
    d_cli_init(&cli, (argc > 0) ? argv[0] : "dominium_game",
               DOMINIUM_GAME_VERSION);
    cli_initialized = 1;

    rc = d_cli_register(&cli, "run-headless",
                        "Run deterministic headless simulation",
                        game_cmd_run_headless, &ctx);
    if (rc != D_CLI_OK) goto cleanup;
    rc = d_cli_register(&cli, "run-tui", "Launch text UI (stub)",
                        game_cmd_run_tui, &ctx);
    if (rc != D_CLI_OK) goto cleanup;
    rc = d_cli_register(&cli, "run-gui", "Launch graphical UI (stub)",
                        game_cmd_run_gui, &ctx);
    if (rc != D_CLI_OK) goto cleanup;
    rc = d_cli_register(&cli, "world-checksum",
                        "Load a world file and print its checksum",
                        game_cmd_world_checksum, &ctx);
    if (rc != D_CLI_OK) goto cleanup;
    rc = d_cli_register(&cli, "world-load",
                        "Load a world file to verify format integrity",
                        game_cmd_world_load, &ctx);
    if (rc != D_CLI_OK) goto cleanup;

    rc = d_cli_dispatch(&cli, argc, (const char**)argv);

cleanup:
    if (cli_initialized) {
        d_cli_shutdown(&cli);
    }
    if (input_initialized) {
        d_ime_shutdown();
        d_input_shutdown();
    }
    return rc;
}

int GameApp::run_headless(u32 seed, u32 ticks, u32 width, u32 height) {
    d_state states[GAME_STATE_MAX];
    d_state_machine sm;
    GameStateContext ctx;
    u32 i;

    ctx.app = this;
    ctx.seed = seed;
    ctx.ticks = ticks;
    ctx.width = width;
    ctx.height = height;
    ctx.running = 1;
    ctx.result = 0;

    for (i = 0u; i < GAME_STATE_MAX; ++i) {
        states[i].on_enter = NULL;
        states[i].on_update = NULL;
        states[i].on_exit = NULL;
    }
    states[GAME_STATE_MENU].on_update = game_state_stop;
    states[GAME_STATE_RUNNING_HEADLESS].on_enter = game_state_enter_headless;
    states[GAME_STATE_RUNNING_HEADLESS].on_update = game_state_stop;

    d_state_machine_init(&sm, states, GAME_STATE_MAX, &ctx);
    d_state_machine_set(&sm, GAME_STATE_RUNNING_HEADLESS);
    while (ctx.running) {
        d_state_machine_update(&sm);
    }
    return ctx.result;
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

int GameApp::run_tui_mode(void) {
    d_state states[GAME_STATE_MAX];
    d_state_machine sm;
    GameStateContext ctx;
    u32 i;

    ctx.app = this;
    ctx.seed = 0u;
    ctx.ticks = 0u;
    ctx.width = 0u;
    ctx.height = 0u;
    ctx.running = 1;
    ctx.result = 0;

    for (i = 0u; i < GAME_STATE_MAX; ++i) {
        states[i].on_enter = NULL;
        states[i].on_update = NULL;
        states[i].on_exit = NULL;
    }
    states[GAME_STATE_MENU].on_update = game_state_stop;
    states[GAME_STATE_RUNNING_TUI].on_enter = game_state_enter_tui;
    states[GAME_STATE_RUNNING_TUI].on_update = game_state_stop;

    d_state_machine_init(&sm, states, GAME_STATE_MAX, &ctx);
    d_state_machine_set(&sm, GAME_STATE_RUNNING_TUI);
    while (ctx.running) {
        d_state_machine_update(&sm);
    }
    return ctx.result;
}

int GameApp::run_gui_mode(void) {
    d_state states[GAME_STATE_MAX];
    d_state_machine sm;
    GameStateContext ctx;
    u32 i;

    ctx.app = this;
    ctx.seed = 0u;
    ctx.ticks = 0u;
    ctx.width = 0u;
    ctx.height = 0u;
    ctx.running = 1;
    ctx.result = 0;

    for (i = 0u; i < GAME_STATE_MAX; ++i) {
        states[i].on_enter = NULL;
        states[i].on_update = NULL;
        states[i].on_exit = NULL;
    }
    states[GAME_STATE_MENU].on_update = game_state_stop;
    states[GAME_STATE_RUNNING_GUI].on_enter = game_state_enter_gui;
    states[GAME_STATE_RUNNING_GUI].on_update = game_state_stop;

    d_state_machine_init(&sm, states, GAME_STATE_MAX, &ctx);
    d_state_machine_set(&sm, GAME_STATE_RUNNING_GUI);
    while (ctx.running) {
        d_state_machine_update(&sm);
    }
    return ctx.result;
}

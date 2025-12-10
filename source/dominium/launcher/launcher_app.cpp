#include "domino/cli/cli.h"
#include "domino/pkg/repo.h"
#include "domino/system/dsys.h"
#include "domino/tui/tui.h"
#include "dominium/launcher/launcher_app.hpp"
#include "dominium/version.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>

struct LauncherCliContext {
    LauncherApp* app;
    d_cli*       cli;
};

static void launcher_copy_string(const char* src, char* dst, size_t cap) {
    size_t len;
    if (!dst || cap == 0) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = std::strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    std::memcpy(dst, src, len);
    dst[len] = '\0';
}

static int launcher_parse_u32(const char* text, u32* out_val) {
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

static int launcher_cmd_list_products(int argc, const char** argv, void* userdata) {
    LauncherCliContext* ctx = (LauncherCliContext*)userdata;
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
            std::printf("Launcher: unexpected positional argument '%s'\n",
                        t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Launcher: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->run_list_products();
    d_cli_args_dispose(&args);
    return rc;
}

static int launcher_cmd_run_game(int argc, const char** argv, void* userdata) {
    LauncherCliContext* ctx = (LauncherCliContext*)userdata;
    d_cli_args args;
    const d_cli_token* tok;
    char instance_buf[D_CLI_INSTANCE_ID_MAX];
    const char* instance_id = NULL;
    u32 seed = 12345u;
    u32 ticks = 100u;
    int rc;
    int i;

    if (!ctx || !ctx->app) {
        return D_CLI_ERR_STATE;
    }
    instance_buf[0] = '\0';
    if (ctx->cli) {
        const d_cli_instance* inst = d_cli_get_instance(ctx->cli);
        if (inst && inst->present) {
            launcher_copy_string(inst->id, instance_buf, sizeof(instance_buf));
            instance_id = instance_buf;
        }
    }

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    tok = d_cli_find_option(&args, "seed");
    if (tok && tok->has_value && tok->value) {
        if (!launcher_parse_u32(tok->value, &seed)) {
            d_cli_args_dispose(&args);
            std::printf("Launcher: invalid seed value\n");
            return D_CLI_BAD_USAGE;
        }
    }
    tok = d_cli_find_option(&args, "ticks");
    if (tok && tok->has_value && tok->value) {
        if (!launcher_parse_u32(tok->value, &ticks)) {
            d_cli_args_dispose(&args);
            std::printf("Launcher: invalid ticks value\n");
            return D_CLI_BAD_USAGE;
        }
    }
    tok = d_cli_find_option(&args, "instance");
    if (tok && tok->has_value && tok->value) {
        launcher_copy_string(tok->value, instance_buf, sizeof(instance_buf));
        instance_id = instance_buf;
    }

    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            d_cli_args_dispose(&args);
            std::printf("Launcher: unexpected positional argument '%s'\n",
                        t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "seed") ||
            d_cli_match_key(t, "ticks") ||
            d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Launcher: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->run_run_game(seed, ticks, instance_id);
    d_cli_args_dispose(&args);
    return rc;
}

static int launcher_cmd_run_tool(int argc, const char** argv, void* userdata) {
    LauncherCliContext* ctx = (LauncherCliContext*)userdata;
    d_cli_args args;
    const d_cli_token* pos0;
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
        if (!t->is_positional && !d_cli_match_key(t, "instance")) {
            d_cli_args_dispose(&args);
            std::printf("Launcher: unknown option '%.*s'\n",
                        t->key_len, t->key ? t->key : "");
            return D_CLI_BAD_USAGE;
        }
    }

    pos0 = d_cli_get_positional(&args, 0);
    if (!pos0 || !pos0->value) {
        d_cli_args_dispose(&args);
        std::printf("Launcher: run-tool requires a tool id\n");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->run_run_tool(pos0->value);
    d_cli_args_dispose(&args);
    return rc;
}

static int launcher_cmd_manifest_info(int argc, const char** argv, void* userdata) {
    LauncherCliContext* ctx = (LauncherCliContext*)userdata;
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
            std::printf("Launcher: unexpected positional argument '%s'\n",
                        t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Launcher: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }

    rc = ctx->app->run_manifest_info();
    d_cli_args_dispose(&args);
    return rc;
}

static int launcher_cmd_tui(int argc, const char** argv, void* userdata) {
    LauncherCliContext* ctx = (LauncherCliContext*)userdata;
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
            std::printf("Launcher: unexpected positional argument '%s'\n",
                        t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) {
            continue;
        }
        d_cli_args_dispose(&args);
        std::printf("Launcher: unknown option '%.*s'\n",
                    t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    d_cli_args_dispose(&args);
    return ctx->app->run_tui();
}

static int launcher_cmd_gui(int argc, const char** argv, void* userdata) {
    LauncherCliContext* ctx = (LauncherCliContext*)userdata;
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
            std::printf("Launcher: unexpected positional '%s'\n", t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) continue;
        d_cli_args_dispose(&args);
        std::printf("Launcher: unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    d_cli_args_dispose(&args);
    return ctx->app->run_gui();
}

LauncherApp::LauncherApp() {
}

LauncherApp::~LauncherApp() {
}

int LauncherApp::run(int argc, char** argv) {
    d_cli cli;
    LauncherCliContext ctx;
    int rc;

    ctx.app = this;
    ctx.cli = &cli;

    d_cli_init(&cli, (argc > 0) ? argv[0] : "dominium_launcher",
               DOMINIUM_LAUNCHER_VERSION);

    rc = d_cli_register(&cli, "list-products",
                        "List known Dominium products", launcher_cmd_list_products, &ctx);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "run-game",
                        "Launch the game in headless mode", launcher_cmd_run_game, &ctx);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "run-tool",
                        "Launch a Dominium tool by id", launcher_cmd_run_tool, &ctx);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "manifest-info",
                        "Print manifest root and product metadata", launcher_cmd_manifest_info, &ctx);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "tui",
                        "Launch launcher text UI", launcher_cmd_tui, &ctx);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "gui",
                        "Launch launcher GUI", launcher_cmd_gui, &ctx);
    if (rc != D_CLI_OK) return rc;

    rc = d_cli_dispatch(&cli, argc, (const char**)argv);
    d_cli_shutdown(&cli);
    return rc;
}

int LauncherApp::run_list_products() {
    dom_product_info info;
    std::memset(&info, 0, sizeof(info));

    if (!dom_repo_load_primary_game(&info)) {
        std::printf("Launcher: failed to load primary game product manifest.\n");
        return 1;
    }

    std::printf("Launcher: primary game product:\n");
    std::printf("  product_id      = %s\n", info.product_id);
    std::printf("  role            = %d\n", (int)info.role);
    std::printf("  product_version = %s\n", info.product_version);
    std::printf("  core_version    = %s\n", info.core_version);
    std::printf("  os_family       = %d\n", (int)info.os_family);
    std::printf("  arch            = %d\n", (int)info.arch);
    std::printf("  exec_rel_path   = %s\n", info.exec_rel_path);
    std::printf("  compat.save_format_version    = %u\n", (unsigned)info.compat.save_format_version);
    std::printf("  compat.pack_format_version    = %u\n", (unsigned)info.compat.pack_format_version);
    std::printf("  compat.net_protocol_version   = %u\n", (unsigned)info.compat.net_protocol_version);
    std::printf("  compat.replay_format_version  = %u\n", (unsigned)info.compat.replay_format_version);
    std::printf("  compat.launcher_proto_version = %u\n", (unsigned)info.compat.launcher_proto_version);
    std::printf("  compat.tools_proto_version    = %u\n", (unsigned)info.compat.tools_proto_version);

    return 0;
}

int LauncherApp::run_run_game(u32 seed, u32 ticks, const char* instance_id) {
    dom_product_info info;
    char root[512];
    const char* platform_dir = "posix-x86_64";
    char exec_dir[768];
    char exec_full_path[1024];
    char seed_buf[32];
    char ticks_buf[32];
    char instance_buf[80];
    const char* game_argv[7];
    dsys_process_handle handle;
    dsys_proc_result pr;
    int exit_code;
    int argi = 0;

    std::memset(&info, 0, sizeof(info));
    if (!dom_repo_load_primary_game(&info)) {
        std::printf("Launcher: failed to load primary game product manifest.\n");
        return 1;
    }

    if (!dom_repo_get_root(root, sizeof(root))) {
        std::printf("Launcher: dom_repo_get_root failed.\n");
        return 1;
    }

    std::snprintf(exec_dir, sizeof(exec_dir),
                  "%s/repo/products/%s/%s/core-%s/%s",
                  root,
                  info.product_id,
                  info.product_version,
                  info.core_version,
                  platform_dir);

    std::snprintf(exec_full_path, sizeof(exec_full_path),
                  "%s/%s",
                  exec_dir,
                  info.exec_rel_path);

    std::printf("Launcher: spawning game:\n");
    std::printf("  path     = %s\n", exec_full_path);
    std::printf("  seed     = %lu\n", (unsigned long)seed);
    std::printf("  ticks    = %lu\n", (unsigned long)ticks);
    if (instance_id && instance_id[0]) {
        std::printf("  instance = %s\n", instance_id);
    }

    std::snprintf(seed_buf, sizeof(seed_buf), "--seed=%lu", (unsigned long)seed);
    std::snprintf(ticks_buf, sizeof(ticks_buf), "--ticks=%lu", (unsigned long)ticks);

    game_argv[argi++] = exec_full_path;
    game_argv[argi++] = "--mode=headless";
    game_argv[argi++] = seed_buf;
    game_argv[argi++] = ticks_buf;
    if (instance_id && instance_id[0]) {
        std::snprintf(instance_buf, sizeof(instance_buf), "--instance=%s", instance_id);
        game_argv[argi++] = instance_buf;
    }
    game_argv[argi] = 0;

    handle.impl = 0;

    if (dsys_init() != DSYS_OK) {
        std::printf("Launcher: dsys_init failed.\n");
        return 1;
    }

    pr = dsys_proc_spawn(exec_full_path, game_argv, 1, &handle);
    if (pr != DSYS_PROC_OK) {
        std::printf("Launcher: dsys_proc_spawn failed (%d)\n", (int)pr);
        dsys_shutdown();
        return 1;
    }

    exit_code = -1;
    pr = dsys_proc_wait(&handle, &exit_code);
    if (pr != DSYS_PROC_OK) {
        std::printf("Launcher: dsys_proc_wait failed (%d)\n", (int)pr);
        dsys_shutdown();
        return 1;
    }

    std::printf("Launcher: game exited with code %d\n", exit_code);

    dsys_shutdown();
    return exit_code;
}

int LauncherApp::run_run_tool(const char* tool_id) {
    std::printf("Launcher: run-tool '%s' is not implemented in this build.\n",
                tool_id ? tool_id : "(null)");
    return D_CLI_BAD_USAGE;
}

int LauncherApp::run_manifest_info() {
    dom_product_info info;
    char root[512];

    std::memset(&info, 0, sizeof(info));
    if (!dom_repo_get_root(root, sizeof(root))) {
        std::printf("Launcher: dom_repo_get_root failed.\n");
        return 1;
    }
    if (!dom_repo_load_primary_game(&info)) {
        std::printf("Launcher: failed to load primary game product manifest.\n");
        return 1;
    }

    std::printf("Launcher manifest info:\n");
    std::printf("  root          = %s\n", root);
    std::printf("  product_id    = %s\n", info.product_id);
    std::printf("  product_ver   = %s\n", info.product_version);
    std::printf("  core_version  = %s\n", info.core_version);
    return 0;
}

struct LauncherTuiState {
    d_tui_widget* status;
    int*          running_flag;
};

static void launcher_tui_set_status(LauncherTuiState* st, const char* text) {
    if (!st || !st->status) return;
    d_tui_widget_set_text(st->status, text);
}

static void launcher_tui_on_list(d_tui_widget* self, void* user) {
    (void)self;
    launcher_tui_set_status((LauncherTuiState*)user, "List products (stub)");
}

static void launcher_tui_on_run_headless(d_tui_widget* self, void* user) {
    (void)self;
    launcher_tui_set_status((LauncherTuiState*)user, "Run headless (stub)");
}

static void launcher_tui_on_run_gui(d_tui_widget* self, void* user) {
    (void)self;
    launcher_tui_set_status((LauncherTuiState*)user, "Run GUI (stub)");
}

static void launcher_tui_on_run_tui(d_tui_widget* self, void* user) {
    (void)self;
    launcher_tui_set_status((LauncherTuiState*)user, "Run TUI (stub)");
}

static void launcher_tui_on_exit(d_tui_widget* self, void* user) {
    LauncherTuiState* st = (LauncherTuiState*)user;
    (void)self;
    if (st && st->running_flag) {
        *(st->running_flag) = 0;
    }
}

int LauncherApp::run_tui() {
    d_tui_context* tui;
    d_tui_widget* root;
    d_tui_widget* header;
    d_tui_widget* actions;
    d_tui_widget* status;
    LauncherTuiState st;
    int running = 1;

    if (!dsys_terminal_init()) {
        std::printf("Launcher: terminal init failed.\n");
        return 1;
    }

    tui = d_tui_create();
    if (!tui) {
        dsys_terminal_shutdown();
        return 1;
    }

    root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    header = d_tui_label(tui, "Dominium Launcher TUI");
    actions = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    status = d_tui_label(tui, "Ready");

    d_tui_widget_add(root, header);
    d_tui_widget_add(root, actions);
    d_tui_widget_add(root, status);

    st.status = status;
    st.running_flag = &running;

    d_tui_widget_add(actions, d_tui_button(tui, "List products", launcher_tui_on_list, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Run headless", launcher_tui_on_run_headless, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Run GUI", launcher_tui_on_run_gui, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Run TUI", launcher_tui_on_run_tui, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Exit", launcher_tui_on_exit, &st));

    d_tui_set_root(tui, root);

    while (running) {
        int key;
        d_tui_render(tui);
        key = dsys_terminal_poll_key();
        if (key == 'q' || key == 'Q' || key == 27) {
            break;
        }
        if (key != 0) {
            d_tui_handle_key(tui, key);
        }
    }

    d_tui_destroy(tui);
    dsys_terminal_shutdown();
    return 0;
}

int LauncherApp::run_gui() {
    dgui_context* gui;
    dgui_widget* root;
    dgui_widget* header;
    dgui_widget* actions;
    dgui_widget* status;
    struct dcvs_t* canvas;
    dgfx_desc gdesc;

    if (dsys_init() != DSYS_OK) {
        std::printf("Launcher: dsys_init failed.\n");
        return 1;
    }

    gdesc.backend = DGFX_BACKEND_SOFT;
    gdesc.width = 640;
    gdesc.height = 360;
    gdesc.fullscreen = 0;
    gdesc.vsync = 0;
    gdesc.native_window = NULL;
    gdesc.window = NULL;
    if (!dgfx_init(&gdesc)) {
        std::printf("Launcher: dgfx_init failed.\n");
        dsys_shutdown();
        return 1;
    }

    gui = dgui_create();
    if (!gui) {
        dgfx_shutdown();
        dsys_shutdown();
        return 1;
    }

    root = dgui_panel(gui, DGUI_LAYOUT_VERTICAL);
    header = dgui_label(gui, "Dominium Launcher GUI");
    actions = dgui_panel(gui, DGUI_LAYOUT_VERTICAL);
    status = dgui_label(gui, "Ready");
    dgui_widget_add(root, header);
    dgui_widget_add(root, actions);
    dgui_widget_add(root, status);
    dgui_widget_add(actions, dgui_button(gui, "Run Game (GUI)", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "Run Game (TUI)", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "Run Game (Headless)", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "Exit", NULL, NULL));
    dgui_set_root(gui, root);

    canvas = dgfx_get_frame_canvas();
    dgfx_begin_frame();
    dgui_render(gui, canvas);
    dgfx_execute(dcvs_get_cmd_buffer(canvas));
    dgfx_end_frame();

    dgui_destroy(gui);
    dgfx_shutdown();
    dsys_shutdown();
    return 0;
}

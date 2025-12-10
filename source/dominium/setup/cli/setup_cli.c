#include <stdio.h>
#include <string.h>

#include "domino/cli/cli.h"
#include "domino/sys.h"
#include "domino/core.h"
#include "domino/gfx.h"
#include "domino/canvas.h"
#include "domino/gui/gui.h"
#include "domino/tui/tui.h"
#include "dominium/version.h"
#include "dominium/setup_api.h"
#include "dominium/product_info.h"

static int dom_setup_cli_parse_scope(const char* value, dom_setup_scope* out) {
    if (!value || !out) {
        return 0;
    }
    if (strcmp(value, "portable") == 0) {
        *out = DOM_SETUP_SCOPE_PORTABLE;
        return 1;
    }
    if (strcmp(value, "user") == 0 || strcmp(value, "per-user") == 0) {
        *out = DOM_SETUP_SCOPE_PER_USER;
        return 1;
    }
    if (strcmp(value, "system") == 0 || strcmp(value, "all-users") == 0) {
        *out = DOM_SETUP_SCOPE_ALL_USERS;
        return 1;
    }
    return 0;
}

static const char* dom_setup_cli_status_str(dom_setup_status st) {
    switch (st) {
    case DOM_SETUP_STATUS_OK: return "ok";
    case DOM_SETUP_STATUS_ERROR: return "error";
    case DOM_SETUP_STATUS_INVALID_ARGUMENT: return "invalid_argument";
    case DOM_SETUP_STATUS_IO_ERROR: return "io_error";
    case DOM_SETUP_STATUS_PERMISSION_DENIED: return "permission_denied";
    default: break;
    }
    return "unknown";
}

static void dom_setup_cli_progress(const dom_setup_progress* prog, void* user) {
    int quiet;
    const char* step;

    quiet = user ? *((int*)user) : 0;
    if (quiet || !prog) {
        return;
    }

    step = prog->current_step ? prog->current_step : "progress";
    printf("%s: %u/%u files, %lu/%lu bytes\n",
           step,
           (unsigned int)prog->files_done,
           (unsigned int)prog->files_total,
           (unsigned long)prog->bytes_done,
           (unsigned long)prog->bytes_total);
    fflush(stdout);
}

static void dom_setup_defaults(dom_setup_desc* desc,
                               dom_setup_command* cmd,
                               dom_setup_action action) {
    memset(desc, 0, sizeof(*desc));
    desc->struct_size = sizeof(*desc);
    desc->struct_version = 1u;
    desc->product_id = "dominium";
    desc->product_version = DOMINIUM_VERSION_SEMVER;
    desc->build_id = NULL;
    desc->scope = DOM_SETUP_SCOPE_PER_USER;
    desc->target_dir = NULL;
    desc->quiet = 0;
    desc->no_launcher = 0;
    desc->no_desktop_shortcuts = 0;

    memset(cmd, 0, sizeof(*cmd));
    cmd->struct_size = sizeof(*cmd);
    cmd->struct_version = 1u;
    cmd->action = action;
    cmd->existing_install_dir = NULL;
}

static int dom_setup_parse_options(const d_cli_args* args,
                                   dom_setup_desc* desc,
                                   dom_setup_command* cmd,
                                   char* platform_value,
                                   size_t platform_cap,
                                   char* renderer_value,
                                   size_t renderer_cap,
                                   int* introspect_json) {
    int i;
    if (!args || !desc || !cmd || !platform_value || !renderer_value || !introspect_json) {
        return D_CLI_ERR_STATE;
    }
    *introspect_json = 0;
    for (i = 0; i < args->token_count; ++i) {
        const d_cli_token* t = &args->tokens[i];
        if (t->is_positional) {
            printf("Unexpected positional argument '%s'\n", t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "scope")) {
            if (!t->has_value || !t->value || !dom_setup_cli_parse_scope(t->value, &desc->scope)) {
                printf("Invalid scope value\n");
                return D_CLI_BAD_USAGE;
            }
            continue;
        }
        if (d_cli_match_key(t, "dir")) {
            if (!t->has_value || !t->value) {
                printf("Missing value for --dir\n");
                return D_CLI_BAD_USAGE;
            }
            desc->target_dir = t->value;
            cmd->existing_install_dir = t->value;
            continue;
        }
        if (d_cli_match_key(t, "quiet")) {
            desc->quiet = 1;
            continue;
        }
        if (d_cli_match_key(t, "platform")) {
            if (!t->has_value || !t->value) {
                printf("Missing value for --platform\n");
                return D_CLI_BAD_USAGE;
            }
            strncpy(platform_value, t->value, platform_cap - 1u);
            platform_value[platform_cap - 1u] = '\0';
            continue;
        }
        if (d_cli_match_key(t, "renderer")) {
            if (!t->has_value || !t->value) {
                printf("Missing value for --renderer\n");
                return D_CLI_BAD_USAGE;
            }
            strncpy(renderer_value, t->value, renderer_cap - 1u);
            renderer_value[renderer_cap - 1u] = '\0';
            continue;
        }
        if (d_cli_match_key(t, "introspect-json")) {
            *introspect_json = 1;
            continue;
        }
        if (d_cli_match_key(t, "instance")) {
            continue; /* ignore global instance flag */
        }
        printf("Unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    return D_CLI_OK;
}

static int dom_setup_apply_backends(const char* platform_value,
                                    const char* renderer_value) {
    if (platform_value && platform_value[0]) {
        if (dom_sys_select_backend(platform_value) != 0) {
            fprintf(stderr, "Unsupported platform backend '%s'\n", platform_value);
            return 1;
        }
    }
    if (renderer_value && renderer_value[0]) {
        if (dom_gfx_select_backend(renderer_value) != 0) {
            fprintf(stderr, "Unsupported renderer backend '%s'\n", renderer_value);
            return 1;
        }
    }
    return 0;
}

static int dom_setup_run(dom_setup_action action, int argc, const char** argv) {
    dom_setup_desc desc;
    dom_setup_command cmd;
    dom_core_desc core_desc;
    dom_core* core;
    void* setup_ctx;
    dom_setup_status status;
    d_cli_args args;
    char platform_value[32];
    char renderer_value[32];
    int introspect;
    int rc;

    dom_setup_defaults(&desc, &cmd, action);
    platform_value[0] = '\0';
    renderer_value[0] = '\0';

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    rc = dom_setup_parse_options(&args, &desc, &cmd,
                                 platform_value, sizeof(platform_value),
                                 renderer_value, sizeof(renderer_value),
                                 &introspect);
    if (rc != D_CLI_OK) {
        d_cli_args_dispose(&args);
        return rc;
    }

    if (introspect) {
        dominium_print_product_info_json(dom_get_product_info_setup(), stdout);
        d_cli_args_dispose(&args);
        return 0;
    }

    if (dom_setup_apply_backends(platform_value, renderer_value) != 0) {
        d_cli_args_dispose(&args);
        return 1;
    }

    core_desc.api_version = 1u;
    if (dsys_init() != DSYS_OK) {
        printf("Failed to initialize dsys\n");
        d_cli_args_dispose(&args);
        return 1;
    }

    core = dom_core_create(&core_desc);
    if (!core) {
        printf("Failed to create core\n");
        dsys_shutdown();
        d_cli_args_dispose(&args);
        return 1;
    }

    status = dom_setup_create(core, &desc, &setup_ctx);
    if (status != DOM_SETUP_STATUS_OK) {
        printf("dom_setup_create failed: %s\n", dom_setup_cli_status_str(status));
        dom_core_destroy(core);
        dsys_shutdown();
        d_cli_args_dispose(&args);
        return 1;
    }

    if (!cmd.existing_install_dir && desc.target_dir) {
        cmd.existing_install_dir = desc.target_dir;
    }

    status = dom_setup_execute(setup_ctx, &cmd,
                               desc.quiet ? NULL : dom_setup_cli_progress,
                               &desc.quiet);

    dom_setup_destroy(setup_ctx);
    dom_core_destroy(core);
    dsys_shutdown();
    d_cli_args_dispose(&args);

    if (status != DOM_SETUP_STATUS_OK) {
        printf("dom_setup_execute failed: %s\n", dom_setup_cli_status_str(status));
        return 1;
    }

    if (!desc.quiet) {
        printf("Action '%d' completed successfully.\n", (int)cmd.action);
    }
    return 0;
}

static int dom_setup_stub(int argc, const char** argv, const char* name) {
    dom_setup_desc desc;
    dom_setup_command cmd;
    d_cli_args args;
    char platform_value[32];
    char renderer_value[32];
    int introspect;
    int rc;

    dom_setup_defaults(&desc, &cmd, DOM_SETUP_ACTION_VERIFY);
    platform_value[0] = '\0';
    renderer_value[0] = '\0';

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    rc = dom_setup_parse_options(&args, &desc, &cmd,
                                 platform_value, sizeof(platform_value),
                                 renderer_value, sizeof(renderer_value),
                                 &introspect);
    if (rc != D_CLI_OK) {
        d_cli_args_dispose(&args);
        return rc;
    }
    d_cli_args_dispose(&args);

    if (introspect) {
        dominium_print_product_info_json(dom_get_product_info_setup(), stdout);
        return 0;
    }

    printf("Setup: command '%s' is not implemented.\n", name ? name : "(unknown)");
    return D_CLI_BAD_USAGE;
}

static int dom_setup_cmd_install(int argc, const char** argv, void* user) {
    (void)user;
    return dom_setup_run(DOM_SETUP_ACTION_INSTALL, argc, argv);
}

static int dom_setup_cmd_repair(int argc, const char** argv, void* user) {
    (void)user;
    return dom_setup_run(DOM_SETUP_ACTION_REPAIR, argc, argv);
}

static int dom_setup_cmd_uninstall(int argc, const char** argv, void* user) {
    (void)user;
    return dom_setup_run(DOM_SETUP_ACTION_UNINSTALL, argc, argv);
}

static int dom_setup_cmd_import(int argc, const char** argv, void* user) {
    (void)user;
    return dom_setup_stub(argc, argv, "import");
}

static int dom_setup_cmd_gc(int argc, const char** argv, void* user) {
    (void)user;
    return dom_setup_stub(argc, argv, "gc");
}

typedef struct dom_setup_tui_state {
    d_tui_widget* status;
    int*          running;
} dom_setup_tui_state;

static void dom_setup_tui_set(dom_setup_tui_state* st, const char* text) {
    if (!st || !st->status) return;
    d_tui_widget_set_text(st->status, text);
}

static void dom_setup_tui_install(d_tui_widget* self, void* user) {
    (void)self;
    dom_setup_tui_set((dom_setup_tui_state*)user, "Install (stub)");
}

static void dom_setup_tui_repair(d_tui_widget* self, void* user) {
    (void)self;
    dom_setup_tui_set((dom_setup_tui_state*)user, "Repair (stub)");
}

static void dom_setup_tui_uninstall(d_tui_widget* self, void* user) {
    (void)self;
    dom_setup_tui_set((dom_setup_tui_state*)user, "Uninstall (stub)");
}

static void dom_setup_tui_import(d_tui_widget* self, void* user) {
    (void)self;
    dom_setup_tui_set((dom_setup_tui_state*)user, "Import (stub)");
}

static void dom_setup_tui_gc(d_tui_widget* self, void* user) {
    (void)self;
    dom_setup_tui_set((dom_setup_tui_state*)user, "GC (stub)");
}

static void dom_setup_tui_exit(d_tui_widget* self, void* user) {
    dom_setup_tui_state* st = (dom_setup_tui_state*)user;
    (void)self;
    if (st && st->running) {
        *(st->running) = 0;
    }
}

static int dom_setup_run_tui(void) {
    d_tui_context* tui;
    d_tui_widget* root;
    d_tui_widget* header;
    d_tui_widget* actions;
    d_tui_widget* status;
    dom_setup_tui_state st;
    int running = 1;

    if (!dsys_terminal_init()) {
        printf("Setup: terminal init failed.\n");
        return 1;
    }

    tui = d_tui_create();
    if (!tui) {
        dsys_terminal_shutdown();
        return 1;
    }

    root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    header = d_tui_label(tui, "Dominium Setup TUI");
    actions = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    status = d_tui_label(tui, "Ready");

    d_tui_widget_add(root, header);
    d_tui_widget_add(root, actions);
    d_tui_widget_add(root, status);

    st.status = status;
    st.running = &running;

    d_tui_widget_add(actions, d_tui_button(tui, "Install", dom_setup_tui_install, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Repair", dom_setup_tui_repair, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Uninstall", dom_setup_tui_uninstall, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Import", dom_setup_tui_import, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "GC", dom_setup_tui_gc, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Exit", dom_setup_tui_exit, &st));

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

static int dom_setup_cmd_tui(int argc, const char** argv, void* user) {
    d_cli_args args;
    int rc;
    int i;
    (void)user;

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) return rc;
    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            d_cli_args_dispose(&args);
            printf("Setup: unexpected positional argument '%s'\n", t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) continue;
        d_cli_args_dispose(&args);
        printf("Setup: unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    d_cli_args_dispose(&args);
    return dom_setup_run_tui();
}

static int dom_setup_run_gui(void) {
    dgui_context* gui;
    dgui_widget* root;
    dgui_widget* header;
    dgui_widget* actions;
    dgui_widget* status;
    struct dcvs_t* canvas;
    dgfx_desc gdesc;

    if (dsys_init() != DSYS_OK) {
        printf("Setup: dsys_init failed.\n");
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
        printf("Setup: dgfx_init failed.\n");
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
    header = dgui_label(gui, "Dominium Setup GUI");
    actions = dgui_panel(gui, DGUI_LAYOUT_VERTICAL);
    status = dgui_label(gui, "Ready");
    dgui_widget_add(root, header);
    dgui_widget_add(root, actions);
    dgui_widget_add(root, status);
    dgui_widget_add(actions, dgui_button(gui, "Install", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "Repair", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "Uninstall", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "Import", NULL, NULL));
    dgui_widget_add(actions, dgui_button(gui, "GC", NULL, NULL));
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

static int dom_setup_cmd_gui(int argc, const char** argv, void* user) {
    d_cli_args args;
    int rc;
    int i;
    (void)user;
    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) return rc;
    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            d_cli_args_dispose(&args);
            printf("Setup: unexpected positional '%s'\n", t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) continue;
        d_cli_args_dispose(&args);
        printf("Setup: unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    d_cli_args_dispose(&args);
    return dom_setup_run_gui();
}

int main(int argc, char** argv) {
    d_cli cli;
    int rc;

    d_cli_init(&cli, (argc > 0) ? argv[0] : "dominium-setup-cli",
               DOMINIUM_SETUP_VERSION);

    rc = d_cli_register(&cli, "install", "Install Dominium", dom_setup_cmd_install, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "repair", "Repair an existing installation", dom_setup_cmd_repair, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "uninstall", "Uninstall Dominium", dom_setup_cmd_uninstall, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "import", "Import an existing installation (stub)", dom_setup_cmd_import, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "gc", "Garbage-collect installer caches (stub)", dom_setup_cmd_gc, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "tui", "Launch setup text UI", dom_setup_cmd_tui, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "gui", "Launch setup GUI", dom_setup_cmd_gui, NULL);
    if (rc != D_CLI_OK) return rc;

    rc = d_cli_dispatch(&cli, argc, (const char**)argv);
    d_cli_shutdown(&cli);
    return rc;
}

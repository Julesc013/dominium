#include <stdio.h>
#include <string.h>

#include "domino/cli/cli.h"
#include "domino/sys.h"
#include "domino/mod.h"
#include "domino/gfx.h"
#include "domino/pkg/repo.h"
#include "domino/tui/tui.h"
#include "dominium/product_info.h"
#include "dominium/version.h"

typedef struct modcheck_options {
    char        root_override[260];
    char        platform_value[32];
    char        renderer_value[32];
    const char* filter_id;
    int         introspect;
} modcheck_options;

static void modcheck_copy_string(const char* src, char* dst, size_t cap) {
    size_t len;
    if (!dst || cap == 0) return;
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static int modcheck_apply_backends(const modcheck_options* opts) {
    if (opts->platform_value[0]) {
        if (dom_sys_select_backend(opts->platform_value) != 0) {
            fprintf(stderr, "Unsupported platform backend '%s'\n", opts->platform_value);
            return 1;
        }
    }
    if (opts->renderer_value[0]) {
        if (dom_gfx_select_backend(opts->renderer_value) != 0) {
            fprintf(stderr, "Unsupported renderer backend '%s'\n", opts->renderer_value);
            return 1;
        }
    }
    return 0;
}

static int modcheck_parse_options(int argc, const char** argv, modcheck_options* opts) {
    d_cli_args args;
    int rc;
    int i;

    if (!opts) return D_CLI_ERR_STATE;

    opts->root_override[0] = '\0';
    opts->platform_value[0] = '\0';
    opts->renderer_value[0] = '\0';
    opts->filter_id = NULL;
    opts->introspect = 0;

    rc = d_cli_tokenize(argc, argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    for (i = 0; i < args.token_count; ++i) {
        const d_cli_token* t = &args.tokens[i];
        if (t->is_positional) {
            if (opts->filter_id == NULL) {
                opts->filter_id = t->value;
            } else {
                printf("Too many positional arguments\n");
                d_cli_args_dispose(&args);
                return D_CLI_BAD_USAGE;
            }
            continue;
        }
        if (d_cli_match_key(t, "root")) {
            if (!t->has_value || !t->value) {
                printf("Missing value for --root\n");
                d_cli_args_dispose(&args);
                return D_CLI_BAD_USAGE;
            }
            modcheck_copy_string(t->value, opts->root_override, sizeof(opts->root_override));
        } else if (d_cli_match_key(t, "platform")) {
            if (!t->has_value || !t->value) {
                printf("Missing value for --platform\n");
                d_cli_args_dispose(&args);
                return D_CLI_BAD_USAGE;
            }
            modcheck_copy_string(t->value, opts->platform_value, sizeof(opts->platform_value));
        } else if (d_cli_match_key(t, "renderer")) {
            if (!t->has_value || !t->value) {
                printf("Missing value for --renderer\n");
                d_cli_args_dispose(&args);
                return D_CLI_BAD_USAGE;
            }
            modcheck_copy_string(t->value, opts->renderer_value, sizeof(opts->renderer_value));
        } else if (d_cli_match_key(t, "introspect-json")) {
            opts->introspect = 1;
        } else if (d_cli_match_key(t, "instance")) {
            /* ignored */
        } else {
            printf("Unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
            d_cli_args_dispose(&args);
            return D_CLI_BAD_USAGE;
        }
    }

    d_cli_args_dispose(&args);
    return D_CLI_OK;
}

static int modcheck_build_registry(const modcheck_options* opts,
                                   domino_sys_context** out_sys,
                                   domino_package_registry** out_reg) {
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    domino_sys_paths paths;
    const char* roots[2];
    unsigned int root_count = 0;
    domino_package_registry* reg;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
    if (domino_sys_init(&sdesc, &sys) != 0) {
        return 1;
    }
    domino_sys_get_paths(sys, &paths);

    if (opts->root_override[0]) {
        roots[0] = opts->root_override;
        root_count = 1;
    } else {
        roots[0] = paths.data_root;
        roots[1] = paths.user_root;
        root_count = 2;
    }

    reg = domino_package_registry_create();
    if (!reg) {
        domino_sys_shutdown(sys);
        return 1;
    }
    domino_package_registry_set_sys(reg, sys);
    domino_package_registry_scan_roots(reg, roots, root_count);

    *out_sys = sys;
    *out_reg = reg;
    return 0;
}

static int modcheck_verify_desc(domino_package_registry* reg,
                                const domino_package_desc* desc,
                                domino_package_kind expected_kind) {
    domino_instance_desc inst;
    domino_resolve_error err;

    if (!desc || !reg) return 1;
    if (desc->kind != expected_kind) {
        return 0;
    }

    memset(&inst, 0, sizeof(inst));
    strncpy(inst.id, desc->id, sizeof(inst.id) - 1);
    strncpy(inst.product_id, DOMINIUM_GAME_ID, sizeof(inst.product_id) - 1);
    dominium_game_get_version(&inst.product_version);

    if (expected_kind == DOMINO_PACKAGE_KIND_MOD) {
        inst.mod_count = 1;
        strncpy(inst.mods_enabled[0], desc->id, sizeof(inst.mods_enabled[0]) - 1);
    } else if (expected_kind == DOMINO_PACKAGE_KIND_PACK) {
        inst.pack_count = 1;
        strncpy(inst.packs_enabled[0], desc->id, sizeof(inst.packs_enabled[0]) - 1);
    } else {
        return 0;
    }

    err.message[0] = '\0';
    if (domino_instance_resolve(reg, &inst, &err) != 0) {
        printf("%s %s: incompatible (%s)\n",
               (expected_kind == DOMINO_PACKAGE_KIND_MOD) ? "Mod" : "Pack",
               desc->id,
               err.message[0] ? err.message : "unknown reason");
        return 1;
    }

    printf("%s %s: ok\n",
           (expected_kind == DOMINO_PACKAGE_KIND_MOD) ? "Mod" : "Pack",
           desc->id);
    return 0;
}

typedef struct modcheck_visit_ctx {
    domino_package_registry* reg;
    domino_package_kind      kind;
    int                      failure_count;
} modcheck_visit_ctx;

static int modcheck_visit(const domino_package_desc* desc, void* user) {
    modcheck_visit_ctx* ctx = (modcheck_visit_ctx*)user;
    if (!ctx || !desc) return 0;
    if (desc->kind != ctx->kind) return 0;
    if (modcheck_verify_desc(ctx->reg, desc, ctx->kind) != 0) {
        ctx->failure_count += 1;
    }
    return 0;
}

static int modcheck_verify_packages(domino_package_kind kind,
                                    const modcheck_options* opts) {
    domino_sys_context* sys = NULL;
    domino_package_registry* reg = NULL;
    int rc;

    rc = modcheck_build_registry(opts, &sys, &reg);
    if (rc != 0) {
        return rc;
    }

    if (opts->filter_id) {
        const domino_package_desc* desc = domino_package_registry_find(reg, opts->filter_id);
        if (!desc) {
            printf("Package '%s' not found\n", opts->filter_id);
            rc = 1;
        } else if (desc->kind != kind) {
            printf("Package '%s' is not of the requested type\n", opts->filter_id);
            rc = 1;
        } else {
            rc = modcheck_verify_desc(reg, desc, kind);
        }
    } else {
        modcheck_visit_ctx ctx;
        ctx.reg = reg;
        ctx.kind = kind;
        ctx.failure_count = 0;
        domino_package_registry_visit(reg, modcheck_visit, &ctx);
        rc = (ctx.failure_count > 0) ? 1 : 0;
    }

    domino_package_registry_destroy(reg);
    domino_sys_shutdown(sys);
    return rc;
}

static int modcheck_verify_product(const modcheck_options* opts) {
    dom_product_info info;
    (void)opts;

    memset(&info, 0, sizeof(info));
    if (!dom_repo_load_primary_game(&info)) {
        printf("Product manifest: failed to load primary game product.\n");
        return 1;
    }

    printf("Product manifest OK:\n");
    printf("  product_id    = %s\n", info.product_id);
    printf("  product_ver   = %s\n", info.product_version);
    printf("  core_version  = %s\n", info.core_version);
    return 0;
}

static int modcheck_cmd_verify_mod(int argc, const char** argv, void* user) {
    modcheck_options opts;
    int rc;
    (void)user;

    rc = modcheck_parse_options(argc, argv, &opts);
    if (rc != D_CLI_OK) return rc;
    if (opts.introspect) {
        dominium_print_product_info_json(dom_get_product_info_tools(), stdout);
        return 0;
    }
    if (modcheck_apply_backends(&opts) != 0) return 1;
    return modcheck_verify_packages(DOMINO_PACKAGE_KIND_MOD, &opts);
}

static int modcheck_cmd_verify_pack(int argc, const char** argv, void* user) {
    modcheck_options opts;
    int rc;
    (void)user;

    rc = modcheck_parse_options(argc, argv, &opts);
    if (rc != D_CLI_OK) return rc;
    if (opts.introspect) {
        dominium_print_product_info_json(dom_get_product_info_tools(), stdout);
        return 0;
    }
    if (modcheck_apply_backends(&opts) != 0) return 1;
    return modcheck_verify_packages(DOMINO_PACKAGE_KIND_PACK, &opts);
}

static int modcheck_cmd_verify_product(int argc, const char** argv, void* user) {
    modcheck_options opts;
    int rc;
    (void)user;

    rc = modcheck_parse_options(argc, argv, &opts);
    if (rc != D_CLI_OK) return rc;
    if (opts.introspect) {
        dominium_print_product_info_json(dom_get_product_info_tools(), stdout);
        return 0;
    }
    if (modcheck_apply_backends(&opts) != 0) return 1;

    if (opts.filter_id) {
        /* simple check: ensure loaded manifest id matches filter */
        dom_product_info info;
        memset(&info, 0, sizeof(info));
        if (!dom_repo_load_primary_game(&info)) {
            printf("Product manifest: failed to load primary game product.\n");
            return 1;
        }
        if (strcmp(info.product_id, opts.filter_id) != 0) {
            printf("Product id mismatch (wanted %s, found %s)\n",
                   opts.filter_id, info.product_id);
            return 1;
        }
        printf("Product manifest OK for %s\n", opts.filter_id);
        return 0;
    }

    return modcheck_verify_product(&opts);
}

typedef struct modcheck_tui_state {
    d_tui_widget* status;
    int*          running;
} modcheck_tui_state;

static void modcheck_tui_set(modcheck_tui_state* st, const char* text) {
    if (!st || !st->status) return;
    d_tui_widget_set_text(st->status, text);
}

static void modcheck_tui_verify_mod(d_tui_widget* self, void* user) {
    (void)self;
    modcheck_tui_set((modcheck_tui_state*)user, "verify-mod (stub)");
}

static void modcheck_tui_verify_pack(d_tui_widget* self, void* user) {
    (void)self;
    modcheck_tui_set((modcheck_tui_state*)user, "verify-pack (stub)");
}

static void modcheck_tui_verify_product_action(d_tui_widget* self, void* user) {
    (void)self;
    modcheck_tui_set((modcheck_tui_state*)user, "verify-product (stub)");
}

static void modcheck_tui_exit(d_tui_widget* self, void* user) {
    modcheck_tui_state* st = (modcheck_tui_state*)user;
    (void)self;
    if (st && st->running) {
        *(st->running) = 0;
    }
}

static int modcheck_run_tui(void) {
    d_tui_context* tui;
    d_tui_widget* root;
    d_tui_widget* header;
    d_tui_widget* actions;
    d_tui_widget* status;
    modcheck_tui_state st;
    int running = 1;

    if (!dsys_terminal_init()) {
        printf("Modcheck: terminal init failed.\n");
        return 1;
    }

    tui = d_tui_create();
    if (!tui) {
        dsys_terminal_shutdown();
        return 1;
    }

    root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    header = d_tui_label(tui, "Dominium Tools (modcheck) TUI");
    actions = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    status = d_tui_label(tui, "Ready");

    d_tui_widget_add(root, header);
    d_tui_widget_add(root, actions);
    d_tui_widget_add(root, status);

    st.status = status;
    st.running = &running;

    d_tui_widget_add(actions, d_tui_button(tui, "verify-mod", modcheck_tui_verify_mod, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "verify-pack", modcheck_tui_verify_pack, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "verify-product", modcheck_tui_verify_product_action, &st));
    d_tui_widget_add(actions, d_tui_button(tui, "Exit", modcheck_tui_exit, &st));

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

static int modcheck_cmd_tui(int argc, const char** argv, void* user) {
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
            printf("Modcheck: unexpected positional '%s'\n", t->value ? t->value : "(null)");
            return D_CLI_BAD_USAGE;
        }
        if (d_cli_match_key(t, "instance")) continue;
        d_cli_args_dispose(&args);
        printf("Modcheck: unknown option '%.*s'\n", t->key_len, t->key ? t->key : "");
        return D_CLI_BAD_USAGE;
    }
    d_cli_args_dispose(&args);
    return modcheck_run_tui();
}

int main(int argc, char** argv) {
    d_cli cli;
    int rc;

    d_cli_init(&cli, (argc > 0) ? argv[0] : "dominium_modcheck",
               DOMINIUM_TOOLS_VERSION);

    rc = d_cli_register(&cli, "verify-mod", "Verify compatibility of mods", modcheck_cmd_verify_mod, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "verify-pack", "Verify compatibility of packs", modcheck_cmd_verify_pack, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "verify-product", "Verify product manifests", modcheck_cmd_verify_product, NULL);
    if (rc != D_CLI_OK) return rc;
    rc = d_cli_register(&cli, "tui", "Launch modcheck text UI", modcheck_cmd_tui, NULL);
    if (rc != D_CLI_OK) return rc;

    rc = d_cli_dispatch(&cli, argc, (const char**)argv);
    d_cli_shutdown(&cli);
    return rc;
}

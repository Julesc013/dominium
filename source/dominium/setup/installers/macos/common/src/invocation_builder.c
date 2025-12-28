/*
FILE: source/dominium/setup/installers/macos/common/src/invocation_builder.c
MODULE: Dominium Setup macOS
PURPOSE: Build invocation payloads from CLI/UI selections.
*/
#include "dsu_macos_invocation.h"

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

static char *dsu_macos_strdup(const char *s) {
    size_t n;
    char *p;
    if (!s) return NULL;
    n = strlen(s);
    p = (char *)malloc(n + 1u);
    if (!p) return NULL;
    memcpy(p, s, n);
    p[n] = '\0';
    return p;
}

static int streq_nocase(const char *a, const char *b) {
    unsigned char ca;
    unsigned char cb;
    if (a == b) return 1;
    if (!a || !b) return 0;
    for (;;) {
        ca = (unsigned char)*a++;
        cb = (unsigned char)*b++;
        ca = (unsigned char)tolower(ca);
        cb = (unsigned char)tolower(cb);
        if (ca != cb) return 0;
        if (ca == 0) return 1;
    }
}

void dsu_macos_csv_list_free(dsu_macos_csv_list_t *list) {
    unsigned long i;
    if (!list || !list->items) {
        return;
    }
    for (i = 0; i < list->count; ++i) {
        free(list->items[i]);
    }
    free(list->items);
    list->items = NULL;
    list->count = 0;
}

int dsu_macos_csv_list_parse(const char *csv, dsu_macos_csv_list_t *out_list) {
    char *tmp;
    char *p;
    unsigned long cap = 0;
    unsigned long count = 0;
    char **items = NULL;

    if (!out_list) {
        return 0;
    }
    out_list->items = NULL;
    out_list->count = 0;
    if (!csv || !csv[0]) {
        return 1;
    }
    if (streq_nocase(csv, "ALL")) {
        return 1;
    }

    tmp = dsu_macos_strdup(csv);
    if (!tmp) {
        return 0;
    }
    p = tmp;
    while (*p) {
        char *token = p;
        char *end;
        while (*token == ' ' || *token == '\t') ++token;
        end = token;
        while (*end && *end != ',') ++end;
        if (*end == ',') {
            *end = '\0';
            p = end + 1;
        } else {
            p = end;
        }
        while (end > token && (end[-1] == ' ' || end[-1] == '\t')) {
            end[-1] = '\0';
            --end;
        }
        if (*token) {
            char *dup = dsu_macos_strdup(token);
            char **next;
            if (!dup) {
                free(tmp);
                dsu_macos_csv_list_free(out_list);
                return 0;
            }
            if (count == cap) {
                unsigned long new_cap = (cap == 0) ? 8u : (cap * 2u);
                next = (char **)realloc(items, new_cap * sizeof(*items));
                if (!next) {
                    free(dup);
                    free(tmp);
                    dsu_macos_csv_list_free(out_list);
                    return 0;
                }
                items = next;
                cap = new_cap;
            }
            items[count++] = dup;
        }
    }
    free(tmp);
    out_list->items = items;
    out_list->count = count;
    return 1;
}

static int parse_operation(const char *s, dsu_invocation_operation_t *out_op) {
    if (!s || !out_op) return 0;
    if (streq_nocase(s, "install")) {
        *out_op = DSU_INVOCATION_OPERATION_INSTALL;
        return 1;
    }
    if (streq_nocase(s, "upgrade")) {
        *out_op = DSU_INVOCATION_OPERATION_UPGRADE;
        return 1;
    }
    if (streq_nocase(s, "repair")) {
        *out_op = DSU_INVOCATION_OPERATION_REPAIR;
        return 1;
    }
    if (streq_nocase(s, "uninstall")) {
        *out_op = DSU_INVOCATION_OPERATION_UNINSTALL;
        return 1;
    }
    return 0;
}

static int parse_scope(const char *s, dsu_invocation_scope_t *out_scope) {
    if (!s || !out_scope) return 0;
    if (streq_nocase(s, "portable")) {
        *out_scope = DSU_INVOCATION_SCOPE_PORTABLE;
        return 1;
    }
    if (streq_nocase(s, "user")) {
        *out_scope = DSU_INVOCATION_SCOPE_USER;
        return 1;
    }
    if (streq_nocase(s, "system")) {
        *out_scope = DSU_INVOCATION_SCOPE_SYSTEM;
        return 1;
    }
    return 0;
}

static int set_single_list(char ***out_items, dsu_u32 *out_count, const char *value) {
    char **items;
    if (!out_items || !out_count || !value) return 0;
    items = (char **)malloc(sizeof(*items));
    if (!items) return 0;
    items[0] = dsu_macos_strdup(value);
    if (!items[0]) {
        free(items);
        return 0;
    }
    *out_items = items;
    *out_count = 1u;
    return 1;
}

int dsu_macos_build_invocation(const dsu_macos_cli_args_t *args,
                               const char *platform_default,
                               const char *ui_mode_default,
                               const char *frontend_default,
                               dsu_invocation_t *out_invocation) {
    dsu_macos_csv_list_t components;
    dsu_macos_csv_list_t exclude;
    dsu_invocation_operation_t op = DSU_INVOCATION_OPERATION_INSTALL;
    dsu_invocation_scope_t scope = DSU_INVOCATION_SCOPE_USER;
    dsu_u32 policy = 0u;
    const char *platform;
    const char *ui_mode;
    const char *frontend_id;

    if (!args || !out_invocation) {
        return 0;
    }
    memset(&components, 0, sizeof(components));
    memset(&exclude, 0, sizeof(exclude));

    dsu_invocation_init(out_invocation);

    if (args->operation && !parse_operation(args->operation, &op)) {
        return 0;
    }
    if (args->scope && !parse_scope(args->scope, &scope)) {
        return 0;
    }

    out_invocation->operation = (dsu_u8)op;
    out_invocation->scope = (dsu_u8)scope;

    platform = args->platform ? args->platform : platform_default;
    ui_mode = args->ui_mode ? args->ui_mode : ui_mode_default;
    frontend_id = args->frontend_id ? args->frontend_id : frontend_default;

    out_invocation->platform_triple = dsu_macos_strdup(platform ? platform : "macos-x64");
    out_invocation->ui_mode = dsu_macos_strdup(ui_mode ? ui_mode : "cli");
    out_invocation->frontend_id = dsu_macos_strdup(frontend_id ? frontend_id : "tui-macos");

    if (!out_invocation->platform_triple || !out_invocation->ui_mode || !out_invocation->frontend_id) {
        dsu_invocation_destroy(NULL, out_invocation);
        return 0;
    }

    if (args->install_root && args->install_root[0]) {
        if (!set_single_list(&out_invocation->install_roots, &out_invocation->install_root_count, args->install_root)) {
            dsu_invocation_destroy(NULL, out_invocation);
            return 0;
        }
    }

    if (args->components_csv && !dsu_macos_csv_list_parse(args->components_csv, &components)) {
        dsu_invocation_destroy(NULL, out_invocation);
        return 0;
    }
    if (args->exclude_csv && !dsu_macos_csv_list_parse(args->exclude_csv, &exclude)) {
        dsu_macos_csv_list_free(&components);
        dsu_invocation_destroy(NULL, out_invocation);
        return 0;
    }

    if (components.count != 0u) {
        out_invocation->selected_components = (char **)components.items;
        out_invocation->selected_component_count = (dsu_u32)components.count;
        components.items = NULL;
        components.count = 0u;
    }
    if (exclude.count != 0u) {
        out_invocation->excluded_components = (char **)exclude.items;
        out_invocation->excluded_component_count = (dsu_u32)exclude.count;
        exclude.items = NULL;
        exclude.count = 0u;
    }

    if (args->deterministic) policy |= DSU_INVOCATION_POLICY_DETERMINISTIC;
    if (args->policy_offline) policy |= DSU_INVOCATION_POLICY_OFFLINE;
    if (args->policy_allow_prerelease) policy |= DSU_INVOCATION_POLICY_ALLOW_PRERELEASE;
    if (args->policy_legacy) policy |= DSU_INVOCATION_POLICY_LEGACY_MODE;
    if (args->policy_shortcuts) policy |= DSU_INVOCATION_POLICY_ENABLE_SHORTCUTS;
    if (args->policy_file_assoc) policy |= DSU_INVOCATION_POLICY_ENABLE_FILE_ASSOC;
    if (args->policy_url_handlers) policy |= DSU_INVOCATION_POLICY_ENABLE_URL_HANDLERS;
    out_invocation->policy_flags = policy;

    dsu_macos_csv_list_free(&components);
    dsu_macos_csv_list_free(&exclude);
    return 1;
}

int dsu_macos_write_invocation(const dsu_invocation_t *inv, const char *path, dsu_u64 *out_digest) {
    dsu_ctx_t *ctx = NULL;
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_status_t st;
    dsu_u64 digest = 0u;

    if (!inv || !path) {
        return 0;
    }

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        return 0;
    }

    st = dsu_invocation_write_file(ctx, inv, path);
    if (st == DSU_STATUS_SUCCESS) {
        digest = dsu_invocation_digest(inv);
    }
    if (ctx) {
        dsu_ctx_destroy(ctx);
    }
    if (out_digest) {
        *out_digest = digest;
    }
    return (st == DSU_STATUS_SUCCESS);
}

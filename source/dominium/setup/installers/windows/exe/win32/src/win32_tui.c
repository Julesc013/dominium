/*
FILE: source/dominium/setup/installers/windows/exe/win32/src/win32_tui.c
MODULE: Dominium Setup EXE (Win32)
PURPOSE: Text UI installer flow (shared across Win32/Win64).
*/
#include "dsu_exe_win32.h"

#include "dsu_exe_log.h"

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

#if defined(_MSC_VER)
#define dsu_exe_snprintf _snprintf
#else
#define dsu_exe_snprintf snprintf
#endif

static int tui_read_line(char *out, size_t cap) {
    if (!out || cap == 0u) return 0;
    if (!fgets(out, (int)cap, stdin)) return 0;
    while (*out && (out[strlen(out) - 1u] == '\n' || out[strlen(out) - 1u] == '\r')) {
        out[strlen(out) - 1u] = '\0';
    }
    return 1;
}

static int tui_prompt_yesno(const char *question, int default_yes) {
    char buf[32];
    for (;;) {
        fprintf(stdout, "%s [%s]: ", question, default_yes ? "Y/n" : "y/N");
        if (!tui_read_line(buf, sizeof(buf))) return default_yes;
        if (buf[0] == '\0') return default_yes;
        if (buf[0] == 'y' || buf[0] == 'Y') return 1;
        if (buf[0] == 'n' || buf[0] == 'N') return 0;
    }
}

static int tui_prompt_choice(const char *question, const char **options, int count, int default_index) {
    char buf[32];
    int i;
    if (!options || count <= 0) return default_index;
    fprintf(stdout, "%s\n", question);
    for (i = 0; i < count; ++i) {
        fprintf(stdout, "  %d) %s%s\n", i + 1, options[i], (i == default_index) ? " (default)" : "");
    }
    for (;;) {
        fprintf(stdout, "Select [1-%d]: ", count);
        if (!tui_read_line(buf, sizeof(buf))) return default_index;
        if (buf[0] == '\0') return default_index;
        i = atoi(buf);
        if (i >= 1 && i <= count) return i - 1;
    }
}

static int tui_load_manifest(const char *path, dsu_ctx_t **out_ctx, dsu_manifest_t **out_manifest) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_status_t st;
    if (!path || !out_ctx || !out_manifest) return 0;
    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    if (st != DSU_STATUS_SUCCESS) return 0;
    st = dsu_manifest_load_file(ctx, path, &manifest);
    if (st != DSU_STATUS_SUCCESS || !manifest) {
        dsu_ctx_destroy(ctx);
        return 0;
    }
    *out_ctx = ctx;
    *out_manifest = manifest;
    return 1;
}

static int tui_select_install_root(const dsu_manifest_t *manifest,
                                   dsu_manifest_install_scope_t scope,
                                   const char *platform,
                                   char *out,
                                   size_t cap) {
    dsu_u32 i;
    dsu_u32 count;
    const char *fallback = NULL;
    if (!manifest || !out || cap == 0u) return 0;
    count = dsu_manifest_install_root_count(manifest);
    for (i = 0u; i < count; ++i) {
        if (dsu_manifest_install_root_scope(manifest, i) != scope) {
            continue;
        }
        if (!fallback) {
            fallback = dsu_manifest_install_root_path(manifest, i);
        }
        if (platform) {
            const char *p = dsu_manifest_install_root_platform(manifest, i);
            if (p && _stricmp(p, platform) == 0) {
                fallback = dsu_manifest_install_root_path(manifest, i);
                break;
            }
        }
    }
    if (!fallback || !fallback[0]) return 0;
    strncpy(out, fallback, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int tui_detect_installed(const dsu_manifest_t *manifest,
                                const char *platform,
                                dsu_ui_state_t *state) {
    dsu_u32 count;
    dsu_u32 i;
    if (!manifest || !state) return 0;
    count = dsu_manifest_install_root_count(manifest);
    for (i = 0u; i < count; ++i) {
        const char *root = dsu_manifest_install_root_path(manifest, i);
        const char *plat = dsu_manifest_install_root_platform(manifest, i);
        char state_path[1024];
        if (!root || !root[0]) continue;
        if (platform && plat && _stricmp(platform, plat) != 0) continue;
        if (dsu_exe_snprintf(state_path, sizeof(state_path), "%s\\.dsu\\installed_state.dsustate", root) <= 0) {
            continue;
        }
        if (GetFileAttributesA(state_path) != INVALID_FILE_ATTRIBUTES) {
            state->installed_detected = 1;
            state->scope = dsu_manifest_install_root_scope(manifest, i);
            strncpy(state->install_root, root, sizeof(state->install_root) - 1u);
            state->install_root[sizeof(state->install_root) - 1u] = '\0';
            return 1;
        }
    }
    return 0;
}

static int tui_build_components(const dsu_manifest_t *manifest,
                                int **out_selected,
                                char ***out_ids,
                                dsu_u32 *out_count) {
    dsu_u32 count;
    dsu_u32 i;
    int *selected;
    char **ids;
    int any_default = 0;

    if (!manifest || !out_selected || !out_ids || !out_count) return 0;
    count = dsu_manifest_component_count(manifest);
    if (count == 0u) return 0;
    selected = (int *)calloc(count, sizeof(int));
    ids = (char **)calloc(count, sizeof(char *));
    if (!selected || !ids) {
        free(selected);
        free(ids);
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        const char *id = dsu_manifest_component_id(manifest, i);
        dsu_u32 flags = dsu_manifest_component_flags(manifest, i);
        ids[i] = _strdup(id ? id : "");
        if (!ids[i]) {
            dsu_u32 j;
            for (j = 0u; j < i; ++j) free(ids[j]);
            free(ids);
            free(selected);
            return 0;
        }
        if (flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) {
            selected[i] = 1;
            any_default = 1;
        }
    }
    if (!any_default) {
        for (i = 0u; i < count; ++i) {
            selected[i] = 1;
        }
    }
    *out_selected = selected;
    *out_ids = ids;
    *out_count = count;
    return 1;
}

static void tui_free_components(char **ids, int *selected, dsu_u32 count) {
    dsu_u32 i;
    if (ids) {
        for (i = 0u; i < count; ++i) {
            free(ids[i]);
        }
        free(ids);
    }
    if (selected) {
        free(selected);
    }
}

static char *tui_join_selected(char **ids, int *selected, dsu_u32 count) {
    dsu_u32 i;
    size_t total = 0u;
    char *buf;
    size_t pos = 0u;
    if (!ids || !selected || count == 0u) return NULL;
    for (i = 0u; i < count; ++i) {
        if (!selected[i]) continue;
        total += strlen(ids[i]) + 1u;
    }
    if (total == 0u) return NULL;
    buf = (char *)malloc(total + 1u);
    if (!buf) return NULL;
    for (i = 0u; i < count; ++i) {
        if (!selected[i]) continue;
        if (pos != 0u) buf[pos++] = ',';
        memcpy(buf + pos, ids[i], strlen(ids[i]));
        pos += strlen(ids[i]);
    }
    buf[pos] = '\0';
    return buf;
}

int dsu_exe_run_tui(const dsu_exe_bridge_paths_t *paths,
                    const char *platform,
                    const char *frontend_id,
                    int quiet) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_ui_state_t state;
    int *selected = NULL;
    char **ids = NULL;
    dsu_u32 count = 0u;
    char *components_csv = NULL;
    int ok = 0;
    int result = 1;

    if (!paths || !paths->manifest_path) {
        fprintf(stderr, "error: manifest missing\n");
        return 1;
    }
    if (!tui_load_manifest(paths->manifest_path, &ctx, &manifest)) {
        fprintf(stderr, "error: failed to load manifest\n");
        return 1;
    }

    dsu_ui_state_init(&state);
    tui_detect_installed(manifest, platform, &state);

    fprintf(stdout, "Dominium Setup (TUI)\n\n");

    if (state.installed_detected) {
        const char *ops[] = { "Change (install/upgrade)", "Repair", "Remove" };
        int choice = tui_prompt_choice("Existing installation detected. Choose operation:", ops, 3, 0);
        if (choice == 1) {
            state.operation = 2;
        } else if (choice == 2) {
            state.operation = 3;
        } else {
            state.operation = 1;
        }
    } else {
        state.operation = 0;
    }

    if (state.operation != 3) {
        const char *modes[] = { "Quick Install", "Custom Install" };
        int choice = tui_prompt_choice("Install mode:", modes, 2, 0);
        state.install_mode = (choice == 1) ? DSU_UI_INSTALL_MODE_CUSTOM : DSU_UI_INSTALL_MODE_QUICK;
    }

    {
        const char *scopes[] = { "Per-user", "Per-machine", "Portable" };
        int choice = tui_prompt_choice("Install scope:", scopes, 3, 0);
        if (choice == 1) {
            state.scope = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
        } else if (choice == 2) {
            state.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        } else {
            state.scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
        }
    }

    if (!state.install_root[0]) {
        tui_select_install_root(manifest, state.scope, platform, state.install_root, sizeof(state.install_root));
    }
    if (state.install_mode == DSU_UI_INSTALL_MODE_CUSTOM) {
        char buf[512];
        fprintf(stdout, "Install path [%s]: ", state.install_root);
        if (tui_read_line(buf, sizeof(buf)) && buf[0] != '\0') {
            strncpy(state.install_root, buf, sizeof(state.install_root) - 1u);
            state.install_root[sizeof(state.install_root) - 1u] = '\0';
        }
    }

    ok = tui_build_components(manifest, &selected, &ids, &count);
    if (!ok) {
        fprintf(stderr, "error: failed to load components\n");
        goto done;
    }

    if (state.install_mode == DSU_UI_INSTALL_MODE_CUSTOM) {
        dsu_u32 i;
        for (i = 0u; i < count; ++i) {
            char q[256];
            dsu_exe_snprintf(q, sizeof(q), "Install component '%s'?", ids[i]);
            selected[i] = tui_prompt_yesno(q, selected[i]);
        }
    }

    state.enable_shortcuts = tui_prompt_yesno("Create shortcuts?", 1);
    state.enable_file_assoc = tui_prompt_yesno("Enable file associations?", 1);
    state.enable_url_handlers = tui_prompt_yesno("Enable URL handlers?", 1);

    components_csv = tui_join_selected(ids, selected, count);
    if (components_csv) {
        fprintf(stdout, "\nSelected components: %s\n", components_csv);
    }
    fprintf(stdout, "Install root: %s\n", state.install_root);

    if (!tui_prompt_yesno("Proceed?", 1)) {
        result = 1;
        goto done;
    }

    result = dsu_exe_apply_from_state(paths, platform, frontend_id, &state, components_csv, NULL, "tui", quiet);

done:
    if (components_csv) free(components_csv);
    tui_free_components(ids, selected, count);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return result;
}

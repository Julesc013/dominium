/*
FILE: source/dominium/setup/adapters/macos/dsu_macos_platform_iface.c
MODULE: Dominium Setup
PURPOSE: macOS platform adapter implementation for declarative registrations (Plan S-6).
*/
#if !defined(__APPLE__)
#error "dsu_macos_platform_iface.c is macOS-only"
#endif

#include "dsu_macos_platform_iface.h"

#include "dsu/dsu_fs.h"

#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static int dsu__mac_path_exists(const char *path, int *out_is_dir) {
    struct stat st;
    if (!path || !path[0]) return 0;
    if (stat(path, &st) != 0) return 0;
    if (out_is_dir) {
        *out_is_dir = S_ISDIR(st.st_mode) ? 1 : 0;
    }
    return 1;
}

static int dsu__mac_mkdir_p(const char *path) {
    char tmp[1024];
    size_t len;
    size_t i;
    if (!path || !path[0]) return 0;
    len = strlen(path);
    if (len >= sizeof(tmp)) return 0;
    memcpy(tmp, path, len + 1u);
    for (i = 1u; i < len; ++i) {
        if (tmp[i] == '/') {
            tmp[i] = '\0';
            mkdir(tmp, 0755);
            tmp[i] = '/';
        }
    }
    if (mkdir(tmp, 0755) != 0 && !dsu__mac_path_exists(tmp, NULL)) {
        return 0;
    }
    return 1;
}

static int dsu__mac_write_text(const char *path, const char *text, int make_exec) {
    FILE *f;
    if (!path || !text) return 0;
    f = fopen(path, "w");
    if (!f) return 0;
    fputs(text, f);
    fclose(f);
    if (make_exec) {
        chmod(path, 0755);
    }
    return 1;
}

static void dsu__mac_sanitize_label(const char *in, char *out, size_t cap, int allow_space) {
    size_t i = 0u;
    size_t o = 0u;
    if (!out || cap == 0u) return;
    out[0] = '\0';
    if (!in) return;
    while (in[i] && o + 1u < cap) {
        char c = in[i++];
        if ((c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') ||
            c == '-' || c == '_' || c == '.') {
            out[o++] = c;
        } else if (allow_space && c == ' ') {
            out[o++] = c;
        } else {
            out[o++] = '-';
        }
    }
    out[o] = '\0';
}

static int dsu__mac_get_applications_dir(dsu_u8 scope, const char *install_root, char *out, size_t cap) {
    const char *home;
    if (!out || cap == 0u) return 0;
    out[0] = '\0';
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        strncpy(out, "/Applications", cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) {
        if (!install_root || !install_root[0]) return 0;
        snprintf(out, cap, "%s/Applications", install_root);
        return 1;
    }
    home = getenv("HOME");
    if (!home || !home[0]) return 0;
    snprintf(out, cap, "%s/Applications", home);
    return 1;
}

static int dsu__mac_bundle_path(const char *app_id,
                                const char *display_name,
                                dsu_u8 scope,
                                const char *install_root,
                                char *out,
                                size_t cap) {
    char dir[512];
    char name[256];
    if (!out || cap == 0u) return 0;
    out[0] = '\0';
    if (!dsu__mac_get_applications_dir(scope, install_root, dir, sizeof(dir))) return 0;
    if (display_name && display_name[0]) {
        dsu__mac_sanitize_label(display_name, name, sizeof(name), 1);
    } else if (app_id && app_id[0]) {
        dsu__mac_sanitize_label(app_id, name, sizeof(name), 0);
    } else {
        strncpy(name, "Dominium", sizeof(name) - 1u);
        name[sizeof(name) - 1u] = '\0';
    }
    if (!name[0]) {
        strncpy(name, "Dominium", sizeof(name) - 1u);
        name[sizeof(name) - 1u] = '\0';
    }
    if (!dsu__mac_mkdir_p(dir)) return 0;
    snprintf(out, cap, "%s/%s.app", dir, name);
    return 1;
}

static const dsu_platform_intent_t *dsu__mac_find_app_intent(const dsu_platform_registrations_state_t *state,
                                                             const char *app_id) {
    dsu_u32 i;
    if (!state || !app_id) return NULL;
    for (i = 0u; i < state->intent_count; ++i) {
        const dsu_platform_intent_t *it = &state->intents[i];
        if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY &&
            it->app_id && strcmp(it->app_id, app_id) == 0) {
            return it;
        }
    }
    return NULL;
}

static int dsu__mac_exec_path(const dsu_platform_registrations_state_t *state,
                              const dsu_platform_intent_t *intent,
                              const dsu_platform_intent_t *app_intent,
                              char *out,
                              size_t cap) {
    char joined[1024];
    char canon[1024];
    const char *rel = NULL;
    int is_dir = 0;
    if (!state || !out || cap == 0u) return 0;
    out[0] = '\0';

    if (intent && intent->exec_relpath && intent->exec_relpath[0]) {
        rel = intent->exec_relpath;
    } else if (app_intent && app_intent->exec_relpath && app_intent->exec_relpath[0]) {
        rel = app_intent->exec_relpath;
    } else {
        return 0;
    }

    if (dsu_fs_path_join(state->install_root, rel, joined, (dsu_u32)sizeof(joined)) != DSU_STATUS_SUCCESS) {
        return 0;
    }
    if (dsu_fs_path_canonicalize(joined, canon, (dsu_u32)sizeof(canon)) != DSU_STATUS_SUCCESS) {
        return 0;
    }
    if (!dsu__mac_path_exists(canon, &is_dir) && strlen(rel) > 4u) {
        const char *suffix = rel + strlen(rel) - 4u;
        if (strcmp(suffix, ".exe") == 0) {
            char rel_noexe[512];
            size_t n = strlen(rel) - 4u;
            if (n < sizeof(rel_noexe)) {
                memcpy(rel_noexe, rel, n);
                rel_noexe[n] = '\0';
                if (dsu_fs_path_join(state->install_root, rel_noexe, joined, (dsu_u32)sizeof(joined)) == DSU_STATUS_SUCCESS &&
                    dsu_fs_path_canonicalize(joined, canon, (dsu_u32)sizeof(canon)) == DSU_STATUS_SUCCESS) {
                    (void)dsu__mac_path_exists(canon, &is_dir);
                }
            }
        }
    }
    if (is_dir || !dsu__mac_path_exists(canon, NULL)) {
        return 0;
    }
    strncpy(out, canon, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static void dsu__mac_exec_name(const char *app_id, char *out, size_t cap) {
    if (!out || cap == 0u) return;
    out[0] = '\0';
    if (app_id && app_id[0]) {
        dsu__mac_sanitize_label(app_id, out, cap, 0);
    }
    if (!out[0]) {
        strncpy(out, "dominium-launcher", cap - 1u);
        out[cap - 1u] = '\0';
    }
}

static const char *dsu__mac_bundle_identifier(const dsu_platform_registrations_state_t *state,
                                              const dsu_platform_intent_t *intent,
                                              char *out,
                                              size_t cap) {
    if (!out || cap == 0u) return "";
    out[0] = '\0';
    if (intent && intent->app_id && intent->app_id[0]) {
        strncpy(out, intent->app_id, cap - 1u);
        out[cap - 1u] = '\0';
        return out;
    }
    if (state && state->product_id && state->product_id[0]) {
        snprintf(out, cap, "com.dominium.%s", state->product_id);
        return out;
    }
    strncpy(out, "com.dominium.app", cap - 1u);
    out[cap - 1u] = '\0';
    return out;
}

static dsu_status_t dsu__mac_write_plist(const char *plist_path,
                                         const dsu_platform_registrations_state_t *state,
                                         const dsu_platform_intent_t *intent,
                                         const char *exec_name,
                                         const char *display_name) {
    char ident[256];
    const char *version = (state && state->product_version && state->product_version[0]) ? state->product_version : "0.0.0";
    char text[2048];
    const char *id = dsu__mac_bundle_identifier(state, intent, ident, sizeof(ident));
    snprintf(text,
             sizeof(text),
             "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
             "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
             "<plist version=\"1.0\">\n"
             "<dict>\n"
             "  <key>CFBundleIdentifier</key><string>%s</string>\n"
             "  <key>CFBundleName</key><string>%s</string>\n"
             "  <key>CFBundleDisplayName</key><string>%s</string>\n"
             "  <key>CFBundleExecutable</key><string>%s</string>\n"
             "  <key>CFBundlePackageType</key><string>APPL</string>\n"
             "  <key>CFBundleShortVersionString</key><string>%s</string>\n"
             "  <key>CFBundleVersion</key><string>%s</string>\n"
             "  <key>LSMinimumSystemVersion</key><string>10.9</string>\n"
             "</dict>\n"
             "</plist>\n",
             id,
             display_name ? display_name : "Dominium",
             display_name ? display_name : "Dominium",
             exec_name ? exec_name : "dominium-launcher",
             version,
             version);
    if (!dsu__mac_write_text(plist_path, text, 0)) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__mac_register_app_bundle(const dsu_platform_registrations_state_t *state,
                                                 const dsu_platform_intent_t *intent,
                                                 const dsu_platform_intent_t *app_intent) {
    char bundle_path[512];
    char contents[640];
    char macos_dir[720];
    char resources_dir[720];
    char exec_path[1024];
    char exec_name[128];
    char plist_path[768];
    char script_path[768];
    char script[2048];
    const char *display_name;

    if (!state || !intent) return DSU_STATUS_INVALID_ARGS;
    display_name = (intent->display_name && intent->display_name[0]) ? intent->display_name :
                   (app_intent && app_intent->display_name && app_intent->display_name[0]) ? app_intent->display_name : "Dominium";

    if (!dsu__mac_bundle_path(intent->app_id, display_name, state->scope, state->install_root, bundle_path, sizeof(bundle_path))) {
        return DSU_STATUS_IO_ERROR;
    }
    if (!dsu__mac_exec_path(state, intent, app_intent, exec_path, sizeof(exec_path))) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    dsu__mac_exec_name(intent->app_id, exec_name, sizeof(exec_name));

    snprintf(contents, sizeof(contents), "%s/Contents", bundle_path);
    snprintf(macos_dir, sizeof(macos_dir), "%s/MacOS", contents);
    snprintf(resources_dir, sizeof(resources_dir), "%s/Resources", contents);
    if (!dsu__mac_mkdir_p(macos_dir)) return DSU_STATUS_IO_ERROR;
    if (!dsu__mac_mkdir_p(resources_dir)) return DSU_STATUS_IO_ERROR;

    snprintf(plist_path, sizeof(plist_path), "%s/Info.plist", contents);
    if (dsu__mac_write_plist(plist_path, state, intent, exec_name, display_name) != DSU_STATUS_SUCCESS) {
        return DSU_STATUS_IO_ERROR;
    }

    snprintf(script_path, sizeof(script_path), "%s/%s", macos_dir, exec_name);
    if (intent->arguments && intent->arguments[0]) {
        snprintf(script, sizeof(script),
                 "#!/bin/sh\n\"%s\" %s \"$@\"\n",
                 exec_path,
                 intent->arguments);
    } else if (app_intent && app_intent->arguments && app_intent->arguments[0]) {
        snprintf(script, sizeof(script),
                 "#!/bin/sh\n\"%s\" %s \"$@\"\n",
                 exec_path,
                 app_intent->arguments);
    } else {
        snprintf(script, sizeof(script),
                 "#!/bin/sh\n\"%s\" \"$@\"\n",
                 exec_path);
    }
    if (!dsu__mac_write_text(script_path, script, 1)) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__mac_register_app_entry(void *user,
                                               dsu_ctx_t *ctx,
                                               const dsu_platform_registrations_state_t *state,
                                               const dsu_platform_intent_t *intent) {
    const dsu_platform_intent_t *app_intent;
    (void)user;
    (void)ctx;
    if (!state || !intent) return DSU_STATUS_INVALID_ARGS;
    app_intent = dsu__mac_find_app_intent(state, intent->app_id ? intent->app_id : "");
    return dsu__mac_register_app_bundle(state, intent, app_intent);
}

static dsu_status_t dsu__mac_register_file_assoc(void *user,
                                                dsu_ctx_t *ctx,
                                                const dsu_platform_registrations_state_t *state,
                                                const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    if (!state || !intent) return DSU_STATUS_INVALID_ARGS;
    /* Best-effort: ensure the app bundle exists; LaunchServices integration is documented separately. */
    return dsu__mac_register_app_entry(user, ctx, state, intent);
}

static dsu_status_t dsu__mac_register_url_handler(void *user,
                                                 dsu_ctx_t *ctx,
                                                 const dsu_platform_registrations_state_t *state,
                                                 const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    if (!state || !intent) return DSU_STATUS_INVALID_ARGS;
    /* Best-effort: ensure the app bundle exists; LaunchServices integration is documented separately. */
    return dsu__mac_register_app_entry(user, ctx, state, intent);
}

static dsu_status_t dsu__mac_register_uninstall_entry(void *user,
                                                     dsu_ctx_t *ctx,
                                                     const dsu_platform_registrations_state_t *state,
                                                     const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    (void)state;
    (void)intent;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__mac_declare_capability(void *user,
                                               dsu_ctx_t *ctx,
                                               const dsu_platform_registrations_state_t *state,
                                               const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    (void)state;
    (void)intent;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__mac_remove_tree(const char *path) {
    struct stat st;
    DIR *dir;
    struct dirent *ent;
    if (!path || !path[0]) return DSU_STATUS_INVALID_ARGS;
    if (lstat(path, &st) != 0) {
        return (errno == ENOENT) ? DSU_STATUS_SUCCESS : DSU_STATUS_IO_ERROR;
    }
    if (!S_ISDIR(st.st_mode)) {
        return (unlink(path) == 0) ? DSU_STATUS_SUCCESS : DSU_STATUS_IO_ERROR;
    }
    dir = opendir(path);
    if (!dir) {
        return DSU_STATUS_IO_ERROR;
    }
    while ((ent = readdir(dir)) != NULL) {
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) continue;
        {
            char child[1024];
            snprintf(child, sizeof(child), "%s/%s", path, ent->d_name);
            if (dsu__mac_remove_tree(child) != DSU_STATUS_SUCCESS) {
                closedir(dir);
                return DSU_STATUS_IO_ERROR;
            }
        }
    }
    closedir(dir);
    return (rmdir(path) == 0) ? DSU_STATUS_SUCCESS : DSU_STATUS_IO_ERROR;
}

static dsu_status_t dsu__mac_remove_registrations(void *user,
                                                  dsu_ctx_t *ctx,
                                                  const dsu_platform_registrations_state_t *state) {
    dsu_u32 i;
    (void)user;
    (void)ctx;
    if (!state) return DSU_STATUS_INVALID_ARGS;

    for (i = 0u; i < state->intent_count; ++i) {
        const dsu_platform_intent_t *it = &state->intents[i];
        if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY ||
            it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC ||
            it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER) {
            char bundle_path[512];
            const char *display_name = (it->display_name && it->display_name[0]) ? it->display_name : "Dominium";
            if (dsu__mac_bundle_path(it->app_id, display_name, state->scope, state->install_root, bundle_path, sizeof(bundle_path))) {
                (void)dsu__mac_remove_tree(bundle_path);
            }
        }
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__mac_plat_request_elevation(void *user, dsu_ctx_t *ctx) {
    (void)user;
    (void)ctx;
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__mac_plat_atomic_dir_swap(void *user, dsu_ctx_t *ctx, const char *src_abs, const char *dst_abs) {
    (void)user;
    (void)ctx;
    (void)src_abs;
    (void)dst_abs;
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__mac_plat_flush_fs(void *user, dsu_ctx_t *ctx) {
    (void)user;
    (void)ctx;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_macos_platform_iface_init(dsu_platform_iface_t *out_iface) {
    if (!out_iface) {
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu_platform_iface_init(out_iface);
    out_iface->plat_request_elevation = dsu__mac_plat_request_elevation;
    out_iface->plat_register_app_entry = dsu__mac_register_app_entry;
    out_iface->plat_register_file_assoc = dsu__mac_register_file_assoc;
    out_iface->plat_register_url_handler = dsu__mac_register_url_handler;
    out_iface->plat_register_uninstall_entry = dsu__mac_register_uninstall_entry;
    out_iface->plat_declare_capability = dsu__mac_declare_capability;
    out_iface->plat_remove_registrations = dsu__mac_remove_registrations;
    out_iface->plat_atomic_dir_swap = dsu__mac_plat_atomic_dir_swap;
    out_iface->plat_flush_fs = dsu__mac_plat_flush_fs;
    return DSU_STATUS_SUCCESS;
}

/*
FILE: source/dominium/setup/adapters/linux/dsu_linux_platform_iface.c
MODULE: Dominium Setup
PURPOSE: Linux platform adapter implementation for declarative registrations (Plan S-6).
*/
#if !defined(__linux__)
#error "dsu_linux_platform_iface.c is Linux-only"
#endif

#include "dsu_linux_platform_iface.h"

#include "dsu/dsu_fs.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/stat.h>
#include <unistd.h>

static int dsu__linux_path_exists(const char *path, int *out_is_dir) {
    struct stat st;
    if (!path || !path[0]) return 0;
    if (stat(path, &st) != 0) return 0;
    if (out_is_dir) {
        *out_is_dir = S_ISDIR(st.st_mode) ? 1 : 0;
    }
    return 1;
}

static int dsu__linux_mkdir_p(const char *path) {
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
    if (mkdir(tmp, 0755) != 0 && !dsu__linux_path_exists(tmp, NULL)) {
        return 0;
    }
    return 1;
}

static int dsu__linux_write_text(const char *path, const char *text) {
    FILE *f;
    if (!path || !text) return 0;
    f = fopen(path, "w");
    if (!f) return 0;
    fputs(text, f);
    fclose(f);
    return 1;
}

static void dsu__linux_sanitize_id(const char *in, char *out, size_t cap) {
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
            if (c >= 'A' && c <= 'Z') c = (char)(c - 'A' + 'a');
            out[o++] = c;
        } else {
            out[o++] = '-';
        }
    }
    out[o] = '\0';
}

static int dsu__linux_get_applications_dir(dsu_u8 scope, char *out, size_t cap) {
    const char *base = NULL;
    if (!out || cap == 0u) return 0;
    out[0] = '\0';
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        strncpy(out, "/usr/share/applications", cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }
    base = getenv("XDG_DATA_HOME");
    if (!base || !base[0]) {
        const char *home = getenv("HOME");
        if (!home || !home[0]) return 0;
        snprintf(out, cap, "%s/.local/share/applications", home);
    } else {
        snprintf(out, cap, "%s/applications", base);
    }
    return 1;
}

static int dsu__linux_get_mime_dir(dsu_u8 scope, char *out, size_t cap) {
    const char *base = NULL;
    if (!out || cap == 0u) return 0;
    out[0] = '\0';
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        strncpy(out, "/usr/share/mime/packages", cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }
    base = getenv("XDG_DATA_HOME");
    if (!base || !base[0]) {
        const char *home = getenv("HOME");
        if (!home || !home[0]) return 0;
        snprintf(out, cap, "%s/.local/share/mime/packages", home);
    } else {
        snprintf(out, cap, "%s/mime/packages", base);
    }
    return 1;
}

static int dsu__linux_desktop_path(const char *app_id, dsu_u8 scope, char *out, size_t cap) {
    char dir[512];
    char base[256];
    if (!out || cap == 0u) return 0;
    out[0] = '\0';
    if (!dsu__linux_get_applications_dir(scope, dir, sizeof(dir))) return 0;
    dsu__linux_sanitize_id(app_id ? app_id : "dominium", base, sizeof(base));
    if (!dsu__linux_mkdir_p(dir)) return 0;
    snprintf(out, cap, "%s/%s.desktop", dir, base);
    return 1;
}

static int dsu__linux_mime_xml_path(const char *extension, dsu_u8 scope, char *out, size_t cap) {
    char dir[512];
    char ext_id[128];
    size_t i = 0u;
    size_t o = 0u;
    if (!extension || !extension[0] || !out || cap == 0u) return 0;
    if (!dsu__linux_get_mime_dir(scope, dir, sizeof(dir))) return 0;
    if (!dsu__linux_mkdir_p(dir)) return 0;
    if (extension[0] == '.') {
        extension++;
    }
    while (extension[i] && o + 1u < sizeof(ext_id)) {
        char c = extension[i++];
        if ((c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9')) {
            if (c >= 'A' && c <= 'Z') c = (char)(c - 'A' + 'a');
            ext_id[o++] = c;
        } else {
            ext_id[o++] = '-';
        }
    }
    ext_id[o] = '\0';
    snprintf(out, cap, "%s/dominium-%s.xml", dir, ext_id);
    return 1;
}

static int dsu__linux_write_mime_xml(const char *extension, dsu_u8 scope) {
    char path[512];
    char ext_id[128];
    char xml[1024];
    size_t i = 0u;
    size_t o = 0u;
    if (!extension || !extension[0]) return 0;
    if (!dsu__linux_mime_xml_path(extension, scope, path, sizeof(path))) return 0;
    if (extension[0] == '.') {
        extension++;
    }
    while (extension[i] && o + 1u < sizeof(ext_id)) {
        char c = extension[i++];
        if ((c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9')) {
            if (c >= 'A' && c <= 'Z') c = (char)(c - 'A' + 'a');
            ext_id[o++] = c;
        } else {
            ext_id[o++] = '-';
        }
    }
    ext_id[o] = '\0';
    snprintf(xml,
             sizeof(xml),
             "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
             "<mime-info xmlns=\"http://www.freedesktop.org/standards/shared-mime-info\">\n"
             "  <mime-type type=\"application/x-dominium-%s\">\n"
             "    <comment>Application data</comment>\n"
             "    <glob pattern=\"*.%s\"/>\n"
             "  </mime-type>\n"
             "</mime-info>\n",
             ext_id,
             extension);
    return dsu__linux_write_text(path, xml);
}

static int dsu__linux_mime_has(const char *list, const char *mime) {
    const char *p;
    size_t mime_len;
    if (!list || !mime) return 0;
    mime_len = strlen(mime);
    p = list;
    while (*p) {
        const char *end = strchr(p, ';');
        size_t len = end ? (size_t)(end - p) : strlen(p);
        if (len == mime_len && strncmp(p, mime, len) == 0) {
            return 1;
        }
        if (!end) break;
        p = end + 1;
    }
    return 0;
}

static int dsu__linux_merge_mime_line(const char *desktop_path, const char *extra_mime, char *out, size_t cap) {
    FILE *f;
    char line[512];
    char existing[512];
    existing[0] = '\0';
    if (!out || cap == 0u) return 0;
    out[0] = '\0';
    if (!extra_mime || !extra_mime[0]) return 0;

    f = fopen(desktop_path, "r");
    if (f) {
        while (fgets(line, sizeof(line), f)) {
            if (strncmp(line, "MimeType=", 9) == 0) {
                strncpy(existing, line + 9, sizeof(existing) - 1u);
                existing[sizeof(existing) - 1u] = '\0';
                break;
            }
        }
        fclose(f);
    }

    {
        size_t len = strlen(existing);
        size_t start = 0u;
        while (start < len && (existing[start] == ' ' || existing[start] == '\t' || existing[start] == '\r' || existing[start] == '\n')) {
            ++start;
        }
        while (len > start && (existing[len - 1u] == ' ' || existing[len - 1u] == '\t' || existing[len - 1u] == '\r' || existing[len - 1u] == '\n')) {
            existing[len - 1u] = '\0';
            --len;
        }
        if (start != 0u) {
            memmove(existing, existing + start, len - start + 1u);
        }
    }
    if (existing[0] != '\0' && existing[strlen(existing) - 1u] != ';') {
        size_t n = strlen(existing);
        if (n + 1u < sizeof(existing)) {
            existing[n] = ';';
            existing[n + 1u] = '\0';
        }
    }

    strncpy(out, existing, cap - 1u);
    out[cap - 1u] = '\0';
    if (!dsu__linux_mime_has(out, extra_mime)) {
        size_t n = strlen(out);
        size_t m = strlen(extra_mime);
        if (n + m + 2u < cap) {
            memcpy(out + n, extra_mime, m);
            out[n + m] = ';';
            out[n + m + 1u] = '\0';
        }
    }
    return 1;
}

static int dsu__linux_build_exec_command(char *out_cmd,
                                         size_t out_cap,
                                         const dsu_platform_registrations_state_t *state,
                                         const dsu_platform_intent_t *intent,
                                         const dsu_platform_intent_t *app_intent) {
    char joined[1024];
    char canon[1024];
    const char *rel = NULL;
    int is_dir = 0;
    if (!out_cmd || out_cap == 0u || !state) return 0;
    out_cmd[0] = '\0';

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
    if (!dsu__linux_path_exists(canon, &is_dir) && strlen(rel) > 4u) {
        const char *suffix = rel + strlen(rel) - 4u;
        if (strcmp(suffix, ".exe") == 0) {
            char rel_noexe[512];
            size_t n = strlen(rel) - 4u;
            if (n < sizeof(rel_noexe)) {
                memcpy(rel_noexe, rel, n);
                rel_noexe[n] = '\0';
                if (dsu_fs_path_join(state->install_root, rel_noexe, joined, (dsu_u32)sizeof(joined)) == DSU_STATUS_SUCCESS &&
                    dsu_fs_path_canonicalize(joined, canon, (dsu_u32)sizeof(canon)) == DSU_STATUS_SUCCESS) {
                    (void)dsu__linux_path_exists(canon, &is_dir);
                }
            }
        }
    }

    if (is_dir) {
        return 0;
    }
    if (intent && intent->arguments && intent->arguments[0]) {
        snprintf(out_cmd, out_cap, "\"%s\" %s", canon, intent->arguments);
    } else if (app_intent && app_intent->arguments && app_intent->arguments[0]) {
        snprintf(out_cmd, out_cap, "\"%s\" %s", canon, app_intent->arguments);
    } else {
        snprintf(out_cmd, out_cap, "\"%s\"", canon);
    }
    return 1;
}

static const dsu_platform_intent_t *dsu__linux_find_app_intent(const dsu_platform_registrations_state_t *state, const char *app_id) {
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

static dsu_status_t dsu__linux_write_desktop(const char *desktop_path,
                                             const char *display_name,
                                             const char *exec_cmd,
                                             const char *mime_line) {
    char text[2048];
    if (!desktop_path || !exec_cmd) return DSU_STATUS_INVALID_ARGS;
    if (mime_line && mime_line[0]) {
        snprintf(text,
                 sizeof(text),
                 "[Desktop Entry]\n"
                 "Type=Application\n"
                 "Name=%s\n"
                 "Exec=%s\n"
                 "Terminal=false\n"
                 "Categories=Game;\n"
                 "MimeType=%s\n",
                 display_name ? display_name : "Application",
                 exec_cmd,
                 mime_line);
    } else {
        snprintf(text,
                 sizeof(text),
                 "[Desktop Entry]\n"
                 "Type=Application\n"
                 "Name=%s\n"
                 "Exec=%s\n"
                 "Terminal=false\n"
                 "Categories=Game;\n",
                 display_name ? display_name : "Application",
                 exec_cmd);
    }
    if (!dsu__linux_write_text(desktop_path, text)) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__linux_register_desktop(const dsu_platform_registrations_state_t *state,
                                               const dsu_platform_intent_t *intent,
                                               const char *extra_mime) {
    char desktop_path[512];
    char exec_cmd[1024];
    char mime_line[512];
    const dsu_platform_intent_t *app_intent;
    const char *app_id;
    const char *display_name;

    if (!state || !intent) return DSU_STATUS_INVALID_ARGS;
    app_id = (intent->app_id && intent->app_id[0]) ? intent->app_id : "dominium";
    app_intent = dsu__linux_find_app_intent(state, app_id);
    display_name = (intent->display_name && intent->display_name[0]) ? intent->display_name :
                   (app_intent && app_intent->display_name && app_intent->display_name[0]) ? app_intent->display_name : "Application";

    if (!dsu__linux_desktop_path(app_id, state->scope, desktop_path, sizeof(desktop_path))) {
        return DSU_STATUS_IO_ERROR;
    }
    if (!dsu__linux_build_exec_command(exec_cmd, sizeof(exec_cmd), state, intent, app_intent)) {
        return DSU_STATUS_INVALID_REQUEST;
    }

    mime_line[0] = '\0';
    if (extra_mime && extra_mime[0]) {
        (void)dsu__linux_merge_mime_line(desktop_path, extra_mime, mime_line, sizeof(mime_line));
    }

    return dsu__linux_write_desktop(desktop_path, display_name, exec_cmd, mime_line[0] ? mime_line : NULL);
}

static dsu_status_t dsu__linux_register_app_entry(void *user,
                                                 dsu_ctx_t *ctx,
                                                 const dsu_platform_registrations_state_t *state,
                                                 const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    return dsu__linux_register_desktop(state, intent, NULL);
}

static dsu_status_t dsu__linux_register_file_assoc(void *user,
                                                  dsu_ctx_t *ctx,
                                                  const dsu_platform_registrations_state_t *state,
                                                  const dsu_platform_intent_t *intent) {
    char mime[128];
    const char *ext;
    size_t i = 0u;
    size_t o = 0u;
    (void)user;
    (void)ctx;
    if (!intent || !intent->extension || !intent->extension[0]) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    ext = intent->extension;
    if (ext[0] == '.') ext++;
    while (ext[i] && o + 1u < sizeof(mime)) {
        char c = ext[i++];
        if ((c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9')) {
            if (c >= 'A' && c <= 'Z') c = (char)(c - 'A' + 'a');
            mime[o++] = c;
        } else {
            mime[o++] = '-';
        }
    }
    mime[o] = '\0';
    {
        char full[160];
        snprintf(full, sizeof(full), "application/x-dominium-%s", mime);
        (void)dsu__linux_write_mime_xml(intent->extension, state->scope);
        return dsu__linux_register_desktop(state, intent, full);
    }
}

static dsu_status_t dsu__linux_register_url_handler(void *user,
                                                   dsu_ctx_t *ctx,
                                                   const dsu_platform_registrations_state_t *state,
                                                   const dsu_platform_intent_t *intent) {
    char full[256];
    (void)user;
    (void)ctx;
    if (!intent || !intent->protocol || !intent->protocol[0]) {
        return DSU_STATUS_INVALID_REQUEST;
    }
    snprintf(full, sizeof(full), "x-scheme-handler/%s", intent->protocol);
    return dsu__linux_register_desktop(state, intent, full);
}

static dsu_status_t dsu__linux_register_uninstall_entry(void *user,
                                                       dsu_ctx_t *ctx,
                                                       const dsu_platform_registrations_state_t *state,
                                                       const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    (void)state;
    (void)intent;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__linux_declare_capability(void *user,
                                                 dsu_ctx_t *ctx,
                                                 const dsu_platform_registrations_state_t *state,
                                                 const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    (void)state;
    (void)intent;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__linux_remove_registrations(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state) {
    dsu_u32 i;
    (void)user;
    (void)ctx;
    if (!state) return DSU_STATUS_INVALID_ARGS;

    for (i = 0u; i < state->intent_count; ++i) {
        const dsu_platform_intent_t *it = &state->intents[i];
        char desktop_path[512];
        char mime_path[512];
        const char *app_id = (it->app_id && it->app_id[0]) ? it->app_id : "dominium";

        if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY ||
            it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC ||
            it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER) {
            if (dsu__linux_desktop_path(app_id, state->scope, desktop_path, sizeof(desktop_path))) {
                (void)remove(desktop_path);
            }
        }
        if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC) {
            if (it->extension && dsu__linux_mime_xml_path(it->extension, state->scope, mime_path, sizeof(mime_path))) {
                (void)remove(mime_path);
            }
        }
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__linux_plat_request_elevation(void *user, dsu_ctx_t *ctx) {
    (void)user;
    (void)ctx;
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__linux_plat_atomic_dir_swap(void *user, dsu_ctx_t *ctx, const char *src_abs, const char *dst_abs) {
    (void)user;
    (void)ctx;
    (void)src_abs;
    (void)dst_abs;
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__linux_plat_flush_fs(void *user, dsu_ctx_t *ctx) {
    (void)user;
    (void)ctx;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_linux_platform_iface_init(dsu_platform_iface_t *out_iface) {
    if (!out_iface) {
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu_platform_iface_init(out_iface);
    out_iface->plat_request_elevation = dsu__linux_plat_request_elevation;
    out_iface->plat_register_app_entry = dsu__linux_register_app_entry;
    out_iface->plat_register_file_assoc = dsu__linux_register_file_assoc;
    out_iface->plat_register_url_handler = dsu__linux_register_url_handler;
    out_iface->plat_register_uninstall_entry = dsu__linux_register_uninstall_entry;
    out_iface->plat_declare_capability = dsu__linux_declare_capability;
    out_iface->plat_remove_registrations = dsu__linux_remove_registrations;
    out_iface->plat_atomic_dir_swap = dsu__linux_plat_atomic_dir_swap;
    out_iface->plat_flush_fs = dsu__linux_plat_flush_fs;
    return DSU_STATUS_SUCCESS;
}

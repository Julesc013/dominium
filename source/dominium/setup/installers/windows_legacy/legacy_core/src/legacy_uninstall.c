/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_uninstall.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Uninstall using legacy installed-state file list.
*/
#include "legacy_internal.h"

#if defined(_WIN32)
#include <direct.h>
#define dsu_legacy_rmdir _rmdir
#else
#include <unistd.h>
#define dsu_legacy_rmdir rmdir
#endif

static char *dsu_legacy_join_path(const char *a, const char *b) {
    dsu_legacy_u32 na;
    dsu_legacy_u32 nb;
    char *out;
    if (!a || !b) return NULL;
    na = dsu_legacy_strlen(a);
    nb = dsu_legacy_strlen(b);
    out = (char *)malloc((size_t)(na + nb + 2u));
    if (!out) return NULL;
    memcpy(out, a, (size_t)na);
    out[na] = '/';
    memcpy(out + na + 1u, b, (size_t)nb);
    out[na + 1u + nb] = '\0';
    return out;
}

static void dsu_legacy_remove_parent_dirs(const char *install_root, const char *rel_path) {
    char *full = dsu_legacy_join_path(install_root, rel_path);
    char *p;
    if (!full) return;
    p = full + dsu_legacy_strlen(full);
    while (p > full) {
        if (*p == '/' || *p == '\\') {
            *p = '\0';
            dsu_legacy_rmdir(full);
        }
        --p;
    }
    free(full);
}

dsu_legacy_status_t dsu_legacy_uninstall(const char *state_path,
                                         const char *log_path) {
    dsu_legacy_state_t *state = NULL;
    dsu_legacy_status_t st;
    dsu_legacy_u32 i;
    dsu_legacy_log_t log;
    int ok = 1;

    if (!state_path) return DSU_LEGACY_STATUS_INVALID_ARGS;
    memset(&log, 0, sizeof(log));
    if (log_path && log_path[0] != '\0') {
        st = dsu_legacy_log_open(&log, log_path);
        if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    }

    st = dsu_legacy_state_load(state_path, &state);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_legacy_log_close(&log);
        return st;
    }

    for (i = state->file_count; i > 0u; --i) {
        dsu_legacy_state_file_t *f = &state->files[i - 1u];
        char *full = dsu_legacy_join_path(state->install_root, f->path);
        if (!full) {
            ok = 0;
            continue;
        }
        if (remove(full) != 0) {
            ok = 0;
            if (log.f) dsu_legacy_log_printf(&log, "REMOVE_FAIL %s", f->path);
        } else {
            if (log.f) dsu_legacy_log_printf(&log, "REMOVED %s", f->path);
        }
        free(full);
        dsu_legacy_remove_parent_dirs(state->install_root, f->path);
    }

    if (remove(state_path) == 0) {
        if (log.f) dsu_legacy_log_printf(&log, "STATE_REMOVED %s", state_path);
    }

    dsu_legacy_state_free(state);
    dsu_legacy_log_close(&log);
    return ok ? DSU_LEGACY_STATUS_SUCCESS : DSU_LEGACY_STATUS_IO_ERROR;
}

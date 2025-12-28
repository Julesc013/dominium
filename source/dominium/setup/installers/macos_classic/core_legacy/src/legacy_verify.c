/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_verify.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Basic verify for legacy installs (exists + size).
*/
#include "legacy_internal.h"

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

static int dsu_legacy_file_size(const char *path, dsu_legacy_u64 *out_size) {
    FILE *f;
    long sz;
    if (!path || !out_size) return 0;
    *out_size = 0u;
    f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    sz = ftell(f);
    fclose(f);
    if (sz < 0) return 0;
    *out_size = (dsu_legacy_u64)(unsigned long)sz;
    return 1;
}

dsu_legacy_status_t dsu_legacy_verify(const char *state_path,
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

    for (i = 0u; i < state->file_count; ++i) {
        dsu_legacy_state_file_t *f = &state->files[i];
        char *full = dsu_legacy_join_path(state->install_root, f->path);
        dsu_legacy_u64 size = 0u;
        if (!full) {
            ok = 0;
            continue;
        }
        if (!dsu_legacy_file_size(full, &size)) {
            ok = 0;
            if (log.f) dsu_legacy_log_printf(&log, "MISSING %s", f->path);
        } else if (f->has_size && size != f->size) {
            ok = 0;
            if (log.f) dsu_legacy_log_printf(&log, "SIZE_MISMATCH %s", f->path);
        } else {
            if (log.f) dsu_legacy_log_printf(&log, "OK %s", f->path);
        }
        free(full);
    }

    dsu_legacy_state_free(state);
    dsu_legacy_log_close(&log);
    return ok ? DSU_LEGACY_STATUS_SUCCESS : DSU_LEGACY_STATUS_INTEGRITY_ERROR;
}

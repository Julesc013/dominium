/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_log.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Simple deterministic text logging for Classic legacy installs.
*/
#include "legacy_internal.h"

#include <stdarg.h>

dsu_legacy_status_t dsu_legacy_log_open(dsu_legacy_log_t *log, const char *path) {
    if (!log || !path || path[0] == '\0') {
        return DSU_LEGACY_STATUS_INVALID_ARGS;
    }
    log->f = fopen(path, "wb");
    if (!log->f) {
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    return DSU_LEGACY_STATUS_SUCCESS;
}

void dsu_legacy_log_close(dsu_legacy_log_t *log) {
    if (!log) {
        return;
    }
    if (log->f) {
        fclose(log->f);
        log->f = NULL;
    }
}

void dsu_legacy_log_printf(dsu_legacy_log_t *log, const char *fmt, ...) {
    va_list args;
    if (!log || !log->f || !fmt) {
        return;
    }
    va_start(args, fmt);
    vfprintf(log->f, fmt, args);
    va_end(args);
    fputc('\n', log->f);
    fflush(log->f);
}

/*
FILE: source/dominium/setup/installers/linux/common/src/log_forward.c
MODULE: Dominium Setup Linux
PURPOSE: Minimal log forwarding for Linux installer frontends.
*/
#include "dsu_linux_log.h"

#include <stdio.h>
#include <string.h>

static char g_log_path[512];

void dsu_linux_log_set_file(const char *path) {
    if (!path) {
        g_log_path[0] = '\0';
        return;
    }
    strncpy(g_log_path, path, sizeof(g_log_path) - 1u);
    g_log_path[sizeof(g_log_path) - 1u] = '\0';
}

static void dsu__log_write(const char *prefix, const char *fmt, va_list args) {
    FILE *f = NULL;
    if (g_log_path[0] != '\0') {
        f = fopen(g_log_path, "a");
    }
    if (!f) {
        f = stderr;
    }
    if (prefix) {
        fputs(prefix, f);
    }
    vfprintf(f, fmt, args);
    fputc('\n', f);
    if (f != stderr) {
        fclose(f);
    }
}

void dsu_linux_log_info(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    dsu__log_write("INFO: ", fmt, args);
    va_end(args);
}

void dsu_linux_log_error(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    dsu__log_write("ERROR: ", fmt, args);
    va_end(args);
}

/*
FILE: source/dominium/setup/installers/macos/common/src/tui.c
MODULE: Dominium Setup macOS
PURPOSE: Minimal TUI helpers (ANSI, no external deps).
*/
#include "dsu_macos_tui.h"

#include <stdio.h>
#include <string.h>

#if defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
#endif

int dsu_macos_tui_is_tty(void) {
#if defined(__unix__) || defined(__APPLE__)
    return isatty(0) && isatty(1);
#else
    return 0;
#endif
}

void dsu_macos_tui_clear(void) {
    if (!dsu_macos_tui_is_tty()) {
        return;
    }
    fputs("\033[2J\033[H", stdout);
}

void dsu_macos_tui_flush(void) {
    fflush(stdout);
}

int dsu_macos_tui_read_line(char *buf, unsigned long cap) {
    size_t n;
    if (!buf || cap == 0u) {
        return 0;
    }
    if (!fgets(buf, (int)cap, stdin)) {
        return 0;
    }
    n = strlen(buf);
    while (n > 0u && (buf[n - 1u] == '\n' || buf[n - 1u] == '\r')) {
        buf[n - 1u] = '\0';
        --n;
    }
    return 1;
}

void dsu_macos_tui_trim(char *s) {
    size_t len;
    size_t start;
    if (!s) return;
    len = strlen(s);
    start = 0u;
    while (start < len && (s[start] == ' ' || s[start] == '\t')) {
        ++start;
    }
    while (len > start && (s[len - 1u] == ' ' || s[len - 1u] == '\t')) {
        s[len - 1u] = '\0';
        --len;
    }
    if (start != 0u) {
        memmove(s, s + start, len - start + 1u);
    }
}

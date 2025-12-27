/*
FILE: source/dominium/setup/installers/linux/gui/dominium-setup-gui.c
MODULE: Dominium Setup Linux
PURPOSE: Minimal GUI wrapper (launches TUI in a terminal when available).
*/
#include "dsu_linux_args.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
#endif

#define DSU_LINUX_GUI_NAME "dominium-setup-gui"
#define DSU_LINUX_GUI_VERSION "0.0.0"

static void dsu__usage(FILE *out) {
    fprintf(out,
            "%s %s\n"
            "Usage: %s [args]\n",
            DSU_LINUX_GUI_NAME, DSU_LINUX_GUI_VERSION,
            DSU_LINUX_GUI_NAME);
}

static int dsu__has_display(void) {
    const char *d = getenv("DISPLAY");
    const char *w = getenv("WAYLAND_DISPLAY");
    return (d && d[0]) || (w && w[0]);
}

static int dsu__is_exec(const char *path) {
#if defined(__unix__) || defined(__APPLE__)
    return (path && path[0] && access(path, X_OK) == 0);
#else
    (void)path;
    return 0;
#endif
}

static int dsu__find_in_path(const char *name, char *out, size_t cap) {
    const char *path = getenv("PATH");
    const char *p;
    const char *next;
    char buf[512];
    size_t len;

    if (!name || !out || cap == 0u) return 0;
    out[0] = '\0';

    if (dsu__is_exec(name)) {
        strncpy(out, name, cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }

    if (!path || !path[0]) return 0;
    p = path;
    while (p && *p) {
        next = strchr(p, ':');
        len = next ? (size_t)(next - p) : strlen(p);
        if (len > 0 && len < sizeof(buf)) {
            memcpy(buf, p, len);
            buf[len] = '\0';
            snprintf(out, cap, "%s/%s", buf, name);
            if (dsu__is_exec(out)) {
                return 1;
            }
        }
        if (!next) break;
        p = next + 1;
    }
    out[0] = '\0';
    return 0;
}

static int dsu__dir_from_argv0(const char *argv0, char *out, size_t cap) {
    const char *slash = NULL;
    if (!argv0 || !out || cap == 0u) return 0;
    {
        const char *s1 = strrchr(argv0, '/');
        const char *s2 = strrchr(argv0, '\\');
        slash = s1;
        if (s2 && (!slash || s2 > slash)) slash = s2;
    }
    if (!slash) return 0;
    {
        size_t len = (size_t)(slash - argv0);
        if (len + 1u > cap) return 0;
        memcpy(out, argv0, len);
        out[len] = '\0';
        return 1;
    }
}

static const char *dsu__resolve_tui_path(const char *argv0, char *out, size_t cap) {
    char dir[512];
    if (out && cap) out[0] = '\0';
    if (dsu__dir_from_argv0(argv0, dir, sizeof(dir))) {
        snprintf(out, cap, "%s/%s", dir, "dominium-setup-tui");
        if (dsu__is_exec(out)) {
            return out;
        }
    }
    if (out && cap && dsu__find_in_path("dominium-setup-tui", out, cap)) {
        return out;
    }
    return "dominium-setup-tui";
}

static char *dsu__quote_arg(const char *s) {
    const char *p;
    size_t extra = 0u;
    size_t len;
    char *out;
    size_t idx = 0u;
    int needs = 0;
    if (!s) return NULL;
    for (p = s; *p; ++p) {
        if (*p == ' ' || *p == '\t') {
            needs = 1;
        }
        if (*p == '"') {
            needs = 1;
            extra += 1u;
        }
    }
    if (!needs) {
        len = strlen(s);
        out = (char *)malloc(len + 1u);
        if (!out) return NULL;
        memcpy(out, s, len);
        out[len] = '\0';
        return out;
    }
    len = strlen(s);
    out = (char *)malloc(len + extra + 3u);
    if (!out) return NULL;
    out[idx++] = '"';
    for (p = s; *p; ++p) {
        if (*p == '"') {
            out[idx++] = '\\';
        }
        out[idx++] = *p;
    }
    out[idx++] = '"';
    out[idx] = '\0';
    return out;
}

static char *dsu__build_cmdline(const char *exe, int argc, char **argv) {
    size_t cap = 256u;
    size_t len = 0u;
    char *buf = (char *)malloc(cap);
    int i;

    if (!buf) return NULL;
    buf[0] = '\0';
    if (exe) {
        char *q = dsu__quote_arg(exe);
        if (!q) {
            free(buf);
            return NULL;
        }
        len = strlen(q);
        if (len + 2u > cap) {
            cap = len + 64u;
            buf = (char *)realloc(buf, cap);
            if (!buf) {
                free(q);
                return NULL;
            }
        }
        memcpy(buf, q, len);
        buf[len] = '\0';
        free(q);
    }

    for (i = 1; i < argc; ++i) {
        char *q = dsu__quote_arg(argv[i] ? argv[i] : "");
        size_t need;
        if (!q) continue;
        need = len + strlen(q) + 2u;
        if (need > cap) {
            cap = need + 64u;
            buf = (char *)realloc(buf, cap);
            if (!buf) {
                free(q);
                return NULL;
            }
        }
        buf[len++] = ' ';
        memcpy(buf + len, q, strlen(q));
        len += strlen(q);
        buf[len] = '\0';
        free(q);
    }
    return buf;
}

int main(int argc, char **argv) {
    dsu_linux_cli_args_t args;
    char term[256];
    char tui_path[512];
    const char *tui = dsu__resolve_tui_path(argv[0], tui_path, sizeof(tui_path));
    char *cmd = NULL;
    int use_term = 0;

    dsu_linux_args_parse(argc, argv, &args);
    if (args.want_help) {
        dsu__usage(stdout);
        return 0;
    }
    if (args.want_version) {
        fprintf(stdout, "%s %s\n", DSU_LINUX_GUI_NAME, DSU_LINUX_GUI_VERSION);
        return 0;
    }

    if (dsu__has_display()) {
        static const char *candidates[] = {
            "x-terminal-emulator",
            "gnome-terminal",
            "konsole",
            "xfce4-terminal",
            "xterm",
            "kitty",
            "alacritty",
            "tilix",
            "mate-terminal",
            "lxterminal"
        };
        size_t i;
        for (i = 0u; i < sizeof(candidates) / sizeof(candidates[0]); ++i) {
            if (dsu__find_in_path(candidates[i], term, sizeof(term))) {
                use_term = 1;
                break;
            }
        }
    }

    if (use_term) {
        char *tui_cmd = dsu__build_cmdline(tui, argc, argv);
        if (!tui_cmd) {
            return 1;
        }
        {
            size_t cmd_cap = strlen(term) + strlen(tui_cmd) + 8u;
            cmd = (char *)malloc(cmd_cap);
            if (!cmd) {
                free(tui_cmd);
                return 1;
            }
            snprintf(cmd, cmd_cap, "%s -e %s", term, tui_cmd);
        }
        free(tui_cmd);
    } else {
        cmd = dsu__build_cmdline(tui, argc, argv);
    }

    if (!cmd) {
        return 1;
    }
    if (system(cmd) != 0) {
        free(cmd);
        return 1;
    }
    free(cmd);
    return 0;
}

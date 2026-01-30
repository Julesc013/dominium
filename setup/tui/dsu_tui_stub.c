/*
Setup TUI frontend wrapper (delegates to setup_cli.py).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_frontend.h"

static void dsu_normalize_path(char* path)
{
    char* p;
    if (!path) {
        return;
    }
    for (p = path; *p; ++p) {
        if (*p == '\\') {
            *p = '/';
        }
    }
}

static int dsu_file_exists(const char* path)
{
    FILE* f = 0;
    if (!path || !path[0]) {
        return 0;
    }
    f = fopen(path, "rb");
    if (f) {
        fclose(f);
        return 1;
    }
    return 0;
}

static int dsu_append_quoted(char* buf, size_t cap, const char* arg)
{
    size_t len;
    size_t pos;
    size_t i;
    if (!buf || cap == 0u || !arg) {
        return 0;
    }
    len = strlen(buf);
    if (len + 3u >= cap) {
        return 0;
    }
    pos = len;
    buf[pos++] = ' ';
    buf[pos++] = '"';
    for (i = 0u; arg[i]; ++i) {
        char c = arg[i];
        if (c == '"') {
            if (pos + 2u >= cap) {
                return 0;
            }
            buf[pos++] = '\\';
            buf[pos++] = '"';
            continue;
        }
        if (pos + 1u >= cap) {
            return 0;
        }
        buf[pos++] = c;
    }
    if (pos + 2u >= cap) {
        return 0;
    }
    buf[pos++] = '"';
    buf[pos] = '\0';
    return 1;
}

static void dsu_dir_from_argv0(char* out, size_t cap, const char* argv0)
{
    const char* slash;
    size_t len;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!argv0 || !argv0[0]) {
        return;
    }
    strncpy(out, argv0, cap - 1u);
    out[cap - 1u] = '\0';
    dsu_normalize_path(out);
    slash = strrchr(out, '/');
    if (!slash) {
        out[0] = '\0';
        return;
    }
    len = (size_t)(slash - out);
    if (len + 1u >= cap) {
        out[0] = '\0';
        return;
    }
    out[len] = '\0';
}

static int dsu_resolve_setup_script(char* out, size_t cap, const char* argv0)
{
    const char* env = getenv("DOM_SETUP_SCRIPT");
    char dir[512];
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (env && env[0]) {
        strncpy(out, env, cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }
    dsu_dir_from_argv0(dir, sizeof(dir), argv0);
    if (dir[0]) {
        snprintf(out, cap, "%s/setup_cli.py", dir);
        if (dsu_file_exists(out)) {
            return 1;
        }
    }
    strncpy(out, "tools/setup/setup_cli.py", cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int dsu_run_setup_cli(int argc, char** argv, const char* ui_mode)
{
    char script_path[512];
    char cmd[4096];
    int i;
    int rc;
    if (!dsu_resolve_setup_script(script_path, sizeof(script_path), argv[0])) {
        fprintf(stderr, "setup_tui: unable to resolve setup cli script\\n");
        return 1;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        return 1;
    }
    if (!dsu_append_quoted(cmd, sizeof(cmd), script_path)) {
        return 1;
    }
    for (i = 1; i < argc; ++i) {
        if (!dsu_append_quoted(cmd, sizeof(cmd), argv[i])) {
            return 1;
        }
    }
    if (ui_mode && ui_mode[0]) {
        if (!dsu_append_quoted(cmd, sizeof(cmd), "--ui-mode")) {
            return 1;
        }
        if (!dsu_append_quoted(cmd, sizeof(cmd), ui_mode)) {
            return 1;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        return 1;
    }
    return rc;
}

int dsu_tui_run(int argc, char** argv)
{
    return dsu_run_setup_cli(argc, argv, "tui");
}

int main(int argc, char** argv)
{
    return dsu_tui_run(argc, argv);
}

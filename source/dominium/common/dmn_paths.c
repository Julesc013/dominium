#include "dominium/paths.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#include <direct.h>
#else
#include <unistd.h>
#endif

#if defined(__APPLE__)
#include <mach-o/dyld.h>
#endif

static char g_home[512];
static int g_home_init = 0;
static char g_install_root[512];
static int g_install_init = 0;

static void dmn_dirname_inplace(char* path)
{
    size_t len;
    if (!path) return;
    len = strlen(path);
    while (len > 0) {
        char c = path[len - 1];
        if (c == '\\' || c == '/') {
            path[len - 1] = '\0';
            break;
        }
        path[len - 1] = '\0';
        --len;
    }
}

static int dmn_get_executable_dir(char* out, size_t cap)
{
    if (!out || cap == 0) return 0;
#if defined(_WIN32)
    DWORD len = GetModuleFileNameA(NULL, out, (DWORD)cap);
    if (len == 0 || len >= cap) {
        return 0;
    }
    dmn_dirname_inplace(out);
    return 1;
#elif defined(__APPLE__)
    uint32_t size = (uint32_t)cap;
    if (_NSGetExecutablePath(out, &size) != 0) {
        return 0;
    }
    dmn_dirname_inplace(out);
    return 1;
#else
    ssize_t len = readlink("/proc/self/exe", out, cap - 1);
    if (len <= 0 || (size_t)len >= cap) {
        return 0;
    }
    out[len] = '\0';
    dmn_dirname_inplace(out);
    return 1;
#endif
}

const char* dmn_get_install_root(void)
{
    if (!g_install_init) {
        if (!dmn_get_executable_dir(g_install_root, sizeof(g_install_root))) {
            g_install_root[0] = '\0';
        }
        g_install_init = 1;
    }
    return g_install_root[0] ? g_install_root : NULL;
}

const char* dmn_get_dominium_home(void)
{
    const char* env = NULL;
    const char* home = NULL;

    if (g_home_init) {
        return g_home[0] ? g_home : NULL;
    }
    g_home_init = 1;
    g_home[0] = '\0';

    env = getenv("DOMINIUM_HOME");
    if (env && env[0]) {
        strncpy(g_home, env, sizeof(g_home) - 1);
        return g_home;
    }

#if defined(_WIN32)
    env = getenv("LOCALAPPDATA");
    if (!env || !env[0]) {
        env = getenv("APPDATA");
    }
    if (env && env[0]) {
        snprintf(g_home, sizeof(g_home), "%s\\Dominium", env);
        return g_home;
    }
#elif defined(__APPLE__)
    home = getenv("HOME");
    if (home && home[0]) {
        snprintf(g_home, sizeof(g_home), "%s/Library/Application Support/Dominium", home);
        return g_home;
    }
#else
    env = getenv("XDG_DATA_HOME");
    if (env && env[0]) {
        snprintf(g_home, sizeof(g_home), "%s/dominium", env);
        return g_home;
    }
    home = getenv("HOME");
    if (home && home[0]) {
        snprintf(g_home, sizeof(g_home), "%s/.local/share/dominium", home);
        return g_home;
    }
#endif

    home = dmn_get_install_root();
    if (home && home[0]) {
#if defined(_WIN32)
        snprintf(g_home, sizeof(g_home), "%s\\dominium_home", home);
#else
        snprintf(g_home, sizeof(g_home), "%s/dominium_home", home);
#endif
    }
    return g_home[0] ? g_home : NULL;
}

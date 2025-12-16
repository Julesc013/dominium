/*
FILE: source/domino/system/plat/sdl1/sdl1_sys.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl1/sdl1_sys
RESPONSIBILITY: Implements `sdl1_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "sdl1_sys.h"

#include <SDL.h>

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <direct.h>
#include <windows.h>
#else
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

static dsys_caps g_sdl1_caps = { "sdl1", 1u, true, true, false, false };
sdl1_global_t    g_sdl1;

static dsys_result sdl1_init(void);
static void        sdl1_shutdown(void);
static dsys_caps   sdl1_get_caps(void);

static uint64_t sdl1_time_now_us(void);
static void     sdl1_sleep_ms(uint32_t ms);

static dsys_window* sdl1_window_create(const dsys_window_desc* desc);
static void         sdl1_window_destroy(dsys_window* win);
static void         sdl1_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         sdl1_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         sdl1_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        sdl1_window_get_native_handle(dsys_window* win);

static bool sdl1_poll_event(dsys_event* ev);

static bool   sdl1_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  sdl1_file_open(const char* path, const char* mode);
static size_t sdl1_file_read(void* fh, void* buf, size_t size);
static size_t sdl1_file_write(void* fh, const void* buf, size_t size);
static int    sdl1_file_seek(void* fh, long offset, int origin);
static long   sdl1_file_tell(void* fh);
static int    sdl1_file_close(void* fh);

static dsys_dir_iter* sdl1_dir_open(const char* path);
static bool           sdl1_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           sdl1_dir_close(dsys_dir_iter* it);

static dsys_process* sdl1_process_spawn(const dsys_process_desc* desc);
static int           sdl1_process_wait(dsys_process* p);
static void          sdl1_process_destroy(dsys_process* p);

static Uint32 sdl1_compute_flags(dsys_window_mode mode);
static bool   sdl1_apply_video_mode(int32_t w, int32_t h, dsys_window_mode mode);
static void   sdl1_sync_window(void);
static bool   sdl1_copy_path(const char* src, char* buf, size_t buf_size);
static bool   sdl1_copy_cwd(char* buf, size_t buf_size);
static void   sdl1_join_path(char* dst, size_t cap, const char* base, const char* leaf);
static bool   sdl1_dirname(const char* path, char* out, size_t cap);
static bool   sdl1_resolve_exe_dir(char* buf, size_t buf_size);
static bool   sdl1_pick_home(char* buf, size_t buf_size);
#if !defined(_WIN32)
static bool   sdl1_pick_xdg(const char* env_name, const char* fallback_suffix, char* buf, size_t buf_size);
#endif
#if defined(_WIN32)
static bool   sdl1_build_cmdline(const dsys_process_desc* desc, char* out, size_t cap);
#endif

static const dsys_backend_vtable g_sdl1_vtable = {
    sdl1_init,
    sdl1_shutdown,
    sdl1_get_caps,
    sdl1_time_now_us,
    sdl1_sleep_ms,
    sdl1_window_create,
    sdl1_window_destroy,
    sdl1_window_set_mode,
    sdl1_window_set_size,
    sdl1_window_get_size,
    sdl1_window_get_native_handle,
    sdl1_poll_event,
    sdl1_get_path,
    sdl1_file_open,
    sdl1_file_read,
    sdl1_file_write,
    sdl1_file_seek,
    sdl1_file_tell,
    sdl1_file_close,
    sdl1_dir_open,
    sdl1_dir_next,
    sdl1_dir_close,
    sdl1_process_spawn,
    sdl1_process_wait,
    sdl1_process_destroy
};

static Uint32 sdl1_compute_flags(dsys_window_mode mode)
{
    Uint32 flags;
    flags = SDL_SWSURFACE | SDL_RESIZABLE;
    if (mode == DWIN_MODE_FULLSCREEN) {
        flags |= SDL_FULLSCREEN;
    } else if (mode == DWIN_MODE_BORDERLESS) {
        flags |= SDL_NOFRAME;
    }
    return flags;
}

static bool sdl1_apply_video_mode(int32_t w, int32_t h, dsys_window_mode mode)
{
    SDL_Surface* surface;
    Uint32       flags;
    int          bpp;

    if (w <= 0) {
        w = 800;
    }
    if (h <= 0) {
        h = 600;
    }

    flags = sdl1_compute_flags(mode);
    bpp = 32;
    surface = SDL_SetVideoMode(w, h, bpp, flags);
    if (!surface) {
        return false;
    }

    g_sdl1.screen = surface;
    g_sdl1.width = surface->w;
    g_sdl1.height = surface->h;
    g_sdl1.fullscreen = (flags & SDL_FULLSCREEN) ? 1 : 0;
    sdl1_sync_window();
    return true;
}

static void sdl1_sync_window(void)
{
    if (g_sdl1.main_window) {
        g_sdl1.main_window->surface = g_sdl1.screen;
        g_sdl1.main_window->width = g_sdl1.width;
        g_sdl1.main_window->height = g_sdl1.height;
    }
}

static bool sdl1_copy_path(const char* src, char* buf, size_t buf_size)
{
    size_t len;
    if (!src || !buf || buf_size == 0u) {
        return false;
    }
    len = strlen(src);
    if (len >= buf_size) {
        len = buf_size - 1u;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return true;
}

static bool sdl1_copy_cwd(char* buf, size_t buf_size)
{
    char cwd[PATH_MAX];

    if (!buf || buf_size == 0u) {
        return false;
    }

#if defined(_WIN32)
    if (_getcwd(cwd, sizeof(cwd)) != NULL) {
        return sdl1_copy_path(cwd, buf, buf_size);
    }
#else
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        return sdl1_copy_path(cwd, buf, buf_size);
    }
#endif
    buf[0] = '\0';
    return false;
}

static void sdl1_join_path(char* dst, size_t cap, const char* base, const char* leaf)
{
    size_t i;
    size_t j;

    if (!dst || cap == 0u) {
        return;
    }

    dst[0] = '\0';
    i = 0u;
    if (base) {
        while (base[i] != '\0' && i + 1u < cap) {
            dst[i] = base[i];
            ++i;
        }
        if (i > 0u && dst[i - 1u] != '/' && dst[i - 1u] != '\\' && i + 1u < cap) {
            dst[i] = '/';
            ++i;
        }
    }

    j = 0u;
    if (leaf) {
        while (leaf[j] != '\0' && i + 1u < cap) {
            dst[i] = leaf[j];
            ++i;
            ++j;
        }
    }
    dst[i] = '\0';
}

static bool sdl1_dirname(const char* path, char* out, size_t cap)
{
    size_t len;

    if (!path || !out || cap == 0u) {
        return false;
    }

    len = strlen(path);
    while (len > 0u && (path[len - 1u] == '/' || path[len - 1u] == '\\')) {
        len -= 1u;
    }
    while (len > 0u) {
        char c;
        c = path[len - 1u];
        if (c == '/' || c == '\\') {
            break;
        }
        len -= 1u;
    }
    if (len == 0u) {
        if (cap > 1u) {
            out[0] = '.';
            out[1] = '\0';
            return true;
        }
        return false;
    }
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(out, path, len);
    out[len] = '\0';
    return true;
}

static bool sdl1_resolve_exe_dir(char* buf, size_t buf_size)
{
    if (!buf || buf_size == 0u) {
        return false;
    }

#if defined(_WIN32)
    {
        char  tmp[MAX_PATH];
        DWORD n;

        n = GetModuleFileNameA(NULL, tmp, (DWORD)sizeof(tmp));
        if (n > 0u && n < (DWORD)sizeof(tmp)) {
            if (sdl1_dirname(tmp, buf, buf_size)) {
                return true;
            }
        }
    }
    return sdl1_copy_cwd(buf, buf_size);
#else
    {
        char    tmp[PATH_MAX];
        ssize_t n;

        n = readlink("/proc/self/exe", tmp, sizeof(tmp) - 1u);
        if (n > 0 && (size_t)n < sizeof(tmp)) {
            tmp[n] = '\0';
            if (sdl1_dirname(tmp, buf, buf_size)) {
                return true;
            }
        }
    }
    if (sdl1_copy_cwd(buf, buf_size)) {
        return true;
    }
    buf[0] = '\0';
    return false;
#endif
}

static bool sdl1_pick_home(char* buf, size_t buf_size)
{
    const char* env_home;

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_home = getenv("HOME");
#if defined(_WIN32)
    if ((!env_home || env_home[0] == '\0')) {
        env_home = getenv("USERPROFILE");
    }
    if ((!env_home || env_home[0] == '\0')) {
        const char* drive;
        const char* path;
        drive = getenv("HOMEDRIVE");
        path = getenv("HOMEPATH");
        if (drive && path) {
            char tmp[260];
            size_t len_drive;
            size_t len_path;
            len_drive = strlen(drive);
            len_path = strlen(path);
            if (len_drive + len_path < sizeof(tmp)) {
                memcpy(tmp, drive, len_drive);
                memcpy(tmp + len_drive, path, len_path);
                tmp[len_drive + len_path] = '\0';
                return sdl1_copy_path(tmp, buf, buf_size);
            }
        }
    }
#endif

    if (env_home && env_home[0] != '\0') {
        return sdl1_copy_path(env_home, buf, buf_size);
    }

    return sdl1_copy_cwd(buf, buf_size);
}

#if !defined(_WIN32)
static bool sdl1_pick_xdg(const char* env_name, const char* fallback_suffix, char* buf, size_t buf_size)
{
    const char* env_val;
    char        home[PATH_MAX];
    char        tmp[PATH_MAX];

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_val = getenv(env_name);
    if (env_val && env_val[0] != '\0') {
        return sdl1_copy_path(env_val, buf, buf_size);
    }

    if (!sdl1_pick_home(home, sizeof(home))) {
        return false;
    }

    sdl1_join_path(tmp, sizeof(tmp), home, fallback_suffix);
    return sdl1_copy_path(tmp, buf, buf_size);
}
#endif

#if defined(_WIN32)
static bool sdl1_build_cmdline(const dsys_process_desc* desc, char* out, size_t cap)
{
    const char* const* argp;
    const char*        local_args[2];
    size_t             pos;

    if (!desc || !desc->exe || !out || cap == 0u) {
        return false;
    }

    pos = 0u;
    if (desc->argv) {
        argp = desc->argv;
    } else {
        local_args[0] = desc->exe;
        local_args[1] = NULL;
        argp = local_args;
    }

    out[0] = '\0';
    while (*argp) {
        const char* arg;
        size_t      i;
        int         need_quotes;

        arg = *argp;
        need_quotes = 0;
        for (i = 0u; arg[i] != '\0'; ++i) {
            if (arg[i] == ' ' || arg[i] == '\t') {
                need_quotes = 1;
                break;
            }
        }

        if (need_quotes) {
            if (pos + 1u >= cap) {
                return false;
            }
            out[pos++] = '"';
        }

        i = 0u;
        while (arg[i] != '\0' && pos + 1u < cap) {
            out[pos++] = arg[i];
            ++i;
        }

        if (need_quotes) {
            if (pos + 1u >= cap) {
                return false;
            }
            out[pos++] = '"';
        }

        ++argp;
        if (*argp) {
            if (pos + 1u >= cap) {
                return false;
            }
            out[pos++] = ' ';
        }
    }

    if (pos >= cap) {
        out[cap - 1u] = '\0';
        return false;
    }
    out[pos] = '\0';
    return true;
}
#endif

static dsys_result sdl1_init(void)
{
    if (g_sdl1.initialized) {
        return DSYS_OK;
    }

    memset(&g_sdl1, 0, sizeof(g_sdl1));
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_NOPARACHUTE) != 0) {
        return DSYS_ERR;
    }

    g_sdl1.initialized = 1;
    return DSYS_OK;
}

static void sdl1_shutdown(void)
{
    if (!g_sdl1.initialized) {
        return;
    }

    if (g_sdl1.main_window) {
        free(g_sdl1.main_window);
        g_sdl1.main_window = NULL;
    }
    g_sdl1.screen = NULL;
    g_sdl1.width = 0;
    g_sdl1.height = 0;
    g_sdl1.fullscreen = 0;
    g_sdl1.initialized = 0;
    SDL_Quit();
}

static dsys_caps sdl1_get_caps(void)
{
    return g_sdl1_caps;
}

static uint64_t sdl1_time_now_us(void)
{
    uint32_t ms;
    ms = SDL_GetTicks();
    return ((uint64_t)ms) * 1000u;
}

static void sdl1_sleep_ms(uint32_t ms)
{
    SDL_Delay(ms);
}

static dsys_window* sdl1_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local_desc;
    dsys_window*     win;

    if (g_sdl1.main_window) {
        return NULL;
    }

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 800;
        local_desc.height = 600;
        local_desc.mode = DWIN_MODE_WINDOWED;
    }

    if (!sdl1_apply_video_mode(local_desc.width, local_desc.height, local_desc.mode)) {
        return NULL;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }

    win->surface = g_sdl1.screen;
    win->width = g_sdl1.width;
    win->height = g_sdl1.height;
    win->mode = local_desc.mode;
    g_sdl1.main_window = win;
    SDL_WM_SetCaption("Domino", NULL);
    return win;
}

static void sdl1_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win == g_sdl1.main_window) {
        g_sdl1.main_window = NULL;
    }
    free(win);
}

static void sdl1_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    if (sdl1_apply_video_mode(win->width, win->height, mode)) {
        win->mode = mode;
    }
}

static void sdl1_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    if (sdl1_apply_video_mode(w, h, win->mode)) {
        /* size updated inside sdl1_apply_video_mode */
    }
}

static void sdl1_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        return;
    }

    if (g_sdl1.screen) {
        win->width = g_sdl1.screen->w;
        win->height = g_sdl1.screen->h;
    }
    if (w) {
        *w = win->width;
    }
    if (h) {
        *h = win->height;
    }
}

static void* sdl1_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)win->surface;
}

static bool sdl1_poll_event(dsys_event* ev)
{
    SDL_Event sdl_ev;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    while (SDL_PollEvent(&sdl_ev)) {
        if (ev) {
            memset(ev, 0, sizeof(*ev));
        }

        switch (sdl_ev.type) {
        case SDL_QUIT:
            if (ev) {
                ev->type = DSYS_EVENT_QUIT;
            }
            return true;

        case SDL_VIDEORESIZE:
            if (g_sdl1.main_window) {
                if (sdl1_apply_video_mode(sdl_ev.resize.w,
                                          sdl_ev.resize.h,
                                          g_sdl1.main_window->mode)) {
                    sdl1_sync_window();
                }
            }
            if (ev) {
                ev->type = DSYS_EVENT_WINDOW_RESIZED;
                ev->payload.window.width = g_sdl1.width;
                ev->payload.window.height = g_sdl1.height;
            }
            return true;

        case SDL_KEYDOWN:
        case SDL_KEYUP:
            if (ev) {
                ev->type = (sdl_ev.type == SDL_KEYDOWN) ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
                ev->payload.key.key = (int32_t)sdl_ev.key.keysym.sym;
                ev->payload.key.repeat = false;
            }
            return true;

        case SDL_MOUSEMOTION:
            if (ev) {
                ev->type = DSYS_EVENT_MOUSE_MOVE;
                ev->payload.mouse_move.x = sdl_ev.motion.x;
                ev->payload.mouse_move.y = sdl_ev.motion.y;
                ev->payload.mouse_move.dx = sdl_ev.motion.xrel;
                ev->payload.mouse_move.dy = sdl_ev.motion.yrel;
            }
            return true;

        case SDL_MOUSEBUTTONDOWN:
        case SDL_MOUSEBUTTONUP:
            if (sdl_ev.button.button == 4 || sdl_ev.button.button == 5 ||
                sdl_ev.button.button == 6 || sdl_ev.button.button == 7) {
                if (ev) {
                    ev->type = DSYS_EVENT_MOUSE_WHEEL;
                    ev->payload.mouse_wheel.delta_x = 0;
                    ev->payload.mouse_wheel.delta_y = 0;
                    if (sdl_ev.button.button == 4) {
                        ev->payload.mouse_wheel.delta_y = 1;
                    } else if (sdl_ev.button.button == 5) {
                        ev->payload.mouse_wheel.delta_y = -1;
                    } else if (sdl_ev.button.button == 6) {
                        ev->payload.mouse_wheel.delta_x = -1;
                    } else if (sdl_ev.button.button == 7) {
                        ev->payload.mouse_wheel.delta_x = 1;
                    }
                }
            } else if (ev) {
                ev->type = DSYS_EVENT_MOUSE_BUTTON;
                ev->payload.mouse_button.button = sdl_ev.button.button;
                ev->payload.mouse_button.pressed = (sdl_ev.type == SDL_MOUSEBUTTONDOWN) ? true : false;
                ev->payload.mouse_button.clicks = 1;
            }
            return true;

        default:
            break;
        }
    }

    return false;
}

static bool sdl1_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    char base[PATH_MAX];
    char joined[PATH_MAX];
    bool ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';
    joined[0] = '\0';
    ok = false;

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        ok = sdl1_resolve_exe_dir(buf, buf_size);
        break;

    case DSYS_PATH_USER_DATA:
    case DSYS_PATH_USER_CONFIG:
    case DSYS_PATH_USER_CACHE:
        {
            const char* leaf;
            leaf = NULL;
            if (kind == DSYS_PATH_USER_DATA) {
                leaf = "dominium/data";
            } else if (kind == DSYS_PATH_USER_CONFIG) {
                leaf = "dominium/config";
            } else {
                leaf = "dominium/cache";
            }

#if defined(_WIN32)
            {
                const char* env_val;
                env_val = NULL;
                if (kind == DSYS_PATH_USER_DATA || kind == DSYS_PATH_USER_CACHE) {
                    env_val = getenv("LOCALAPPDATA");
                    if (!env_val || env_val[0] == '\0') {
                        env_val = getenv("APPDATA");
                    }
                } else {
                    env_val = getenv("APPDATA");
                }
                if (env_val && env_val[0] != '\0') {
                    ok = sdl1_copy_path(env_val, base, sizeof(base));
                } else {
                    ok = sdl1_pick_home(base, sizeof(base));
                }
            }
#else
            if (kind == DSYS_PATH_USER_DATA) {
                ok = sdl1_pick_xdg("XDG_DATA_HOME", ".local/share", base, sizeof(base));
            } else if (kind == DSYS_PATH_USER_CONFIG) {
                ok = sdl1_pick_xdg("XDG_CONFIG_HOME", ".config", base, sizeof(base));
            } else {
                ok = sdl1_pick_xdg("XDG_CACHE_HOME", ".cache", base, sizeof(base));
            }
#endif
            if (ok) {
                sdl1_join_path(joined, sizeof(joined), base, leaf);
                ok = sdl1_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_TEMP:
        {
#if defined(_WIN32)
            DWORD n;
            n = GetTempPathA((DWORD)sizeof(joined), joined);
            if (n > 0u && n < (DWORD)sizeof(joined)) {
                ok = sdl1_copy_path(joined, buf, buf_size);
            }
#else
            const char* tmpdir;
            tmpdir = getenv("TMPDIR");
            if (tmpdir && tmpdir[0] != '\0') {
                ok = sdl1_copy_path(tmpdir, buf, buf_size);
            } else {
                ok = sdl1_copy_path("/tmp", buf, buf_size);
            }
#endif
            if (!ok) {
                ok = sdl1_copy_cwd(buf, buf_size);
            }
        }
        break;

    default:
        ok = false;
        break;
    }

    if (!ok && buf) {
        buf[0] = '\0';
    }
    return ok;
}

static void* sdl1_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t sdl1_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t sdl1_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int sdl1_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long sdl1_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int sdl1_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* sdl1_dir_open(const char* path)
{
    dsys_dir_iter* it;
    const char*    base;

    base = (path && path[0] != '\0') ? path : ".";
    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        return NULL;
    }

#if defined(_WIN32)
    {
        char   pattern[MAX_PATH];
        size_t len;

        len = strlen(base);
        if (len + 3u >= sizeof(pattern)) {
            free(it);
            return NULL;
        }
        memcpy(pattern, base, len);
        if (len == 0u || (base[len - 1u] != '/' && base[len - 1u] != '\\')) {
            pattern[len] = '\\';
            len += 1u;
        }
        pattern[len] = '*';
        pattern[len + 1u] = '\0';

        it->handle = FindFirstFileA(pattern, &it->data);
        if (it->handle == INVALID_HANDLE_VALUE) {
            free(it);
            return NULL;
        }
        it->first_pending = 1;
    }
#else
    it->dir = opendir(base);
    if (!it->dir) {
        free(it);
        return NULL;
    }
#endif

    return it;
}

static bool sdl1_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    if (!it || !out) {
        return false;
    }

#if defined(_WIN32)
    {
        WIN32_FIND_DATAA* data;
        data = &it->data;

        for (;;) {
            if (it->first_pending) {
                it->first_pending = 0;
            } else {
                if (!FindNextFileA(it->handle, data)) {
                    return false;
                }
            }

            if (!strcmp(data->cFileName, ".") || !strcmp(data->cFileName, "..")) {
                continue;
            }

            strncpy(out->name, data->cFileName, sizeof(out->name) - 1u);
            out->name[sizeof(out->name) - 1u] = '\0';
            out->is_dir = (data->dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) ? true : false;
            return true;
        }
    }
#else
    {
        struct dirent* ent;
        for (;;) {
            ent = readdir(it->dir);
            if (!ent) {
                return false;
            }
            if (ent->d_name[0] == '.' &&
                (ent->d_name[1] == '\0' ||
                 (ent->d_name[1] == '.' && ent->d_name[2] == '\0'))) {
                continue;
            }

            strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
            out->name[sizeof(out->name) - 1u] = '\0';
            out->is_dir = false;
#if defined(DT_DIR)
            if (ent->d_type == DT_DIR) {
                out->is_dir = true;
            } else if (ent->d_type == DT_UNKNOWN) {
                out->is_dir = false;
            }
#endif
            return true;
        }
    }
#endif
}

static void sdl1_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }

#if defined(_WIN32)
    if (it->handle != INVALID_HANDLE_VALUE) {
        FindClose(it->handle);
    }
#else
    if (it->dir) {
        closedir(it->dir);
    }
#endif
    free(it);
}

static dsys_process* sdl1_process_spawn(const dsys_process_desc* desc)
{
    if (!desc || !desc->exe) {
        return NULL;
    }

#if defined(_WIN32)
    {
        STARTUPINFOA        si;
        PROCESS_INFORMATION pi;
        char                cmdline[1024];
        dsys_process*       p;

        if (!sdl1_build_cmdline(desc, cmdline, sizeof(cmdline))) {
            return NULL;
        }

        memset(&si, 0, sizeof(si));
        si.cb = sizeof(si);
        memset(&pi, 0, sizeof(pi));

        if (!CreateProcessA(NULL,
                            cmdline,
                            NULL,
                            NULL,
                            FALSE,
                            0,
                            NULL,
                            NULL,
                            &si,
                            &pi)) {
            return NULL;
        }

        p = (dsys_process*)malloc(sizeof(dsys_process));
        if (!p) {
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
            return NULL;
        }
        p->process = pi.hProcess;
        p->thread = pi.hThread;
        return p;
    }
#else
    {
        pid_t        pid;
        dsys_process* p;

        pid = fork();
        if (pid < 0) {
            return NULL;
        } else if (pid == 0) {
            if (desc->argv) {
                execvp(desc->exe, (char* const*)desc->argv);
            } else {
                char* const argv_local[2];
                argv_local[0] = (char*)desc->exe;
                argv_local[1] = NULL;
                execvp(desc->exe, argv_local);
            }
            _exit(127);
        }

        p = (dsys_process*)malloc(sizeof(dsys_process));
        if (!p) {
            waitpid(pid, (int*)0, 0);
            return NULL;
        }
        p->pid = pid;
        return p;
    }
#endif
}

static int sdl1_process_wait(dsys_process* p)
{
    if (!p) {
        return -1;
    }

#if defined(_WIN32)
    {
        DWORD result;
        DWORD exit_code;

        result = WaitForSingleObject(p->process, INFINITE);
        if (result != WAIT_OBJECT_0) {
            return -1;
        }
        if (!GetExitCodeProcess(p->process, &exit_code)) {
            return -1;
        }
        return (int)exit_code;
    }
#else
    {
        int status;
        status = 0;
        if (waitpid(p->pid, &status, 0) < 0) {
            return -1;
        }
        return status;
    }
#endif
}

static void sdl1_process_destroy(dsys_process* p)
{
    if (!p) {
        return;
    }

#if defined(_WIN32)
    if (p->thread) {
        CloseHandle(p->thread);
    }
    if (p->process) {
        CloseHandle(p->process);
    }
#endif
    free(p);
}

const dsys_backend_vtable* dsys_sdl1_get_vtable(void)
{
    return &g_sdl1_vtable;
}


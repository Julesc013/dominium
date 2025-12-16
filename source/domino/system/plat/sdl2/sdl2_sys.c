/*
FILE: source/domino/system/plat/sdl2/sdl2_sys.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl2/sdl2_sys
RESPONSIBILITY: Implements `sdl2_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "sdl2_sys.h"

#include <SDL.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t     g_perf_freq = 0u;
static dsys_caps    g_sdl2_caps = { "sdl2", 1u, true, true, false, false };
static dsys_window* g_window_list = NULL;

static dsys_result sdl2_init(void);
static void        sdl2_shutdown(void);
static dsys_caps   sdl2_get_caps(void);

static uint64_t sdl2_time_now_us(void);
static void     sdl2_sleep_ms(uint32_t ms);

static dsys_window* sdl2_window_create(const dsys_window_desc* desc);
static void         sdl2_window_destroy(dsys_window* win);
static void         sdl2_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         sdl2_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         sdl2_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        sdl2_window_get_native_handle(dsys_window* win);

static bool sdl2_poll_event(dsys_event* ev);

static bool   sdl2_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  sdl2_file_open(const char* path, const char* mode);
static size_t sdl2_file_read(void* fh, void* buf, size_t size);
static size_t sdl2_file_write(void* fh, const void* buf, size_t size);
static int    sdl2_file_seek(void* fh, long offset, int origin);
static long   sdl2_file_tell(void* fh);
static int    sdl2_file_close(void* fh);

static dsys_dir_iter* sdl2_dir_open(const char* path);
static bool           sdl2_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           sdl2_dir_close(dsys_dir_iter* it);

static dsys_process* sdl2_process_spawn(const dsys_process_desc* desc);
static int           sdl2_process_wait(dsys_process* p);
static void          sdl2_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_sdl2_vtable = {
    sdl2_init,
    sdl2_shutdown,
    sdl2_get_caps,
    sdl2_time_now_us,
    sdl2_sleep_ms,
    sdl2_window_create,
    sdl2_window_destroy,
    sdl2_window_set_mode,
    sdl2_window_set_size,
    sdl2_window_get_size,
    sdl2_window_get_native_handle,
    sdl2_poll_event,
    sdl2_get_path,
    sdl2_file_open,
    sdl2_file_read,
    sdl2_file_write,
    sdl2_file_seek,
    sdl2_file_tell,
    sdl2_file_close,
    sdl2_dir_open,
    sdl2_dir_next,
    sdl2_dir_close,
    sdl2_process_spawn,
    sdl2_process_wait,
    sdl2_process_destroy
};

static dsys_window* sdl2_find_window(uint32_t id)
{
    dsys_window* cur;
    cur = g_window_list;
    while (cur) {
        if (cur->window_id == id) {
            return cur;
        }
        cur = cur->next;
    }
    return NULL;
}

static void sdl2_add_window(dsys_window* win)
{
    if (!win) {
        return;
    }
    win->next = g_window_list;
    g_window_list = win;
}

static void sdl2_remove_window(dsys_window* win)
{
    dsys_window* prev;
    dsys_window* cur;

    prev = NULL;
    cur = g_window_list;
    while (cur) {
        if (cur == win) {
            if (prev) {
                prev->next = cur->next;
            } else {
                g_window_list = cur->next;
            }
            return;
        }
        prev = cur;
        cur = cur->next;
    }
}

static void sdl2_update_window_size(uint32_t id, int32_t w, int32_t h)
{
    dsys_window* win;
    win = sdl2_find_window(id);
    if (win) {
        win->width = w;
        win->height = h;
    }
}

static bool sdl2_translate_event(const SDL_Event* sdl_ev, dsys_event* ev)
{
    if (!sdl_ev || !ev) {
        return false;
    }

    switch (sdl_ev->type) {
    case SDL_QUIT:
        ev->type = DSYS_EVENT_QUIT;
        return true;

    case SDL_WINDOWEVENT:
        if (sdl_ev->window.event == SDL_WINDOWEVENT_RESIZED ||
            sdl_ev->window.event == SDL_WINDOWEVENT_SIZE_CHANGED) {
            ev->type = DSYS_EVENT_WINDOW_RESIZED;
            ev->payload.window.width = sdl_ev->window.data1;
            ev->payload.window.height = sdl_ev->window.data2;
            sdl2_update_window_size(sdl_ev->window.windowID,
                                    sdl_ev->window.data1,
                                    sdl_ev->window.data2);
            return true;
        }
        break;

    case SDL_KEYDOWN:
    case SDL_KEYUP:
        ev->type = (sdl_ev->type == SDL_KEYDOWN) ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
        ev->payload.key.key = (int32_t)sdl_ev->key.keysym.sym;
        ev->payload.key.repeat = sdl_ev->key.repeat ? true : false;
        return true;

    case SDL_TEXTINPUT:
        ev->type = DSYS_EVENT_TEXT_INPUT;
        memset(ev->payload.text.text, 0, sizeof(ev->payload.text.text));
        strncpy(ev->payload.text.text, sdl_ev->text.text, sizeof(ev->payload.text.text) - 1u);
        return true;

    case SDL_MOUSEMOTION:
        ev->type = DSYS_EVENT_MOUSE_MOVE;
        ev->payload.mouse_move.x = sdl_ev->motion.x;
        ev->payload.mouse_move.y = sdl_ev->motion.y;
        ev->payload.mouse_move.dx = sdl_ev->motion.xrel;
        ev->payload.mouse_move.dy = sdl_ev->motion.yrel;
        return true;

    case SDL_MOUSEBUTTONDOWN:
    case SDL_MOUSEBUTTONUP:
        ev->type = DSYS_EVENT_MOUSE_BUTTON;
        ev->payload.mouse_button.button = sdl_ev->button.button;
        ev->payload.mouse_button.pressed = (sdl_ev->type == SDL_MOUSEBUTTONDOWN) ? true : false;
        ev->payload.mouse_button.clicks = sdl_ev->button.clicks;
        return true;

    case SDL_MOUSEWHEEL:
        ev->type = DSYS_EVENT_MOUSE_WHEEL;
        ev->payload.mouse_wheel.delta_x = sdl_ev->wheel.x;
        ev->payload.mouse_wheel.delta_y = sdl_ev->wheel.y;
        if (sdl_ev->wheel.direction == SDL_MOUSEWHEEL_FLIPPED) {
            ev->payload.mouse_wheel.delta_x = -ev->payload.mouse_wheel.delta_x;
            ev->payload.mouse_wheel.delta_y = -ev->payload.mouse_wheel.delta_y;
        }
        return true;

    default:
        break;
    }

    return false;
}

static dsys_result sdl2_init(void)
{
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS | SDL_INIT_TIMER) != 0) {
        return DSYS_ERR;
    }
    g_perf_freq = SDL_GetPerformanceFrequency();
    g_sdl2_caps.has_high_res_timer = g_perf_freq != 0u;
    return DSYS_OK;
}

static void sdl2_shutdown(void)
{
    dsys_window* cur;
    dsys_window* next;

    cur = g_window_list;
    while (cur) {
        next = cur->next;
        if (cur->native_handle) {
            SDL_DestroyWindow((SDL_Window*)cur->native_handle);
        }
        free(cur);
        cur = next;
    }
    g_window_list = NULL;
    SDL_Quit();
}

static dsys_caps sdl2_get_caps(void)
{
    return g_sdl2_caps;
}

static uint64_t sdl2_time_now_us(void)
{
    uint64_t counter;
    if (g_perf_freq != 0u) {
        counter = SDL_GetPerformanceCounter();
        return (counter * 1000000u) / g_perf_freq;
    }
    return (uint64_t)SDL_GetTicks() * 1000u;
}

static void sdl2_sleep_ms(uint32_t ms)
{
    SDL_Delay(ms);
}

static dsys_window* sdl2_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local_desc;
    dsys_window*     win;
    SDL_Window*      sdl_win;
    uint32_t         flags;
    int              x;
    int              y;
    int              w;
    int              h;

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 800;
        local_desc.height = 600;
        local_desc.mode = DWIN_MODE_WINDOWED;
    }

    flags = SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE;
    if (desc) {
        x = local_desc.x;
        y = local_desc.y;
    } else {
        x = SDL_WINDOWPOS_UNDEFINED;
        y = SDL_WINDOWPOS_UNDEFINED;
    }
    w = local_desc.width != 0 ? local_desc.width : 800;
    h = local_desc.height != 0 ? local_desc.height : 600;

    sdl_win = SDL_CreateWindow("Domino",
                               x,
                               y,
                               w,
                               h,
                               flags);
    if (!sdl_win) {
        return NULL;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        SDL_DestroyWindow(sdl_win);
        return NULL;
    }

    win->native_handle = sdl_win;
    win->width = w;
    win->height = h;
    win->mode = local_desc.mode;
    win->window_id = SDL_GetWindowID(sdl_win);
    win->next = NULL;
    sdl2_add_window(win);
    sdl2_window_set_mode(win, local_desc.mode);
    return win;
}

static void sdl2_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    sdl2_remove_window(win);
    if (win->native_handle) {
        SDL_DestroyWindow((SDL_Window*)win->native_handle);
    }
    free(win);
}

static void sdl2_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    uint32_t flags;
    if (!win || !win->native_handle) {
        return;
    }

    flags = 0u;
    switch (mode) {
    case DWIN_MODE_FULLSCREEN:
        flags = SDL_WINDOW_FULLSCREEN;
        break;
    case DWIN_MODE_BORDERLESS:
        flags = SDL_WINDOW_FULLSCREEN_DESKTOP;
        break;
    case DWIN_MODE_WINDOWED:
    default:
        flags = 0u;
        break;
    }

    SDL_SetWindowFullscreen((SDL_Window*)win->native_handle, flags);
    win->mode = mode;
}

static void sdl2_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win || !win->native_handle) {
        return;
    }
    SDL_SetWindowSize((SDL_Window*)win->native_handle, w, h);
    win->width = w;
    win->height = h;
}

static void sdl2_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    int32_t rw;
    int32_t rh;

    if (!win || !win->native_handle) {
        return;
    }

    rw = win->width;
    rh = win->height;
    SDL_GetWindowSize((SDL_Window*)win->native_handle, &rw, &rh);
    win->width = rw;
    win->height = rh;

    if (w) {
        *w = rw;
    }
    if (h) {
        *h = rh;
    }
}

static void* sdl2_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return win->native_handle;
}

static bool sdl2_poll_event(dsys_event* ev)
{
    SDL_Event sdl_ev;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    while (SDL_PollEvent(&sdl_ev)) {
        if (sdl2_translate_event(&sdl_ev, ev)) {
            return true;
        }
    }

    return false;
}

static bool sdl2_copy_path(const char* src, char* buf, size_t buf_size)
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

static bool sdl2_copy_cwd(char* buf, size_t buf_size)
{
    char cwd[260];

#if defined(_WIN32)
    if (_getcwd(cwd, sizeof(cwd)) != NULL) {
        return sdl2_copy_path(cwd, buf, buf_size);
    }
#elif defined(_POSIX_VERSION)
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        return sdl2_copy_path(cwd, buf, buf_size);
    }
#endif
    (void)buf;
    (void)buf_size;
    return false;
}

static bool sdl2_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    char*       path;
    const char* env_fallback;
    bool        ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_fallback = NULL;
    path = NULL;
    ok = false;

    if (kind == DSYS_PATH_APP_ROOT) {
        path = SDL_GetBasePath();
    } else if (kind == DSYS_PATH_USER_DATA ||
               kind == DSYS_PATH_USER_CONFIG ||
               kind == DSYS_PATH_USER_CACHE) {
        path = SDL_GetPrefPath("dominium", "dominium");
    } else if (kind == DSYS_PATH_TEMP) {
        env_fallback = "TMP";
        path = SDL_GetPrefPath("dominium", "dominium");
    }

    if (path) {
        ok = sdl2_copy_path(path, buf, buf_size);
        SDL_free(path);
    }

    if (!ok && env_fallback) {
        const char* env_val;
        env_val = getenv(env_fallback);
        if (env_val && env_val[0] != '\0') {
            ok = sdl2_copy_path(env_val, buf, buf_size);
        }
    }

    if (!ok) {
        ok = sdl2_copy_cwd(buf, buf_size);
    }

    if (!ok && buf && buf_size > 0u) {
        buf[0] = '\0';
    }
    return ok;
}

static void* sdl2_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t sdl2_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t sdl2_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int sdl2_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long sdl2_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int sdl2_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* sdl2_dir_open(const char* path)
{
    dsys_dir_iter* it;

    if (!path) {
        return NULL;
    }

#if defined(_WIN32)
    {
        size_t len;

        it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
        if (!it) {
            return NULL;
        }
        len = strlen(path);
        if (len + 3u >= sizeof(it->pattern)) {
            free(it);
            return NULL;
        }
        memcpy(it->pattern, path, len);
        if (len == 0u || (path[len - 1u] != '/' && path[len - 1u] != '\\')) {
            it->pattern[len] = '\\';
            len += 1u;
        }
        it->pattern[len] = '*';
        it->pattern[len + 1u] = '\0';
        it->handle = _findfirst(it->pattern, &it->data);
        if (it->handle == -1) {
            free(it);
            return NULL;
        }
        it->first_pending = 1;
        return it;
    }
#else
    {
        DIR* dir;
        size_t len;

        dir = opendir(path);
        if (!dir) {
            return NULL;
        }
        it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
        if (!it) {
            closedir(dir);
            return NULL;
        }
        it->dir = dir;
        len = strlen(path);
        if (len >= sizeof(it->base)) {
            len = sizeof(it->base) - 1u;
        }
        memcpy(it->base, path, len);
        it->base[len] = '\0';
        return it;
    }
#endif
}

static bool sdl2_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    if (!it || !out) {
        return false;
    }

#if defined(_WIN32)
    {
        int res;

        if (it->first_pending) {
            it->first_pending = 0;
            res = 0;
        } else {
            res = _findnext(it->handle, &it->data);
        }
        if (res != 0) {
            return false;
        }

        strncpy(out->name, it->data.name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = (it->data.attrib & _A_SUBDIR) != 0 ? true : false;
        return true;
    }
#else
    {
        struct dirent* ent;
        struct stat    st;
        char           full_path[260];
        size_t         base_len;
        size_t         name_len;

        ent = readdir(it->dir);
        if (!ent) {
            return false;
        }

        strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';

        out->is_dir = false;
        base_len = strlen(it->base);
        name_len = strlen(out->name);
        if (base_len + name_len + 2u < sizeof(full_path)) {
            memcpy(full_path, it->base, base_len);
            if (base_len > 0u && full_path[base_len - 1u] != '/') {
                full_path[base_len] = '/';
                base_len += 1u;
            }
            memcpy(full_path + base_len, out->name, name_len);
            full_path[base_len + name_len] = '\0';
            if (stat(full_path, &st) == 0 && S_ISDIR(st.st_mode)) {
                out->is_dir = true;
            }
        }
        return true;
    }
#endif
}

static void sdl2_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }

#if defined(_WIN32)
    if (it->handle != -1) {
        _findclose(it->handle);
    }
#else
    if (it->dir) {
        closedir(it->dir);
    }
#endif
    free(it);
}

static dsys_process* sdl2_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int sdl2_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void sdl2_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_sdl2_get_vtable(void)
{
    return &g_sdl2_vtable;
}

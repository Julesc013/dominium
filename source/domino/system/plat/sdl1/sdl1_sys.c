#include "sdl1_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static dsys_caps    g_sdl1_caps = { "sdl1", 1u, true, true, false, false };
static sdl1_global_t g_sdl1;
static dsys_window*  g_sdl1_window = NULL;

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
    return true;
}

static void sdl1_sync_window(void)
{
    if (g_sdl1_window) {
        g_sdl1_window->surface = g_sdl1.screen;
        g_sdl1_window->width = g_sdl1.width;
        g_sdl1_window->height = g_sdl1.height;
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
    char cwd[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

#if defined(_WIN32)
    if (_getcwd(cwd, sizeof(cwd)) != NULL) {
        return sdl1_copy_path(cwd, buf, buf_size);
    }
#elif defined(_POSIX_VERSION)
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        return sdl1_copy_path(cwd, buf, buf_size);
    }
#else
    (void)cwd;
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
        if (i > 0u && dst[i - 1u] != '/' && i + 1u < cap) {
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

static bool sdl1_pick_home(char* buf, size_t buf_size)
{
    const char* env_home;
#if defined(_WIN32)
    const char* drive;
    const char* path;
#endif

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_home = getenv("HOME");
#if defined(_WIN32)
    if ((!env_home || env_home[0] == '\0')) {
        env_home = getenv("USERPROFILE");
    }
    if ((!env_home || env_home[0] == '\0')) {
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

static dsys_result sdl1_init(void)
{
    if (g_sdl1.initialized) {
        return DSYS_OK;
    }

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_NOPARACHUTE) != 0) {
        return DSYS_ERR;
    }

    g_sdl1.screen = NULL;
    g_sdl1.width = 0;
    g_sdl1.height = 0;
    g_sdl1.fullscreen = 0;
    g_sdl1.initialized = 1;
    g_sdl1_window = NULL;
    return DSYS_OK;
}

static void sdl1_shutdown(void)
{
    if (!g_sdl1.initialized) {
        return;
    }
    if (g_sdl1_window) {
        free(g_sdl1_window);
        g_sdl1_window = NULL;
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
    int32_t          w;
    int32_t          h;

    if (g_sdl1_window) {
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

    w = local_desc.width;
    h = local_desc.height;
    if (!sdl1_apply_video_mode(w, h, local_desc.mode)) {
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
    g_sdl1_window = win;
    return win;
}

static void sdl1_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win == g_sdl1_window) {
        g_sdl1_window = NULL;
    }
    free(win);
}

static void sdl1_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    int32_t w;
    int32_t h;

    if (!win) {
        return;
    }

    w = win->width;
    h = win->height;
    if (sdl1_apply_video_mode(w, h, mode)) {
        win->mode = mode;
        sdl1_sync_window();
    }
}

static void sdl1_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    if (sdl1_apply_video_mode(w, h, win->mode)) {
        sdl1_sync_window();
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
        switch (sdl_ev.type) {
        case SDL_QUIT:
            if (ev) {
                ev->type = DSYS_EVENT_QUIT;
            }
            return true;

        case SDL_VIDEORESIZE:
            if (sdl1_apply_video_mode(sdl_ev.resize.w,
                                      sdl_ev.resize.h,
                                      g_sdl1_window ? g_sdl1_window->mode : DWIN_MODE_WINDOWED)) {
                sdl1_sync_window();
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
    char base[260];
    char joined[260];
    const char* env_val;

    if (!buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';
    joined[0] = '\0';

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        if (sdl1_copy_cwd(buf, buf_size)) {
            return true;
        }
        break;

    case DSYS_PATH_USER_DATA:
        if (sdl1_pick_home(base, sizeof(base))) {
            sdl1_join_path(joined, sizeof(joined), base, "dominium/data");
            return sdl1_copy_path(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_USER_CONFIG:
        if (sdl1_pick_home(base, sizeof(base))) {
            sdl1_join_path(joined, sizeof(joined), base, "dominium/config");
            return sdl1_copy_path(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_USER_CACHE:
        if (sdl1_pick_home(base, sizeof(base))) {
            sdl1_join_path(joined, sizeof(joined), base, "dominium/cache");
            return sdl1_copy_path(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_TEMP:
        env_val = getenv("TMPDIR");
        if (!env_val || env_val[0] == '\0') {
            env_val = getenv("TMP");
        }
        if (!env_val || env_val[0] == '\0') {
            env_val = getenv("TEMP");
        }
        if (env_val && env_val[0] != '\0') {
            return sdl1_copy_path(env_val, buf, buf_size);
        }
        if (sdl1_copy_cwd(buf, buf_size)) {
            return true;
        }
        break;

    default:
        break;
    }

    buf[0] = '\0';
    return false;
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
        DIR*   dir;
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

static bool sdl1_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
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

static void sdl1_dir_close(dsys_dir_iter* it)
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

static dsys_process* sdl1_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int sdl1_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void sdl1_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_sdl1_get_vtable(void)
{
    return &g_sdl1_vtable;
}

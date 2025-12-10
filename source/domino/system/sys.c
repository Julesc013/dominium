#define DOMINO_SYS_INTERNAL 1
#include "domino/sys.h"
#include "dsys_internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#if defined(_WIN32)
#include <windows.h>
#endif

static const dsys_caps g_null_caps = {
    "null",
    0u,
    false,
    false,
    false,
    false
};

static const dsys_backend_vtable g_null_vtable;
static const dsys_backend_vtable* g_dsys = NULL;
static const char* g_requested_backend = NULL;

static int dsys_str_ieq(const char* a, const char* b)
{
    if (!a || !b) return 0;
    while (*a && *b) {
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b)) {
            return 0;
        }
        ++a; ++b;
    }
    return *a == '\0' && *b == '\0';
}

static const char* dsys_compiled_backend_name(void)
{
#if defined(DSYS_BACKEND_CPM80)
    return "cpm80";
#elif defined(DSYS_BACKEND_CPM86)
    return "cpm86";
#elif defined(DSYS_BACKEND_DOS16)
    return "dos16";
#elif defined(DSYS_BACKEND_DOS32)
    return "dos32";
#elif defined(DSYS_BACKEND_WIN16)
    return "win16";
#elif defined(DSYS_BACKEND_POSIX)
    return "posix_headless";
#elif defined(DSYS_BACKEND_COCOA)
    return "cocoa";
#elif defined(DSYS_BACKEND_CARBON)
    return "carbon";
#elif defined(DSYS_BACKEND_WAYLAND)
    return "wayland";
#elif defined(DSYS_BACKEND_X11)
    return "x11";
#elif defined(DSYS_BACKEND_SDL1)
    return "sdl1";
#elif defined(DSYS_BACKEND_SDL2)
    return "sdl2";
#elif defined(DSYS_BACKEND_WIN32)
    return "win32";
#elif defined(DSYS_BACKEND_NULL)
    return "null";
#else
    return "null";
#endif
}

int dom_sys_select_backend(const char* name)
{
    const char* compiled;
    if (!name || !name[0]) {
        return -1;
    }
    compiled = dsys_compiled_backend_name();
    if (dsys_str_ieq(name, compiled)) {
        g_requested_backend = compiled;
        return 0;
    }
    /* Reject unsupported backend names; only one backend is compiled in this pass. */
    return -1;
}

static const dsys_backend_vtable* dsys_active_backend(void)
{
    if (!g_dsys) {
        g_dsys = &g_null_vtable;
    }
    return g_dsys;
}

static dsys_result null_init(void)
{
    return DSYS_OK;
}

static void null_shutdown(void)
{
}

static dsys_caps null_get_caps(void)
{
    return g_null_caps;
}

static uint64_t null_time_now_us(void)
{
    uint64_t ticks;
    ticks = (uint64_t)clock();
    if (CLOCKS_PER_SEC != 0) {
        ticks = (ticks * 1000000u) / (uint64_t)CLOCKS_PER_SEC;
    }
    return ticks;
}

static void null_sleep_ms(uint32_t ms)
{
#if defined(_WIN32)
    Sleep(ms);
#elif defined(_POSIX_VERSION)
    {
        struct timespec ts;
        ts.tv_sec = (time_t)(ms / 1000u);
        ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
        nanosleep(&ts, (struct timespec*)0);
    }
#else
    {
        clock_t start;
        clock_t target;
        start = clock();
        target = start + (clock_t)((ms * CLOCKS_PER_SEC) / 1000u);
        while (clock() < target) {
            /* busy wait */
        }
    }
#endif
}

static dsys_window* null_window_create(const dsys_window_desc* desc)
{
    dsys_window* win;
    dsys_window_desc local_desc;

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 0;
        local_desc.height = 0;
        local_desc.mode = DWIN_MODE_WINDOWED;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->width = local_desc.width;
    win->height = local_desc.height;
    win->mode = local_desc.mode;
    return win;
}

static void null_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    free(win);
}

static void null_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
}

static void null_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

static void null_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        return;
    }
    if (w) {
        *w = win->width;
    }
    if (h) {
        *h = win->height;
    }
}

static void* null_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool null_poll_event(dsys_event* out)
{
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static bool null_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* env_name;
    const char* src;
    size_t      len;
    char        cwd[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_name = NULL;
    switch (kind) {
    case DSYS_PATH_APP_ROOT:    env_name = "DSYS_PATH_APP_ROOT"; break;
    case DSYS_PATH_USER_DATA:   env_name = "DSYS_PATH_USER_DATA"; break;
    case DSYS_PATH_USER_CONFIG: env_name = "DSYS_PATH_USER_CONFIG"; break;
    case DSYS_PATH_USER_CACHE:  env_name = "DSYS_PATH_USER_CACHE"; break;
    case DSYS_PATH_TEMP:        env_name = "DSYS_PATH_TEMP"; break;
    default: break;
    }

    src = NULL;
    if (env_name) {
        src = getenv(env_name);
        if (src && src[0] == '\0') {
            src = NULL;
        }
    }

    if (!src) {
#if defined(_WIN32)
        if (_getcwd(cwd, sizeof(cwd)) != NULL) {
            src = cwd;
        }
#else
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            src = cwd;
        }
#endif
    }

    if (!src) {
        src = ".";
    }

    len = strlen(src);
    if (len >= buf_size) {
        len = buf_size - 1u;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return true;
}

static void* null_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t null_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t null_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int null_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long null_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int null_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* null_dir_open(const char* path)
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

static bool null_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
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

static void null_dir_close(dsys_dir_iter* it)
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

static dsys_process* null_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int null_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void null_process_destroy(dsys_process* p)
{
    (void)p;
}

static const dsys_backend_vtable g_null_vtable = {
    null_init,
    null_shutdown,
    null_get_caps,
    null_time_now_us,
    null_sleep_ms,
    null_window_create,
    null_window_destroy,
    null_window_set_mode,
    null_window_set_size,
    null_window_get_size,
    null_window_get_native_handle,
    null_poll_event,
    null_get_path,
    null_file_open,
    null_file_read,
    null_file_write,
    null_file_seek,
    null_file_tell,
    null_file_close,
    null_dir_open,
    null_dir_next,
    null_dir_close,
    null_process_spawn,
    null_process_wait,
    null_process_destroy
};

dsys_result dsys_init(void)
{
    dsys_result result;
#if defined(DSYS_BACKEND_CPM80)
    {
        extern const dsys_backend_vtable* dsys_cpm80_get_vtable(void);
        g_dsys = dsys_cpm80_get_vtable();
    }
#elif defined(DSYS_BACKEND_CPM86)
    {
        extern const dsys_backend_vtable* dsys_cpm86_get_vtable(void);
        g_dsys = dsys_cpm86_get_vtable();
    }
#elif defined(DSYS_BACKEND_DOS16)
    {
        extern const dsys_backend_vtable* dsys_dos16_get_vtable(void);
        g_dsys = dsys_dos16_get_vtable();
    }
#elif defined(DSYS_BACKEND_DOS32)
    {
        extern const dsys_backend_vtable* dsys_dos32_get_vtable(void);
        g_dsys = dsys_dos32_get_vtable();
    }
#elif defined(DSYS_BACKEND_WIN16)
    {
        extern const dsys_backend_vtable* dsys_win16_get_vtable(void);
        g_dsys = dsys_win16_get_vtable();
    }
#elif defined(DSYS_BACKEND_POSIX)
    {
        extern const dsys_backend_vtable* dsys_posix_get_vtable(void);
        g_dsys = dsys_posix_get_vtable();
    }
#elif defined(DSYS_BACKEND_COCOA)
    {
        extern const dsys_backend_vtable* dsys_cocoa_get_vtable(void);
        g_dsys = dsys_cocoa_get_vtable();
    }
#elif defined(DSYS_BACKEND_CARBON)
    {
        extern const dsys_backend_vtable* dsys_carbon_get_vtable(void);
        g_dsys = dsys_carbon_get_vtable();
    }
#elif defined(DSYS_BACKEND_WAYLAND)
    {
        extern const dsys_backend_vtable* dsys_wayland_get_vtable(void);
        g_dsys = dsys_wayland_get_vtable();
    }
#elif defined(DSYS_BACKEND_X11)
    {
        extern const dsys_backend_vtable* dsys_x11_get_vtable(void);
        g_dsys = dsys_x11_get_vtable();
    }
#elif defined(DSYS_BACKEND_SDL1)
    {
        extern const dsys_backend_vtable* dsys_sdl1_get_vtable(void);
        g_dsys = dsys_sdl1_get_vtable();
    }
#elif defined(DSYS_BACKEND_SDL2)
    {
        extern const dsys_backend_vtable* dsys_sdl2_get_vtable(void);
        g_dsys = dsys_sdl2_get_vtable();
    }
#elif defined(DSYS_BACKEND_WIN32)
    g_dsys = &g_null_vtable;
#elif defined(DSYS_BACKEND_NULL)
    g_dsys = &g_null_vtable;
#else
    g_dsys = &g_null_vtable;
#endif

    if (!g_dsys || !g_dsys->init) {
        g_dsys = &g_null_vtable;
    }
    result = g_dsys->init();
    if (result != DSYS_OK && g_dsys != &g_null_vtable) {
        g_dsys = &g_null_vtable;
    }
    return result;
}

void dsys_shutdown(void)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->shutdown) {
        backend->shutdown();
    }
    g_dsys = NULL;
}

dsys_caps dsys_get_caps(void)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->get_caps) {
        return backend->get_caps();
    }
    return g_null_caps;
}

uint64_t dsys_time_now_us(void)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    return backend->time_now_us ? backend->time_now_us() : 0u;
}

void dsys_sleep_ms(uint32_t ms)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->sleep_ms) {
        backend->sleep_ms(ms);
    }
}

dsys_window* dsys_window_create(const dsys_window_desc* desc)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->window_create) {
        return backend->window_create(desc);
    }
    return NULL;
}

void dsys_window_destroy(dsys_window* win)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->window_destroy) {
        backend->window_destroy(win);
    }
}

void dsys_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->window_set_mode) {
        backend->window_set_mode(win, mode);
    }
}

void dsys_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->window_set_size) {
        backend->window_set_size(win, w, h);
    }
}

void dsys_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->window_get_size) {
        backend->window_get_size(win, w, h);
    }
}

void* dsys_window_get_native_handle(dsys_window* win)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->window_get_native_handle) {
        return backend->window_get_native_handle(win);
    }
    return NULL;
}

int dsys_window_should_close(dsys_window* win)
{
    /* No backend-driven close signal in this ABI yet; treat null as closed. */
    return win ? 0 : 1;
}

void dsys_window_present(dsys_window* win)
{
    (void)win;
    /* Rendering is handled by higher layers; nothing to do here. */
}

bool dsys_poll_event(dsys_event* out)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->poll_event) {
        return backend->poll_event(out);
    }
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

bool dsys_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->get_path) {
        return backend->get_path(kind, buf, buf_size);
    }
    return false;
}

void* dsys_file_open(const char* path, const char* mode)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->file_open) {
        return backend->file_open(path, mode);
    }
    return NULL;
}

size_t dsys_file_read(void* fh, void* buf, size_t size)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->file_read) {
        return backend->file_read(fh, buf, size);
    }
    return 0u;
}

size_t dsys_file_write(void* fh, const void* buf, size_t size)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->file_write) {
        return backend->file_write(fh, buf, size);
    }
    return 0u;
}

int dsys_file_seek(void* fh, long offset, int origin)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->file_seek) {
        return backend->file_seek(fh, offset, origin);
    }
    return -1;
}

long dsys_file_tell(void* fh)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->file_tell) {
        return backend->file_tell(fh);
    }
    return -1L;
}

int dsys_file_close(void* fh)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->file_close) {
        return backend->file_close(fh);
    }
    return -1;
}

dsys_dir_iter* dsys_dir_open(const char* path)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->dir_open) {
        return backend->dir_open(path);
    }
    return NULL;
}

bool dsys_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->dir_next) {
        return backend->dir_next(it, out);
    }
    return false;
}

void dsys_dir_close(dsys_dir_iter* it)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->dir_close) {
        backend->dir_close(it);
    }
}

dsys_process* dsys_process_spawn(const dsys_process_desc* desc)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->process_spawn) {
        return backend->process_spawn(desc);
    }
    return NULL;
}

int dsys_process_wait(dsys_process* p)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->process_wait) {
        return backend->process_wait(p);
    }
    return -1;
}

void dsys_process_destroy(dsys_process* p)
{
    const dsys_backend_vtable* backend;
    backend = dsys_active_backend();
    if (backend->process_destroy) {
        backend->process_destroy(p);
    }
}

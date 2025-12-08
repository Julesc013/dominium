#include "domino/sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
#include <direct.h>
#include <io.h>
#elif defined(_POSIX_VERSION)
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

struct dsys_window_t {
    int32_t          x;
    int32_t          y;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

struct dsys_process_t {
    int placeholder;
};

struct dsys_dir_iter_t {
#if defined(_WIN32)
    intptr_t          handle;
    struct _finddata_t data;
    int               first_pending;
    char              pattern[260];
#else
    DIR*  dir;
    char  base[260];
#endif
};

static const dsys_caps g_dsys_caps = {
    "stub",
    0u,
    false,
    false,
    false,
    false
};

dsys_result dsys_init(void)
{
    return DSYS_OK;
}

void dsys_shutdown(void)
{
}

dsys_caps dsys_get_caps(void)
{
    return g_dsys_caps;
}

uint64_t dsys_time_now_us(void)
{
    uint64_t ticks;
    ticks = (uint64_t)clock();
    if (CLOCKS_PER_SEC != 0) {
        ticks = (ticks * 1000000u) / (uint64_t)CLOCKS_PER_SEC;
    }
    return ticks;
}

void dsys_sleep_ms(uint32_t ms)
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

dsys_window* dsys_window_create(const dsys_window_desc* desc)
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
    win->x = local_desc.x;
    win->y = local_desc.y;
    win->width = local_desc.width;
    win->height = local_desc.height;
    win->mode = local_desc.mode;
    return win;
}

void dsys_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    free(win);
}

void dsys_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
}

void dsys_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

void dsys_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

void* dsys_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

bool dsys_poll_event(dsys_event* out)
{
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

bool dsys_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
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
    case DSYS_PATH_APP_ROOT:   env_name = "DSYS_PATH_APP_ROOT"; break;
    case DSYS_PATH_USER_DATA:  env_name = "DSYS_PATH_USER_DATA"; break;
    case DSYS_PATH_USER_CONFIG: env_name = "DSYS_PATH_USER_CONFIG"; break;
    case DSYS_PATH_USER_CACHE: env_name = "DSYS_PATH_USER_CACHE"; break;
    case DSYS_PATH_TEMP:       env_name = "DSYS_PATH_TEMP"; break;
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

void* dsys_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

size_t dsys_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

size_t dsys_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

int dsys_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

long dsys_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

int dsys_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

dsys_dir_iter* dsys_dir_open(const char* path)
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

bool dsys_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
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

void dsys_dir_close(dsys_dir_iter* it)
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

dsys_process* dsys_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

int dsys_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

void dsys_process_destroy(dsys_process* p)
{
    (void)p;
}

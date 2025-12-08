#include "cocoa_sys.h"

#include <errno.h>
#include <dirent.h>
#include <mach-o/dyld.h>
#include <mach/mach_time.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

static dsys_caps    g_cocoa_caps = { "cocoa", 1u, true, true, false, true };
static uint64_t     g_timebase_numer = 0u;
static uint64_t     g_timebase_denom = 0u;

static dsys_result cocoa_init(void);
static void        cocoa_shutdown(void);
static dsys_caps   cocoa_get_caps(void);

static uint64_t cocoa_time_now_us(void);
static void     cocoa_sleep_ms(uint32_t ms);

static dsys_window* cocoa_window_create(const dsys_window_desc* desc);
static void         cocoa_window_destroy(dsys_window* win);
static void         cocoa_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         cocoa_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         cocoa_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        cocoa_window_get_native_handle(dsys_window* win);

static bool cocoa_poll_event(dsys_event* ev);

static bool   cocoa_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  cocoa_file_open(const char* path, const char* mode);
static size_t cocoa_file_read(void* fh, void* buf, size_t size);
static size_t cocoa_file_write(void* fh, const void* buf, size_t size);
static int    cocoa_file_seek(void* fh, long offset, int origin);
static long   cocoa_file_tell(void* fh);
static int    cocoa_file_close(void* fh);

static dsys_dir_iter* cocoa_dir_open(const char* path);
static bool           cocoa_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           cocoa_dir_close(dsys_dir_iter* it);

static dsys_process* cocoa_process_spawn(const dsys_process_desc* desc);
static int           cocoa_process_wait(dsys_process* p);
static void          cocoa_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_cocoa_vtable = {
    cocoa_init,
    cocoa_shutdown,
    cocoa_get_caps,
    cocoa_time_now_us,
    cocoa_sleep_ms,
    cocoa_window_create,
    cocoa_window_destroy,
    cocoa_window_set_mode,
    cocoa_window_set_size,
    cocoa_window_get_size,
    cocoa_window_get_native_handle,
    cocoa_poll_event,
    cocoa_get_path,
    cocoa_file_open,
    cocoa_file_read,
    cocoa_file_write,
    cocoa_file_seek,
    cocoa_file_tell,
    cocoa_file_close,
    cocoa_dir_open,
    cocoa_dir_next,
    cocoa_dir_close,
    cocoa_process_spawn,
    cocoa_process_wait,
    cocoa_process_destroy
};

static bool cocoa_copy_path(const char* src, char* buf, size_t buf_size)
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

static void cocoa_join_path(char* dst, size_t cap, const char* base, const char* leaf)
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

static bool cocoa_dirname(const char* path, char* out, size_t cap)
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

static bool cocoa_get_home(char* buf, size_t buf_size)
{
    const char* home_env;

    home_env = getenv("HOME");
    if (home_env && home_env[0] != '\0') {
        return cocoa_copy_path(home_env, buf, buf_size);
    }

#if defined(_POSIX_VERSION)
    {
        struct passwd* pw;
        pw = getpwuid(getuid());
        if (pw && pw->pw_dir) {
            return cocoa_copy_path(pw->pw_dir, buf, buf_size);
        }
    }
#endif

    return false;
}

static bool cocoa_resolve_exe_dir(char* buf, size_t buf_size)
{
    uint32_t size;
    char     stack_buf[PATH_MAX];
    char*    tmp;
    char*    resolved;
    bool     ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    size = (uint32_t)sizeof(stack_buf);
    tmp = stack_buf;
    if (_NSGetExecutablePath(tmp, &size) != 0) {
        tmp = (char*)malloc((size_t)size);
        if (!tmp) {
            return false;
        }
        if (_NSGetExecutablePath(tmp, &size) != 0) {
            free(tmp);
            return false;
        }
    }

    resolved = realpath(tmp, (char*)0);
    if (tmp != stack_buf) {
        free(tmp);
    }
    if (!resolved) {
        return false;
    }

    ok = cocoa_dirname(resolved, buf, buf_size);
    free(resolved);
    return ok;
}

static bool cocoa_pick_library_dir(char* buf, size_t buf_size, const char* subpath)
{
    char home[260];
    char joined[260];

    if (!buf || buf_size == 0u || !subpath) {
        return false;
    }

    if (!cocoa_get_home(home, sizeof(home))) {
        return false;
    }

    cocoa_join_path(joined, sizeof(joined), home, subpath);
    return cocoa_copy_path(joined, buf, buf_size);
}

static dsys_result cocoa_init(void)
{
    mach_timebase_info_data_t info;

    if (cocoa_app_init() != DSYS_OK) {
        return DSYS_ERR;
    }

    if (mach_timebase_info(&info) == KERN_SUCCESS && info.denom != 0u) {
        g_timebase_numer = (uint64_t)info.numer;
        g_timebase_denom = (uint64_t)info.denom;
        g_cocoa_caps.has_high_res_timer = true;
    } else {
        g_cocoa_caps.has_high_res_timer = false;
    }

    return DSYS_OK;
}

static void cocoa_shutdown(void)
{
    cocoa_app_shutdown();
}

static dsys_caps cocoa_get_caps(void)
{
    return g_cocoa_caps;
}

static uint64_t cocoa_time_now_us(void)
{
#if defined(CLOCK_MONOTONIC)
    {
        struct timespec ts;
        if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
            return ((uint64_t)ts.tv_sec * 1000000u) + ((uint64_t)ts.tv_nsec / 1000u);
        }
    }
#endif
    {
        uint64_t ticks;
        uint64_t nanos;

        ticks = mach_absolute_time();
        if (g_timebase_denom == 0u) {
            mach_timebase_info_data_t info;
            if (mach_timebase_info(&info) == KERN_SUCCESS && info.denom != 0u) {
                g_timebase_numer = (uint64_t)info.numer;
                g_timebase_denom = (uint64_t)info.denom;
            } else {
                g_timebase_numer = 1u;
                g_timebase_denom = 1u;
            }
        }

        nanos = (ticks * g_timebase_numer) / g_timebase_denom;
        return nanos / 1000u;
    }
}

static void cocoa_sleep_ms(uint32_t ms)
{
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR) {
        /* retry interrupted sleep */
    }
}

static dsys_window* cocoa_window_create(const dsys_window_desc* desc)
{
    return cocoa_win_create(desc);
}

static void cocoa_window_destroy(dsys_window* win)
{
    cocoa_win_destroy(win);
}

static void cocoa_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    cocoa_win_set_mode(win, mode);
}

static void cocoa_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    cocoa_win_set_size(win, w, h);
}

static void cocoa_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    cocoa_win_get_size(win, w, h);
}

static void* cocoa_window_get_native_handle(dsys_window* win)
{
    return cocoa_win_get_native_handle(win);
}

static bool cocoa_poll_event(dsys_event* ev)
{
    return cocoa_win_poll_event(ev);
}

static bool cocoa_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    bool ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';
    ok = false;

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        ok = cocoa_resolve_exe_dir(buf, buf_size);
        break;

    case DSYS_PATH_USER_DATA:
        ok = cocoa_pick_library_dir(buf, buf_size, "Library/Application Support/dominium/data");
        break;

    case DSYS_PATH_USER_CONFIG:
        ok = cocoa_pick_library_dir(buf, buf_size, "Library/Application Support/dominium/config");
        break;

    case DSYS_PATH_USER_CACHE:
        ok = cocoa_pick_library_dir(buf, buf_size, "Library/Caches/dominium");
        break;

    case DSYS_PATH_TEMP:
        {
            char tmp[PATH_MAX];
#ifdef _CS_DARWIN_USER_TEMP_DIR
            size_t len;
            len = (size_t)confstr(_CS_DARWIN_USER_TEMP_DIR, tmp, sizeof(tmp));
            if (len > 0u && len < sizeof(tmp)) {
                ok = cocoa_copy_path(tmp, buf, buf_size);
                break;
            }
#endif
            if (!ok) {
                const char* env_tmp;
                env_tmp = getenv("TMPDIR");
                if (env_tmp && env_tmp[0] != '\0') {
                    ok = cocoa_copy_path(env_tmp, buf, buf_size);
                } else {
                    ok = cocoa_copy_path("/tmp", buf, buf_size);
                }
            }
        }
        break;

    default:
        break;
    }

    if (!ok && buf_size > 0u) {
        buf[0] = '\0';
    }
    return ok;
}

static void* cocoa_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t cocoa_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t cocoa_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int cocoa_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long cocoa_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int cocoa_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* cocoa_dir_open(const char* path)
{
    dsys_dir_iter* it;
    DIR*           dir;
    size_t         len;

    if (!path) {
        return NULL;
    }

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

static bool cocoa_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;

    if (!it || !out) {
        return false;
    }

    for (;;) {
        ent = readdir(it->dir);
        if (!ent) {
            return false;
        }
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) {
            continue;
        }
        strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = false;

#if defined(DT_DIR)
        if (ent->d_type == DT_DIR) {
            out->is_dir = true;
        } else if (ent->d_type == DT_UNKNOWN) {
            struct stat st;
            char        full[260];
            size_t      base_len;
            size_t      name_len;
            base_len = strlen(it->base);
            name_len = strlen(out->name);
            if (base_len + name_len + 2u < sizeof(full)) {
                memcpy(full, it->base, base_len);
                if (base_len > 0u && full[base_len - 1u] != '/') {
                    full[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full + base_len, out->name, name_len);
                full[base_len + name_len] = '\0';
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    out->is_dir = true;
                }
            }
        }
#else
        {
            struct stat st;
            char        full[260];
            size_t      base_len;
            size_t      name_len;
            base_len = strlen(it->base);
            name_len = strlen(out->name);
            if (base_len + name_len + 2u < sizeof(full)) {
                memcpy(full, it->base, base_len);
                if (base_len > 0u && full[base_len - 1u] != '/') {
                    full[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full + base_len, out->name, name_len);
                full[base_len + name_len] = '\0';
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    out->is_dir = true;
                }
            }
        }
#endif
        return true;
    }
}

static void cocoa_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* cocoa_process_spawn(const dsys_process_desc* desc)
{
    pid_t        pid;
    dsys_process* proc;

    if (!desc || !desc->exe) {
        return NULL;
    }

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

    proc = (dsys_process*)malloc(sizeof(dsys_process));
    if (!proc) {
        waitpid(pid, (int*)0, 0);
        return NULL;
    }
    proc->pid = pid;
    return proc;
}

static int cocoa_process_wait(dsys_process* p)
{
    int   status;
    pid_t res;

    if (!p) {
        return -1;
    }

    res = waitpid(p->pid, &status, 0);
    if (res < 0) {
        return -1;
    }
    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return -1;
}

static void cocoa_process_destroy(dsys_process* p)
{
    if (!p) {
        return;
    }
    free(p);
}

const dsys_backend_vtable* dsys_cocoa_get_vtable(void)
{
    return &g_cocoa_vtable;
}

#include "posix_sys.h"

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

static dsys_caps g_posix_caps = { "posix", 0u, false, false, false, false };

static dsys_result posix_init(void);
static void        posix_shutdown(void);
static dsys_caps   posix_get_caps(void);

static uint64_t posix_time_now_us(void);
static void     posix_sleep_ms(uint32_t ms);

static dsys_window* posix_window_create(const dsys_window_desc* desc);
static void         posix_window_destroy(dsys_window* win);
static void         posix_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         posix_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         posix_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        posix_window_get_native_handle(dsys_window* win);

static bool posix_poll_event(dsys_event* ev);

static bool   posix_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  posix_file_open(const char* path, const char* mode);
static size_t posix_file_read(void* fh, void* buf, size_t size);
static size_t posix_file_write(void* fh, const void* buf, size_t size);
static int    posix_file_seek(void* fh, long offset, int origin);
static long   posix_file_tell(void* fh);
static int    posix_file_close(void* fh);

static dsys_dir_iter* posix_dir_open(const char* path);
static bool           posix_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           posix_dir_close(dsys_dir_iter* it);

static dsys_process* posix_process_spawn(const dsys_process_desc* desc);
static int           posix_process_wait(dsys_process* p);
static void          posix_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_posix_vtable = {
    posix_init,
    posix_shutdown,
    posix_get_caps,
    posix_time_now_us,
    posix_sleep_ms,
    posix_window_create,
    posix_window_destroy,
    posix_window_set_mode,
    posix_window_set_size,
    posix_window_get_size,
    posix_window_get_native_handle,
    posix_poll_event,
    posix_get_path,
    posix_file_open,
    posix_file_read,
    posix_file_write,
    posix_file_seek,
    posix_file_tell,
    posix_file_close,
    posix_dir_open,
    posix_dir_next,
    posix_dir_close,
    posix_process_spawn,
    posix_process_wait,
    posix_process_destroy
};

static bool posix_copy_path(const char* src, char* buf, size_t buf_size)
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

static void posix_join_path(char* dst, size_t cap, const char* base, const char* leaf)
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

static bool posix_dirname(const char* path, char* out, size_t cap)
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

static bool posix_get_home(char* buf, size_t buf_size)
{
    const char* home_env;

    home_env = getenv("HOME");
    if (home_env && home_env[0] != '\0') {
        return posix_copy_path(home_env, buf, buf_size);
    }
#if defined(_POSIX_VERSION)
    {
        struct passwd* pw;
        pw = getpwuid(getuid());
        if (pw && pw->pw_dir) {
            return posix_copy_path(pw->pw_dir, buf, buf_size);
        }
    }
#endif
    return false;
}

static bool posix_resolve_exe_dir(char* buf, size_t buf_size)
{
    char    tmp[PATH_MAX];
    ssize_t n;

    if (!buf || buf_size == 0u) {
        return false;
    }

    n = readlink("/proc/self/exe", tmp, sizeof(tmp) - 1u);
    if (n > 0 && (size_t)n < sizeof(tmp)) {
        tmp[n] = '\0';
        if (posix_dirname(tmp, buf, buf_size)) {
            return true;
        }
    }

    if (getcwd(tmp, sizeof(tmp)) != NULL) {
        return posix_copy_path(tmp, buf, buf_size);
    }

    buf[0] = '\0';
    return false;
}

static bool posix_pick_xdg(const char* env_name,
                           const char* fallback_suffix,
                           char* buf,
                           size_t buf_size)
{
    const char* env_val;
    char        home[260];
    char        tmp[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_val = getenv(env_name);
    if (env_val && env_val[0] != '\0') {
        return posix_copy_path(env_val, buf, buf_size);
    }

    if (!posix_get_home(home, sizeof(home))) {
        return false;
    }

    posix_join_path(tmp, sizeof(tmp), home, fallback_suffix);
    return posix_copy_path(tmp, buf, buf_size);
}

static dsys_result posix_init(void)
{
#if defined(CLOCK_MONOTONIC)
    {
        struct timespec ts;
        if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
            g_posix_caps.has_high_res_timer = true;
        }
    }
#endif
    return DSYS_OK;
}

static void posix_shutdown(void)
{
}

static dsys_caps posix_get_caps(void)
{
    return g_posix_caps;
}

static uint64_t posix_time_now_us(void)
{
#if defined(CLOCK_MONOTONIC)
    {
        struct timespec ts;
        if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
            return ((uint64_t)ts.tv_sec * 1000000ULL) + ((uint64_t)ts.tv_nsec / 1000ULL);
        }
    }
#endif
    {
        struct timeval tv;
        gettimeofday(&tv, (struct timezone*)0);
        return ((uint64_t)tv.tv_sec * 1000000ULL) + (uint64_t)tv.tv_usec;
    }
}

static void posix_sleep_ms(uint32_t ms)
{
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR) {
        /* retry interrupted sleep */
    }
}

static dsys_window* posix_window_create(const dsys_window_desc* desc)
{
    (void)desc;
    return NULL;
}

static void posix_window_destroy(dsys_window* win)
{
    (void)win;
}

static void posix_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    (void)win;
    (void)mode;
}

static void posix_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    (void)win;
    (void)w;
    (void)h;
}

static void posix_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    (void)win;
    if (w) {
        *w = 0;
    }
    if (h) {
        *h = 0;
    }
}

static void* posix_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool posix_poll_event(dsys_event* ev)
{
    (void)ev;
    return false;
}

static bool posix_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    bool ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    ok = false;
    buf[0] = '\0';

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        ok = posix_resolve_exe_dir(buf, buf_size);
        break;

    case DSYS_PATH_USER_DATA:
        {
            char base[260];
            char joined[260];
            if (posix_pick_xdg("XDG_DATA_HOME", ".local/share", base, sizeof(base))) {
                posix_join_path(joined, sizeof(joined), base, "dominium");
                ok = posix_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_USER_CONFIG:
        {
            char base[260];
            char joined[260];
            if (posix_pick_xdg("XDG_CONFIG_HOME", ".config", base, sizeof(base))) {
                posix_join_path(joined, sizeof(joined), base, "dominium");
                ok = posix_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_USER_CACHE:
        {
            char base[260];
            char joined[260];
            if (posix_pick_xdg("XDG_CACHE_HOME", ".cache", base, sizeof(base))) {
                posix_join_path(joined, sizeof(joined), base, "dominium");
                ok = posix_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_TEMP:
        {
            const char* tmpdir;
            tmpdir = getenv("TMPDIR");
            if (tmpdir && tmpdir[0] != '\0') {
                ok = posix_copy_path(tmpdir, buf, buf_size);
            } else {
                ok = posix_copy_path("/tmp", buf, buf_size);
            }
        }
        break;

    default:
        break;
    }

    if (!ok) {
        buf[0] = '\0';
    }
    return ok;
}

static void* posix_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t posix_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t posix_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int posix_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long posix_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int posix_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* posix_dir_open(const char* path)
{
    dsys_dir_iter* it;

    if (!path) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        return NULL;
    }

    it->dir = opendir(path);
    if (!it->dir) {
        free(it);
        return NULL;
    }
    return it;
}

static bool posix_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
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
        }
#endif
#if defined(AT_FDCWD)
        if (!out->is_dir) {
            int         dir_fd;
            struct stat st;
            dir_fd = dirfd(it->dir);
            if (dir_fd != -1 &&
                fstatat(dir_fd, out->name, &st, 0) == 0 &&
                S_ISDIR(st.st_mode)) {
                out->is_dir = true;
            }
        }
#endif
        return true;
    }
}

static void posix_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* posix_process_spawn(const dsys_process_desc* desc)
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

static int posix_process_wait(dsys_process* p)
{
    int status;

    if (!p) {
        return -1;
    }

    status = 0;
    if (waitpid(p->pid, &status, 0) < 0) {
        return -1;
    }
    return status;
}

static void posix_process_destroy(dsys_process* p)
{
    if (!p) {
        return;
    }
    free(p);
}

const dsys_backend_vtable* dsys_posix_get_vtable(void)
{
    return &g_posix_vtable;
}

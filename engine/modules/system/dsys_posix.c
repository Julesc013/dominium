/*
FILE: source/domino/system/dsys_posix.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_posix
RESPONSIBILITY: POSIX headless DSYS backend (filesystem, time, processes stubs).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic directory order via sorted listings; time is monotonic where available.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Replace with windowed POSIX backends (X11/Wayland) behind same contract.
*/
#define DOMINO_SYS_INTERNAL 1
#include "domino/system/dsys.h"
#include "dsys_internal.h"
#include "dsys_dir_sorted.h"

#if !defined(_WIN32)
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>

static dsys_caps dsys_posix_get_caps(void)
{
    dsys_caps caps;
    caps.name = "posix_headless";
    caps.ui_modes = 0u;
    caps.has_windows = false;
    caps.has_mouse = false;
    caps.has_gamepad = false;
    caps.has_high_res_timer = true;
    return caps;
}

static dsys_result dsys_posix_init(void)
{
    return DSYS_OK;
}

static void dsys_posix_shutdown(void)
{
}

static uint64_t dsys_posix_time_now_us(void)
{
#if defined(CLOCK_MONOTONIC)
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return (uint64_t)ts.tv_sec * 1000000ull + (uint64_t)(ts.tv_nsec / 1000ull);
    }
#endif
    {
        struct timeval tv;
        gettimeofday(&tv, NULL);
        return (uint64_t)tv.tv_sec * 1000000ull + (uint64_t)tv.tv_usec;
    }
}

static void dsys_posix_sleep_ms(uint32_t ms)
{
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
    nanosleep(&ts, NULL);
}

static dsys_window* dsys_posix_window_create(const dsys_window_desc* desc)
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

static void dsys_posix_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    free(win);
}

static void dsys_posix_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
}

static void dsys_posix_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

static void dsys_posix_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        if (w) *w = 0;
        if (h) *h = 0;
        return;
    }
    if (w) *w = win->width;
    if (h) *h = win->height;
}

static void dsys_posix_window_show(dsys_window* win) { (void)win; }
static void dsys_posix_window_hide(dsys_window* win) { (void)win; }

static void dsys_posix_window_get_state(dsys_window* win, dsys_window_state* out_state)
{
    if (!out_state) {
        return;
    }
    memset(out_state, 0, sizeof(*out_state));
    if (!win) {
        out_state->should_close = true;
    }
}

static void dsys_posix_window_get_framebuffer_size(dsys_window* win, int32_t* w, int32_t* h)
{
    dsys_posix_window_get_size(win, w, h);
}

static float dsys_posix_window_get_dpi_scale(dsys_window* win)
{
    (void)win;
    return 1.0f;
}

static void* dsys_posix_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool dsys_posix_poll_event(dsys_event* out)
{
    if (dsys_internal_event_pop(out)) {
        return true;
    }
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static bool dsys_posix_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* env_name;
    const char* src;
    size_t len;
    char cwd[260];

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
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            src = cwd;
        }
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

static void* dsys_posix_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t dsys_posix_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t dsys_posix_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int dsys_posix_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long dsys_posix_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int dsys_posix_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* dsys_posix_dir_open(const char* path)
{
    dsys_dir_iter* it;
    dsys_dir_entry* entries = NULL;
    uint32_t count = 0u;

    if (!path) {
        return NULL;
    }
    if (!dsys_dir_collect_sorted(path, &entries, &count)) {
        return NULL;
    }
    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        free(entries);
        return NULL;
    }
    memset(it, 0, sizeof(*it));
    it->entries = entries;
    it->entry_count = count;
    it->entry_index = 0u;
    return it;
}

static bool dsys_posix_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    return dsys_dir_next_sorted(it, out);
}

static void dsys_posix_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    dsys_dir_free_sorted(it);
    free(it);
}

static dsys_process* dsys_posix_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int dsys_posix_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void dsys_posix_process_destroy(dsys_process* p)
{
    (void)p;
}

static const dsys_backend_vtable g_posix_vtable = {
    dsys_posix_init,
    dsys_posix_shutdown,
    dsys_posix_get_caps,
    dsys_posix_time_now_us,
    dsys_posix_sleep_ms,
    dsys_posix_window_create,
    dsys_posix_window_destroy,
    dsys_posix_window_set_mode,
    dsys_posix_window_set_size,
    dsys_posix_window_get_size,
    dsys_posix_window_show,
    dsys_posix_window_hide,
    dsys_posix_window_get_state,
    dsys_posix_window_get_framebuffer_size,
    dsys_posix_window_get_dpi_scale,
    dsys_posix_window_get_native_handle,
    dsys_posix_poll_event,
    dsys_posix_get_path,
    dsys_posix_file_open,
    dsys_posix_file_read,
    dsys_posix_file_write,
    dsys_posix_file_seek,
    dsys_posix_file_tell,
    dsys_posix_file_close,
    dsys_posix_dir_open,
    dsys_posix_dir_next,
    dsys_posix_dir_close,
    dsys_posix_process_spawn,
    dsys_posix_process_wait,
    dsys_posix_process_destroy
};

const dsys_backend_vtable* dsys_posix_get_vtable(void)
{
    return &g_posix_vtable;
}

#endif /* !_WIN32 */

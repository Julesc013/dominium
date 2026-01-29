/*
FILE: source/domino/system/dsys_win32_headless.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_win32_headless
RESPONSIBILITY: Win32 headless DSYS backend (no windowing; filesystem + time).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic directory order; monotonic time via QPC.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Replace with real win32 headless backend if needed.
*/
#define DOMINO_SYS_INTERNAL 1
#include "domino/system/dsys.h"
#include "dsys_internal.h"
#include "dsys_dir_sorted.h"

#if defined(_WIN32)
#include <windows.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static LARGE_INTEGER g_win32_headless_freq;

static dsys_caps dsys_win32_headless_get_caps(void)
{
    dsys_caps caps;
    caps.name = "win32_headless";
    caps.ui_modes = 0u;
    caps.has_windows = false;
    caps.has_mouse = false;
    caps.has_gamepad = false;
    caps.has_high_res_timer = true;
    return caps;
}

static dsys_result dsys_win32_headless_init(void)
{
    if (!QueryPerformanceFrequency(&g_win32_headless_freq)) {
        g_win32_headless_freq.QuadPart = 0;
    }
    return DSYS_OK;
}

static void dsys_win32_headless_shutdown(void)
{
}

static uint64_t dsys_win32_headless_time_now_us(void)
{
    LARGE_INTEGER now;
    if (g_win32_headless_freq.QuadPart == 0) {
        return (uint64_t)GetTickCount64() * 1000ull;
    }
    QueryPerformanceCounter(&now);
    return (uint64_t)((now.QuadPart * 1000000ull) / g_win32_headless_freq.QuadPart);
}

static void dsys_win32_headless_sleep_ms(uint32_t ms)
{
    Sleep(ms);
}

static dsys_window* dsys_win32_headless_window_create(const dsys_window_desc* desc)
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

static void dsys_win32_headless_window_destroy(dsys_window* win)
{
    if (win) {
        free(win);
    }
}

static void dsys_win32_headless_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (win) {
        win->mode = mode;
    }
}

static void dsys_win32_headless_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

static void dsys_win32_headless_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        if (w) *w = 0;
        if (h) *h = 0;
        return;
    }
    if (w) *w = win->width;
    if (h) *h = win->height;
}

static void dsys_win32_headless_window_show(dsys_window* win) { (void)win; }
static void dsys_win32_headless_window_hide(dsys_window* win) { (void)win; }

static void dsys_win32_headless_window_get_state(dsys_window* win, dsys_window_state* out_state)
{
    if (!out_state) {
        return;
    }
    memset(out_state, 0, sizeof(*out_state));
    if (!win) {
        out_state->should_close = true;
    }
}

static void dsys_win32_headless_window_get_framebuffer_size(dsys_window* win, int32_t* w, int32_t* h)
{
    dsys_win32_headless_window_get_size(win, w, h);
}

static float dsys_win32_headless_window_get_dpi_scale(dsys_window* win)
{
    (void)win;
    return 1.0f;
}

static void* dsys_win32_headless_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool dsys_win32_headless_poll_event(dsys_event* out)
{
    if (dsys_internal_event_pop(out)) {
        return true;
    }
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static bool dsys_win32_headless_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* env_name;
    const char* src;
    DWORD len;
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
        len = GetCurrentDirectoryA((DWORD)sizeof(cwd), cwd);
        if (len > 0 && len < sizeof(cwd)) {
            src = cwd;
        }
    }

    if (!src) {
        src = ".";
    }

    len = (DWORD)strlen(src);
    if (len >= buf_size) {
        len = (DWORD)buf_size - 1u;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return true;
}

static void* dsys_win32_headless_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t dsys_win32_headless_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t dsys_win32_headless_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int dsys_win32_headless_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long dsys_win32_headless_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int dsys_win32_headless_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* dsys_win32_headless_dir_open(const char* path)
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

static bool dsys_win32_headless_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    return dsys_dir_next_sorted(it, out);
}

static void dsys_win32_headless_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    dsys_dir_free_sorted(it);
    free(it);
}

static dsys_process* dsys_win32_headless_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int dsys_win32_headless_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void dsys_win32_headless_process_destroy(dsys_process* p)
{
    (void)p;
}

static const dsys_backend_vtable g_win32_headless_vtable = {
    dsys_win32_headless_init,
    dsys_win32_headless_shutdown,
    dsys_win32_headless_get_caps,
    dsys_win32_headless_time_now_us,
    dsys_win32_headless_sleep_ms,
    dsys_win32_headless_window_create,
    dsys_win32_headless_window_destroy,
    dsys_win32_headless_window_set_mode,
    dsys_win32_headless_window_set_size,
    dsys_win32_headless_window_get_size,
    dsys_win32_headless_window_show,
    dsys_win32_headless_window_hide,
    dsys_win32_headless_window_get_state,
    dsys_win32_headless_window_get_framebuffer_size,
    dsys_win32_headless_window_get_dpi_scale,
    dsys_win32_headless_window_get_native_handle,
    dsys_win32_headless_poll_event,
    dsys_win32_headless_get_path,
    dsys_win32_headless_file_open,
    dsys_win32_headless_file_read,
    dsys_win32_headless_file_write,
    dsys_win32_headless_file_seek,
    dsys_win32_headless_file_tell,
    dsys_win32_headless_file_close,
    dsys_win32_headless_dir_open,
    dsys_win32_headless_dir_next,
    dsys_win32_headless_dir_close,
    dsys_win32_headless_process_spawn,
    dsys_win32_headless_process_wait,
    dsys_win32_headless_process_destroy
};

const dsys_backend_vtable* dsys_win32_headless_get_vtable(void)
{
    return &g_win32_headless_vtable;
}

#endif /* _WIN32 */

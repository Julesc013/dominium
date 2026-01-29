/*
FILE: source/domino/system/dsys_platform_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_platform_stub
RESPONSIBILITY: Provides stub backends for legacy/optional platforms (X11/Wayland/Cocoa/etc.).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic directory ordering; monotonic time where available.
VERSIONING / ABI / DATA FORMAT NOTES: Internal only.
EXTENSION POINTS: Replace stubs with real platform backends behind same contract.
*/
#define DOMINO_SYS_INTERNAL 1
#include "domino/system/dsys.h"
#include "dsys_internal.h"
#include "dsys_dir_sorted.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#endif

static dsys_caps dsys_stub_get_caps(const char* name)
{
    dsys_caps caps;
    caps.name = name ? name : "stub";
    caps.ui_modes = 0u;
    caps.has_windows = false;
    caps.has_mouse = false;
    caps.has_gamepad = false;
    caps.has_high_res_timer = true;
    return caps;
}

static dsys_result dsys_stub_init(void) { return DSYS_OK; }
static void dsys_stub_shutdown(void) { }

static uint64_t dsys_stub_time_now_us(void)
{
#if defined(_WIN32)
    return (uint64_t)GetTickCount64() * 1000ull;
#else
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
#endif
}

static void dsys_stub_sleep_ms(uint32_t ms)
{
#if defined(_WIN32)
    Sleep(ms);
#else
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
    nanosleep(&ts, NULL);
#endif
}

static dsys_window* dsys_stub_window_create(const dsys_window_desc* desc)
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

static void dsys_stub_window_destroy(dsys_window* win)
{
    if (win) {
        free(win);
    }
}

static void dsys_stub_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (win) {
        win->mode = mode;
    }
}

static void dsys_stub_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

static void dsys_stub_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        if (w) *w = 0;
        if (h) *h = 0;
        return;
    }
    if (w) *w = win->width;
    if (h) *h = win->height;
}

static void dsys_stub_window_show(dsys_window* win) { (void)win; }
static void dsys_stub_window_hide(dsys_window* win) { (void)win; }

static void dsys_stub_window_get_state(dsys_window* win, dsys_window_state* out_state)
{
    if (!out_state) {
        return;
    }
    memset(out_state, 0, sizeof(*out_state));
    if (!win) {
        out_state->should_close = true;
    }
}

static void dsys_stub_window_get_framebuffer_size(dsys_window* win, int32_t* w, int32_t* h)
{
    dsys_stub_window_get_size(win, w, h);
}

static float dsys_stub_window_get_dpi_scale(dsys_window* win)
{
    (void)win;
    return 1.0f;
}

static void* dsys_stub_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool dsys_stub_poll_event(dsys_event* out)
{
    if (dsys_internal_event_pop(out)) {
        return true;
    }
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static bool dsys_stub_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
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
#if defined(_WIN32)
        DWORD len = GetCurrentDirectoryA((DWORD)sizeof(cwd), cwd);
        if (len > 0 && len < sizeof(cwd)) {
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

static void* dsys_stub_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t dsys_stub_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t dsys_stub_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int dsys_stub_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long dsys_stub_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int dsys_stub_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* dsys_stub_dir_open(const char* path)
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

static bool dsys_stub_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    return dsys_dir_next_sorted(it, out);
}

static void dsys_stub_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    dsys_dir_free_sorted(it);
    free(it);
}

static dsys_process* dsys_stub_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int dsys_stub_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void dsys_stub_process_destroy(dsys_process* p)
{
    (void)p;
}

static const dsys_backend_vtable g_stub_vtable = {
    dsys_stub_init,
    dsys_stub_shutdown,
    NULL, /* caps set per-backend helper */
    dsys_stub_time_now_us,
    dsys_stub_sleep_ms,
    dsys_stub_window_create,
    dsys_stub_window_destroy,
    dsys_stub_window_set_mode,
    dsys_stub_window_set_size,
    dsys_stub_window_get_size,
    dsys_stub_window_show,
    dsys_stub_window_hide,
    dsys_stub_window_get_state,
    dsys_stub_window_get_framebuffer_size,
    dsys_stub_window_get_dpi_scale,
    dsys_stub_window_get_native_handle,
    dsys_stub_poll_event,
    dsys_stub_get_path,
    dsys_stub_file_open,
    dsys_stub_file_read,
    dsys_stub_file_write,
    dsys_stub_file_seek,
    dsys_stub_file_tell,
    dsys_stub_file_close,
    dsys_stub_dir_open,
    dsys_stub_dir_next,
    dsys_stub_dir_close,
    dsys_stub_process_spawn,
    dsys_stub_process_wait,
    dsys_stub_process_destroy
};

static dsys_backend_vtable dsys_stub_vtable_named(const char* name)
{
    dsys_backend_vtable vt = g_stub_vtable;
    vt.get_caps = NULL;
    (void)name;
    return vt;
}

static dsys_backend_vtable g_x11_vt;
static dsys_backend_vtable g_wayland_vt;
static dsys_backend_vtable g_cocoa_vt;
static dsys_backend_vtable g_carbon_vt;
static dsys_backend_vtable g_sdl1_vt;
static dsys_backend_vtable g_dos16_vt;
static dsys_backend_vtable g_dos32_vt;
static dsys_backend_vtable g_win16_vt;
static dsys_backend_vtable g_cpm80_vt;
static dsys_backend_vtable g_cpm86_vt;

static dsys_caps dsys_caps_x11(void) { return dsys_stub_get_caps("x11"); }
static dsys_caps dsys_caps_wayland(void) { return dsys_stub_get_caps("wayland"); }
static dsys_caps dsys_caps_cocoa(void) { return dsys_stub_get_caps("cocoa"); }
static dsys_caps dsys_caps_carbon(void) { return dsys_stub_get_caps("carbon"); }
static dsys_caps dsys_caps_sdl1(void) { return dsys_stub_get_caps("sdl1"); }
static dsys_caps dsys_caps_dos16(void) { return dsys_stub_get_caps("dos16"); }
static dsys_caps dsys_caps_dos32(void) { return dsys_stub_get_caps("dos32"); }
static dsys_caps dsys_caps_win16(void) { return dsys_stub_get_caps("win16"); }
static dsys_caps dsys_caps_cpm80(void) { return dsys_stub_get_caps("cpm80"); }
static dsys_caps dsys_caps_cpm86(void) { return dsys_stub_get_caps("cpm86"); }

static const dsys_backend_vtable* dsys_stub_get_named(dsys_backend_vtable* slot, dsys_caps (*caps_fn)(void))
{
    if (!slot->init) {
        *slot = dsys_stub_vtable_named(NULL);
        slot->get_caps = caps_fn;
    }
    return slot;
}

const dsys_backend_vtable* dsys_x11_get_vtable(void)     { return dsys_stub_get_named(&g_x11_vt, dsys_caps_x11); }
const dsys_backend_vtable* dsys_wayland_get_vtable(void) { return dsys_stub_get_named(&g_wayland_vt, dsys_caps_wayland); }
const dsys_backend_vtable* dsys_cocoa_get_vtable(void)   { return dsys_stub_get_named(&g_cocoa_vt, dsys_caps_cocoa); }
const dsys_backend_vtable* dsys_carbon_get_vtable(void)  { return dsys_stub_get_named(&g_carbon_vt, dsys_caps_carbon); }
const dsys_backend_vtable* dsys_sdl1_get_vtable(void)    { return dsys_stub_get_named(&g_sdl1_vt, dsys_caps_sdl1); }
const dsys_backend_vtable* dsys_dos16_get_vtable(void)   { return dsys_stub_get_named(&g_dos16_vt, dsys_caps_dos16); }
const dsys_backend_vtable* dsys_dos32_get_vtable(void)   { return dsys_stub_get_named(&g_dos32_vt, dsys_caps_dos32); }
const dsys_backend_vtable* dsys_win16_get_vtable(void)   { return dsys_stub_get_named(&g_win16_vt, dsys_caps_win16); }
const dsys_backend_vtable* dsys_cpm80_get_vtable(void)   { return dsys_stub_get_named(&g_cpm80_vt, dsys_caps_cpm80); }
const dsys_backend_vtable* dsys_cpm86_get_vtable(void)   { return dsys_stub_get_named(&g_cpm86_vt, dsys_caps_cpm86); }

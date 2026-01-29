/*
FILE: source/domino/system/sys.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/sys
RESPONSIBILITY: Implements `sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#define DOMINO_SYS_INTERNAL 1
#include "domino/sys.h"
#include "domino/system/dsys_guard.h"
#include "domino/caps.h"
#include "dsys_internal.h"
#include "dsys_dir_sorted.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <time.h>
#include <ctype.h>
#include <signal.h>

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
static uint64_t g_null_time_us = 0u;

static dsys_log_fn g_dsys_log_cb = 0;

#define DSYS_LAST_ERROR_TEXT_MAX 256u
static dsys_result g_dsys_last_error_code = DSYS_OK;
static char g_dsys_last_error_text[DSYS_LAST_ERROR_TEXT_MAX];

static dsys_window* g_dsys_window_list = NULL;
static uint32_t g_dsys_window_next_id = 1u;
static int g_dsys_cursor_visible = 1;

uint64_t dsys_time_now_us(void);

#define DSYS_EVENT_QUEUE_MAX 128u
static dsys_event g_dsys_event_queue[DSYS_EVENT_QUEUE_MAX];
static unsigned int g_dsys_event_head = 0u;
static unsigned int g_dsys_event_tail = 0u;

static volatile sig_atomic_t g_dsys_shutdown_requested = 0;
static volatile sig_atomic_t g_dsys_shutdown_reason = (sig_atomic_t)DSYS_SHUTDOWN_NONE;
#if !defined(_WIN32)
static struct sigaction g_dsys_prev_sigint;
static struct sigaction g_dsys_prev_sigterm;
#endif

static void dsys_set_last_error(dsys_result code, const char* text)
{
    g_dsys_last_error_code = code;
    if (!text) {
        g_dsys_last_error_text[0] = '\0';
        return;
    }
    strncpy(g_dsys_last_error_text, text, DSYS_LAST_ERROR_TEXT_MAX - 1u);
    g_dsys_last_error_text[DSYS_LAST_ERROR_TEXT_MAX - 1u] = '\0';
}

static void dsys_clear_last_error(void)
{
    dsys_set_last_error(DSYS_OK, "");
}

static void dsys_event_queue_reset(void)
{
    g_dsys_event_head = 0u;
    g_dsys_event_tail = 0u;
}

static void dsys_window_registry_reset(void)
{
    g_dsys_window_list = NULL;
    g_dsys_window_next_id = 1u;
}

static void dsys_window_register(dsys_window* win)
{
    if (!win) {
        return;
    }
    win->window_id = g_dsys_window_next_id++;
    win->cursor_visible = 1;
    win->cursor_confined = 0;
    win->relative_mouse = 0;
    win->cursor_shape = (uint32_t)DSYS_CURSOR_ARROW;
    win->next = g_dsys_window_list;
    g_dsys_window_list = win;
}

static void dsys_window_unregister(dsys_window* win)
{
    dsys_window** it;
    if (!win) {
        return;
    }
    it = &g_dsys_window_list;
    while (*it) {
        if (*it == win) {
            *it = win->next;
            win->next = NULL;
            return;
        }
        it = &(*it)->next;
    }
}

int dsys_internal_event_push(const dsys_event* ev)
{
    unsigned int next_tail;
    dsys_event local;
    if (!ev) {
        return 0;
    }
    local = *ev;
    if (local.timestamp_us == 0u) {
        local.timestamp_us = dsys_time_now_us();
    }
    if (local.window && local.window_id == 0u) {
        local.window_id = local.window->window_id;
    }
    next_tail = g_dsys_event_tail + 1u;
    if (next_tail >= DSYS_EVENT_QUEUE_MAX) {
        next_tail = 0u;
    }
    if (next_tail == g_dsys_event_head) {
        return 0;
    }
    g_dsys_event_queue[g_dsys_event_tail] = local;
    g_dsys_event_tail = next_tail;
    return 1;
}

int dsys_internal_event_pop(dsys_event* out)
{
    if (g_dsys_event_head == g_dsys_event_tail) {
        return 0;
    }
    if (out) {
        *out = g_dsys_event_queue[g_dsys_event_head];
    }
    g_dsys_event_head += 1u;
    if (g_dsys_event_head >= DSYS_EVENT_QUEUE_MAX) {
        g_dsys_event_head = 0u;
    }
    return 1;
}

void dsys_set_log_callback(dsys_log_fn fn)
{
    g_dsys_log_cb = fn;
}

static dom_abi_result dsys_core_query_interface(dom_iid iid, void** out_iface);

static const dsys_time_api_v1 g_dsys_time_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_time_api_v1),
    dsys_time_now_us,
    dsys_sleep_ms
};

static const dsys_fs_api_v1 g_dsys_fs_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_fs_api_v1),
    dsys_get_path,

    dsys_file_open,
    dsys_file_read,
    dsys_file_write,
    dsys_file_seek,
    dsys_file_tell,
    dsys_file_close,

    dsys_dir_open,
    dsys_dir_next,
    dsys_dir_close
};

static const dsys_process_api_v1 g_dsys_process_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_process_api_v1),
    dsys_process_spawn,
    dsys_process_wait,
    dsys_process_destroy
};

static void* dsys_dynlib_open(const char* path);
static void  dsys_dynlib_close(void* lib);
static void* dsys_dynlib_sym(void* lib, const char* name);

static const dsys_dynlib_api_v1 g_dsys_dynlib_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_dynlib_api_v1),
    dsys_dynlib_open,
    dsys_dynlib_close,
    dsys_dynlib_sym
};

static const dsys_window_api_v1 g_dsys_window_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_window_api_v1),
    dsys_window_create,
    dsys_window_destroy,
    dsys_window_set_mode,
    dsys_window_set_size,
    dsys_window_get_size,
    dsys_window_get_native_handle,
    dsys_window_should_close,
    dsys_window_present
};

static const dsys_window_ex_api_v1 g_dsys_window_ex_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_window_ex_api_v1),
    dsys_window_show,
    dsys_window_hide,
    dsys_window_get_state,
    dsys_window_get_framebuffer_size,
    dsys_window_get_dpi_scale
};

static const dsys_input_api_v1 g_dsys_input_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_input_api_v1),
    dsys_poll_event,
    dsys_input_poll_raw,
    dsys_ime_start,
    dsys_ime_stop,
    dsys_ime_set_cursor,
    dsys_ime_poll
};

static dsys_result dsys_cliptext_get_text(char* buf, size_t cap);
static dsys_result dsys_cliptext_set_text(const char* text);
static dsys_result dsys_cursor_set(dsys_window* win, dsys_cursor_shape shape);
static dsys_result dsys_cursor_show(dsys_window* win, bool visible);
static dsys_result dsys_cursor_confine(dsys_window* win, bool confined);
static dsys_result dsys_cursor_set_relative(dsys_window* win, bool enabled);
static dsys_result dsys_text_input_start(dsys_window* win);
static dsys_result dsys_text_input_stop(dsys_window* win);
static dsys_result dsys_text_input_set_cursor(dsys_window* win, int32_t x, int32_t y);
static int dsys_text_input_poll(dsys_ime_event* ev);
static dsys_result dsys_window_mode_set(dsys_window* win, dsys_window_mode mode);
static dsys_window_mode dsys_window_mode_get(dsys_window* win);

static const dsys_cliptext_api_v1 g_dsys_cliptext_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_cliptext_api_v1),
    dsys_cliptext_get_text,
    dsys_cliptext_set_text
};

static const dsys_cursor_api_v1 g_dsys_cursor_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_cursor_api_v1),
    dsys_cursor_set,
    dsys_cursor_show,
    dsys_cursor_confine,
    dsys_cursor_set_relative
};

static const dsys_dragdrop_api_v1 g_dsys_dragdrop_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_dragdrop_api_v1),
    NULL,
    NULL
};

static const dsys_gamepad_api_v1 g_dsys_gamepad_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_gamepad_api_v1),
    NULL,
    NULL
};

static const dsys_power_api_v1 g_dsys_power_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_power_api_v1),
    NULL,
    NULL
};

static const dsys_text_input_api_v1 g_dsys_text_input_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_text_input_api_v1),
    dsys_text_input_start,
    dsys_text_input_stop,
    dsys_text_input_set_cursor,
    dsys_text_input_poll
};

static const dsys_window_mode_api_v1 g_dsys_window_mode_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_window_mode_api_v1),
    dsys_window_mode_set,
    dsys_window_mode_get
};

static const dsys_error_api_v1 g_dsys_error_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_error_api_v1),
    dsys_last_error_code,
    dsys_last_error_text
};

static const dsys_core_api_v1 g_dsys_core_api_v1 = {
    DOM_ABI_HEADER_INIT(1u, dsys_core_api_v1),
    dsys_core_query_interface,
    dsys_init,
    dsys_shutdown,
    dsys_get_caps,
    dsys_set_log_callback
};

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
#if defined(DSYS_BACKEND_POSIX)
    return "posix_headless";
#elif defined(DSYS_BACKEND_COCOA)
    return "cocoa";
#elif defined(DSYS_BACKEND_SDL2)
    return "sdl2";
#elif defined(DSYS_BACKEND_WIN32_HEADLESS)
    return "win32_headless";
#elif defined(DSYS_BACKEND_WIN32)
    return "win32";
#elif defined(DSYS_BACKEND_NULL)
    return "null";
#else
    return "null";
#endif
}

static const void* dsys_caps_get_core_api_ptr(u32 requested_abi)
{
    if (requested_abi != g_dsys_core_api_v1.abi_version) {
        return (const void*)0;
    }
    return (const void*)&g_dsys_core_api_v1;
}

dom_caps_result dom_dsys_register_caps_backends(void)
{
    dom_backend_desc desc;

    memset(&desc, 0, sizeof(desc));
    desc.abi_version = DOM_CAPS_ABI_VERSION;
    desc.struct_size = (u32)sizeof(dom_backend_desc);

    desc.subsystem_id = DOM_SUBSYS_DSYS;
    desc.subsystem_name = "sys";

    desc.backend_name = dsys_compiled_backend_name();
    desc.backend_priority = 100u;

    desc.required_hw_flags = 0u;
#if defined(DSYS_BACKEND_WIN32) || defined(DSYS_BACKEND_WIN32_HEADLESS) || defined(DSYS_BACKEND_WIN16)
    desc.required_hw_flags |= DOM_HW_OS_WIN32;
#elif defined(DSYS_BACKEND_COCOA) || defined(DSYS_BACKEND_CARBON)
    desc.required_hw_flags |= DOM_HW_OS_APPLE;
#elif defined(DSYS_BACKEND_POSIX) || defined(DSYS_BACKEND_X11) || defined(DSYS_BACKEND_WAYLAND)
    desc.required_hw_flags |= DOM_HW_OS_UNIX;
#endif
    desc.subsystem_flags = 0u;
    desc.backend_flags = 0u;

    desc.determinism = DOM_DET_D2_BEST_EFFORT;
    if (dsys_str_ieq(desc.backend_name, "null")) {
        desc.determinism = DOM_DET_D0_BIT_EXACT;
    }
    desc.perf_class = DOM_CAPS_PERF_BASELINE;

    desc.get_api = dsys_caps_get_core_api_ptr;
    desc.probe = (dom_caps_probe_fn)0;

    return dom_caps_register_backend(&desc);
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
    g_null_time_us = 0u;
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
    /* Deterministic synthetic time for CI/headless validation. */
    g_null_time_us += (uint64_t)1000u;
    return g_null_time_us;
}

static void null_sleep_ms(uint32_t ms)
{
    g_null_time_us += (uint64_t)ms * (uint64_t)1000u;
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

static void null_window_show(dsys_window* win)
{
    (void)win;
}

static void null_window_hide(dsys_window* win)
{
    (void)win;
}

static void null_window_get_state(dsys_window* win, dsys_window_state* out_state)
{
    if (!out_state) {
        return;
    }
    memset(out_state, 0, sizeof(*out_state));
    if (!win) {
        out_state->should_close = true;
    }
}

static void null_window_get_framebuffer_size(dsys_window* win, int32_t* w, int32_t* h)
{
    null_window_get_size(win, w, h);
}

static float null_window_get_dpi_scale(dsys_window* win)
{
    (void)win;
    return 1.0f;
}

static void* null_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool null_poll_event(dsys_event* out)
{
    if (dsys_internal_event_pop(out)) {
        return true;
    }
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

static bool null_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    return dsys_dir_next_sorted(it, out);
}

static void null_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    dsys_dir_free_sorted(it);
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
    null_window_show,
    null_window_hide,
    null_window_get_state,
    null_window_get_framebuffer_size,
    null_window_get_dpi_scale,
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
    dsys_clear_last_error();
    dsys_event_queue_reset();
    dsys_window_registry_reset();
#if defined(DSYS_BACKEND_POSIX)
    {
        extern const dsys_backend_vtable* dsys_posix_get_vtable(void);
        g_dsys = dsys_posix_get_vtable();
    }
#elif defined(DSYS_BACKEND_COCOA)
    {
        extern const dsys_backend_vtable* dsys_cocoa_get_vtable(void);
        g_dsys = dsys_cocoa_get_vtable();
    }
#elif defined(DSYS_BACKEND_SDL2)
    {
        extern const dsys_backend_vtable* dsys_sdl2_get_vtable(void);
        g_dsys = dsys_sdl2_get_vtable();
    }
#elif defined(DSYS_BACKEND_WIN32_HEADLESS)
    {
        extern const dsys_backend_vtable* dsys_win32_headless_get_vtable(void);
        g_dsys = dsys_win32_headless_get_vtable();
    }
#elif defined(DSYS_BACKEND_WIN32)
    {
        extern const dsys_backend_vtable* dsys_win32_get_vtable(void);
        g_dsys = dsys_win32_get_vtable();
    }
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
    if (result != DSYS_OK) {
        dsys_set_last_error(result, "dsys_init: backend init failed");
    }
    return result;
}

void dsys_shutdown(void)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    backend = dsys_active_backend();
    if (backend->shutdown) {
        backend->shutdown();
    }
    dsys_window_registry_reset();
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
    dsys_clear_last_error();
    backend = dsys_active_backend();
    if (backend->window_create) {
        dsys_window* win = backend->window_create(desc);
        if (win) {
            dsys_window_register(win);
            return win;
        }
        dsys_set_last_error(DSYS_ERR, "window_create: backend failure");
        return NULL;
    }
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_create: unsupported");
    return NULL;
}

void dsys_window_destroy(dsys_window* win)
{
    const dsys_backend_vtable* backend;
    dsys_window_unregister(win);
    backend = dsys_active_backend();
    if (backend->window_destroy) {
        backend->window_destroy(win);
    }
}

void dsys_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "window_set_mode: null window");
        return;
    }
    backend = dsys_active_backend();
    if (backend->window_set_mode) {
        backend->window_set_mode(win, mode);
        return;
    }
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_set_mode: unsupported");
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
    dsys_window_state state;
    dsys_window_get_state(win, &state);
    return state.should_close ? 1 : 0;
}

void dsys_window_present(dsys_window* win)
{
    (void)win;
    /* Rendering is handled by higher layers; nothing to do here. */
}

void dsys_window_show(dsys_window* win)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "window_show: null window");
        return;
    }
    backend = dsys_active_backend();
    if (backend->window_show) {
        backend->window_show(win);
        return;
    }
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_show: unsupported");
}

void dsys_window_hide(dsys_window* win)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "window_hide: null window");
        return;
    }
    backend = dsys_active_backend();
    if (backend->window_hide) {
        backend->window_hide(win);
        return;
    }
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_hide: unsupported");
}

void dsys_window_get_state(dsys_window* win, dsys_window_state* out_state)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    if (!out_state) {
        dsys_set_last_error(DSYS_ERR, "window_get_state: null out_state");
        return;
    }
    memset(out_state, 0, sizeof(*out_state));
    if (!win) {
        out_state->should_close = true;
        dsys_set_last_error(DSYS_ERR, "window_get_state: null window");
        return;
    }
    backend = dsys_active_backend();
    if (backend->window_get_state) {
        backend->window_get_state(win, out_state);
        return;
    }
    out_state->should_close = false;
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_get_state: unsupported");
}

void dsys_window_get_framebuffer_size(dsys_window* win, int32_t* w, int32_t* h)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    backend = dsys_active_backend();
    if (backend->window_get_framebuffer_size) {
        backend->window_get_framebuffer_size(win, w, h);
        return;
    }
    dsys_window_get_size(win, w, h);
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_get_framebuffer_size: unsupported");
}

float dsys_window_get_dpi_scale(dsys_window* win)
{
    const dsys_backend_vtable* backend;
    dsys_clear_last_error();
    backend = dsys_active_backend();
    if (backend->window_get_dpi_scale) {
        return backend->window_get_dpi_scale(win);
    }
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_get_dpi_scale: unsupported");
    return 1.0f;
}

uint32_t dsys_window_get_id(dsys_window* win)
{
    return win ? win->window_id : 0u;
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

bool dsys_inject_event(const dsys_event* ev)
{
    dsys_clear_last_error();
    if (!ev) {
        dsys_set_last_error(DSYS_ERR, "dsys_inject_event: null event");
        return false;
    }
    if (!dsys_internal_event_push(ev)) {
        dsys_set_last_error(DSYS_ERR, "dsys_inject_event: queue full");
        return false;
    }
    return true;
}

int dsys_input_poll_raw(dsys_input_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
        ev->type = DSYS_INPUT_EVENT_NONE;
    }
    return 0;
}

void dsys_ime_start(void)
{
}

void dsys_ime_stop(void)
{
}

void dsys_ime_set_cursor(int32_t x, int32_t y)
{
    (void)x;
    (void)y;
}

int dsys_ime_poll(dsys_ime_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }
    return 0;
}

static dsys_result dsys_cliptext_get_text(char* buf, size_t cap)
{
    dsys_clear_last_error();
    if (!buf || cap == 0u) {
        dsys_set_last_error(DSYS_ERR, "cliptext_get: null buffer");
        return DSYS_ERR;
    }
#if defined(_WIN32)
    {
        HANDLE handle;
        wchar_t* wide;
        int needed;
        int written;

        if (!OpenClipboard(NULL)) {
            dsys_set_last_error(DSYS_ERR, "cliptext_get: open failed");
            return DSYS_ERR;
        }
        handle = GetClipboardData(CF_UNICODETEXT);
        if (!handle) {
            CloseClipboard();
            dsys_set_last_error(DSYS_ERR_NOT_FOUND, "cliptext_get: empty");
            return DSYS_ERR_NOT_FOUND;
        }
        wide = (wchar_t*)GlobalLock(handle);
        if (!wide) {
            CloseClipboard();
            dsys_set_last_error(DSYS_ERR, "cliptext_get: lock failed");
            return DSYS_ERR;
        }
        needed = WideCharToMultiByte(CP_UTF8, 0, wide, -1, NULL, 0, NULL, NULL);
        if (needed <= 0) {
            GlobalUnlock(handle);
            CloseClipboard();
            dsys_set_last_error(DSYS_ERR, "cliptext_get: convert failed");
            return DSYS_ERR;
        }
        if ((size_t)needed > cap) {
            written = WideCharToMultiByte(CP_UTF8, 0, wide, -1, buf, (int)cap - 1, NULL, NULL);
            if (written <= 0) {
                GlobalUnlock(handle);
                CloseClipboard();
                dsys_set_last_error(DSYS_ERR, "cliptext_get: truncation failed");
                return DSYS_ERR;
            }
            buf[cap - 1u] = '\0';
            GlobalUnlock(handle);
            CloseClipboard();
            dsys_set_last_error(DSYS_ERR, "cliptext_get: buffer too small");
            return DSYS_ERR;
        }
        written = WideCharToMultiByte(CP_UTF8, 0, wide, -1, buf, (int)cap, NULL, NULL);
        GlobalUnlock(handle);
        CloseClipboard();
        if (written <= 0) {
            dsys_set_last_error(DSYS_ERR, "cliptext_get: conversion failed");
            return DSYS_ERR;
        }
        return DSYS_OK;
    }
#else
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "cliptext_get: unsupported");
    return DSYS_ERR_UNSUPPORTED;
#endif
}

static dsys_result dsys_cliptext_set_text(const char* text)
{
    dsys_clear_last_error();
    if (!text) {
        text = "";
    }
#if defined(_WIN32)
    {
        int wlen;
        HGLOBAL hmem;
        wchar_t* wide;

        wlen = MultiByteToWideChar(CP_UTF8, 0, text, -1, NULL, 0);
        if (wlen <= 0) {
            dsys_set_last_error(DSYS_ERR, "cliptext_set: convert failed");
            return DSYS_ERR;
        }
        hmem = GlobalAlloc(GMEM_MOVEABLE, (SIZE_T)wlen * sizeof(wchar_t));
        if (!hmem) {
            dsys_set_last_error(DSYS_ERR, "cliptext_set: alloc failed");
            return DSYS_ERR;
        }
        wide = (wchar_t*)GlobalLock(hmem);
        if (!wide) {
            GlobalFree(hmem);
            dsys_set_last_error(DSYS_ERR, "cliptext_set: lock failed");
            return DSYS_ERR;
        }
        MultiByteToWideChar(CP_UTF8, 0, text, -1, wide, wlen);
        GlobalUnlock(hmem);
        if (!OpenClipboard(NULL)) {
            GlobalFree(hmem);
            dsys_set_last_error(DSYS_ERR, "cliptext_set: open failed");
            return DSYS_ERR;
        }
        EmptyClipboard();
        if (!SetClipboardData(CF_UNICODETEXT, hmem)) {
            CloseClipboard();
            GlobalFree(hmem);
            dsys_set_last_error(DSYS_ERR, "cliptext_set: set failed");
            return DSYS_ERR;
        }
        CloseClipboard();
        return DSYS_OK;
    }
#else
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "cliptext_set: unsupported");
    return DSYS_ERR_UNSUPPORTED;
#endif
}

static dsys_result dsys_cursor_set(dsys_window* win, dsys_cursor_shape shape)
{
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "cursor_set: null window");
        return DSYS_ERR;
    }
    win->cursor_shape = (uint32_t)shape;
#if defined(_WIN32)
    {
        HCURSOR cursor = NULL;
        switch (shape) {
        case DSYS_CURSOR_IBEAM: cursor = LoadCursor(NULL, IDC_IBEAM); break;
        case DSYS_CURSOR_HAND: cursor = LoadCursor(NULL, IDC_HAND); break;
        case DSYS_CURSOR_SIZE_H: cursor = LoadCursor(NULL, IDC_SIZEWE); break;
        case DSYS_CURSOR_SIZE_V: cursor = LoadCursor(NULL, IDC_SIZENS); break;
        case DSYS_CURSOR_SIZE_ALL: cursor = LoadCursor(NULL, IDC_SIZEALL); break;
        case DSYS_CURSOR_ARROW:
        default:
            cursor = LoadCursor(NULL, IDC_ARROW);
            break;
        }
        if (cursor) {
            SetCursor(cursor);
        }
    }
    return DSYS_OK;
#else
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "cursor_set: unsupported");
    return DSYS_ERR_UNSUPPORTED;
#endif
}

static void dsys_win32_set_cursor_visible(int visible)
{
#if defined(_WIN32)
    int count;
    if (visible) {
        count = ShowCursor(TRUE);
        while (count < 0) {
            count = ShowCursor(TRUE);
        }
    } else {
        count = ShowCursor(FALSE);
        while (count >= 0) {
            count = ShowCursor(FALSE);
        }
    }
#else
    (void)visible;
#endif
}

static dsys_result dsys_cursor_show(dsys_window* win, bool visible)
{
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "cursor_show: null window");
        return DSYS_ERR;
    }
    win->cursor_visible = visible ? 1 : 0;
#if defined(_WIN32)
    if (g_dsys_cursor_visible != win->cursor_visible) {
        g_dsys_cursor_visible = win->cursor_visible;
        dsys_win32_set_cursor_visible(g_dsys_cursor_visible);
    }
    return DSYS_OK;
#else
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "cursor_show: unsupported");
    return DSYS_ERR_UNSUPPORTED;
#endif
}

static dsys_result dsys_cursor_confine(dsys_window* win, bool confined)
{
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "cursor_confine: null window");
        return DSYS_ERR;
    }
#if defined(_WIN32)
    if (!confined) {
        ClipCursor(NULL);
        win->cursor_confined = 0;
        return DSYS_OK;
    }
    {
        HWND hwnd = (HWND)dsys_window_get_native_handle(win);
        RECT rc;
        POINT tl;
        POINT br;
        if (!hwnd) {
            dsys_set_last_error(DSYS_ERR, "cursor_confine: null hwnd");
            return DSYS_ERR;
        }
        if (!GetClientRect(hwnd, &rc)) {
            dsys_set_last_error(DSYS_ERR, "cursor_confine: rect failed");
            return DSYS_ERR;
        }
        tl.x = rc.left;
        tl.y = rc.top;
        br.x = rc.right;
        br.y = rc.bottom;
        ClientToScreen(hwnd, &tl);
        ClientToScreen(hwnd, &br);
        rc.left = tl.x;
        rc.top = tl.y;
        rc.right = br.x;
        rc.bottom = br.y;
        if (!ClipCursor(&rc)) {
            dsys_set_last_error(DSYS_ERR, "cursor_confine: clip failed");
            return DSYS_ERR;
        }
    }
    win->cursor_confined = 1;
    return DSYS_OK;
#else
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "cursor_confine: unsupported");
    return DSYS_ERR_UNSUPPORTED;
#endif
}

static dsys_result dsys_cursor_set_relative(dsys_window* win, bool enabled)
{
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "cursor_relative: null window");
        return DSYS_ERR;
    }
#if defined(_WIN32)
    if (enabled) {
        RAWINPUTDEVICE rid;
        HWND hwnd = (HWND)dsys_window_get_native_handle(win);
        if (!hwnd) {
            dsys_set_last_error(DSYS_ERR, "cursor_relative: null hwnd");
            return DSYS_ERR;
        }
        rid.usUsagePage = 0x01;
        rid.usUsage = 0x02;
        rid.dwFlags = RIDEV_INPUTSINK;
        rid.hwndTarget = hwnd;
        if (!RegisterRawInputDevices(&rid, 1, sizeof(rid))) {
            dsys_set_last_error(DSYS_ERR, "cursor_relative: raw input failed");
            return DSYS_ERR;
        }
        win->relative_mouse = 1;
        (void)dsys_cursor_show(win, false);
    } else {
        win->relative_mouse = 0;
        (void)dsys_cursor_show(win, true);
    }
    return DSYS_OK;
#else
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "cursor_relative: unsupported");
    return DSYS_ERR_UNSUPPORTED;
#endif
}

static dsys_result dsys_text_input_start(dsys_window* win)
{
    (void)win;
    dsys_clear_last_error();
    dsys_ime_start();
    return DSYS_OK;
}

static dsys_result dsys_text_input_stop(dsys_window* win)
{
    (void)win;
    dsys_clear_last_error();
    dsys_ime_stop();
    return DSYS_OK;
}

static dsys_result dsys_text_input_set_cursor(dsys_window* win, int32_t x, int32_t y)
{
    (void)win;
    dsys_clear_last_error();
    dsys_ime_set_cursor(x, y);
    return DSYS_OK;
}

static int dsys_text_input_poll(dsys_ime_event* ev)
{
    return dsys_ime_poll(ev);
}

static dsys_result dsys_window_mode_set(dsys_window* win, dsys_window_mode mode)
{
    dsys_clear_last_error();
    if (!win) {
        dsys_set_last_error(DSYS_ERR, "window_mode_set: null window");
        return DSYS_ERR;
    }
    if (!dsys_get_caps().has_windows) {
        dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "window_mode_set: unsupported");
        return DSYS_ERR_UNSUPPORTED;
    }
    dsys_window_set_mode(win, mode);
    return DSYS_OK;
}

static dsys_window_mode dsys_window_mode_get(dsys_window* win)
{
    if (!win) {
        return DWIN_MODE_WINDOWED;
    }
    return win->mode;
}

#if defined(_WIN32)
static BOOL WINAPI dsys_console_ctrl_handler(DWORD type)
{
    dsys_shutdown_reason reason = DSYS_SHUTDOWN_SIGNAL;
    switch (type) {
    case CTRL_C_EVENT:
    case CTRL_BREAK_EVENT:
        reason = DSYS_SHUTDOWN_SIGNAL;
        break;
    case CTRL_CLOSE_EVENT:
    case CTRL_LOGOFF_EVENT:
    case CTRL_SHUTDOWN_EVENT:
        reason = DSYS_SHUTDOWN_CONSOLE;
        break;
    default:
        break;
    }
    g_dsys_shutdown_reason = (sig_atomic_t)reason;
    g_dsys_shutdown_requested = 1;
    return TRUE;
}
#else
static void dsys_posix_signal_handler(int sig)
{
    (void)sig;
    g_dsys_shutdown_reason = (sig_atomic_t)DSYS_SHUTDOWN_SIGNAL;
    g_dsys_shutdown_requested = 1;
}
#endif

void dsys_lifecycle_init(void)
{
    g_dsys_shutdown_requested = 0;
    g_dsys_shutdown_reason = (sig_atomic_t)DSYS_SHUTDOWN_NONE;
#if defined(_WIN32)
    SetConsoleCtrlHandler(dsys_console_ctrl_handler, TRUE);
#else
    {
        struct sigaction sa;
        memset(&sa, 0, sizeof(sa));
        sa.sa_handler = dsys_posix_signal_handler;
        sigemptyset(&sa.sa_mask);
        sigaction(SIGINT, &sa, &g_dsys_prev_sigint);
        sigaction(SIGTERM, &sa, &g_dsys_prev_sigterm);
    }
#endif
}

void dsys_lifecycle_shutdown(void)
{
#if defined(_WIN32)
    SetConsoleCtrlHandler(dsys_console_ctrl_handler, FALSE);
#else
    sigaction(SIGINT, &g_dsys_prev_sigint, NULL);
    sigaction(SIGTERM, &g_dsys_prev_sigterm, NULL);
#endif
}

void dsys_lifecycle_request_shutdown(dsys_shutdown_reason reason)
{
    if (!g_dsys_shutdown_requested) {
        g_dsys_shutdown_reason = (sig_atomic_t)reason;
        g_dsys_shutdown_requested = 1;
    }
}

bool dsys_lifecycle_shutdown_requested(void)
{
    return g_dsys_shutdown_requested ? true : false;
}

dsys_shutdown_reason dsys_lifecycle_shutdown_reason(void)
{
    return (dsys_shutdown_reason)g_dsys_shutdown_reason;
}

const char* dsys_lifecycle_shutdown_reason_text(dsys_shutdown_reason reason)
{
    switch (reason) {
    case DSYS_SHUTDOWN_NONE: return "none";
    case DSYS_SHUTDOWN_SIGNAL: return "signal";
    case DSYS_SHUTDOWN_CONSOLE: return "console_close";
    case DSYS_SHUTDOWN_WINDOW: return "window_close";
    case DSYS_SHUTDOWN_APP_REQUEST: return "app_request";
    default: break;
    }
    return "unknown";
}

static void* dsys_dynlib_open(const char* path)
{
#if defined(_WIN32)
    if (!path || !path[0]) {
        return NULL;
    }
    return (void*)LoadLibraryA(path);
#else
    (void)path;
    return NULL;
#endif
}

static void dsys_dynlib_close(void* lib)
{
#if defined(_WIN32)
    if (lib) {
        FreeLibrary((HMODULE)lib);
    }
#else
    (void)lib;
#endif
}

static void* dsys_dynlib_sym(void* lib, const char* name)
{
#if defined(_WIN32)
    if (!lib || !name || !name[0]) {
        return NULL;
    }
    return (void*)GetProcAddress((HMODULE)lib, name);
#else
    (void)lib;
    (void)name;
    return NULL;
#endif
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
    if (dsys_guard_io_blocked("file_open", path, NULL, 0u)) {
        return NULL;
    }
    backend = dsys_active_backend();
    if (backend->file_open) {
        void* fh = backend->file_open(path, mode);
        if (fh) {
            dsys_guard_track_file_handle(fh, path);
        }
        return fh;
    }
    return NULL;
}

size_t dsys_file_read(void* fh, void* buf, size_t size)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_file_path(fh);
    if (dsys_guard_io_blocked("file_read", path, NULL, 0u)) {
        return 0u;
    }
    backend = dsys_active_backend();
    if (backend->file_read) {
        return backend->file_read(fh, buf, size);
    }
    return 0u;
}

size_t dsys_file_write(void* fh, const void* buf, size_t size)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_file_path(fh);
    if (dsys_guard_io_blocked("file_write", path, NULL, 0u)) {
        return 0u;
    }
    backend = dsys_active_backend();
    if (backend->file_write) {
        return backend->file_write(fh, buf, size);
    }
    return 0u;
}

int dsys_file_seek(void* fh, long offset, int origin)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_file_path(fh);
    if (dsys_guard_io_blocked("file_seek", path, NULL, 0u)) {
        return -1;
    }
    backend = dsys_active_backend();
    if (backend->file_seek) {
        return backend->file_seek(fh, offset, origin);
    }
    return -1;
}

long dsys_file_tell(void* fh)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_file_path(fh);
    if (dsys_guard_io_blocked("file_tell", path, NULL, 0u)) {
        return -1L;
    }
    backend = dsys_active_backend();
    if (backend->file_tell) {
        return backend->file_tell(fh);
    }
    return -1L;
}

int dsys_file_close(void* fh)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_file_path(fh);
    if (dsys_guard_io_blocked("file_close", path, NULL, 0u)) {
        dsys_guard_untrack_file_handle(fh);
        return -1;
    }
    backend = dsys_active_backend();
    if (backend->file_close) {
        int rc = backend->file_close(fh);
        dsys_guard_untrack_file_handle(fh);
        return rc;
    }
    dsys_guard_untrack_file_handle(fh);
    return -1;
}

dsys_dir_iter* dsys_dir_open(const char* path)
{
    const dsys_backend_vtable* backend;
    if (dsys_guard_io_blocked("dir_open", path, NULL, 0u)) {
        return NULL;
    }
    backend = dsys_active_backend();
    if (backend->dir_open) {
        dsys_dir_iter* it = backend->dir_open(path);
        if (it) {
            dsys_guard_track_dir_handle(it, path);
        }
        return it;
    }
    return NULL;
}

bool dsys_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_dir_path(it);
    if (dsys_guard_io_blocked("dir_next", path, NULL, 0u)) {
        return false;
    }
    backend = dsys_active_backend();
    if (backend->dir_next) {
        return backend->dir_next(it, out);
    }
    return false;
}

void dsys_dir_close(dsys_dir_iter* it)
{
    const dsys_backend_vtable* backend;
    const char* path = dsys_guard_lookup_dir_path(it);
    if (dsys_guard_io_blocked("dir_close", path, NULL, 0u)) {
        dsys_guard_untrack_dir_handle(it);
        return;
    }
    backend = dsys_active_backend();
    if (backend->dir_close) {
        backend->dir_close(it);
    }
    dsys_guard_untrack_dir_handle(it);
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

static dom_abi_result dsys_core_query_interface(dom_iid iid, void** out_iface)
{
    if (!out_iface) {
        return DSYS_ERR;
    }
    *out_iface = NULL;

    switch (iid) {
    case DSYS_IID_FS_API_V1:
        *out_iface = (void*)&g_dsys_fs_api_v1;
        return DSYS_OK;
    case DSYS_IID_TIME_API_V1:
        *out_iface = (void*)&g_dsys_time_api_v1;
        return DSYS_OK;
    case DSYS_IID_PROCESS_API_V1:
        *out_iface = (void*)&g_dsys_process_api_v1;
        return DSYS_OK;
    case DSYS_IID_DYNLIB_API_V1:
        *out_iface = (void*)&g_dsys_dynlib_api_v1;
        return DSYS_OK;
    case DSYS_IID_WINDOW_API_V1:
        *out_iface = (void*)&g_dsys_window_api_v1;
        return DSYS_OK;
    case DSYS_IID_INPUT_API_V1:
        *out_iface = (void*)&g_dsys_input_api_v1;
        return DSYS_OK;
    case DSYS_IID_WINDOW_EX_API_V1:
        *out_iface = (void*)&g_dsys_window_ex_api_v1;
        return DSYS_OK;
    case DSYS_IID_ERROR_API_V1:
        *out_iface = (void*)&g_dsys_error_api_v1;
        return DSYS_OK;
    case DSYS_IID_CLIPTEXT_API_V1:
        *out_iface = (void*)&g_dsys_cliptext_api_v1;
        return DSYS_OK;
    case DSYS_IID_CURSOR_API_V1:
        *out_iface = (void*)&g_dsys_cursor_api_v1;
        return DSYS_OK;
    case DSYS_IID_DRAGDROP_API_V1:
        *out_iface = (void*)&g_dsys_dragdrop_api_v1;
        return DSYS_OK;
    case DSYS_IID_GAMEPAD_API_V1:
        *out_iface = (void*)&g_dsys_gamepad_api_v1;
        return DSYS_OK;
    case DSYS_IID_POWER_API_V1:
        *out_iface = (void*)&g_dsys_power_api_v1;
        return DSYS_OK;
    default:
        break;
    }

    return DSYS_ERR_UNSUPPORTED;
}

dsys_result dsys_get_core_api(u32 requested_abi, dsys_core_api_v1* out)
{
    dsys_clear_last_error();
    if (!out) {
        dsys_set_last_error(DSYS_ERR, "dsys_get_core_api: null out");
        return DSYS_ERR;
    }
    if (requested_abi != g_dsys_core_api_v1.abi_version) {
        dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "dsys_get_core_api: unsupported abi");
        return DSYS_ERR_UNSUPPORTED;
    }
    *out = g_dsys_core_api_v1;
    return DSYS_OK;
}

void* dsys_query_extension(const char* name, u32 version)
{
    dsys_clear_last_error();
    if (!name || !name[0]) {
        dsys_set_last_error(DSYS_ERR, "dsys_query_extension: null name");
        return NULL;
    }
    if (version != 1u) {
        dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "dsys_query_extension: unsupported version");
        return NULL;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_WINDOW_EX)) {
        return (void*)&g_dsys_window_ex_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_DPI)) {
        return (void*)&g_dsys_window_ex_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_ERROR)) {
        return (void*)&g_dsys_error_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_CLIPTEXT)) {
#if defined(_WIN32)
        return (void*)&g_dsys_cliptext_api_v1;
#else
        dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "dsys_query_extension: unsupported");
        return NULL;
#endif
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_CURSOR)) {
#if defined(_WIN32)
        return (void*)&g_dsys_cursor_api_v1;
#else
        dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "dsys_query_extension: unsupported");
        return NULL;
#endif
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_TEXT_INPUT)) {
        return (void*)&g_dsys_text_input_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_WINDOW_MODE)) {
        return (void*)&g_dsys_window_mode_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_DRAGDROP)) {
        return (void*)&g_dsys_dragdrop_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_GAMEPAD)) {
        return (void*)&g_dsys_gamepad_api_v1;
    }
    if (dsys_str_ieq(name, DSYS_EXTENSION_POWER)) {
        return (void*)&g_dsys_power_api_v1;
    }
    dsys_set_last_error(DSYS_ERR_UNSUPPORTED, "dsys_query_extension: unsupported");
    return NULL;
}

dsys_result dsys_last_error_code(void)
{
    return g_dsys_last_error_code;
}

const char* dsys_last_error_text(void)
{
    return g_dsys_last_error_text;
}

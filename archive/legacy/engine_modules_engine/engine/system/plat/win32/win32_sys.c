/*
FILE: source/domino/system/plat/win32/win32_sys.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/win32/win32_sys
RESPONSIBILITY: Implements `win32_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "win32_sys.h"

#include "../../dsys_internal.h"

#if defined(_WIN32)
#include <windows.h>
#include <io.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static dsys_caps g_win32_caps = { "win32", 1u, true, true, false, true };
static dsys_caps g_win32_headless_caps = { "win32_headless", 0u, false, false, false, true };

static dsys_result win32_init(void);
static void        win32_shutdown(void);
static dsys_caps   win32_get_caps(void);
static dsys_caps   win32_headless_get_caps(void);

static uint64_t win32_time_now_us(void);
static void     win32_sleep_ms(uint32_t ms);

static dsys_window* win32_window_create(const dsys_window_desc* desc);
static void         win32_window_destroy(dsys_window* win);
static void         win32_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         win32_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         win32_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        win32_window_get_native_handle(dsys_window* win);

static bool win32_poll_event(dsys_event* ev);
static bool win32_headless_poll_event(dsys_event* ev);

static dsys_window* win32_headless_window_create(const dsys_window_desc* desc);
static void         win32_headless_window_destroy(dsys_window* win);
static void         win32_headless_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         win32_headless_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         win32_headless_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        win32_headless_window_get_native_handle(dsys_window* win);

static bool   win32_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  win32_file_open(const char* path, const char* mode);
static size_t win32_file_read(void* fh, void* buf, size_t size);
static size_t win32_file_write(void* fh, const void* buf, size_t size);
static int    win32_file_seek(void* fh, long offset, int origin);
static long   win32_file_tell(void* fh);
static int    win32_file_close(void* fh);

static dsys_dir_iter* win32_dir_open(const char* path);
static bool           win32_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           win32_dir_close(dsys_dir_iter* it);

static dsys_process* win32_process_spawn(const dsys_process_desc* desc);
static int           win32_process_wait(dsys_process* p);
static void          win32_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_win32_vtable = {
    win32_init,
    win32_shutdown,
    win32_get_caps,
    win32_time_now_us,
    win32_sleep_ms,
    win32_window_create,
    win32_window_destroy,
    win32_window_set_mode,
    win32_window_set_size,
    win32_window_get_size,
    win32_window_get_native_handle,
    win32_poll_event,
    win32_get_path,
    win32_file_open,
    win32_file_read,
    win32_file_write,
    win32_file_seek,
    win32_file_tell,
    win32_file_close,
    win32_dir_open,
    win32_dir_next,
    win32_dir_close,
    win32_process_spawn,
    win32_process_wait,
    win32_process_destroy
};

static const dsys_backend_vtable g_win32_headless_vtable = {
    win32_init,
    win32_shutdown,
    win32_headless_get_caps,
    win32_time_now_us,
    win32_sleep_ms,
    win32_headless_window_create,
    win32_headless_window_destroy,
    win32_headless_window_set_mode,
    win32_headless_window_set_size,
    win32_headless_window_get_size,
    win32_headless_window_get_native_handle,
    win32_headless_poll_event,
    win32_get_path,
    win32_file_open,
    win32_file_read,
    win32_file_write,
    win32_file_seek,
    win32_file_tell,
    win32_file_close,
    win32_dir_open,
    win32_dir_next,
    win32_dir_close,
    win32_process_spawn,
    win32_process_wait,
    win32_process_destroy
};

static uint64_t g_qpc_freq = 0u;
static uint64_t g_qpc_last_us = 0u;

#if defined(_WIN32)
enum {
    WIN32_DSYS_EVENT_CAP = 128
};

static dsys_event g_win32_events[WIN32_DSYS_EVENT_CAP];
static unsigned   g_win32_ev_r = 0u;
static unsigned   g_win32_ev_w = 0u;
#endif

static int win32_copy_path(const char* src, char* buf, size_t buf_size)
{
    size_t len;

    if (!src || !buf || buf_size == 0u) {
        return 0;
    }

    len = strlen(src);
    if (len >= buf_size) {
        len = buf_size - 1u;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return 1;
}

static void win32_join_path(char* dst, size_t cap, const char* base, const char* leaf)
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
        if (i > 0u && dst[i - 1u] != '/' && dst[i - 1u] != '\\' && i + 1u < cap) {
            dst[i] = '\\';
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

static void win32_dirname(char* path)
{
    size_t len;

    if (!path) {
        return;
    }

    len = strlen(path);
    while (len > 0u) {
        char c;
        c = path[len - 1u];
        if (c == '\\' || c == '/') {
            path[len - 1u] = '\0';
            return;
        }
        len -= 1u;
    }
}

static int win32_get_env(const char* name, char* buf, size_t buf_size)
{
#if defined(_WIN32)
    DWORD n;
    if (!name || !buf || buf_size == 0u) {
        return 0;
    }
    n = GetEnvironmentVariableA(name, buf, (DWORD)buf_size);
    if (n == 0u || n >= (DWORD)buf_size) {
        buf[0] = '\0';
        return 0;
    }
    return 1;
#else
    (void)name;
    if (buf && buf_size) {
        buf[0] = '\0';
    }
    return 0;
#endif
}

static int win32_get_temp(char* buf, size_t buf_size)
{
#if defined(_WIN32)
    DWORD n;
    if (!buf || buf_size == 0u) {
        return 0;
    }
    n = GetTempPathA((DWORD)buf_size, buf);
    if (n == 0u || n >= (DWORD)buf_size) {
        buf[0] = '\0';
        return 0;
    }
    /* Strip trailing slashes for consistency with other backends. */
    while (n > 0u && (buf[n - 1u] == '\\' || buf[n - 1u] == '/')) {
        buf[n - 1u] = '\0';
        n -= 1u;
    }
    return n > 0u ? 1 : 0;
#else
    (void)buf;
    (void)buf_size;
    return 0;
#endif
}

static dsys_result win32_init(void)
{
#if defined(_WIN32)
    LARGE_INTEGER freq;
    if (QueryPerformanceFrequency(&freq) && freq.QuadPart > 0) {
        g_qpc_freq = (uint64_t)freq.QuadPart;
        g_win32_caps.has_high_res_timer = true;
        g_win32_headless_caps.has_high_res_timer = true;
    } else {
        g_qpc_freq = 0u;
        g_win32_caps.has_high_res_timer = false;
        g_win32_headless_caps.has_high_res_timer = false;
    }
#endif
    g_qpc_last_us = 0u;
    g_win32_ev_r = 0u;
    g_win32_ev_w = 0u;
    return DSYS_OK;
}

static void win32_shutdown(void)
{
}

static dsys_caps win32_get_caps(void)
{
    return g_win32_caps;
}

static dsys_caps win32_headless_get_caps(void)
{
    return g_win32_headless_caps;
}

static uint64_t win32_qpc_us(void)
{
#if defined(_WIN32)
    LARGE_INTEGER now;
    uint64_t ticks;
    uint64_t freq;
    uint64_t sec;
    uint64_t rem;
    if (g_qpc_freq == 0u) {
        return 0u;
    }
    if (!QueryPerformanceCounter(&now)) {
        return 0u;
    }
    ticks = (uint64_t)now.QuadPart;
    freq = g_qpc_freq;
    sec = ticks / freq;
    rem = ticks % freq;
    return sec * 1000000u + (rem * 1000000u) / freq;
#else
    return 0u;
#endif
}

static uint64_t win32_time_now_us(void)
{
    uint64_t us;
#if defined(_WIN32)
    if (g_qpc_freq != 0u) {
        us = win32_qpc_us();
    } else {
        us = (uint64_t)GetTickCount64() * 1000u;
    }
#else
    us = 0u;
#endif
    if (us < g_qpc_last_us) {
        us = g_qpc_last_us;
    } else {
        g_qpc_last_us = us;
    }
    return us;
}

static void win32_sleep_ms(uint32_t ms)
{
#if defined(_WIN32)
    Sleep((DWORD)ms);
#else
    (void)ms;
#endif
}

#if defined(_WIN32)
typedef struct win32_window_impl {
    HWND hwnd;
    RECT windowed_rect;
    int  has_windowed_rect;
    int  should_close;
    int  last_x;
    int  last_y;
} win32_window_impl;

static const wchar_t* win32_class_name(void)
{
    return L"DominoDsysWin32";
}

static unsigned win32_ev_next(unsigned idx)
{
    return (idx + 1u) % (unsigned)WIN32_DSYS_EVENT_CAP;
}

static int win32_ev_empty(void)
{
    return g_win32_ev_r == g_win32_ev_w;
}

static void win32_ev_push(const dsys_event* ev)
{
    unsigned next;
    if (!ev) {
        return;
    }
    next = win32_ev_next(g_win32_ev_w);
    if (next == g_win32_ev_r) {
        /* Drop newest when full; deterministic under overflow. */
        return;
    }
    g_win32_events[g_win32_ev_w] = *ev;
    g_win32_ev_w = next;
}

static int win32_ev_pop(dsys_event* out)
{
    if (win32_ev_empty()) {
        return 0;
    }
    if (out) {
        *out = g_win32_events[g_win32_ev_r];
    }
    g_win32_ev_r = win32_ev_next(g_win32_ev_r);
    return 1;
}

static void win32_push_quit(void)
{
    dsys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_QUIT;
    win32_ev_push(&ev);
}

static void win32_push_resized(int32_t w, int32_t h)
{
    dsys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_WINDOW_RESIZED;
    ev.payload.window.width = w;
    ev.payload.window.height = h;
    win32_ev_push(&ev);
}

static void win32_push_key(int down, WPARAM vk, LPARAM lp)
{
    dsys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = down ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
    ev.payload.key.key = (int32_t)vk;
    ev.payload.key.repeat = down ? (((lp >> 30) & 1) ? true : false) : false;
    win32_ev_push(&ev);
}

static void win32_push_mouse_move(dsys_window* win, int x, int y)
{
    win32_window_impl* impl;
    dsys_event ev;

    if (!win) {
        return;
    }
    impl = (win32_window_impl*)win->native_handle;
    if (!impl) {
        return;
    }

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_MOVE;
    ev.payload.mouse_move.x = (int32_t)x;
    ev.payload.mouse_move.y = (int32_t)y;
    ev.payload.mouse_move.dx = (int32_t)(x - impl->last_x);
    ev.payload.mouse_move.dy = (int32_t)(y - impl->last_y);
    impl->last_x = x;
    impl->last_y = y;
    win32_ev_push(&ev);
}

static void win32_push_mouse_button(int button, int pressed, int clicks)
{
    dsys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_BUTTON;
    ev.payload.mouse_button.button = (int32_t)button;
    ev.payload.mouse_button.pressed = pressed ? true : false;
    ev.payload.mouse_button.clicks = (int32_t)clicks;
    win32_ev_push(&ev);
}

static void win32_push_mouse_wheel(int dx, int dy)
{
    dsys_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_WHEEL;
    ev.payload.mouse_wheel.delta_x = (int32_t)dx;
    ev.payload.mouse_wheel.delta_y = (int32_t)dy;
    win32_ev_push(&ev);
}

static void win32_push_text_utf16(WPARAM wp)
{
    unsigned u;
    dsys_event ev;
    char out[8];

    u = (unsigned)(wp & 0xFFFFu);
    if (u >= 0xD800u && u <= 0xDFFFu) {
        return;
    }

    memset(out, 0, sizeof(out));
    if (u < 0x80u) {
        out[0] = (char)u;
    } else if (u < 0x800u) {
        out[0] = (char)(0xC0u | (u >> 6));
        out[1] = (char)(0x80u | (u & 0x3Fu));
    } else {
        out[0] = (char)(0xE0u | (u >> 12));
        out[1] = (char)(0x80u | ((u >> 6) & 0x3Fu));
        out[2] = (char)(0x80u | (u & 0x3Fu));
    }

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_TEXT_INPUT;
    memcpy(ev.payload.text.text, out, sizeof(ev.payload.text.text));
    win32_ev_push(&ev);
}

static LRESULT CALLBACK win32_wndproc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    dsys_window* win;
    win32_window_impl* impl;

    win = (dsys_window*)GetWindowLongPtrW(hwnd, GWLP_USERDATA);
    impl = win ? (win32_window_impl*)win->native_handle : NULL;

    switch (msg) {
    case WM_CLOSE:
        if (impl) {
            impl->should_close = 1;
        }
        win32_push_quit();
        DestroyWindow(hwnd);
        return 0;

    case WM_DESTROY:
        if (impl) {
            impl->should_close = 1;
        }
        return 0;

    case WM_SIZE:
        if (win) {
            win->width = (int32_t)(lp & 0xFFFF);
            win->height = (int32_t)((lp >> 16) & 0xFFFF);
            win32_push_resized(win->width, win->height);
        }
        return 0;

    case WM_KEYDOWN:
    case WM_SYSKEYDOWN:
        win32_push_key(1, wp, lp);
        return 0;

    case WM_KEYUP:
    case WM_SYSKEYUP:
        win32_push_key(0, wp, lp);
        return 0;

    case WM_CHAR:
        win32_push_text_utf16(wp);
        return 0;

    case WM_MOUSEMOVE:
        if (win) {
            int x;
            int y;
            x = (int)(short)(lp & 0xFFFF);
            y = (int)(short)((lp >> 16) & 0xFFFF);
            win32_push_mouse_move(win, x, y);
        }
        return 0;

    case WM_LBUTTONDOWN:
    case WM_LBUTTONUP:
        win32_push_mouse_button(1, (msg == WM_LBUTTONDOWN), 1);
        return 0;
    case WM_MBUTTONDOWN:
    case WM_MBUTTONUP:
        win32_push_mouse_button(2, (msg == WM_MBUTTONDOWN), 1);
        return 0;
    case WM_RBUTTONDOWN:
    case WM_RBUTTONUP:
        win32_push_mouse_button(3, (msg == WM_RBUTTONDOWN), 1);
        return 0;

    case WM_MOUSEWHEEL:
        {
            int delta;
            delta = (int)(short)((wp >> 16) & 0xFFFF);
            if (delta != 0) {
                win32_push_mouse_wheel(0, delta / 120);
            }
        }
        return 0;

    case WM_MOUSEHWHEEL:
        {
            int delta;
            delta = (int)(short)((wp >> 16) & 0xFFFF);
            if (delta != 0) {
                win32_push_mouse_wheel(delta / 120, 0);
            }
        }
        return 0;

    default:
        break;
    }

    return DefWindowProcW(hwnd, msg, wp, lp);
}

static ATOM win32_register_class(void)
{
    static ATOM s_atom = 0;
    WNDCLASSW wc;

    if (s_atom) {
        return s_atom;
    }
    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = win32_wndproc;
    wc.hInstance = GetModuleHandleW(NULL);
    wc.lpszClassName = win32_class_name();
    wc.hCursor = LoadCursorW(NULL, MAKEINTRESOURCEW(32512));
    s_atom = RegisterClassW(&wc);
    return s_atom;
}
#endif

static dsys_window* win32_window_create(const dsys_window_desc* desc)
{
#if defined(_WIN32)
    dsys_window_desc local;
    RECT rc;
    DWORD style;
    HWND hwnd;
    win32_window_impl* impl;
    dsys_window* win;

    if (!win32_register_class()) {
        return NULL;
    }

    if (desc) {
        local = *desc;
    } else {
        local.x = CW_USEDEFAULT;
        local.y = CW_USEDEFAULT;
        local.width = 640;
        local.height = 360;
        local.mode = DWIN_MODE_WINDOWED;
    }

    style = WS_OVERLAPPEDWINDOW;
    rc.left = 0;
    rc.top = 0;
    rc.right = (local.width > 0) ? local.width : 640;
    rc.bottom = (local.height > 0) ? local.height : 360;
    AdjustWindowRect(&rc, style, FALSE);

    hwnd = CreateWindowW(
        win32_class_name(),
        L"Dominium",
        style,
        local.x,
        local.y,
        rc.right - rc.left,
        rc.bottom - rc.top,
        NULL,
        NULL,
        GetModuleHandleW(NULL),
        NULL);
    if (!hwnd) {
        return NULL;
    }

    impl = (win32_window_impl*)malloc(sizeof(win32_window_impl));
    if (!impl) {
        DestroyWindow(hwnd);
        return NULL;
    }
    impl->hwnd = hwnd;
    impl->has_windowed_rect = 0;
    impl->should_close = 0;
    impl->last_x = 0;
    impl->last_y = 0;

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        DestroyWindow(hwnd);
        free(impl);
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->native_handle = impl;
    win->width = local.width;
    win->height = local.height;
    win->mode = local.mode;

    SetWindowLongPtrW(hwnd, GWLP_USERDATA, (LONG_PTR)win);
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);
    return win;
#else
    (void)desc;
    return NULL;
#endif
}

static void win32_window_destroy(dsys_window* win)
{
#if defined(_WIN32)
    win32_window_impl* impl;
    if (!win) {
        return;
    }
    impl = (win32_window_impl*)win->native_handle;
    if (impl && impl->hwnd) {
        DestroyWindow(impl->hwnd);
    }
    free(impl);
    free(win);
#else
    (void)win;
#endif
}

static void win32_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
#if defined(_WIN32)
    win32_window_impl* impl;
    DWORD style;
    DWORD ex_style;
    int wants_fullscreen;

    if (!win) {
        return;
    }

    impl = (win32_window_impl*)win->native_handle;
    if (!impl || !impl->hwnd) {
        win->mode = mode;
        return;
    }

    wants_fullscreen = (mode == DWIN_MODE_FULLSCREEN || mode == DWIN_MODE_BORDERLESS) ? 1 : 0;

    if (win->mode == DWIN_MODE_WINDOWED && wants_fullscreen && !impl->has_windowed_rect) {
        if (GetWindowRect(impl->hwnd, &impl->windowed_rect)) {
            impl->has_windowed_rect = 1;
        }
    }

    style = wants_fullscreen ? (WS_POPUP | WS_VISIBLE) : (WS_OVERLAPPEDWINDOW | WS_VISIBLE);
    ex_style = (DWORD)GetWindowLongPtrW(impl->hwnd, GWL_EXSTYLE);
    SetWindowLongPtrW(impl->hwnd, GWL_STYLE, (LONG_PTR)style);
    SetWindowLongPtrW(impl->hwnd, GWL_EXSTYLE, (LONG_PTR)ex_style);

    if (wants_fullscreen) {
        HMONITOR mon;
        MONITORINFO mi;
        RECT mr;

        mon = MonitorFromWindow(impl->hwnd, MONITOR_DEFAULTTONEAREST);
        memset(&mi, 0, sizeof(mi));
        mi.cbSize = sizeof(mi);
        if (GetMonitorInfoW(mon, &mi)) {
            mr = mi.rcMonitor;
            SetWindowPos(impl->hwnd, HWND_TOP,
                         mr.left, mr.top,
                         mr.right - mr.left,
                         mr.bottom - mr.top,
                         SWP_FRAMECHANGED);
        } else {
            SetWindowPos(impl->hwnd, HWND_TOP, 0, 0, win->width, win->height, SWP_FRAMECHANGED);
        }
    } else if (impl->has_windowed_rect) {
        RECT r;
        r = impl->windowed_rect;
        SetWindowPos(impl->hwnd, HWND_NOTOPMOST,
                     r.left, r.top,
                     r.right - r.left,
                     r.bottom - r.top,
                     SWP_FRAMECHANGED);
    } else {
        win32_window_set_size(win, win->width, win->height);
    }

    win->mode = mode;
#else
    (void)win;
    (void)mode;
#endif
}

static void win32_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
#if defined(_WIN32)
    win32_window_impl* impl;
    RECT rc;
    DWORD style;

    if (!win) {
        return;
    }
    impl = (win32_window_impl*)win->native_handle;
    if (!impl || !impl->hwnd) {
        return;
    }
    style = (DWORD)GetWindowLongPtrW(impl->hwnd, GWL_STYLE);
    rc.left = 0;
    rc.top = 0;
    rc.right = (w > 0) ? w : 1;
    rc.bottom = (h > 0) ? h : 1;
    AdjustWindowRect(&rc, style, FALSE);
    SetWindowPos(impl->hwnd, NULL, 0, 0, rc.right - rc.left, rc.bottom - rc.top, SWP_NOMOVE | SWP_NOZORDER);
    win->width = w;
    win->height = h;
#else
    (void)win;
    (void)w;
    (void)h;
#endif
}

static void win32_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
#if defined(_WIN32)
    win32_window_impl* impl;
    RECT rc;
    if (!win) {
        if (w) *w = 0;
        if (h) *h = 0;
        return;
    }
    impl = (win32_window_impl*)win->native_handle;
    if (impl && impl->hwnd && GetClientRect(impl->hwnd, &rc)) {
        win->width = (int32_t)(rc.right - rc.left);
        win->height = (int32_t)(rc.bottom - rc.top);
    }
    if (w) *w = win->width;
    if (h) *h = win->height;
#else
    if (w) *w = win ? win->width : 0;
    if (h) *h = win ? win->height : 0;
#endif
}

static void* win32_window_get_native_handle(dsys_window* win)
{
#if defined(_WIN32)
    win32_window_impl* impl;
    if (!win) {
        return NULL;
    }
    impl = (win32_window_impl*)win->native_handle;
    return impl ? (void*)impl->hwnd : NULL;
#else
    (void)win;
    return NULL;
#endif
}

static dsys_window* win32_headless_window_create(const dsys_window_desc* desc)
{
    (void)desc;
    return NULL;
}

static void win32_headless_window_destroy(dsys_window* win)
{
    (void)win;
}

static void win32_headless_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    (void)win;
    (void)mode;
}

static void win32_headless_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    (void)win;
    (void)w;
    (void)h;
}

static void win32_headless_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    (void)win;
    if (w) *w = 0;
    if (h) *h = 0;
}

static void* win32_headless_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

static bool win32_headless_poll_event(dsys_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }
    return false;
}

static bool win32_poll_event(dsys_event* ev)
{
#if defined(_WIN32)
    MSG msg;
    unsigned pumped;

    if (win32_ev_pop(ev)) {
        return true;
    }

    pumped = 0u;
    while (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) {
            win32_push_quit();
            break;
        }
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
        pumped += 1u;
        if (!win32_ev_empty() || pumped >= 64u) {
            break;
        }
    }

    if (win32_ev_pop(ev)) {
        return true;
    }
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }
    return false;
#else
    (void)ev;
    return false;
#endif
}

static bool win32_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
#if defined(_WIN32)
    char tmp[260];

    if (!buf || buf_size == 0u) {
        return false;
    }
    buf[0] = '\0';

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        {
            DWORD n;
            n = GetModuleFileNameA(NULL, tmp, (DWORD)sizeof(tmp));
            if (n == 0u || n >= (DWORD)sizeof(tmp)) {
                return false;
            }
            tmp[sizeof(tmp) - 1u] = '\0';
            win32_dirname(tmp);
            return win32_copy_path(tmp, buf, buf_size) ? true : false;
        }

    case DSYS_PATH_USER_DATA:
        if (win32_get_env("LOCALAPPDATA", tmp, sizeof(tmp))) {
            char joined[260];
            win32_join_path(joined, sizeof(joined), tmp, "dominium\\data");
            return win32_copy_path(joined, buf, buf_size) ? true : false;
        }
        break;

    case DSYS_PATH_USER_CONFIG:
        if (win32_get_env("APPDATA", tmp, sizeof(tmp))) {
            char joined[260];
            win32_join_path(joined, sizeof(joined), tmp, "dominium\\config");
            return win32_copy_path(joined, buf, buf_size) ? true : false;
        }
        break;

    case DSYS_PATH_USER_CACHE:
        if (win32_get_env("LOCALAPPDATA", tmp, sizeof(tmp))) {
            char joined[260];
            win32_join_path(joined, sizeof(joined), tmp, "dominium\\cache");
            return win32_copy_path(joined, buf, buf_size) ? true : false;
        }
        break;

    case DSYS_PATH_TEMP:
        if (win32_get_temp(tmp, sizeof(tmp))) {
            return win32_copy_path(tmp, buf, buf_size) ? true : false;
        }
        break;

    default:
        break;
    }

    return false;
#else
    (void)kind;
    if (buf && buf_size) {
        buf[0] = '\0';
    }
    return false;
#endif
}

static void* win32_file_open(const char* path, const char* mode)
{
    if (!path || !mode) {
        return NULL;
    }
    return (void*)fopen(path, mode);
}

static size_t win32_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t win32_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int win32_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long win32_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int win32_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* win32_dir_open(const char* path)
{
#if defined(_WIN32)
    dsys_dir_iter* it;
    size_t len;

    if (!path) {
        return NULL;
    }

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
#else
    (void)path;
    return NULL;
#endif
}

static bool win32_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
#if defined(_WIN32)
    int res;

    if (!it || !out) {
        return false;
    }

    for (;;) {
        if (it->first_pending) {
            it->first_pending = 0;
            res = 0;
        } else {
            res = _findnext(it->handle, &it->data);
        }
        if (res != 0) {
            return false;
        }
        if (strcmp(it->data.name, ".") == 0 || strcmp(it->data.name, "..") == 0) {
            continue;
        }
        strncpy(out->name, it->data.name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = (it->data.attrib & _A_SUBDIR) != 0 ? true : false;
        return true;
    }
#else
    (void)it;
    (void)out;
    return false;
#endif
}

static void win32_dir_close(dsys_dir_iter* it)
{
#if defined(_WIN32)
    if (!it) {
        return;
    }
    if (it->handle != -1) {
        _findclose(it->handle);
    }
    free(it);
#else
    (void)it;
#endif
}

static dsys_process* win32_process_spawn(const dsys_process_desc* desc)
{
#if defined(_WIN32)
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    const char* const* argv;
    const char* argv_local[2];
    size_t total;
    size_t i;
    char* cmdline;
    BOOL ok;
    dsys_process* proc;

    if (!desc || !desc->exe) {
        return NULL;
    }

    argv = desc->argv;
    if (!argv || !argv[0]) {
        argv_local[0] = desc->exe;
        argv_local[1] = NULL;
        argv = argv_local;
    }

    total = 0u;
    for (i = 0u; argv[i]; ++i) {
        size_t n;
        n = strlen(argv[i]);
        total += (n * 2u) + 3u; /* worst-case quoting/escaping + space */
    }

    cmdline = (char*)malloc(total + 1u);
    if (!cmdline) {
        return NULL;
    }
    cmdline[0] = '\0';

    for (i = 0u; argv[i]; ++i) {
        const char* a;
        int needs_quotes;
        size_t len;
        size_t out_len;
        size_t bs_run;
        if (i > 0u) {
            strcat(cmdline, " ");
        }

        a = argv[i];
        needs_quotes = 0;
        for (len = 0u; a[len]; ++len) {
            char c;
            c = a[len];
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '"') {
                needs_quotes = 1;
                break;
            }
        }

        out_len = strlen(cmdline);
        if (!needs_quotes) {
            strcat(cmdline, a);
            continue;
        }

        cmdline[out_len++] = '"';
        cmdline[out_len] = '\0';

        bs_run = 0u;
        while (*a) {
            if (*a == '\\') {
                bs_run += 1u;
                ++a;
                continue;
            }
            if (*a == '"') {
                size_t k;
                for (k = 0u; k < bs_run * 2u + 1u; ++k) {
                    cmdline[out_len++] = '\\';
                }
                cmdline[out_len++] = '"';
                cmdline[out_len] = '\0';
                bs_run = 0u;
                ++a;
                continue;
            }
            while (bs_run) {
                cmdline[out_len++] = '\\';
                bs_run -= 1u;
            }
            cmdline[out_len++] = *a;
            cmdline[out_len] = '\0';
            ++a;
        }
        while (bs_run) {
            cmdline[out_len++] = '\\';
            bs_run -= 1u;
        }
        cmdline[out_len++] = '"';
        cmdline[out_len] = '\0';
    }

    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);
    memset(&pi, 0, sizeof(pi));

    ok = CreateProcessA(NULL,
                        cmdline,
                        NULL,
                        NULL,
                        FALSE,
                        0,
                        NULL,
                        NULL,
                        &si,
                        &pi);
    free(cmdline);

    if (!ok) {
        return NULL;
    }

    CloseHandle(pi.hThread);

    proc = (dsys_process*)malloc(sizeof(dsys_process));
    if (!proc) {
        TerminateProcess(pi.hProcess, 1u);
        CloseHandle(pi.hProcess);
        return NULL;
    }
    proc->handle = (void*)pi.hProcess;
    return proc;
#else
    (void)desc;
    return NULL;
#endif
}

static int win32_process_wait(dsys_process* p)
{
#if defined(_WIN32)
    HANDLE h;
    DWORD code;
    DWORD wait_res;

    if (!p || !p->handle) {
        return -1;
    }

    h = (HANDLE)p->handle;
    wait_res = WaitForSingleObject(h, INFINITE);
    if (wait_res != WAIT_OBJECT_0) {
        return -1;
    }
    code = 0u;
    if (!GetExitCodeProcess(h, &code)) {
        return -1;
    }
    CloseHandle(h);
    p->handle = NULL;
    return (int)code;
#else
    (void)p;
    return -1;
#endif
}

static void win32_process_destroy(dsys_process* p)
{
    if (!p) {
        return;
    }
#if defined(_WIN32)
    if (p->handle) {
        CloseHandle((HANDLE)p->handle);
        p->handle = NULL;
    }
#endif
    free(p);
}

const dsys_backend_vtable* dsys_win32_get_vtable(void)
{
    return &g_win32_vtable;
}

const dsys_backend_vtable* dsys_win32_headless_get_vtable(void)
{
    return &g_win32_headless_vtable;
}

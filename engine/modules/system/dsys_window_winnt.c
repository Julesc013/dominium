/*
FILE: source/domino/system/dsys_window_winnt.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_window_winnt
RESPONSIBILITY: Implements Win32 DSYS backend windowing and event pump.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Windowing is best-effort; input events are ordered but non-deterministic across OS.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#define DOMINO_SYS_INTERNAL 1
#include "domino/system/dsys.h"
#include "dsys_internal.h"
#include "dsys_dir_sorted.h"

#if defined(_WIN32)
#include <windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <io.h>

#ifndef WM_DPICHANGED
#define WM_DPICHANGED 0x02E0
#endif

typedef struct dsys_window_impl {
    HWND hwnd;
    int should_close;
    int focused;
    int minimized;
    int maximized;
    float dpi_scale;
    dsys_window* owner;
    int last_mouse_x;
    int last_mouse_y;
} dsys_window_impl;

static LARGE_INTEGER g_win32_perf_freq;
static uint64_t dsys_win32_time_now_us(void);

static void dsys_win32_push_event(const dsys_event* ev)
{
    dsys_event local;
    if (!ev) {
        return;
    }
    local = *ev;
    if (local.timestamp_us == 0u) {
        local.timestamp_us = dsys_win32_time_now_us();
    }
    (void)dsys_internal_event_push(&local);
}

static void dsys_win32_event_init(dsys_event* ev, dsys_window_impl* impl)
{
    if (!ev) {
        return;
    }
    memset(ev, 0, sizeof(*ev));
    if (impl && impl->owner) {
        ev->window = impl->owner;
        ev->window_id = impl->owner->window_id;
    }
}

static int dsys_win32_pop_event(dsys_event* out)
{
    return dsys_internal_event_pop(out);
}

static UINT dsys_win32_query_dpi(HWND hwnd)
{
    typedef UINT (WINAPI *get_dpi_for_window_fn)(HWND);
    static get_dpi_for_window_fn fn = NULL;
    static int fn_checked = 0;
    UINT dpi = 96u;

    if (!fn_checked) {
        HMODULE user32 = GetModuleHandleA("user32.dll");
        if (user32) {
            fn = (get_dpi_for_window_fn)GetProcAddress(user32, "GetDpiForWindow");
        }
        fn_checked = 1;
    }
    if (fn) {
        dpi = fn(hwnd);
        if (dpi > 0u) {
            return dpi;
        }
    }
    {
        HDC dc = GetDC(hwnd);
        if (dc) {
            int cap = GetDeviceCaps(dc, LOGPIXELSX);
            if (cap > 0) {
                dpi = (UINT)cap;
            }
            ReleaseDC(hwnd, dc);
        }
    }
    return dpi;
}

static float dsys_win32_query_scale(HWND hwnd)
{
    UINT dpi = dsys_win32_query_dpi(hwnd);
    if (dpi == 0u) {
        return 1.0f;
    }
    return (float)dpi / 96.0f;
}

static HCURSOR dsys_win32_cursor_for_shape(dsys_cursor_shape shape)
{
    switch (shape) {
    case DSYS_CURSOR_IBEAM: return LoadCursor(NULL, IDC_IBEAM);
    case DSYS_CURSOR_HAND: return LoadCursor(NULL, IDC_HAND);
    case DSYS_CURSOR_SIZE_H: return LoadCursor(NULL, IDC_SIZEWE);
    case DSYS_CURSOR_SIZE_V: return LoadCursor(NULL, IDC_SIZENS);
    case DSYS_CURSOR_SIZE_ALL: return LoadCursor(NULL, IDC_SIZEALL);
    case DSYS_CURSOR_ARROW:
    default:
        break;
    }
    return LoadCursor(NULL, IDC_ARROW);
}

static const char* dsys_win_class_name(void)
{
    return "DominoDsysWindowClass";
}

static LRESULT CALLBACK dsys_win_proc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    dsys_window_impl* impl;
    impl = (dsys_window_impl*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    switch (msg) {
    case WM_CLOSE: {
        dsys_event ev;
        if (impl) {
            impl->should_close = 1;
        }
        dsys_win32_event_init(&ev, impl);
        ev.type = DSYS_EVENT_QUIT;
        dsys_win32_push_event(&ev);
        return 0;
    }
    case WM_DESTROY:
        if (impl) {
            impl->should_close = 1;
        }
        return 0;
    case WM_SETFOCUS:
        if (impl) {
            impl->focused = 1;
        }
        break;
    case WM_KILLFOCUS:
        if (impl) {
            impl->focused = 0;
        }
        break;
    case WM_SIZE:
        if (impl && impl->owner) {
            dsys_event ev;
            int width = (int)(short)LOWORD(lp);
            int height = (int)(short)HIWORD(lp);
            impl->minimized = (wp == SIZE_MINIMIZED) ? 1 : 0;
            impl->maximized = (wp == SIZE_MAXIMIZED) ? 1 : 0;
            impl->owner->width = (int32_t)width;
            impl->owner->height = (int32_t)height;
            dsys_win32_event_init(&ev, impl);
            ev.type = DSYS_EVENT_WINDOW_RESIZED;
            ev.payload.window.width = (int32_t)width;
            ev.payload.window.height = (int32_t)height;
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_KEYDOWN:
    case WM_SYSKEYDOWN:
    case WM_KEYUP:
    case WM_SYSKEYUP:
        if (impl) {
            dsys_event ev;
            dsys_win32_event_init(&ev, impl);
            ev.type = (msg == WM_KEYDOWN || msg == WM_SYSKEYDOWN)
                ? DSYS_EVENT_KEY_DOWN
                : DSYS_EVENT_KEY_UP;
            ev.payload.key.key = (int32_t)wp;
            ev.payload.key.repeat = ((lp & (1 << 30)) != 0) ? true : false;
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_CHAR:
        if (impl) {
            dsys_event ev;
            unsigned int ch = (unsigned int)wp;
            dsys_win32_event_init(&ev, impl);
            ev.type = DSYS_EVENT_TEXT_INPUT;
            if (ch > 0u && ch < 0x80u) {
                ev.payload.text.text[0] = (char)ch;
                ev.payload.text.text[1] = '\0';
            } else {
                ev.payload.text.text[0] = '\0';
            }
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_MOUSEMOVE:
        if (impl) {
            dsys_event ev;
            int x = (int)(short)LOWORD(lp);
            int y = (int)(short)HIWORD(lp);
            if (impl->owner && impl->owner->relative_mouse) {
                impl->last_mouse_x = x;
                impl->last_mouse_y = y;
                break;
            }
            dsys_win32_event_init(&ev, impl);
            ev.type = DSYS_EVENT_MOUSE_MOVE;
            ev.payload.mouse_move.x = (int32_t)x;
            ev.payload.mouse_move.y = (int32_t)y;
            ev.payload.mouse_move.dx = (int32_t)(x - impl->last_mouse_x);
            ev.payload.mouse_move.dy = (int32_t)(y - impl->last_mouse_y);
            impl->last_mouse_x = x;
            impl->last_mouse_y = y;
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_LBUTTONDOWN:
    case WM_LBUTTONUP:
    case WM_RBUTTONDOWN:
    case WM_RBUTTONUP:
    case WM_MBUTTONDOWN:
    case WM_MBUTTONUP:
    case WM_XBUTTONDOWN:
    case WM_XBUTTONUP:
        if (impl) {
            dsys_event ev;
            int pressed = (msg == WM_LBUTTONDOWN || msg == WM_RBUTTONDOWN ||
                           msg == WM_MBUTTONDOWN || msg == WM_XBUTTONDOWN);
            int button = 0;
            if (msg == WM_LBUTTONDOWN || msg == WM_LBUTTONUP) button = 1;
            else if (msg == WM_RBUTTONDOWN || msg == WM_RBUTTONUP) button = 2;
            else if (msg == WM_MBUTTONDOWN || msg == WM_MBUTTONUP) button = 3;
            else if (msg == WM_XBUTTONDOWN || msg == WM_XBUTTONUP) {
                int xbtn = (int)HIWORD(wp);
                button = (xbtn == XBUTTON2) ? 5 : 4;
            }
            dsys_win32_event_init(&ev, impl);
            ev.type = DSYS_EVENT_MOUSE_BUTTON;
            ev.payload.mouse_button.button = (int32_t)button;
            ev.payload.mouse_button.pressed = pressed ? true : false;
            ev.payload.mouse_button.clicks = 1;
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_MOUSEWHEEL:
    case WM_MOUSEHWHEEL:
        if (impl) {
            dsys_event ev;
            int delta = (short)HIWORD(wp);
            dsys_win32_event_init(&ev, impl);
            ev.type = DSYS_EVENT_MOUSE_WHEEL;
            if (msg == WM_MOUSEHWHEEL) {
                ev.payload.mouse_wheel.delta_x = (int32_t)(delta / WHEEL_DELTA);
                ev.payload.mouse_wheel.delta_y = 0;
            } else {
                ev.payload.mouse_wheel.delta_x = 0;
                ev.payload.mouse_wheel.delta_y = (int32_t)(delta / WHEEL_DELTA);
            }
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_DPICHANGED:
        if (impl) {
            dsys_event ev;
            UINT dpi = (UINT)HIWORD(wp);
            if (dpi == 0u) {
                dpi = (UINT)LOWORD(wp);
            }
            if (dpi == 0u) {
                dpi = dsys_win32_query_dpi(hwnd);
            }
            impl->dpi_scale = (dpi > 0u) ? ((float)dpi / 96.0f) : 1.0f;
            if (lp) {
                RECT* rc = (RECT*)lp;
                SetWindowPos(hwnd, NULL,
                             rc->left, rc->top,
                             rc->right - rc->left,
                             rc->bottom - rc->top,
                             SWP_NOZORDER | SWP_NOACTIVATE);
            }
            dsys_win32_event_init(&ev, impl);
            ev.type = DSYS_EVENT_DPI_CHANGED;
            ev.payload.dpi.scale = impl->dpi_scale;
            dsys_win32_push_event(&ev);
        }
        break;
    case WM_INPUT:
        if (impl && impl->owner && impl->owner->relative_mouse) {
            UINT size = 0u;
            if (GetRawInputData((HRAWINPUT)lp, RID_INPUT, NULL, &size, sizeof(RAWINPUTHEADER)) == 0 && size > 0u) {
                unsigned char stack_buf[128];
                void* heap_buf = NULL;
                RAWINPUT* raw = (RAWINPUT*)stack_buf;
                if (size > sizeof(stack_buf)) {
                    heap_buf = malloc(size);
                    raw = (RAWINPUT*)heap_buf;
                }
                if (raw) {
                    if (GetRawInputData((HRAWINPUT)lp, RID_INPUT, raw, &size, sizeof(RAWINPUTHEADER)) == size) {
                        if (raw->header.dwType == RIM_TYPEMOUSE) {
                            int dx = (int)raw->data.mouse.lLastX;
                            int dy = (int)raw->data.mouse.lLastY;
                            if (dx != 0 || dy != 0) {
                                dsys_event ev;
                                impl->last_mouse_x += dx;
                                impl->last_mouse_y += dy;
                                dsys_win32_event_init(&ev, impl);
                                ev.type = DSYS_EVENT_MOUSE_MOVE;
                                ev.payload.mouse_move.x = (int32_t)impl->last_mouse_x;
                                ev.payload.mouse_move.y = (int32_t)impl->last_mouse_y;
                                ev.payload.mouse_move.dx = (int32_t)dx;
                                ev.payload.mouse_move.dy = (int32_t)dy;
                                dsys_win32_push_event(&ev);
                            }
                        }
                    }
                }
                if (heap_buf) {
                    free(heap_buf);
                }
            }
            return 0;
        }
        break;
    case WM_SETCURSOR:
        if (impl && impl->owner) {
            HCURSOR cursor = dsys_win32_cursor_for_shape((dsys_cursor_shape)impl->owner->cursor_shape);
            if (cursor) {
                SetCursor(cursor);
                return TRUE;
            }
        }
        break;
    default:
        break;
    }
    return DefWindowProc(hwnd, msg, wp, lp);
}

static ATOM dsys_win_register_class(void)
{
    static ATOM s_atom = 0;
    if (s_atom != 0) {
        return s_atom;
    }
    {
        WNDCLASSA wc;
        ZeroMemory(&wc, sizeof(wc));
        wc.lpfnWndProc = dsys_win_proc;
        wc.hInstance = GetModuleHandleA(NULL);
        wc.lpszClassName = dsys_win_class_name();
        wc.hCursor = LoadCursor(NULL, IDC_ARROW);
        s_atom = RegisterClassA(&wc);
    }
    return s_atom;
}

static DWORD dsys_win_style(int resizable)
{
    DWORD style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX;
    if (resizable) {
        style |= WS_THICKFRAME | WS_MAXIMIZEBOX;
    }
    return style;
}

static void dsys_win32_apply_mode(dsys_window* win, dsys_window_impl* impl)
{
    DWORD style;
    if (!win || !impl || !impl->hwnd) {
        return;
    }
    if (win->mode == DWIN_MODE_BORDERLESS || win->mode == DWIN_MODE_FULLSCREEN) {
        style = WS_POPUP;
    } else {
        style = dsys_win_style(1);
    }
    SetWindowLong(impl->hwnd, GWL_STYLE, (LONG)style);
    if (win->mode == DWIN_MODE_FULLSCREEN) {
        int w = GetSystemMetrics(SM_CXSCREEN);
        int h = GetSystemMetrics(SM_CYSCREEN);
        SetWindowPos(impl->hwnd, HWND_TOP, 0, 0, w, h,
                     SWP_NOACTIVATE | SWP_FRAMECHANGED);
    } else {
        SetWindowPos(impl->hwnd, NULL, 0, 0, 0, 0,
                     SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED);
    }
}

static dsys_window* dsys_win32_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local;
    RECT rect;
    DWORD style;
    HWND hwnd;
    dsys_window_impl* impl;
    dsys_window* win;
    const char* title = "Dominium";
    int resizable = 1;

    if (!dsys_win_register_class()) {
        return NULL;
    }

    if (desc) {
        local = *desc;
    } else {
        local.x = CW_USEDEFAULT;
        local.y = CW_USEDEFAULT;
        local.width = 800;
        local.height = 600;
        local.mode = DWIN_MODE_WINDOWED;
    }

    style = dsys_win_style(resizable);
    rect.left = 0;
    rect.top = 0;
    rect.right = local.width > 0 ? local.width : 800;
    rect.bottom = local.height > 0 ? local.height : 600;
    AdjustWindowRect(&rect, style, FALSE);

    hwnd = CreateWindowExA(
        0,
        dsys_win_class_name(),
        title,
        style,
        local.x,
        local.y,
        rect.right - rect.left,
        rect.bottom - rect.top,
        NULL,
        NULL,
        GetModuleHandleA(NULL),
        NULL);

    if (!hwnd) {
        return NULL;
    }

    impl = (dsys_window_impl*)malloc(sizeof(dsys_window_impl));
    if (!impl) {
        DestroyWindow(hwnd);
        return NULL;
    }
    memset(impl, 0, sizeof(*impl));
    impl->hwnd = hwnd;
    impl->dpi_scale = dsys_win32_query_scale(hwnd);

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
    impl->owner = win;

    SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)impl);
    dsys_win32_apply_mode(win, impl);

    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    return win;
}

static void dsys_win32_window_destroy(dsys_window* win)
{
    dsys_window_impl* impl;
    if (!win) {
        return;
    }
    impl = (dsys_window_impl*)win->native_handle;
    if (impl && impl->hwnd) {
        DestroyWindow(impl->hwnd);
    }
    if (impl) {
        free(impl);
    }
    free(win);
}

static void dsys_win32_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    dsys_window_impl* impl;
    if (!win) {
        return;
    }
    win->mode = mode;
    impl = (dsys_window_impl*)win->native_handle;
    dsys_win32_apply_mode(win, impl);
}

static void dsys_win32_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    dsys_window_impl* impl;
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
    impl = (dsys_window_impl*)win->native_handle;
    if (impl && impl->hwnd && w > 0 && h > 0) {
        SetWindowPos(impl->hwnd, NULL, 0, 0, w, h,
                     SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE);
    }
}

static void dsys_win32_window_get_size(dsys_window* win, int32_t* out_w, int32_t* out_h)
{
    dsys_window_impl* impl;
    RECT rc;
    if (!win) {
        if (out_w) *out_w = 0;
        if (out_h) *out_h = 0;
        return;
    }
    impl = (dsys_window_impl*)win->native_handle;
    if (!impl || !impl->hwnd) {
        if (out_w) *out_w = win->width;
        if (out_h) *out_h = win->height;
        return;
    }
    if (!GetClientRect(impl->hwnd, &rc)) {
        if (out_w) *out_w = win->width;
        if (out_h) *out_h = win->height;
        return;
    }
    win->width = (int32_t)(rc.right - rc.left);
    win->height = (int32_t)(rc.bottom - rc.top);
    if (out_w) *out_w = win->width;
    if (out_h) *out_h = win->height;
}

static void dsys_win32_window_show(dsys_window* win)
{
    dsys_window_impl* impl;
    impl = win ? (dsys_window_impl*)win->native_handle : NULL;
    if (!impl || !impl->hwnd) {
        return;
    }
    ShowWindow(impl->hwnd, SW_SHOW);
}

static void dsys_win32_window_hide(dsys_window* win)
{
    dsys_window_impl* impl;
    impl = win ? (dsys_window_impl*)win->native_handle : NULL;
    if (!impl || !impl->hwnd) {
        return;
    }
    ShowWindow(impl->hwnd, SW_HIDE);
}

static void dsys_win32_window_get_state(dsys_window* win, dsys_window_state* out_state)
{
    dsys_window_impl* impl;
    if (!out_state) {
        return;
    }
    memset(out_state, 0, sizeof(*out_state));
    if (!win) {
        out_state->should_close = true;
        return;
    }
    impl = (dsys_window_impl*)win->native_handle;
    if (!impl || !impl->hwnd) {
        out_state->should_close = true;
        return;
    }
    out_state->should_close = impl->should_close ? true : false;
    out_state->focused = impl->focused ? true : false;
    out_state->minimized = IsIconic(impl->hwnd) ? true : false;
    out_state->maximized = IsZoomed(impl->hwnd) ? true : false;
    out_state->occluded = false;
}

static void dsys_win32_window_get_framebuffer_size(dsys_window* win, int32_t* out_w, int32_t* out_h)
{
    dsys_window_impl* impl;
    int32_t w = 0;
    int32_t h = 0;
    float scale = 1.0f;
    dsys_win32_window_get_size(win, &w, &h);
    impl = win ? (dsys_window_impl*)win->native_handle : NULL;
    if (impl) {
        scale = impl->dpi_scale;
    }
    if (out_w) *out_w = (int32_t)((float)w * scale);
    if (out_h) *out_h = (int32_t)((float)h * scale);
}

static float dsys_win32_window_get_dpi_scale(dsys_window* win)
{
    dsys_window_impl* impl;
    impl = win ? (dsys_window_impl*)win->native_handle : NULL;
    if (!impl || !impl->hwnd) {
        return 1.0f;
    }
    return impl->dpi_scale > 0.0f ? impl->dpi_scale : dsys_win32_query_scale(impl->hwnd);
}

static void* dsys_win32_window_get_native_handle(dsys_window* win)
{
    dsys_window_impl* impl;
    impl = win ? (dsys_window_impl*)win->native_handle : NULL;
    if (!impl) {
        return NULL;
    }
    return (void*)impl->hwnd;
}

static bool dsys_win32_poll_event(dsys_event* out)
{
    MSG msg;
    while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    if (dsys_win32_pop_event(out)) {
        return true;
    }
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static dsys_caps dsys_win32_get_caps(void)
{
    dsys_caps caps;
    caps.name = "win32";
    caps.ui_modes = 1u;
    caps.has_windows = true;
    caps.has_mouse = true;
    caps.has_gamepad = false;
    caps.has_high_res_timer = true;
    return caps;
}

static dsys_result dsys_win32_init(void)
{
    if (!QueryPerformanceFrequency(&g_win32_perf_freq)) {
        g_win32_perf_freq.QuadPart = 0;
    }
    return DSYS_OK;
}

static void dsys_win32_shutdown(void)
{
}

static uint64_t dsys_win32_time_now_us(void)
{
    LARGE_INTEGER now;
    if (g_win32_perf_freq.QuadPart == 0) {
        return (uint64_t)GetTickCount64() * 1000ull;
    }
    QueryPerformanceCounter(&now);
    return (uint64_t)((now.QuadPart * 1000000ull) / g_win32_perf_freq.QuadPart);
}

static void dsys_win32_sleep_ms(uint32_t ms)
{
    Sleep(ms);
}

static bool dsys_win32_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
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

static void* dsys_win32_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t dsys_win32_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t dsys_win32_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int dsys_win32_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long dsys_win32_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int dsys_win32_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* dsys_win32_dir_open(const char* path)
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

static bool dsys_win32_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    return dsys_dir_next_sorted(it, out);
}

static void dsys_win32_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    dsys_dir_free_sorted(it);
    free(it);
}

static dsys_process* dsys_win32_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int dsys_win32_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void dsys_win32_process_destroy(dsys_process* p)
{
    (void)p;
}

static const dsys_backend_vtable g_win32_vtable = {
    dsys_win32_init,
    dsys_win32_shutdown,
    dsys_win32_get_caps,
    dsys_win32_time_now_us,
    dsys_win32_sleep_ms,
    dsys_win32_window_create,
    dsys_win32_window_destroy,
    dsys_win32_window_set_mode,
    dsys_win32_window_set_size,
    dsys_win32_window_get_size,
    dsys_win32_window_show,
    dsys_win32_window_hide,
    dsys_win32_window_get_state,
    dsys_win32_window_get_framebuffer_size,
    dsys_win32_window_get_dpi_scale,
    dsys_win32_window_get_native_handle,
    dsys_win32_poll_event,
    dsys_win32_get_path,
    dsys_win32_file_open,
    dsys_win32_file_read,
    dsys_win32_file_write,
    dsys_win32_file_seek,
    dsys_win32_file_tell,
    dsys_win32_file_close,
    dsys_win32_dir_open,
    dsys_win32_dir_next,
    dsys_win32_dir_close,
    dsys_win32_process_spawn,
    dsys_win32_process_wait,
    dsys_win32_process_destroy
};

const dsys_backend_vtable* dsys_win32_get_vtable(void)
{
    return &g_win32_vtable;
}

#endif /* _WIN32 */

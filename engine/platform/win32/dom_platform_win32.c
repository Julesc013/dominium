#include "dom_platform_win32.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <stdlib.h>
#include <string.h>

struct DomPlatformWin32Window {
    HWND hwnd;
    dom_bool8 should_close;
    dom_u32 width;
    dom_u32 height;
};

static const char *g_dom_win32_class = "DominiumWin32Class";
static dom_i32 g_last_mouse_x = 0;
static dom_i32 g_last_mouse_y = 0;

static LRESULT CALLBACK dom_win32_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    DomPlatformWin32Window *win;
    win = (DomPlatformWin32Window *)GetWindowLongPtr(hwnd, GWLP_USERDATA);

    switch (msg) {
    case WM_DESTROY:
        if (win) {
            win->should_close = 1;
        }
        PostQuitMessage(0);
        return 0;
    case WM_CLOSE:
        if (win) {
            win->should_close = 1;
        }
        DestroyWindow(hwnd);
        return 0;
    case WM_SIZE:
        if (win) {
            win->width = LOWORD(lparam);
            win->height = HIWORD(lparam);
        }
        return 0;
    default:
        break;
    }

    return DefWindowProc(hwnd, msg, wparam, lparam);
}

static dom_bool8 dom_win32_register_class(HINSTANCE inst)
{
    WNDCLASSA wc;
    ATOM atom;

    if (GetClassInfoA(inst, g_dom_win32_class, &wc)) {
        return 1;
    }

    memset(&wc, 0, sizeof(wc));
    wc.style = CS_OWNDC;
    wc.lpfnWndProc = dom_win32_wndproc;
    wc.hInstance = inst;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = g_dom_win32_class;

    atom = RegisterClassA(&wc);
    return atom != 0;
}

dom_err_t dom_platform_win32_create_window(const char *title,
                                           dom_u32 width,
                                           dom_u32 height,
                                           dom_bool8 fullscreen,
                                           DomPlatformWin32Window **out_win)
{
    DomPlatformWin32Window *win;
    HINSTANCE inst;
    DWORD style;
    RECT rect;
    HWND hwnd;

    (void)fullscreen; /* fullscreen handled later; MVP windowed only */

    if (!out_win) {
        return DOM_ERR_INVALID_ARG;
    }

    inst = GetModuleHandle(NULL);
    if (!dom_win32_register_class(inst)) {
        return DOM_ERR_IO;
    }

    win = (DomPlatformWin32Window *)malloc(sizeof(DomPlatformWin32Window));
    if (!win) {
        return DOM_ERR_OUT_OF_MEMORY;
    }
    memset(win, 0, sizeof(*win));
    win->width = width;
    win->height = height;

    style = WS_OVERLAPPEDWINDOW | WS_VISIBLE;
    rect.left = 0;
    rect.top = 0;
    rect.right = (LONG)width;
    rect.bottom = (LONG)height;
    AdjustWindowRect(&rect, style, FALSE);

    hwnd = CreateWindowA(
        g_dom_win32_class,
        title ? title : "Dominium",
        style,
        CW_USEDEFAULT, CW_USEDEFAULT,
        rect.right - rect.left,
        rect.bottom - rect.top,
        NULL,
        NULL,
        inst,
        NULL);

    if (!hwnd) {
        free(win);
        return DOM_ERR_IO;
    }

    SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)win);
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    win->hwnd = hwnd;
    win->should_close = 0;
    *out_win = win;
    return DOM_OK;
}

void dom_platform_win32_destroy_window(DomPlatformWin32Window *win)
{
    if (!win) {
        return;
    }
    if (win->hwnd) {
        DestroyWindow(win->hwnd);
    }
    free(win);
}

void dom_platform_win32_pump_messages(DomPlatformWin32Window *win)
{
    MSG msg;
    (void)win;
    while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

dom_bool8 dom_platform_win32_should_close(const DomPlatformWin32Window *win)
{
    if (!win) {
        return 1;
    }
    return win->should_close;
}

void dom_platform_win32_get_size(const DomPlatformWin32Window *win,
                                 dom_u32 *width,
                                 dom_u32 *height)
{
    if (!win) {
        return;
    }
    if (width) {
        *width = win->width;
    }
    if (height) {
        *height = win->height;
    }
}

void *dom_platform_win32_native_handle(DomPlatformWin32Window *win)
{
    if (!win) {
        return 0;
    }
    return (void *)win->hwnd;
}

static void dom_platform_win32_poll_keys(dom_bool8 key_down[256])
{
    int i;
    if (!key_down) return;
    for (i = 0; i < 256; ++i) {
        SHORT state = GetAsyncKeyState(i);
        key_down[i] = (state & 0x8000) ? 1 : 0;
    }
}

void dom_platform_win32_poll_input(DomPlatformWin32Window *win,
                                   DomPlatformInputFrame *out_frame)
{
    POINT pt;
    if (!win || !out_frame) {
        return;
    }

    memset(out_frame, 0, sizeof(*out_frame));
    dom_platform_win32_poll_keys(out_frame->key_down);

    GetCursorPos(&pt);
    ScreenToClient(win->hwnd, &pt);
    out_frame->mouse_x = (dom_i32)pt.x;
    out_frame->mouse_y = (dom_i32)pt.y;
    out_frame->mouse_dx = out_frame->mouse_x - g_last_mouse_x;
    out_frame->mouse_dy = out_frame->mouse_y - g_last_mouse_y;
    g_last_mouse_x = out_frame->mouse_x;
    g_last_mouse_y = out_frame->mouse_y;

    /* Mouse wheel state is event-based; for MVP we ignore WM_MOUSEWHEEL accumulation. */
    out_frame->wheel_delta = 0;
}

dom_u64 dom_platform_win32_now_msec(void)
{
    static LARGE_INTEGER freq = {0};
    LARGE_INTEGER now;
    if (freq.QuadPart == 0) {
        QueryPerformanceFrequency(&freq);
        if (freq.QuadPart == 0) {
            return 0;
        }
    }
    QueryPerformanceCounter(&now);
    return (dom_u64)((now.QuadPart * (dom_u64)1000) / (dom_u64)freq.QuadPart);
}

void dom_platform_win32_sleep_msec(dom_u32 ms)
{
    Sleep(ms);
}

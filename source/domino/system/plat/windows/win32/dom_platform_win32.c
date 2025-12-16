/*
FILE: source/domino/system/plat/windows/win32/dom_platform_win32.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/windows/win32/dom_platform_win32
RESPONSIBILITY: Implements `dom_platform_win32`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

static const wchar_t *g_dom_win32_class = L"DominiumWin32Class";
static dom_i32 g_last_mouse_x = 0;
static dom_i32 g_last_mouse_y = 0;
static dom_i32 g_wheel_delta_accum = 0;

int dom_platform_win32_utf8_to_wide(const char *utf8, wchar_t *out_wide, int out_wide_chars)
{
    int count;
    if (!utf8 || !out_wide || out_wide_chars <= 0) {
        return 0;
    }
    count = MultiByteToWideChar(CP_UTF8, 0, utf8, -1, out_wide, out_wide_chars);
    if (count == 0 && GetLastError() == ERROR_INSUFFICIENT_BUFFER) {
        /* Truncate and null-terminate */
        out_wide[out_wide_chars - 1] = L'\0';
        return out_wide_chars - 1;
    }
    return count;
}

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
    case WM_MOUSEWHEEL:
        g_wheel_delta_accum += (dom_i32)((short)HIWORD(wparam));
        return 0;
    default:
        break;
    }

    return DefWindowProc(hwnd, msg, wparam, lparam);
}

static dom_bool8 dom_win32_register_class(HINSTANCE inst)
{
    WNDCLASSW wc;
    ATOM atom;

    if (GetClassInfoW(inst, g_dom_win32_class, &wc)) {
        return 1;
    }

    memset(&wc, 0, sizeof(wc));
    wc.style = CS_OWNDC;
    wc.lpfnWndProc = dom_win32_wndproc;
    wc.hInstance = inst;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = g_dom_win32_class;

    atom = RegisterClassW(&wc);
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
    wchar_t wtitle[256];

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

    dom_platform_win32_utf8_to_wide(title ? title : "Dominium", wtitle, (int)(sizeof(wtitle) / sizeof(wchar_t)));

    hwnd = CreateWindowW(
        g_dom_win32_class,
        wtitle,
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

static void dom_platform_win32_poll_keys(dom_bool8 key_down[DOM_KEYCODE_MAX])
{
    int i;
    if (!key_down) return;
    for (i = 0; i < DOM_KEYCODE_MAX; ++i) {
        SHORT state = GetAsyncKeyState(i);
        key_down[i] = (state & 0x8000) ? 1 : 0;
    }
}

static void dom_platform_win32_poll_mouse_buttons(dom_bool8 mouse_down[3])
{
    if (!mouse_down) return;
    mouse_down[0] = (GetAsyncKeyState(VK_LBUTTON) & 0x8000) ? 1 : 0;
    mouse_down[1] = (GetAsyncKeyState(VK_RBUTTON) & 0x8000) ? 1 : 0;
    mouse_down[2] = (GetAsyncKeyState(VK_MBUTTON) & 0x8000) ? 1 : 0;
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
    dom_platform_win32_poll_mouse_buttons(out_frame->mouse_down);

    GetCursorPos(&pt);
    ScreenToClient(win->hwnd, &pt);
    out_frame->mouse_x = (dom_i32)pt.x;
    out_frame->mouse_y = (dom_i32)pt.y;
    out_frame->mouse_dx = out_frame->mouse_x - g_last_mouse_x;
    out_frame->mouse_dy = out_frame->mouse_y - g_last_mouse_y;
    g_last_mouse_x = out_frame->mouse_x;
    g_last_mouse_y = out_frame->mouse_y;

    out_frame->wheel_delta = g_wheel_delta_accum;
    g_wheel_delta_accum = 0;
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

void dom_platform_win32_set_title(DomPlatformWin32Window *win, const char *title_utf8)
{
    wchar_t wide[256];
    if (!win || !title_utf8) {
        return;
    }
    dom_platform_win32_utf8_to_wide(title_utf8, wide, (int)(sizeof(wide) / sizeof(wchar_t)));
    SetWindowTextW(win->hwnd, wide);
}

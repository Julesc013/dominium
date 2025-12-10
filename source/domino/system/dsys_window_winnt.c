#include "domino/system/dsys.h"
#include "dsys_internal.h"

#if defined(_WIN32)
#include <windows.h>
#include <stdlib.h>
#include <string.h>

typedef struct dsys_window_impl {
    HWND hwnd;
    int  should_close;
} dsys_window_impl;

static const char* dsys_win_class_name(void) {
    return "DominoDsysWindowClass";
}

static ATOM dsys_win_register_class(void) {
    static ATOM s_atom = 0;
    if (s_atom != 0) {
        return s_atom;
    }
    {
        WNDCLASSA wc;
        ZeroMemory(&wc, sizeof(wc));
        wc.lpfnWndProc = DefWindowProcA;
        wc.hInstance = GetModuleHandleA(NULL);
        wc.lpszClassName = dsys_win_class_name();
        wc.hCursor = LoadCursor(NULL, IDC_ARROW);
        s_atom = RegisterClassA(&wc);
    }
    return s_atom;
}

static LRESULT CALLBACK dsys_win_proc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    dsys_window_impl* impl;
    impl = (dsys_window_impl*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    switch (msg) {
    case WM_CLOSE:
        if (impl) {
            impl->should_close = 1;
        }
        return 0;
    case WM_DESTROY:
        if (impl) {
            impl->should_close = 1;
        }
        return 0;
    default:
        break;
    }
    return DefWindowProc(hwnd, msg, wp, lp);
}

static DWORD dsys_win_style(int resizable) {
    DWORD style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX;
    if (resizable) {
        style |= WS_THICKFRAME | WS_MAXIMIZEBOX;
    }
    return style;
}

dsys_window* dsys_window_create(const dsys_window_desc* desc) {
    dsys_window_desc local;
    RECT rect;
    DWORD style;
    HWND hwnd;
    dsys_window_impl* impl;
    dsys_window* win;
    const char* title = "Domino Window";
    int resizable = 1;

    if (!dsys_win_register_class()) {
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

    style = dsys_win_style(resizable);
    rect.left = 0;
    rect.top = 0;
    rect.right = local.width > 0 ? local.width : 640;
    rect.bottom = local.height > 0 ? local.height : 360;
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
    impl->hwnd = hwnd;
    impl->should_close = 0;
    SetWindowLongPtr(hwnd, GWLP_WNDPROC, (LONG_PTR)dsys_win_proc);
    SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)impl);

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

    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    return win;
}

void dsys_window_destroy(dsys_window* win) {
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

int dsys_window_should_close(dsys_window* win) {
    MSG msg;
    dsys_window_impl* impl;
    if (!win) {
        return 1;
    }
    impl = (dsys_window_impl*)win->native_handle;
    if (!impl) {
        return 1;
    }
    while (PeekMessage(&msg, impl->hwnd, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return impl->should_close;
}

void dsys_window_present(dsys_window* win) {
    dsys_window_impl* impl;
    impl = win ? (dsys_window_impl*)win->native_handle : NULL;
    if (!impl || !impl->hwnd) {
        return;
    }
    /* No swap chain in stub; just ensure window pumps messages. */
    UpdateWindow(impl->hwnd);
}

void dsys_window_get_size(dsys_window* win, int32_t* out_w, int32_t* out_h) {
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

#endif /* _WIN32 */

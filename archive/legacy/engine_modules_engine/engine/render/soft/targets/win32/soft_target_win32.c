/*
FILE: source/domino/render/soft/targets/win32/soft_target_win32.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/targets/win32/soft_target_win32
RESPONSIBILITY: Implements `soft_target_win32`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "../../soft_internal.h"

#if defined(_WIN32)

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdlib.h>
#include <string.h>

typedef struct win32_soft_target {
    HWND  hwnd;
    HDC   hdc;
    BITMAPINFO bmi;
    int   width;
    int   height;
} win32_soft_target;

static LRESULT CALLBACK domino_soft_win32_proc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    if (msg == WM_DESTROY) {
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

static int win32_register_class(HINSTANCE inst)
{
    static int registered = 0;
    WNDCLASSA wc;
    if (registered) return 0;
    memset(&wc, 0, sizeof(wc));
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = domino_soft_win32_proc;
    wc.hInstance = inst;
    wc.lpszClassName = "DominoSoftWin32";
    if (!RegisterClassA(&wc)) {
        return -1;
    }
    registered = 1;
    return 0;
}

static int win32_init(domino_sys_context* sys, int width, int height, domino_pixfmt fmt, void** out_state)
{
    HINSTANCE inst = GetModuleHandle(NULL);
    HWND hwnd;
    RECT rect;
    win32_soft_target* st;
    (void)sys;
    (void)fmt;
    if (!out_state) return -1;
    *out_state = NULL;

    if (win32_register_class(inst) != 0) {
        return -1;
    }

    rect.left = 0; rect.top = 0; rect.right = width; rect.bottom = height;
    AdjustWindowRect(&rect, WS_OVERLAPPEDWINDOW, FALSE);

    hwnd = CreateWindowA("DominoSoftWin32",
                         "Domino Software Renderer",
                         WS_OVERLAPPEDWINDOW,
                         CW_USEDEFAULT, CW_USEDEFAULT,
                         rect.right - rect.left,
                         rect.bottom - rect.top,
                         NULL, NULL, inst, NULL);
    if (!hwnd) {
        return -1;
    }
    st = (win32_soft_target*)malloc(sizeof(win32_soft_target));
    if (!st) {
        DestroyWindow(hwnd);
        return -1;
    }
    st->hwnd = hwnd;
    st->hdc = GetDC(hwnd);
    st->width = width;
    st->height = height;

    memset(&st->bmi, 0, sizeof(st->bmi));
    st->bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    st->bmi.bmiHeader.biWidth = width;
    st->bmi.bmiHeader.biHeight = -height; /* top-down */
    st->bmi.bmiHeader.biPlanes = 1;
    st->bmi.bmiHeader.biBitCount = 32;
    st->bmi.bmiHeader.biCompression = BI_RGB;

    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    *out_state = st;
    return 0;
}

static void win32_shutdown(void* state)
{
    win32_soft_target* st = (win32_soft_target*)state;
    if (!st) return;
    if (st->hwnd && st->hdc) {
        ReleaseDC(st->hwnd, st->hdc);
    }
    if (st->hwnd) {
        DestroyWindow(st->hwnd);
    }
    free(st);
}

static int win32_present(void* state,
                         const void* pixels,
                         int width,
                         int height,
                         int stride_bytes)
{
    MSG msg;
    win32_soft_target* st = (win32_soft_target*)state;
    if (!st || !st->hdc) return -1;

    while (PeekMessage(&msg, st->hwnd, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    StretchDIBits(st->hdc,
                  0, 0, st->width, st->height,
                  0, 0, width, height,
                  pixels,
                  &st->bmi,
                  DIB_RGB_COLORS,
                  SRCCOPY);
    return 0;
}

static const domino_soft_target_ops g_win32_target = {
    "win32_gdi",
    win32_init,
    win32_shutdown,
    win32_present
};

const domino_soft_target_ops* domino_soft_target_win32(void)
{
    return &g_win32_target;
}

#else

const domino_soft_target_ops* domino_soft_target_win32(void)
{
    return domino_soft_target_null();
}

#endif

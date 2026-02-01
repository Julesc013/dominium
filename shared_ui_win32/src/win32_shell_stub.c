/*
FILE: shared_ui_win32/src/win32_shell_stub.c
MODULE: Dominium
PURPOSE: Minimal Win32 shell loop stub.
NOTES: Pure presentation; no business logic.
*/
#include "dom_ui_win32/ui_win32.h"

#if defined(_WIN32)
#include <windows.h>

static LRESULT CALLBACK domui_win32_stub_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    switch (msg) {
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    default:
        break;
    }
    return DefWindowProc(hwnd, msg, wparam, lparam);
}

int domui_win32_run_shell(const wchar_t* title)
{
    const wchar_t* class_name = L"DominiumAppShellStub";
    HINSTANCE inst = GetModuleHandleW(0);
    WNDCLASSW wc;
    HWND hwnd;
    MSG msg;

    ZeroMemory(&wc, sizeof(wc));
    wc.lpfnWndProc = domui_win32_stub_wndproc;
    wc.hInstance = inst;
    wc.lpszClassName = class_name;

    if (!RegisterClassW(&wc)) {
        return 1;
    }

    hwnd = CreateWindowExW(0, class_name,
                           title ? title : L"Dominium App Stub",
                           WS_OVERLAPPEDWINDOW,
                           CW_USEDEFAULT, CW_USEDEFAULT,
                           640, 480,
                           0, 0, inst, 0);
    if (!hwnd) {
        return 1;
    }
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    while (GetMessageW(&msg, 0, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return (int)msg.wParam;
}
#else
int domui_win32_run_shell(const wchar_t* title)
{
    (void)title;
    return 1;
}
#endif

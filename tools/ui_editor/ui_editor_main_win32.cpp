#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string.h>

static const char* kUiEditorWindowClass = "DominiumUiEditorStub";

static LRESULT CALLBACK ui_editor_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    (void)wparam;
    (void)lparam;
    if (msg == WM_DESTROY) {
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

int APIENTRY WinMain(HINSTANCE hinst, HINSTANCE hprev, LPSTR cmd, int show_cmd)
{
    WNDCLASSA wc;
    HWND hwnd;
    MSG msg;

    (void)hprev;
    (void)cmd;

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = ui_editor_wndproc;
    wc.hInstance = hinst;
    wc.lpszClassName = kUiEditorWindowClass;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);

    if (!RegisterClassA(&wc)) {
        return 1;
    }

    hwnd = CreateWindowA(
        kUiEditorWindowClass,
        "Dominium UI Editor (stub)",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        720,
        480,
        NULL,
        NULL,
        hinst,
        NULL);
    if (!hwnd) {
        return 1;
    }

    ShowWindow(hwnd, show_cmd);
    UpdateWindow(hwnd);

    while (GetMessageA(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    return (int)msg.wParam;
}
#else
#include <stdio.h>

int main(void)
{
    printf("dominium-ui-editor: not supported on this platform\n");
    return 0;
}
#endif

#include "d_system.h"

#include <stdlib.h>
#include <string.h>
#include "domino/sys.h"
#include "domino/core/types.h"
#include "d_system_input.h"

#if defined(_WIN32)
#include <windows.h>
#endif

static int g_system_initialized = 0;

#if defined(_WIN32)
static HWND g_hwnd = NULL;

static const char *d_system_class_name(void)
{
    return "DominoDSystemWindow";
}

static LRESULT CALLBACK d_system_wndproc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    d_sys_event ev;
    memset(&ev, 0, sizeof(ev));
    switch (msg) {
    case WM_CLOSE:
        PostQuitMessage(0);
        ev.type = D_SYS_EVENT_QUIT;
        d_system_input_enqueue(&ev);
        return 0;
    case WM_DESTROY:
        return 0;
    case WM_MOUSEMOVE:
        ev.type = D_SYS_EVENT_MOUSE_MOVE;
        ev.u.mouse.x = (i32)(short)LOWORD(lp);
        ev.u.mouse.y = (i32)(short)HIWORD(lp);
        d_system_input_enqueue(&ev);
        return 0;
    case WM_LBUTTONDOWN:
    case WM_RBUTTONDOWN:
    case WM_MBUTTONDOWN:
        ev.type = D_SYS_EVENT_MOUSE_BUTTON_DOWN;
        ev.u.mouse.button = (msg == WM_LBUTTONDOWN) ? 1 : (msg == WM_RBUTTONDOWN ? 2 : 3);
        ev.u.mouse.x = (i32)(short)LOWORD(lp);
        ev.u.mouse.y = (i32)(short)HIWORD(lp);
        d_system_input_enqueue(&ev);
        return 0;
    case WM_LBUTTONUP:
    case WM_RBUTTONUP:
    case WM_MBUTTONUP:
        ev.type = D_SYS_EVENT_MOUSE_BUTTON_UP;
        ev.u.mouse.button = (msg == WM_LBUTTONUP) ? 1 : (msg == WM_RBUTTONUP ? 2 : 3);
        ev.u.mouse.x = (i32)(short)LOWORD(lp);
        ev.u.mouse.y = (i32)(short)HIWORD(lp);
        d_system_input_enqueue(&ev);
        return 0;
    case WM_KEYDOWN:
    case WM_KEYUP: {
        int down = (msg == WM_KEYDOWN);
        d_sys_key key = D_SYS_KEY_UNKNOWN;
        switch (wp) {
        case VK_ESCAPE: key = D_SYS_KEY_ESCAPE; break;
        case VK_RETURN: key = D_SYS_KEY_ENTER; break;
        case VK_SPACE:  key = D_SYS_KEY_SPACE; break;
        case VK_BACK:   key = D_SYS_KEY_BACKSPACE; break;
        case '0': key = D_SYS_KEY_0; break;
        case '1': key = D_SYS_KEY_1; break;
        case '2': key = D_SYS_KEY_2; break;
        case '3': key = D_SYS_KEY_3; break;
        case '4': key = D_SYS_KEY_4; break;
        case '5': key = D_SYS_KEY_5; break;
        case '6': key = D_SYS_KEY_6; break;
        case '7': key = D_SYS_KEY_7; break;
        case '8': key = D_SYS_KEY_8; break;
        case '9': key = D_SYS_KEY_9; break;
        case VK_OEM_PERIOD: key = D_SYS_KEY_PERIOD; break;
        case 'W': case 'w': key = D_SYS_KEY_W; break;
        case 'A': case 'a': key = D_SYS_KEY_A; break;
        case 'S': case 's': key = D_SYS_KEY_S; break;
        case 'D': case 'd': key = D_SYS_KEY_D; break;
        case 'Q': case 'q': key = D_SYS_KEY_Q; break;
        case 'E': case 'e': key = D_SYS_KEY_E; break;
        case VK_UP:    key = D_SYS_KEY_UP; break;
        case VK_DOWN:  key = D_SYS_KEY_DOWN; break;
        case VK_LEFT:  key = D_SYS_KEY_LEFT; break;
        case VK_RIGHT: key = D_SYS_KEY_RIGHT; break;
        default:
            break;
        }
        if (key != D_SYS_KEY_UNKNOWN) {
            ev.type = down ? D_SYS_EVENT_KEY_DOWN : D_SYS_EVENT_KEY_UP;
            ev.u.key.key = key;
            d_system_input_enqueue(&ev);
            return 0;
        }
        break;
    }
    default:
        break;
    }
    return DefWindowProc(hwnd, msg, wp, lp);
}

static int d_system_register_class(void)
{
    static int s_registered = 0;
    WNDCLASS wc;
    if (s_registered) {
        return 1;
    }
    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = d_system_wndproc;
    wc.hInstance = GetModuleHandle(NULL);
    wc.lpszClassName = d_system_class_name();
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    if (!RegisterClass(&wc)) {
        return 0;
    }
    s_registered = 1;
    return 1;
}

static int d_system_create_window(void)
{
    DWORD style;
    RECT rect;
    int width;
    int height;

    if (g_hwnd) {
        return 1;
    }

    if (!d_system_register_class()) {
        return 0;
    }

    width = 800;
    height = 600;
    style = WS_OVERLAPPEDWINDOW;
    rect.left = 0;
    rect.top = 0;
    rect.right = width;
    rect.bottom = height;
    AdjustWindowRect(&rect, style, FALSE);

    g_hwnd = CreateWindowEx(
        0,
        d_system_class_name(),
        "Dominium",
        style,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        rect.right - rect.left,
        rect.bottom - rect.top,
        NULL,
        NULL,
        GetModuleHandle(NULL),
        NULL);

    if (!g_hwnd) {
        return 0;
    }
    ShowWindow(g_hwnd, SW_SHOW);
    UpdateWindow(g_hwnd);
    return 1;
}

static void d_system_destroy_window(void)
{
    if (g_hwnd) {
        DestroyWindow(g_hwnd);
        g_hwnd = NULL;
    }
}
#endif /* _WIN32 */

int d_system_init(const char *backend_name)
{
    int headless = 0;
    (void)backend_name;

    if (backend_name && backend_name[0]) {
        if (backend_name[0] == 'h' || backend_name[0] == 'H') {
            headless = 1;
        }
    }

    if (dsys_init() != DSYS_OK) {
        return 0;
    }

#if defined(_WIN32)
    if (!headless) {
        if (!d_system_create_window()) {
            return 0;
        }
    }
#else
    (void)headless;
#endif

    g_system_initialized = 1;
    return 1;
}

void d_system_shutdown(void)
{
    if (!g_system_initialized) {
        return;
    }
#if defined(_WIN32)
    d_system_destroy_window();
#endif
    dsys_shutdown();
    g_system_initialized = 0;
}

int d_system_pump_events(void)
{
#if defined(_WIN32)
    MSG msg;
    while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) {
            return 1;
        }
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
#endif
    d_system_input_pump_dsys();
    return 0;
}

void d_system_sleep_ms(u32 ms)
{
    dsys_sleep_ms(ms);
}

int d_system_process_spawn(const char *path, const char *args)
{
    (void)path;
    (void)args;
    return -1;
}

int d_system_present_framebuffer(
    const void *pixels,
    i32         width,
    i32         height,
    i32         pitch_bytes
)
{
#if defined(_WIN32)
    BITMAPINFO bmi;
    HDC hdc;
    int rc;
    int expected_pitch;

    if (!g_hwnd || !pixels || width <= 0 || height <= 0) {
        return -1;
    }

    expected_pitch = width * 4;
    if (pitch_bytes != expected_pitch) {
        /* Minimal path: expect tightly packed ARGB32 rows. */
        return -1;
    }

    memset(&bmi, 0, sizeof(bmi));
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = width;
    bmi.bmiHeader.biHeight = -height; /* top-down */
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    hdc = GetDC(g_hwnd);
    if (!hdc) {
        return -1;
    }

    rc = StretchDIBits(
        hdc,
        0, 0, width, height,
        0, 0, width, height,
        pixels,
        &bmi,
        DIB_RGB_COLORS,
        SRCCOPY);

    ReleaseDC(g_hwnd, hdc);
    return (rc == 0) ? -1 : 0;
#else
    (void)pixels;
    (void)width;
    (void)height;
    (void)pitch_bytes;
    return 0;
#endif
}

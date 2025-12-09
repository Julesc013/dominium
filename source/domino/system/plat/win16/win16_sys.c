#include "win16_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WIN16_EVENT_QUEUE_CAP 32

static const char* WIN16_WINDOW_CLASS = "DominoWin16";

static dsys_result win16_init(void);
static void        win16_shutdown(void);
static dsys_caps   win16_get_caps(void);

static uint64_t win16_time_now_us(void);
static void     win16_sleep_ms(uint32_t ms);

static dsys_window* win16_window_create(const dsys_window_desc* desc);
static void         win16_window_destroy(dsys_window* win);
static void         win16_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         win16_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         win16_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        win16_window_get_native_handle(dsys_window* win);

static bool win16_poll_event(dsys_event* ev);

static bool   win16_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  win16_file_open(const char* path, const char* mode);
static size_t win16_file_read(void* fh, void* buf, size_t size);
static size_t win16_file_write(void* fh, const void* buf, size_t size);
static int    win16_file_seek(void* fh, long offset, int origin);
static long   win16_file_tell(void* fh);
static int    win16_file_close(void* fh);

static dsys_dir_iter* win16_dir_open(const char* path);
static bool           win16_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           win16_dir_close(dsys_dir_iter* it);

static dsys_process* win16_process_spawn(const dsys_process_desc* desc);
static int           win16_process_wait(dsys_process* p);
static void          win16_process_destroy(dsys_process* p);

static LRESULT CALLBACK Win16WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);

static const dsys_caps g_win16_caps = { "win16", 1u, true, true, false, false };
win16_global_t         g_win16;
static dsys_window*    g_win16_window = NULL;

static dsys_event g_win16_event_queue[WIN16_EVENT_QUEUE_CAP];
static int        g_win16_event_head = 0;
static int        g_win16_event_tail = 0;

static void win16_reset_state(void)
{
    memset(&g_win16, 0, sizeof(g_win16));
    g_win16_window = NULL;
    g_win16_event_head = 0;
    g_win16_event_tail = 0;
}

static void win16_push_event(const dsys_event* ev)
{
    int next;
    if (!ev) {
        return;
    }
    next = (g_win16_event_tail + 1) % WIN16_EVENT_QUEUE_CAP;
    if (next == g_win16_event_head) {
        return;
    }
    g_win16_event_queue[g_win16_event_tail] = *ev;
    g_win16_event_tail = next;
}

static bool win16_pop_event(dsys_event* ev)
{
    if (g_win16_event_head == g_win16_event_tail) {
        return false;
    }
    if (ev) {
        *ev = g_win16_event_queue[g_win16_event_head];
    }
    g_win16_event_head = (g_win16_event_head + 1) % WIN16_EVENT_QUEUE_CAP;
    return true;
}

static bool win16_copy_string(const char* src, char* dst, size_t dst_size)
{
    size_t len;

    if (!src || !dst || dst_size == 0u) {
        return false;
    }
    len = strlen(src);
    if (len >= dst_size) {
        len = dst_size - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
    return true;
}

static void win16_dirname(char* path)
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
            break;
        }
        path[len - 1u] = '\0';
        len -= 1u;
    }
}

static void win16_join_path(char* dst, size_t cap, const char* base, const char* leaf)
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
        if (i > 0u && dst[i - 1u] != '\\' && dst[i - 1u] != '/' && i + 1u < cap) {
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

static bool win16_get_executable_dir(char* buf, size_t buf_size)
{
    char  exe_path[260];
    UINT  copied;
    BOOL  ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    exe_path[0] = '\0';
    copied = 0u;
    ok = FALSE;
#if defined(_WIN32)
    copied = GetModuleFileNameA(g_win16.hInstance, exe_path, (DWORD)sizeof(exe_path));
    ok = copied > 0u;
#else
    copied = GetModuleFileName(g_win16.hInstance, exe_path, sizeof(exe_path));
    ok = copied > 0u;
#endif
    if (!ok || copied >= sizeof(exe_path)) {
        return false;
    }
    exe_path[sizeof(exe_path) - 1u] = '\0';
    win16_dirname(exe_path);
    return win16_copy_string(exe_path, buf, buf_size);
}

static bool win16_pick_temp(char* buf, size_t buf_size)
{
    char tmp[260];
    const char* env_temp;

    if (!buf || buf_size == 0u) {
        return false;
    }

    tmp[0] = '\0';
#if defined(_WIN32)
    {
        DWORD n;
        n = GetTempPathA((DWORD)sizeof(tmp), tmp);
        if (n > 0u && n < sizeof(tmp)) {
            return win16_copy_string(tmp, buf, buf_size);
        }
    }
#endif
    env_temp = getenv("TEMP");
    if (env_temp && env_temp[0] != '\0') {
        return win16_copy_string(env_temp, buf, buf_size);
    }
    return win16_copy_string(".", buf, buf_size);
}

static bool win16_pick_app_root(char* buf, size_t buf_size)
{
    if (!buf || buf_size == 0u) {
        return false;
    }
    if (win16_get_executable_dir(buf, buf_size)) {
        return true;
    }
    return win16_copy_string(".", buf, buf_size);
}

static bool win16_register_class(void)
{
    WNDCLASS wc;

    if (g_win16.class_registered) {
        return true;
    }
    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = Win16WndProc;
    wc.hInstance = g_win16.hInstance;
    wc.lpszClassName = WIN16_WINDOW_CLASS;
    if (!RegisterClass(&wc)) {
        return false;
    }
    g_win16.class_registered = 1;
    return true;
}

static void win16_apply_mode(dsys_window* win)
{
    int screen_w;
    int screen_h;
    int w;
    int h;

    if (!win || !win->hwnd) {
        return;
    }

    screen_w = GetSystemMetrics(SM_CXSCREEN);
    screen_h = GetSystemMetrics(SM_CYSCREEN);
    w = win->width;
    h = win->height;
    if (w <= 0) {
        w = screen_w;
    }
    if (h <= 0) {
        h = screen_h;
    }
    if (win->mode == DWIN_MODE_FULLSCREEN || win->mode == DWIN_MODE_BORDERLESS) {
        MoveWindow(win->hwnd, 0, 0, w, h, TRUE);
    } else {
        MoveWindow(win->hwnd, 0, 0, w, h, TRUE);
    }
}

static dsys_result win16_init(void)
{
    win16_reset_state();
    g_win16.hInstance = GetModuleHandle(NULL);
    g_win16.running = 1;
    return DSYS_OK;
}

static void win16_shutdown(void)
{
    if (g_win16_window) {
        win16_window_destroy(g_win16_window);
    }
    if (g_win16.class_registered && g_win16.hInstance) {
        UnregisterClass(WIN16_WINDOW_CLASS, g_win16.hInstance);
    }
    win16_reset_state();
}

static dsys_caps win16_get_caps(void)
{
    return g_win16_caps;
}

static uint64_t win16_time_now_us(void)
{
    DWORD ms;
    ms = GetTickCount();
    return ((uint64_t)ms) * 1000u;
}

static void win16_sleep_ms(uint32_t ms)
{
    DWORD start;
    start = GetTickCount();
    while ((DWORD)(GetTickCount() - start) < ms) {
#if defined(_WIN32)
        Sleep(1);
#elif defined(Yield)
        Yield();
#endif
    }
}

static dsys_window* win16_window_create(const dsys_window_desc* desc)
{
    dsys_window*     win;
    dsys_window_desc local_desc;
    DWORD            style;
    HWND             hwnd;

    if (!g_win16.hInstance) {
        g_win16.hInstance = GetModuleHandle(NULL);
    }

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 640;
        local_desc.height = 480;
        local_desc.mode = DWIN_MODE_FULLSCREEN;
    }
    if (local_desc.width <= 0) {
        local_desc.width = 640;
    }
    if (local_desc.height <= 0) {
        local_desc.height = 480;
    }

    if (!win16_register_class()) {
        return NULL;
    }

    style = WS_POPUP | WS_VISIBLE;
    if (local_desc.mode == DWIN_MODE_WINDOWED) {
        style = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX | WS_VISIBLE;
    } else if (local_desc.mode == DWIN_MODE_BORDERLESS) {
        style = WS_POPUP | WS_VISIBLE;
    }

    hwnd = CreateWindow(
        WIN16_WINDOW_CLASS,
        "Domino",
        style,
        local_desc.x,
        local_desc.y,
        local_desc.width,
        local_desc.height,
        (HWND)0,
        (HMENU)0,
        g_win16.hInstance,
        NULL);
    if (!hwnd) {
        return NULL;
    }
    g_win16.hwnd = hwnd;

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        DestroyWindow(hwnd);
        g_win16.hwnd = NULL;
        return NULL;
    }
    win->hwnd = hwnd;
    win->width = local_desc.width;
    win->height = local_desc.height;
    win->mode = local_desc.mode;

    g_win16_window = win;
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);
    win16_apply_mode(win);
    return win;
}

static void win16_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win->hwnd) {
        DestroyWindow(win->hwnd);
    }
    if (g_win16.hwnd == win->hwnd) {
        g_win16.hwnd = NULL;
    }
    if (g_win16_window == win) {
        g_win16_window = NULL;
    }
    free(win);
}

static void win16_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
    win16_apply_mode(win);
}

static void win16_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
    if (win->hwnd) {
        MoveWindow(win->hwnd, 0, 0, w, h, TRUE);
    }
}

static void win16_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

static void* win16_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)win->hwnd;
}

static bool win16_poll_event(dsys_event* ev)
{
    MSG msg;

    while (PeekMessage(&msg, (HWND)0, 0u, 0u, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    if (win16_pop_event(ev)) {
        return true;
    }

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }
    return false;
}

static bool win16_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    char base[260];
    char tmp[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

    if (!win16_pick_app_root(base, sizeof(base))) {
        base[0] = '.';
        base[1] = '\0';
    }

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        return win16_copy_string(base, buf, buf_size);
    case DSYS_PATH_USER_DATA:
        win16_join_path(tmp, sizeof(tmp), base, "DOMINIUM\\DATA");
        return win16_copy_string(tmp, buf, buf_size);
    case DSYS_PATH_USER_CONFIG:
        win16_join_path(tmp, sizeof(tmp), base, "DOMINIUM\\CONFIG");
        return win16_copy_string(tmp, buf, buf_size);
    case DSYS_PATH_USER_CACHE:
        win16_join_path(tmp, sizeof(tmp), base, "DOMINIUM\\CACHE");
        return win16_copy_string(tmp, buf, buf_size);
    case DSYS_PATH_TEMP:
        return win16_pick_temp(buf, buf_size);
    default:
        break;
    }
    return false;
}

static void* win16_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t win16_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t win16_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int win16_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long win16_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int win16_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

#ifndef INVALID_HANDLE_VALUE
#define INVALID_HANDLE_VALUE ((HANDLE)(-1))
#endif
#ifndef FILE_ATTRIBUTE_DIRECTORY
#define FILE_ATTRIBUTE_DIRECTORY 0x10
#endif

static HANDLE win16_find_first(const char* pattern, WIN32_FIND_DATA* data)
{
#if defined(_WIN32)
    return FindFirstFileA(pattern, data);
#else
    return FindFirstFile(pattern, data);
#endif
}

static BOOL win16_find_next(HANDLE handle, WIN32_FIND_DATA* data)
{
#if defined(_WIN32)
    return FindNextFileA(handle, data);
#else
    return FindNextFile(handle, data);
#endif
}

static dsys_dir_iter* win16_dir_open(const char* path)
{
    dsys_dir_iter* it;
    size_t         len;

    if (!path) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        return NULL;
    }
    memset(it, 0, sizeof(*it));

    len = strlen(path);
    if (len + 3u >= sizeof(it->pattern)) {
        free(it);
        return NULL;
    }
    memcpy(it->pattern, path, len);
    if (len == 0u || (path[len - 1u] != '\\' && path[len - 1u] != '/')) {
        it->pattern[len] = '\\';
        len += 1u;
    }
    it->pattern[len] = '*';
    it->pattern[len + 1u] = '\0';

    it->handle = win16_find_first(it->pattern, &it->data);
    if (it->handle == INVALID_HANDLE_VALUE) {
        free(it);
        return NULL;
    }
    it->first_pending = 1;
    return it;
}

static bool win16_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    if (!it || !out) {
        return false;
    }

    if (it->first_pending) {
        it->first_pending = 0;
    } else {
        if (!win16_find_next(it->handle, &it->data)) {
            return false;
        }
    }

    win16_copy_string(it->data.cFileName, out->name, sizeof(out->name));
    out->is_dir = (it->data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) ? true : false;
    return true;
}

static void win16_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->handle && it->handle != INVALID_HANDLE_VALUE) {
        FindClose(it->handle);
    }
    free(it);
}

static dsys_process* win16_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int win16_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void win16_process_destroy(dsys_process* p)
{
    (void)p;
}

static LRESULT CALLBACK Win16WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    dsys_event ev;
    memset(&ev, 0, sizeof(ev));

    switch (msg) {
    case WM_DESTROY:
        ev.type = DSYS_EVENT_QUIT;
        win16_push_event(&ev);
        break;
    case WM_CLOSE:
        ev.type = DSYS_EVENT_QUIT;
        win16_push_event(&ev);
        break;
    case WM_SIZE:
        ev.type = DSYS_EVENT_WINDOW_RESIZED;
        ev.payload.window.width = (int32_t)LOWORD(lParam);
        ev.payload.window.height = (int32_t)HIWORD(lParam);
        if (g_win16_window) {
            g_win16_window->width = ev.payload.window.width;
            g_win16_window->height = ev.payload.window.height;
        }
        win16_push_event(&ev);
        break;
    case WM_KEYDOWN:
        ev.type = DSYS_EVENT_KEY_DOWN;
        ev.payload.key.key = (int32_t)wParam;
        ev.payload.key.repeat = false;
        win16_push_event(&ev);
        break;
    case WM_KEYUP:
        ev.type = DSYS_EVENT_KEY_UP;
        ev.payload.key.key = (int32_t)wParam;
        ev.payload.key.repeat = false;
        win16_push_event(&ev);
        break;
    case WM_MOUSEMOVE:
        ev.type = DSYS_EVENT_MOUSE_MOVE;
        ev.payload.mouse_move.x = (int32_t)LOWORD(lParam);
        ev.payload.mouse_move.y = (int32_t)HIWORD(lParam);
        ev.payload.mouse_move.dx = 0;
        ev.payload.mouse_move.dy = 0;
        win16_push_event(&ev);
        break;
    case WM_LBUTTONDOWN:
    case WM_LBUTTONUP:
    case WM_RBUTTONDOWN:
    case WM_RBUTTONUP:
        ev.type = DSYS_EVENT_MOUSE_BUTTON;
        ev.payload.mouse_button.button = (msg == WM_LBUTTONDOWN || msg == WM_LBUTTONUP) ? 1 : 2;
        ev.payload.mouse_button.pressed = (msg == WM_LBUTTONDOWN || msg == WM_RBUTTONDOWN);
        ev.payload.mouse_button.clicks = 1;
        win16_push_event(&ev);
        break;
    default:
        break;
    }

    return DefWindowProc(hwnd, msg, wParam, lParam);
}

static const dsys_backend_vtable g_win16_vtable = {
    win16_init,
    win16_shutdown,
    win16_get_caps,
    win16_time_now_us,
    win16_sleep_ms,
    win16_window_create,
    win16_window_destroy,
    win16_window_set_mode,
    win16_window_set_size,
    win16_window_get_size,
    win16_window_get_native_handle,
    win16_poll_event,
    win16_get_path,
    win16_file_open,
    win16_file_read,
    win16_file_write,
    win16_file_seek,
    win16_file_tell,
    win16_file_close,
    win16_dir_open,
    win16_dir_next,
    win16_dir_close,
    win16_process_spawn,
    win16_process_wait,
    win16_process_destroy
};

const dsys_backend_vtable* dsys_win16_get_vtable(void)
{
    return &g_win16_vtable;
}

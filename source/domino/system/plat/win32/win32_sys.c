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

static dsys_result win32_init(void);
static void        win32_shutdown(void);
static dsys_caps   win32_get_caps(void);

static uint64_t win32_time_now_us(void);
static void     win32_sleep_ms(uint32_t ms);

static dsys_window* win32_window_create(const dsys_window_desc* desc);
static void         win32_window_destroy(dsys_window* win);
static void         win32_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         win32_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         win32_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        win32_window_get_native_handle(dsys_window* win);

static bool win32_poll_event(dsys_event* ev);

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

static uint64_t g_qpc_freq = 0u;
static uint64_t g_qpc_last_us = 0u;

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
    } else {
        g_qpc_freq = 0u;
        g_win32_caps.has_high_res_timer = false;
    }
#endif
    g_qpc_last_us = 0u;
    return DSYS_OK;
}

static void win32_shutdown(void)
{
}

static dsys_caps win32_get_caps(void)
{
    return g_win32_caps;
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
} win32_window_impl;

static const wchar_t* win32_class_name(void)
{
    return L"DominoDsysWin32";
}

static ATOM win32_register_class(void)
{
    static ATOM s_atom = 0;
    WNDCLASSW wc;

    if (s_atom) {
        return s_atom;
    }
    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = DefWindowProcW;
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

static bool win32_poll_event(dsys_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }
    return false;
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
    (void)desc;
    return NULL;
}

static int win32_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void win32_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_win32_get_vtable(void)
{
    return &g_win32_vtable;
}

#include "x11_sys.h"

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <limits.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

static x11_global_t g_x11 = { 0 };
static dsys_window* g_window_list = NULL;
static dsys_caps    g_x11_caps = { "x11", 1u, true, true, false, true };

static dsys_result x11_init(void);
static void        x11_shutdown(void);
static dsys_caps   x11_get_caps(void);

static uint64_t x11_time_now_us(void);
static void     x11_sleep_ms(uint32_t ms);

static dsys_window* x11_window_create(const dsys_window_desc* desc);
static void         x11_window_destroy(dsys_window* win);
static void         x11_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         x11_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         x11_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        x11_window_get_native_handle(dsys_window* win);

static bool x11_poll_event(dsys_event* ev);

static bool   x11_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  x11_file_open(const char* path, const char* mode);
static size_t x11_file_read(void* fh, void* buf, size_t size);
static size_t x11_file_write(void* fh, const void* buf, size_t size);
static int    x11_file_seek(void* fh, long offset, int origin);
static long   x11_file_tell(void* fh);
static int    x11_file_close(void* fh);

static dsys_dir_iter* x11_dir_open(const char* path);
static bool           x11_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           x11_dir_close(dsys_dir_iter* it);

static dsys_process* x11_process_spawn(const dsys_process_desc* desc);
static int           x11_process_wait(dsys_process* p);
static void          x11_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_x11_vtable = {
    x11_init,
    x11_shutdown,
    x11_get_caps,
    x11_time_now_us,
    x11_sleep_ms,
    x11_window_create,
    x11_window_destroy,
    x11_window_set_mode,
    x11_window_set_size,
    x11_window_get_size,
    x11_window_get_native_handle,
    x11_poll_event,
    x11_get_path,
    x11_file_open,
    x11_file_read,
    x11_file_write,
    x11_file_seek,
    x11_file_tell,
    x11_file_close,
    x11_dir_open,
    x11_dir_next,
    x11_dir_close,
    x11_process_spawn,
    x11_process_wait,
    x11_process_destroy
};

static dsys_window* x11_find_window(Window id)
{
    dsys_window* cur;
    cur = g_window_list;
    while (cur) {
        if (cur->window == id) {
            return cur;
        }
        cur = cur->next;
    }
    return NULL;
}

static void x11_add_window(dsys_window* win)
{
    if (!win) {
        return;
    }
    win->next = g_window_list;
    g_window_list = win;
}

static void x11_remove_window(dsys_window* win)
{
    dsys_window* prev;
    dsys_window* cur;

    prev = NULL;
    cur = g_window_list;
    while (cur) {
        if (cur == win) {
            if (prev) {
                prev->next = cur->next;
            } else {
                g_window_list = cur->next;
            }
            return;
        }
        prev = cur;
        cur = cur->next;
    }
}

static void x11_update_window_size(Window id, int32_t w, int32_t h)
{
    dsys_window* win;
    win = x11_find_window(id);
    if (win) {
        win->width = w;
        win->height = h;
    }
}

static void x11_apply_fullscreen(dsys_window* win, int enable)
{
    XEvent xev;
    Window root;

    if (!win || !g_x11.display || g_x11.net_wm_state == None || g_x11.net_wm_state_fullscreen == None) {
        return;
    }

    root = RootWindow(g_x11.display, g_x11.screen);
    memset(&xev, 0, sizeof(xev));
    xev.xclient.type = ClientMessage;
    xev.xclient.window = win->window;
    xev.xclient.message_type = g_x11.net_wm_state;
    xev.xclient.format = 32;
    xev.xclient.data.l[0] = enable ? 1 : 0;
    xev.xclient.data.l[1] = (long)g_x11.net_wm_state_fullscreen;
    xev.xclient.data.l[2] = 0;
    xev.xclient.data.l[3] = 1;
    xev.xclient.data.l[4] = 0;
    XSendEvent(g_x11.display,
               root,
               False,
               SubstructureRedirectMask | SubstructureNotifyMask,
               &xev);
    XFlush(g_x11.display);
}

static bool x11_translate_event(const XEvent* xev, dsys_event* ev)
{
    dsys_window* win;

    if (!xev || !ev) {
        return false;
    }

    win = x11_find_window(xev->xany.window);

    switch (xev->type) {
    case ClientMessage:
        if ((Atom)xev->xclient.data.l[0] == g_x11.wm_delete_window) {
            ev->type = DSYS_EVENT_QUIT;
            return true;
        }
        break;

    case ConfigureNotify:
        ev->type = DSYS_EVENT_WINDOW_RESIZED;
        ev->payload.window.width = xev->xconfigure.width;
        ev->payload.window.height = xev->xconfigure.height;
        x11_update_window_size(xev->xconfigure.window,
                               xev->xconfigure.width,
                               xev->xconfigure.height);
        return true;

    case KeyPress:
    case KeyRelease:
        {
            KeySym sym;
            int    is_press;
            sym = XLookupKeysym((XKeyEvent*)&xev->xkey, 0);
            is_press = (xev->type == KeyPress) ? 1 : 0;
            ev->type = is_press ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
            ev->payload.key.key = (int32_t)sym;
            ev->payload.key.repeat = false;
            return true;
        }

    case MotionNotify:
        ev->type = DSYS_EVENT_MOUSE_MOVE;
        ev->payload.mouse_move.x = xev->xmotion.x;
        ev->payload.mouse_move.y = xev->xmotion.y;
        ev->payload.mouse_move.dx = 0;
        ev->payload.mouse_move.dy = 0;
        if (win) {
            ev->payload.mouse_move.dx = xev->xmotion.x - win->last_x;
            ev->payload.mouse_move.dy = xev->xmotion.y - win->last_y;
            win->last_x = xev->xmotion.x;
            win->last_y = xev->xmotion.y;
        }
        return true;

    case ButtonPress:
    case ButtonRelease:
        if (xev->xbutton.button == 4 || xev->xbutton.button == 5 ||
            xev->xbutton.button == 6 || xev->xbutton.button == 7) {
            ev->type = DSYS_EVENT_MOUSE_WHEEL;
            ev->payload.mouse_wheel.delta_x = 0;
            ev->payload.mouse_wheel.delta_y = 0;
            if (xev->xbutton.button == 4) {
                ev->payload.mouse_wheel.delta_y = 1;
            } else if (xev->xbutton.button == 5) {
                ev->payload.mouse_wheel.delta_y = -1;
            } else if (xev->xbutton.button == 6) {
                ev->payload.mouse_wheel.delta_x = -1;
            } else if (xev->xbutton.button == 7) {
                ev->payload.mouse_wheel.delta_x = 1;
            }
            return true;
        }
        ev->type = DSYS_EVENT_MOUSE_BUTTON;
        ev->payload.mouse_button.button = (int32_t)xev->xbutton.button;
        ev->payload.mouse_button.pressed = (xev->type == ButtonPress) ? true : false;
        ev->payload.mouse_button.clicks = 1;
        return true;

    default:
        break;
    }

    return false;
}

static bool x11_copy_path(const char* src, char* buf, size_t buf_size)
{
    size_t len;
    if (!src || !buf || buf_size == 0u) {
        return false;
    }
    len = strlen(src);
    if (len >= buf_size) {
        len = buf_size - 1u;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return true;
}

static void x11_join_path(char* dst, size_t cap, const char* base, const char* leaf)
{
    size_t i;
    size_t j;
    if (!dst || cap == 0u) {
        return;
    }
    dst[0] = '\0';
    if (base) {
        i = 0u;
        while (base[i] != '\0' && i + 1u < cap) {
            dst[i] = base[i];
            ++i;
        }
        if (i > 0u && dst[i - 1u] != '/' && i + 1u < cap) {
            dst[i] = '/';
            ++i;
        }
    } else {
        i = 0u;
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

static bool x11_get_home(char* buf, size_t buf_size)
{
    const char* home;
    home = getenv("HOME");
    if (home && home[0] != '\0') {
        return x11_copy_path(home, buf, buf_size);
    }
    return false;
}

static bool x11_dirname(const char* path, char* out, size_t cap)
{
    size_t len;
    if (!path || !out || cap == 0u) {
        return false;
    }
    len = strlen(path);
    while (len > 0u && (path[len - 1u] == '/' || path[len - 1u] == '\\')) {
        len -= 1u;
    }
    while (len > 0u) {
        char c;
        c = path[len - 1u];
        if (c == '/' || c == '\\') {
            break;
        }
        len -= 1u;
    }
    if (len == 0u) {
        if (cap > 1u) {
            out[0] = '.';
            out[1] = '\0';
            return true;
        }
        return false;
    }
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(out, path, len);
    out[len] = '\0';
    return true;
}

static bool x11_resolve_exe_dir(char* buf, size_t buf_size)
{
    char tmp[PATH_MAX];
    ssize_t n;

    if (!buf || buf_size == 0u) {
        return false;
    }

    n = readlink("/proc/self/exe", tmp, sizeof(tmp) - 1u);
    if (n > 0 && (size_t)n < sizeof(tmp)) {
        tmp[n] = '\0';
        if (x11_dirname(tmp, buf, buf_size)) {
            return true;
        }
    }

    if (getcwd(tmp, sizeof(tmp)) != NULL) {
        return x11_copy_path(tmp, buf, buf_size);
    }

    buf[0] = '\0';
    return false;
}

static bool x11_pick_xdg(const char* env_name,
                         const char* fallback_suffix,
                         char* buf,
                         size_t buf_size)
{
    const char* env_val;
    char home[260];
    char tmp[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_val = getenv(env_name);
    if (env_val && env_val[0] != '\0') {
        return x11_copy_path(env_val, buf, buf_size);
    }

    if (!x11_get_home(home, sizeof(home))) {
        return false;
    }

    x11_join_path(tmp, sizeof(tmp), home, fallback_suffix);
    return x11_copy_path(tmp, buf, buf_size);
}

static dsys_result x11_init(void)
{
    g_x11.display = XOpenDisplay(NULL);
    if (!g_x11.display) {
        return DSYS_ERR;
    }

    g_x11.screen = DefaultScreen(g_x11.display);
    g_x11.wm_delete_window = XInternAtom(g_x11.display, "WM_DELETE_WINDOW", False);
    g_x11.net_wm_state = XInternAtom(g_x11.display, "_NET_WM_STATE", False);
    g_x11.net_wm_state_fullscreen = XInternAtom(g_x11.display, "_NET_WM_STATE_FULLSCREEN", False);

    g_x11_caps.has_high_res_timer = true;
    return DSYS_OK;
}

static void x11_shutdown(void)
{
    dsys_window* cur;
    dsys_window* next;

    cur = g_window_list;
    while (cur) {
        next = cur->next;
        if (g_x11.display && cur->window) {
            XDestroyWindow(g_x11.display, cur->window);
        }
        free(cur);
        cur = next;
    }
    g_window_list = NULL;

    if (g_x11.display) {
        XCloseDisplay(g_x11.display);
    }
    memset(&g_x11, 0, sizeof(g_x11));
}

static dsys_caps x11_get_caps(void)
{
    return g_x11_caps;
}

static uint64_t x11_time_now_us(void)
{
#if defined(CLOCK_MONOTONIC)
    {
        struct timespec ts;
        if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
            return ((uint64_t)ts.tv_sec * 1000000u) + ((uint64_t)ts.tv_nsec / 1000u);
        }
    }
#endif
    {
        struct timeval tv;
        gettimeofday(&tv, (struct timezone*)0);
        return ((uint64_t)tv.tv_sec * 1000000u) + (uint64_t)tv.tv_usec;
    }
}

static void x11_sleep_ms(uint32_t ms)
{
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR) {
        /* retry */
    }
}

static dsys_window* x11_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local_desc;
    dsys_window*     win;
    Window           w;
    int              px;
    int              py;
    unsigned int     width;
    unsigned int     height;
    unsigned long    black;
    unsigned long    white;
    XSetWindowAttributes attrs;
    long             mask;

    if (!g_x11.display) {
        return NULL;
    }

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 800;
        local_desc.height = 600;
        local_desc.mode = DWIN_MODE_WINDOWED;
    }

    px = (desc) ? local_desc.x : 0;
    py = (desc) ? local_desc.y : 0;
    width = (local_desc.width > 0) ? (unsigned int)local_desc.width : 800u;
    height = (local_desc.height > 0) ? (unsigned int)local_desc.height : 600u;
    black = BlackPixel(g_x11.display, g_x11.screen);
    white = WhitePixel(g_x11.display, g_x11.screen);

    attrs.background_pixel = black;
    attrs.border_pixel = white;
    mask = CWBackPixel | CWBorderPixel;

    w = XCreateWindow(g_x11.display,
                      RootWindow(g_x11.display, g_x11.screen),
                      px,
                      py,
                      width,
                      height,
                      0,
                      CopyFromParent,
                      InputOutput,
                      CopyFromParent,
                      mask,
                      &attrs);
    if (!w) {
        return NULL;
    }

    XStoreName(g_x11.display, w, "Domino");
    XSelectInput(g_x11.display,
                 w,
                 ExposureMask |
                 KeyPressMask | KeyReleaseMask |
                 ButtonPressMask | ButtonReleaseMask |
                 PointerMotionMask |
                 StructureNotifyMask);
    if (g_x11.wm_delete_window != None) {
        XSetWMProtocols(g_x11.display, w, &g_x11.wm_delete_window, 1);
    }
    XMapWindow(g_x11.display, w);
    XFlush(g_x11.display);

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        XDestroyWindow(g_x11.display, w);
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->display = g_x11.display;
    win->screen = g_x11.screen;
    win->window = w;
    win->wm_delete_window = g_x11.wm_delete_window;
    win->net_wm_state = g_x11.net_wm_state;
    win->net_wm_state_fullscreen = g_x11.net_wm_state_fullscreen;
    win->width = (int32_t)width;
    win->height = (int32_t)height;
    win->last_x = 0;
    win->last_y = 0;
    win->mode = local_desc.mode;
    win->next = NULL;
    x11_add_window(win);
    x11_window_set_mode(win, local_desc.mode);
    return win;
}

static void x11_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    x11_remove_window(win);
    if (g_x11.display && win->window) {
        XDestroyWindow(g_x11.display, win->window);
    }
    free(win);
}

static void x11_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    int enable_fullscreen;

    if (!win) {
        return;
    }
    enable_fullscreen = (mode == DWIN_MODE_FULLSCREEN || mode == DWIN_MODE_BORDERLESS) ? 1 : 0;
    x11_apply_fullscreen(win, enable_fullscreen);
    win->mode = mode;
}

static void x11_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win || !g_x11.display) {
        return;
    }
    XResizeWindow(g_x11.display, win->window, (unsigned int)w, (unsigned int)h);
    win->width = w;
    win->height = h;
}

static void x11_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    XWindowAttributes attr;

    if (!win || !g_x11.display) {
        return;
    }

    if (XGetWindowAttributes(g_x11.display, win->window, &attr)) {
        win->width = attr.width;
        win->height = attr.height;
    }

    if (w) {
        *w = win->width;
    }
    if (h) {
        *h = win->height;
    }
}

static void* x11_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)(uintptr_t)win->window;
}

static bool x11_poll_event(dsys_event* ev)
{
    XEvent xev;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    if (!g_x11.display) {
        return false;
    }

    while (XPending(g_x11.display) > 0) {
        XNextEvent(g_x11.display, &xev);
        if (x11_translate_event(&xev, ev)) {
            return true;
        }
    }
    return false;
}

static bool x11_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    char tmp[260];
    bool ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';
    ok = false;

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        ok = x11_resolve_exe_dir(buf, buf_size);
        break;

    case DSYS_PATH_USER_DATA:
        if (x11_pick_xdg("XDG_DATA_HOME", ".local/share", tmp, sizeof(tmp))) {
            char joined[260];
            x11_join_path(joined, sizeof(joined), tmp, "dominium");
            ok = x11_copy_path(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_USER_CONFIG:
        if (x11_pick_xdg("XDG_CONFIG_HOME", ".config", tmp, sizeof(tmp))) {
            char joined[260];
            x11_join_path(joined, sizeof(joined), tmp, "dominium");
            ok = x11_copy_path(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_USER_CACHE:
        if (x11_pick_xdg("XDG_CACHE_HOME", ".cache", tmp, sizeof(tmp))) {
            char joined[260];
            x11_join_path(joined, sizeof(joined), tmp, "dominium");
            ok = x11_copy_path(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_TEMP:
        {
            const char* tmpdir;
            tmpdir = getenv("TMPDIR");
            if (tmpdir && tmpdir[0] != '\0') {
                ok = x11_copy_path(tmpdir, buf, buf_size);
            } else {
                ok = x11_copy_path("/tmp", buf, buf_size);
            }
        }
        break;

    default:
        break;
    }

    if (!ok && buf && buf_size > 0u) {
        buf[0] = '\0';
    }
    return ok;
}

static void* x11_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t x11_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t x11_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int x11_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long x11_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int x11_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* x11_dir_open(const char* path)
{
    dsys_dir_iter* it;
    DIR*           dir;
    size_t         len;

    if (!path) {
        return NULL;
    }

    dir = opendir(path);
    if (!dir) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        closedir(dir);
        return NULL;
    }
    it->dir = dir;
    len = strlen(path);
    if (len >= sizeof(it->base)) {
        len = sizeof(it->base) - 1u;
    }
    memcpy(it->base, path, len);
    it->base[len] = '\0';
    return it;
}

static bool x11_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;

    if (!it || !out) {
        return false;
    }

    for (;;) {
        ent = readdir(it->dir);
        if (!ent) {
            return false;
        }
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) {
            continue;
        }
        strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = false;
#if defined(DT_DIR)
        if (ent->d_type == DT_DIR) {
            out->is_dir = true;
        } else if (ent->d_type == DT_UNKNOWN) {
            struct stat st;
            char        full[260];
            size_t      base_len;
            size_t      name_len;
            base_len = strlen(it->base);
            name_len = strlen(out->name);
            if (base_len + name_len + 2u < sizeof(full)) {
                memcpy(full, it->base, base_len);
                if (base_len > 0u && full[base_len - 1u] != '/') {
                    full[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full + base_len, out->name, name_len);
                full[base_len + name_len] = '\0';
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    out->is_dir = true;
                }
            }
        }
#else
        {
            struct stat st;
            char        full[260];
            size_t      base_len;
            size_t      name_len;
            base_len = strlen(it->base);
            name_len = strlen(out->name);
            if (base_len + name_len + 2u < sizeof(full)) {
                memcpy(full, it->base, base_len);
                if (base_len > 0u && full[base_len - 1u] != '/') {
                    full[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full + base_len, out->name, name_len);
                full[base_len + name_len] = '\0';
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    out->is_dir = true;
                }
            }
        }
#endif
        return true;
    }
}

static void x11_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* x11_process_spawn(const dsys_process_desc* desc)
{
    pid_t pid;
    dsys_process* proc;

    if (!desc || !desc->exe) {
        return NULL;
    }

    pid = fork();
    if (pid < 0) {
        return NULL;
    } else if (pid == 0) {
        if (desc->argv) {
            execvp(desc->exe, (char* const*)desc->argv);
        } else {
            char* const argv_local[2];
            argv_local[0] = (char*)desc->exe;
            argv_local[1] = NULL;
            execvp(desc->exe, argv_local);
        }
        _exit(127);
    }

    proc = (dsys_process*)malloc(sizeof(dsys_process));
    if (!proc) {
        waitpid(pid, (int*)0, 0);
        return NULL;
    }
    proc->pid = pid;
    return proc;
}

static int x11_process_wait(dsys_process* p)
{
    int   status;
    pid_t res;

    if (!p) {
        return -1;
    }

    res = waitpid(p->pid, &status, 0);
    if (res < 0) {
        return -1;
    }
    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return -1;
}

static void x11_process_destroy(dsys_process* p)
{
    if (!p) {
        return;
    }
    free(p);
}

const dsys_backend_vtable* dsys_x11_get_vtable(void)
{
    return &g_x11_vtable;
}

#include "wayland_sys.h"

#include <errno.h>
#include <limits.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <wayland-client.h>
#include <wayland-client-protocol.h>
#include <xdg-shell-client-protocol.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

static dsys_caps g_wayland_caps = { "wayland", 1u, true, true, false, true };
wayland_global_t g_wayland = { 0 };

static dsys_result wayland_init(void);
static void        wayland_shutdown(void);
static dsys_caps   wayland_get_caps(void);

static uint64_t wayland_time_now_us(void);
static void     wayland_sleep_ms(uint32_t ms);

static dsys_window* wayland_window_create(const dsys_window_desc* desc);
static void         wayland_window_destroy(dsys_window* win);
static void         wayland_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         wayland_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         wayland_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        wayland_window_get_native_handle(dsys_window* win);

static bool wayland_poll_event(dsys_event* ev);

static bool   wayland_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  wayland_file_open(const char* path, const char* mode);
static size_t wayland_file_read(void* fh, void* buf, size_t size);
static size_t wayland_file_write(void* fh, const void* buf, size_t size);
static int    wayland_file_seek(void* fh, long offset, int origin);
static long   wayland_file_tell(void* fh);
static int    wayland_file_close(void* fh);

static dsys_dir_iter* wayland_dir_open(const char* path);
static bool           wayland_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           wayland_dir_close(dsys_dir_iter* it);

static dsys_process* wayland_process_spawn(const dsys_process_desc* desc);
static int           wayland_process_wait(dsys_process* p);
static void          wayland_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_wayland_vtable = {
    wayland_init,
    wayland_shutdown,
    wayland_get_caps,
    wayland_time_now_us,
    wayland_sleep_ms,
    wayland_window_create,
    wayland_window_destroy,
    wayland_window_set_mode,
    wayland_window_set_size,
    wayland_window_get_size,
    wayland_window_get_native_handle,
    wayland_poll_event,
    wayland_get_path,
    wayland_file_open,
    wayland_file_read,
    wayland_file_write,
    wayland_file_seek,
    wayland_file_tell,
    wayland_file_close,
    wayland_dir_open,
    wayland_dir_next,
    wayland_dir_close,
    wayland_process_spawn,
    wayland_process_wait,
    wayland_process_destroy
};

static void wayland_push_event(const dsys_event* ev)
{
    int next;
    next = (g_wayland.event_tail + 1) % 64;
    if (next == g_wayland.event_head) {
        return;
    }
    g_wayland.event_queue[g_wayland.event_tail] = *ev;
    g_wayland.event_tail = next;
}

static bool wayland_copy_path(const char* src, char* buf, size_t buf_size)
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

static void wayland_join_path(char* dst, size_t cap, const char* base, const char* leaf)
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
        if (i > 0u && dst[i - 1u] != '/' && i + 1u < cap) {
            dst[i] = '/';
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

static bool wayland_dirname(const char* path, char* out, size_t cap)
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

static bool wayland_resolve_exe_dir(char* buf, size_t buf_size)
{
    char    tmp[PATH_MAX];
    ssize_t n;

    if (!buf || buf_size == 0u) {
        return false;
    }

    n = readlink("/proc/self/exe", tmp, sizeof(tmp) - 1u);
    if (n > 0 && (size_t)n < sizeof(tmp)) {
        tmp[n] = '\0';
        if (wayland_dirname(tmp, buf, buf_size)) {
            return true;
        }
    }

    if (getcwd(tmp, sizeof(tmp)) != NULL) {
        return wayland_copy_path(tmp, buf, buf_size);
    }

    buf[0] = '\0';
    return false;
}

static bool wayland_get_home(char* buf, size_t buf_size)
{
    const char* home_env;

    home_env = getenv("HOME");
    if (home_env && home_env[0] != '\0') {
        return wayland_copy_path(home_env, buf, buf_size);
    }
    return false;
}

static bool wayland_pick_xdg(const char* env_name,
                             const char* fallback_suffix,
                             char* buf,
                             size_t buf_size)
{
    const char* env_val;
    char        home[260];
    char        tmp[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

    env_val = getenv(env_name);
    if (env_val && env_val[0] != '\0') {
        return wayland_copy_path(env_val, buf, buf_size);
    }

    if (!wayland_get_home(home, sizeof(home))) {
        return false;
    }

    wayland_join_path(tmp, sizeof(tmp), home, fallback_suffix);
    return wayland_copy_path(tmp, buf, buf_size);
}

static void wayland_handle_keyboard_keymap(void* data,
                                           struct wl_keyboard* keyboard,
                                           uint32_t format,
                                           int fd,
                                           uint32_t size)
{
    (void)data;
    (void)keyboard;
    (void)format;
    (void)size;
    if (fd >= 0) {
        close(fd);
    }
}

static void wayland_handle_keyboard_enter(void* data,
                                          struct wl_keyboard* keyboard,
                                          uint32_t serial,
                                          struct wl_surface* surface,
                                          struct wl_array* keys)
{
    (void)data;
    (void)keyboard;
    (void)serial;
    (void)surface;
    (void)keys;
}

static void wayland_handle_keyboard_leave(void* data,
                                          struct wl_keyboard* keyboard,
                                          uint32_t serial,
                                          struct wl_surface* surface)
{
    (void)data;
    (void)keyboard;
    (void)serial;
    (void)surface;
}

static void wayland_handle_keyboard_key(void* data,
                                        struct wl_keyboard* keyboard,
                                        uint32_t serial,
                                        uint32_t time,
                                        uint32_t key,
                                        uint32_t state)
{
    dsys_event ev;
    (void)data;
    (void)keyboard;
    (void)serial;
    (void)time;

    memset(&ev, 0, sizeof(ev));
    ev.type = (state == WL_KEYBOARD_KEY_STATE_PRESSED) ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
    ev.payload.key.key = (int32_t)(key + 8u);
    ev.payload.key.repeat = false;
    wayland_push_event(&ev);
}

static void wayland_handle_keyboard_modifiers(void* data,
                                              struct wl_keyboard* keyboard,
                                              uint32_t serial,
                                              uint32_t depressed,
                                              uint32_t latched,
                                              uint32_t locked,
                                              uint32_t group)
{
    (void)data;
    (void)keyboard;
    (void)serial;
    (void)depressed;
    (void)latched;
    (void)locked;
    (void)group;
}

static void wayland_handle_keyboard_repeat(void* data,
                                           struct wl_keyboard* keyboard,
                                           int32_t rate,
                                           int32_t delay)
{
    (void)data;
    (void)keyboard;
    (void)rate;
    (void)delay;
}

static const struct wl_keyboard_listener g_keyboard_listener = {
    wayland_handle_keyboard_keymap,
    wayland_handle_keyboard_enter,
    wayland_handle_keyboard_leave,
    wayland_handle_keyboard_key,
    wayland_handle_keyboard_modifiers,
    wayland_handle_keyboard_repeat
};

static void wayland_handle_pointer_enter(void* data,
                                         struct wl_pointer* pointer,
                                         uint32_t serial,
                                         struct wl_surface* surface,
                                         wl_fixed_t sx,
                                         wl_fixed_t sy)
{
    (void)data;
    (void)pointer;
    (void)serial;
    if (g_wayland.main_window && g_wayland.main_window->surface == surface) {
        g_wayland.main_window->last_x = wl_fixed_to_int(sx);
        g_wayland.main_window->last_y = wl_fixed_to_int(sy);
    }
}

static void wayland_handle_pointer_leave(void* data,
                                         struct wl_pointer* pointer,
                                         uint32_t serial,
                                         struct wl_surface* surface)
{
    (void)data;
    (void)pointer;
    (void)serial;
    (void)surface;
}

static void wayland_handle_pointer_motion(void* data,
                                          struct wl_pointer* pointer,
                                          uint32_t time,
                                          wl_fixed_t sx,
                                          wl_fixed_t sy)
{
    dsys_event ev;
    int32_t    x;
    int32_t    y;
    dsys_window* win;
    (void)data;
    (void)pointer;
    (void)time;

    x = wl_fixed_to_int(sx);
    y = wl_fixed_to_int(sy);
    win = g_wayland.main_window;

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_MOVE;
    ev.payload.mouse_move.x = x;
    ev.payload.mouse_move.y = y;
    ev.payload.mouse_move.dx = 0;
    ev.payload.mouse_move.dy = 0;
    if (win) {
        ev.payload.mouse_move.dx = x - win->last_x;
        ev.payload.mouse_move.dy = y - win->last_y;
        win->last_x = x;
        win->last_y = y;
    }
    wayland_push_event(&ev);
}

static void wayland_handle_pointer_button(void* data,
                                          struct wl_pointer* pointer,
                                          uint32_t serial,
                                          uint32_t time,
                                          uint32_t button,
                                          uint32_t state)
{
    dsys_event ev;
    (void)data;
    (void)pointer;
    (void)serial;
    (void)time;

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_BUTTON;
    ev.payload.mouse_button.button = (int32_t)button;
    ev.payload.mouse_button.pressed = (state == WL_POINTER_BUTTON_STATE_PRESSED) ? true : false;
    ev.payload.mouse_button.clicks = 1;
    wayland_push_event(&ev);
}

static void wayland_handle_pointer_axis(void* data,
                                        struct wl_pointer* pointer,
                                        uint32_t time,
                                        uint32_t axis,
                                        wl_fixed_t value)
{
    dsys_event ev;
    (void)data;
    (void)pointer;
    (void)time;

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_WHEEL;
    ev.payload.mouse_wheel.delta_x = 0;
    ev.payload.mouse_wheel.delta_y = 0;
    if (axis == WL_POINTER_AXIS_VERTICAL_SCROLL) {
        ev.payload.mouse_wheel.delta_y = wl_fixed_to_int(value);
    } else if (axis == WL_POINTER_AXIS_HORIZONTAL_SCROLL) {
        ev.payload.mouse_wheel.delta_x = wl_fixed_to_int(value);
    }
    wayland_push_event(&ev);
}

static void wayland_handle_pointer_frame(void* data, struct wl_pointer* pointer)
{
    (void)data;
    (void)pointer;
}

static void wayland_handle_pointer_axis_source(void* data,
                                               struct wl_pointer* pointer,
                                               uint32_t axis_source)
{
    (void)data;
    (void)pointer;
    (void)axis_source;
}

static void wayland_handle_pointer_axis_stop(void* data,
                                             struct wl_pointer* pointer,
                                             uint32_t time,
                                             uint32_t axis)
{
    (void)data;
    (void)pointer;
    (void)time;
    (void)axis;
}

static void wayland_handle_pointer_axis_discrete(void* data,
                                                 struct wl_pointer* pointer,
                                                 uint32_t axis,
                                                 int32_t discrete)
{
    (void)data;
    (void)pointer;
    (void)axis;
    (void)discrete;
}

static const struct wl_pointer_listener g_pointer_listener = {
    wayland_handle_pointer_enter,
    wayland_handle_pointer_leave,
    wayland_handle_pointer_motion,
    wayland_handle_pointer_button,
    wayland_handle_pointer_axis,
    wayland_handle_pointer_frame,
    wayland_handle_pointer_axis_source,
    wayland_handle_pointer_axis_stop,
    wayland_handle_pointer_axis_discrete
};

static void wayland_wm_base_ping(void* data,
                                 struct xdg_wm_base* wm_base,
                                 uint32_t serial)
{
    (void)data;
    if (wm_base) {
        xdg_wm_base_pong(wm_base, serial);
    }
}

static const struct xdg_wm_base_listener g_wm_base_listener = {
    wayland_wm_base_ping
};

static void wayland_xdg_surface_configure(void* data,
                                          struct xdg_surface* surface,
                                          uint32_t serial)
{
    dsys_window* win;

    win = (dsys_window*)data;
    if (surface) {
        xdg_surface_ack_configure(surface, serial);
    }
    (void)win;
}

static const struct xdg_surface_listener g_xdg_surface_listener = {
    wayland_xdg_surface_configure
};

static void wayland_xdg_toplevel_configure(void* data,
                                           struct xdg_toplevel* toplevel,
                                           int32_t width,
                                           int32_t height,
                                           struct wl_array* states)
{
    dsys_window* win;
    dsys_event   ev;
    (void)toplevel;
    (void)states;

    win = (dsys_window*)data;
    if (!win) {
        return;
    }

    if (width > 0) {
        win->width = width;
    }
    if (height > 0) {
        win->height = height;
    }

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_WINDOW_RESIZED;
    ev.payload.window.width = win->width;
    ev.payload.window.height = win->height;
    wayland_push_event(&ev);
}

static void wayland_xdg_toplevel_close(void* data, struct xdg_toplevel* toplevel)
{
    dsys_event ev;
    (void)data;
    (void)toplevel;

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_QUIT;
    wayland_push_event(&ev);
}

static const struct xdg_toplevel_listener g_xdg_toplevel_listener = {
    wayland_xdg_toplevel_configure,
    wayland_xdg_toplevel_close
};

static void wayland_shell_ping(void* data, struct wl_shell_surface* shell_surface, uint32_t serial)
{
    (void)data;
    if (shell_surface) {
        wl_shell_surface_pong(shell_surface, serial);
    }
}

static void wayland_shell_configure(void* data,
                                    struct wl_shell_surface* shell_surface,
                                    uint32_t edges,
                                    int32_t width,
                                    int32_t height)
{
    dsys_window* win;
    dsys_event   ev;
    (void)shell_surface;
    (void)edges;

    win = (dsys_window*)data;
    if (!win) {
        return;
    }

    if (width > 0) {
        win->width = width;
    }
    if (height > 0) {
        win->height = height;
    }

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_WINDOW_RESIZED;
    ev.payload.window.width = win->width;
    ev.payload.window.height = win->height;
    wayland_push_event(&ev);
}

static void wayland_shell_popup_done(void* data, struct wl_shell_surface* shell_surface)
{
    (void)data;
    (void)shell_surface;
}

static const struct wl_shell_surface_listener g_shell_surface_listener = {
    wayland_shell_ping,
    wayland_shell_configure,
    wayland_shell_popup_done
};

static void wayland_seat_capabilities(void* data, struct wl_seat* seat, uint32_t capabilities)
{
    (void)data;

    if ((capabilities & WL_SEAT_CAPABILITY_KEYBOARD) && !g_wayland.keyboard) {
        g_wayland.keyboard = wl_seat_get_keyboard(seat);
        if (g_wayland.keyboard) {
            wl_keyboard_add_listener(g_wayland.keyboard, &g_keyboard_listener, NULL);
        }
    } else if (!(capabilities & WL_SEAT_CAPABILITY_KEYBOARD) && g_wayland.keyboard) {
        wl_keyboard_destroy(g_wayland.keyboard);
        g_wayland.keyboard = NULL;
    }

    if ((capabilities & WL_SEAT_CAPABILITY_POINTER) && !g_wayland.pointer) {
        g_wayland.pointer = wl_seat_get_pointer(seat);
        if (g_wayland.pointer) {
            wl_pointer_add_listener(g_wayland.pointer, &g_pointer_listener, NULL);
        }
    } else if (!(capabilities & WL_SEAT_CAPABILITY_POINTER) && g_wayland.pointer) {
        wl_pointer_destroy(g_wayland.pointer);
        g_wayland.pointer = NULL;
    }
}

static void wayland_seat_name(void* data, struct wl_seat* seat, const char* name)
{
    (void)data;
    (void)seat;
    (void)name;
}

static const struct wl_seat_listener g_seat_listener = {
    wayland_seat_capabilities,
    wayland_seat_name
};

static void wayland_registry_global(void* data,
                                    struct wl_registry* registry,
                                    uint32_t name,
                                    const char* interface,
                                    uint32_t version)
{
    (void)data;

    if (strcmp(interface, "wl_compositor") == 0) {
        g_wayland.compositor = (struct wl_compositor*)wl_registry_bind(registry, name, &wl_compositor_interface, version < 4u ? version : 4u);
    } else if (strcmp(interface, "wl_seat") == 0) {
        g_wayland.seat = (struct wl_seat*)wl_registry_bind(registry, name, &wl_seat_interface, 1u);
        if (g_wayland.seat) {
            wl_seat_add_listener(g_wayland.seat, &g_seat_listener, NULL);
        }
    } else if (strcmp(interface, "xdg_wm_base") == 0) {
        g_wayland.xdg_wm_base = (struct xdg_wm_base*)wl_registry_bind(registry, name, &xdg_wm_base_interface, 1u);
        g_wayland.use_xdg_shell = 1;
        if (g_wayland.xdg_wm_base) {
            xdg_wm_base_add_listener(g_wayland.xdg_wm_base, &g_wm_base_listener, NULL);
        }
    } else if (strcmp(interface, "wl_shell") == 0 && g_wayland.xdg_wm_base == NULL) {
        g_wayland.wl_shell = (struct wl_shell*)wl_registry_bind(registry, name, &wl_shell_interface, 1u);
        g_wayland.use_xdg_shell = 0;
    }
}

static void wayland_registry_global_remove(void* data, struct wl_registry* registry, uint32_t name)
{
    (void)data;
    (void)registry;
    (void)name;
}

static const struct wl_registry_listener g_registry_listener = {
    wayland_registry_global,
    wayland_registry_global_remove
};

static dsys_result wayland_init(void)
{
    memset(&g_wayland, 0, sizeof(g_wayland));
    g_wayland_caps.has_high_res_timer = false;

    g_wayland.display = wl_display_connect(NULL);
    if (!g_wayland.display) {
        return DSYS_ERR;
    }

    g_wayland.registry = wl_display_get_registry(g_wayland.display);
    if (!g_wayland.registry) {
        wl_display_disconnect(g_wayland.display);
        memset(&g_wayland, 0, sizeof(g_wayland));
        return DSYS_ERR;
    }
    wl_registry_add_listener(g_wayland.registry, &g_registry_listener, NULL);
    wl_display_roundtrip(g_wayland.display);
    wl_display_roundtrip(g_wayland.display);

    if (!g_wayland.compositor || (!g_wayland.xdg_wm_base && !g_wayland.wl_shell)) {
        wayland_shutdown();
        return DSYS_ERR;
    }

#if defined(CLOCK_MONOTONIC)
    {
        struct timespec ts;
        if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
            g_wayland_caps.has_high_res_timer = true;
        }
    }
#endif

    g_wayland.initialized = 1;
    return DSYS_OK;
}

static void wayland_shutdown(void)
{
    if (g_wayland.keyboard) {
        wl_keyboard_destroy(g_wayland.keyboard);
        g_wayland.keyboard = NULL;
    }
    if (g_wayland.pointer) {
        wl_pointer_destroy(g_wayland.pointer);
        g_wayland.pointer = NULL;
    }
    if (g_wayland.seat) {
        wl_seat_destroy(g_wayland.seat);
        g_wayland.seat = NULL;
    }

    if (g_wayland.main_window) {
        wayland_window_destroy(g_wayland.main_window);
    }

    if (g_wayland.use_xdg_shell) {
        if (g_wayland.xdg_wm_base) {
            xdg_wm_base_destroy(g_wayland.xdg_wm_base);
        }
    } else if (g_wayland.wl_shell) {
        wl_shell_destroy(g_wayland.wl_shell);
    }
    g_wayland.xdg_wm_base = NULL;
    g_wayland.wl_shell = NULL;

    if (g_wayland.compositor) {
        wl_compositor_destroy(g_wayland.compositor);
        g_wayland.compositor = NULL;
    }

    if (g_wayland.registry) {
        wl_registry_destroy(g_wayland.registry);
        g_wayland.registry = NULL;
    }

    if (g_wayland.display) {
        wl_display_disconnect(g_wayland.display);
        g_wayland.display = NULL;
    }

    memset(&g_wayland, 0, sizeof(g_wayland));
}

static dsys_caps wayland_get_caps(void)
{
    return g_wayland_caps;
}

static uint64_t wayland_time_now_us(void)
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
        if (gettimeofday(&tv, (struct timezone*)0) == 0) {
            return ((uint64_t)tv.tv_sec * 1000000u) + (uint64_t)tv.tv_usec;
        }
    }
    return 0u;
}

static void wayland_sleep_ms(uint32_t ms)
{
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR) {
        /* retry */
    }
}

static dsys_window* wayland_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc   local_desc;
    dsys_window*       win;
    struct wl_surface* surface;

    if (!g_wayland.display || !g_wayland.compositor || (!g_wayland.xdg_wm_base && !g_wayland.wl_shell)) {
        return NULL;
    }

    if (g_wayland.main_window) {
        return g_wayland.main_window;
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

    surface = wl_compositor_create_surface(g_wayland.compositor);
    if (!surface) {
        return NULL;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        wl_surface_destroy(surface);
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->surface = surface;
    win->width = local_desc.width > 0 ? local_desc.width : 800;
    win->height = local_desc.height > 0 ? local_desc.height : 600;
    win->last_x = 0;
    win->last_y = 0;
    win->mode = local_desc.mode;

    if (g_wayland.use_xdg_shell) {
        struct xdg_surface*  xsurf;
        struct xdg_toplevel* top;
        xsurf = xdg_wm_base_get_xdg_surface(g_wayland.xdg_wm_base, surface);
        if (!xsurf) {
            wl_surface_destroy(surface);
            free(win);
            return NULL;
        }
        xdg_surface_add_listener(xsurf, &g_xdg_surface_listener, win);
        top = xdg_surface_get_toplevel(xsurf);
        if (!top) {
            xdg_surface_destroy(xsurf);
            wl_surface_destroy(surface);
            free(win);
            return NULL;
        }
        xdg_toplevel_add_listener(top, &g_xdg_toplevel_listener, win);
        xdg_toplevel_set_title(top, "Domino");
        win->xdg_toplevel = top;
        win->xdg_surface = xsurf;
    } else {
        struct wl_shell_surface* shell_surface;
        shell_surface = wl_shell_get_shell_surface(g_wayland.wl_shell, surface);
        if (!shell_surface) {
            wl_surface_destroy(surface);
            free(win);
            return NULL;
        }
        wl_shell_surface_add_listener(shell_surface, &g_shell_surface_listener, win);
        wl_shell_surface_set_toplevel(shell_surface);
        win->shell_surface = shell_surface;
        win->xdg_surface = NULL;
        win->xdg_toplevel = NULL;
    }

    wl_surface_commit(surface);
    wl_display_flush(g_wayland.display);

    g_wayland.main_window = win;
    return win;
}

static void wayland_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }

    if (g_wayland.use_xdg_shell) {
        if (win->xdg_toplevel) {
            xdg_toplevel_destroy(win->xdg_toplevel);
        }
        if (win->xdg_surface) {
            xdg_surface_destroy(win->xdg_surface);
        }
    } else {
        if (win->shell_surface) {
            wl_shell_surface_destroy(win->shell_surface);
        }
    }

    if (win->surface) {
        wl_surface_destroy(win->surface);
    }

    if (g_wayland.main_window == win) {
        g_wayland.main_window = NULL;
    }

    free(win);
}

static void wayland_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }

    if (g_wayland.use_xdg_shell && win->xdg_toplevel) {
        if (mode == DWIN_MODE_FULLSCREEN || mode == DWIN_MODE_BORDERLESS) {
            xdg_toplevel_set_fullscreen(win->xdg_toplevel, NULL);
        } else {
            xdg_toplevel_unset_fullscreen(win->xdg_toplevel);
        }
    }
    win->mode = mode;
}

static void wayland_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

static void wayland_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

static void* wayland_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)win->surface;
}

static bool wayland_poll_event(dsys_event* ev)
{
    struct pollfd pfd;
    int           ret;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    if (!g_wayland.display) {
        return false;
    }

    wl_display_dispatch_pending(g_wayland.display);

    if (wl_display_prepare_read(g_wayland.display) == 0) {
        wl_display_flush(g_wayland.display);
        pfd.fd = wl_display_get_fd(g_wayland.display);
        pfd.events = POLLIN;
        ret = poll(&pfd, 1, 0);
        if (ret > 0 && (pfd.revents & POLLIN)) {
            wl_display_read_events(g_wayland.display);
        } else {
            wl_display_cancel_read(g_wayland.display);
        }
    } else {
        wl_display_dispatch_pending(g_wayland.display);
    }

    wl_display_dispatch_pending(g_wayland.display);
    wl_display_flush(g_wayland.display);

    if (g_wayland.event_head != g_wayland.event_tail) {
        if (ev) {
            *ev = g_wayland.event_queue[g_wayland.event_head];
        }
        g_wayland.event_head = (g_wayland.event_head + 1) % 64;
        return true;
    }

    return false;
}

static bool wayland_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    bool ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';
    ok = false;

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        ok = wayland_resolve_exe_dir(buf, buf_size);
        break;

    case DSYS_PATH_USER_DATA:
        {
            char base[260];
            char joined[260];
            if (wayland_pick_xdg("XDG_DATA_HOME", ".local/share", base, sizeof(base))) {
                wayland_join_path(joined, sizeof(joined), base, "dominium");
                ok = wayland_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_USER_CONFIG:
        {
            char base[260];
            char joined[260];
            if (wayland_pick_xdg("XDG_CONFIG_HOME", ".config", base, sizeof(base))) {
                wayland_join_path(joined, sizeof(joined), base, "dominium");
                ok = wayland_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_USER_CACHE:
        {
            char base[260];
            char joined[260];
            if (wayland_pick_xdg("XDG_CACHE_HOME", ".cache", base, sizeof(base))) {
                wayland_join_path(joined, sizeof(joined), base, "dominium");
                ok = wayland_copy_path(joined, buf, buf_size);
            }
        }
        break;

    case DSYS_PATH_TEMP:
        {
            const char* tmpdir;
            tmpdir = getenv("TMPDIR");
            if (tmpdir && tmpdir[0] != '\0') {
                ok = wayland_copy_path(tmpdir, buf, buf_size);
            } else {
                ok = wayland_copy_path("/tmp", buf, buf_size);
            }
        }
        break;

    default:
        break;
    }

    if (!ok) {
        buf[0] = '\0';
    }
    return ok;
}

static void* wayland_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t wayland_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t wayland_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int wayland_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long wayland_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int wayland_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* wayland_dir_open(const char* path)
{
    dsys_dir_iter* it;
    DIR*           dir;

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
    {
        size_t len;
        len = strlen(path);
        if (len >= sizeof(it->base)) {
            len = sizeof(it->base) - 1u;
        }
        memcpy(it->base, path, len);
        it->base[len] = '\0';
    }
    return it;
}

static bool wayland_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
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
        break;
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
        size_t      name_len;
        size_t      path_len;
        path_len = strlen(it->base);
        name_len = strlen(out->name);
        if (path_len + name_len + 2u < sizeof(full)) {
            memcpy(full, it->base, path_len);
            if (path_len > 0u && full[path_len - 1u] != '/') {
                full[path_len] = '/';
                path_len += 1u;
            }
            memcpy(full + path_len, out->name, name_len);
            full[path_len + name_len] = '\0';
            if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                out->is_dir = true;
            }
        }
    }
#else
    {
        struct stat st;
        char        full[260];
        size_t      name_len;
        size_t      path_len;
        path_len = strlen(it->base);
        name_len = strlen(out->name);
        if (path_len + name_len + 2u < sizeof(full)) {
            memcpy(full, it->base, path_len);
            if (path_len > 0u && full[path_len - 1u] != '/') {
                full[path_len] = '/';
                path_len += 1u;
            }
            memcpy(full + path_len, out->name, name_len);
            full[path_len + name_len] = '\0';
            if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                out->is_dir = true;
            }
        }
    }
#endif

    return true;
}

static void wayland_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* wayland_process_spawn(const dsys_process_desc* desc)
{
    pid_t         pid;
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

static int wayland_process_wait(dsys_process* p)
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

static void wayland_process_destroy(dsys_process* p)
{
    if (!p) {
        return;
    }
    free(p);
}

const dsys_backend_vtable* dsys_wayland_get_vtable(void)
{
    return &g_wayland_vtable;
}

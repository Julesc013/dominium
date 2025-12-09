#include "dos16_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <dirent.h>
#include <conio.h>

#if defined(__TURBOC__) || defined(__WATCOMC__) || defined(_MSC_VER) || defined(__DJGPP__)
#include <dos.h>
#endif

#define DOS16_EVENT_QUEUE_CAP 32

dos16_global_t g_dos16;

static const dsys_caps g_dos16_caps = { "dos16", 1u, true, true, false, false };

/*----------------------------------------------------------------------
 * Helpers
 *----------------------------------------------------------------------*/
static void dos16_push_event(const dsys_event* ev)
{
    int next;
    if (!ev) {
        return;
    }
    next = (g_dos16.ev_tail + 1) % DOS16_EVENT_QUEUE_CAP;
    if (next == g_dos16.ev_head) {
        return;
    }
    g_dos16.event_queue[g_dos16.ev_tail] = *ev;
    g_dos16.ev_tail = next;
}

static bool dos16_pop_event(dsys_event* ev)
{
    if (g_dos16.ev_head == g_dos16.ev_tail) {
        return false;
    }
    if (ev) {
        *ev = g_dos16.event_queue[g_dos16.ev_head];
    }
    g_dos16.ev_head = (g_dos16.ev_head + 1) % DOS16_EVENT_QUEUE_CAP;
    return true;
}

static uint64_t dos16_time_now_us_internal(void)
{
    clock_t c;
    if (CLOCKS_PER_SEC == 0) {
        return 0u;
    }
    c = clock();
    if (c < 0) {
        return 0u;
    }
    return ((uint64_t)c * 1000000ULL) / (uint64_t)CLOCKS_PER_SEC;
}

static void dos16_set_mode_13h(void)
{
#if defined(__TURBOC__) || defined(__WATCOMC__) || defined(_MSC_VER) || defined(__DJGPP__)
    union REGS r;
    r.h.ah = 0x00;
    r.h.al = 0x13;
    int86(0x10, &r, &r);
#endif
}

static void dos16_restore_text_mode(void)
{
#if defined(__TURBOC__) || defined(__WATCOMC__) || defined(_MSC_VER) || defined(__DJGPP__)
    union REGS r;
    r.h.ah = 0x00;
    r.h.al = 0x03;
    int86(0x10, &r, &r);
#endif
}

static void dos16_detect_mouse(void)
{
#if defined(__TURBOC__) || defined(__WATCOMC__) || defined(_MSC_VER) || defined(__DJGPP__)
    union REGS r;
    r.x.ax = 0x0000;
    int86(0x33, &r, &r);
    if (r.x.ax == 0xFFFF) {
        g_dos16.mouse_present = 1;
        r.x.ax = 0x0001;
        int86(0x33, &r, &r);
    }
#endif
}

static void dos16_poll_keyboard(void)
{
    while (kbhit()) {
        int ch;
        dsys_event ev;

        ch = getch();
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_KEY_DOWN;
        ev.payload.key.key = (int32_t)ch;
        ev.payload.key.repeat = false;
        dos16_push_event(&ev);

        memset(&ev, 0, sizeof(ev));
        if (ch == 27) {
            ev.type = DSYS_EVENT_QUIT;
        } else {
            ev.type = DSYS_EVENT_KEY_UP;
            ev.payload.key.key = (int32_t)ch;
            ev.payload.key.repeat = false;
        }
        dos16_push_event(&ev);
    }
}

static void dos16_poll_mouse(void)
{
#if defined(__TURBOC__) || defined(__WATCOMC__) || defined(_MSC_VER) || defined(__DJGPP__)
    union REGS r;
    int        buttons;
    int        x;
    int        y;
    int        changed;

    if (!g_dos16.mouse_present) {
        return;
    }

    r.x.ax = 0x0003;
    int86(0x33, &r, &r);
    buttons = (int)r.x.bx;
    x = (int)r.x.cx;
    y = (int)r.x.dx;

    if (x != g_dos16.mouse_x || y != g_dos16.mouse_y) {
        dsys_event ev;
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_MOUSE_MOVE;
        ev.payload.mouse_move.x = x;
        ev.payload.mouse_move.y = y;
        ev.payload.mouse_move.dx = x - g_dos16.mouse_x;
        ev.payload.mouse_move.dy = y - g_dos16.mouse_y;
        dos16_push_event(&ev);
        g_dos16.mouse_x = (int16_t)x;
        g_dos16.mouse_y = (int16_t)y;
    }

    changed = buttons ^ g_dos16.mouse_buttons;
    if (changed != 0) {
        int i;
        for (i = 0; i < 3; ++i) {
            int mask;
            mask = 1 << i;
            if (changed & mask) {
                dsys_event ev;
                memset(&ev, 0, sizeof(ev));
                ev.type = DSYS_EVENT_MOUSE_BUTTON;
                ev.payload.mouse_button.button = i + 1;
                ev.payload.mouse_button.pressed = (buttons & mask) ? true : false;
                ev.payload.mouse_button.clicks = 1;
                dos16_push_event(&ev);
            }
        }
        g_dos16.mouse_buttons = (unsigned int)buttons;
    }
#endif
}

/*----------------------------------------------------------------------
 * Backend vtable
 *----------------------------------------------------------------------*/
static dsys_result dos16_init(void);
static void        dos16_shutdown(void);
static dsys_caps   dos16_get_caps(void);

static uint64_t dos16_time_now_us(void);
static void     dos16_sleep_ms(uint32_t ms);

static dsys_window* dos16_window_create(const dsys_window_desc* desc);
static void         dos16_window_destroy(dsys_window* win);
static void         dos16_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         dos16_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         dos16_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        dos16_window_get_native_handle(dsys_window* win);

static bool dos16_poll_event(dsys_event* ev);

static bool   dos16_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  dos16_file_open(const char* path, const char* mode);
static size_t dos16_file_read(void* fh, void* buf, size_t size);
static size_t dos16_file_write(void* fh, const void* buf, size_t size);
static int    dos16_file_seek(void* fh, long offset, int origin);
static long   dos16_file_tell(void* fh);
static int    dos16_file_close(void* fh);

static dsys_dir_iter* dos16_dir_open(const char* path);
static bool           dos16_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           dos16_dir_close(dsys_dir_iter* it);

static dsys_process* dos16_process_spawn(const dsys_process_desc* desc);
static int           dos16_process_wait(dsys_process* p);
static void          dos16_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_dos16_vtable = {
    dos16_init,
    dos16_shutdown,
    dos16_get_caps,
    dos16_time_now_us,
    dos16_sleep_ms,
    dos16_window_create,
    dos16_window_destroy,
    dos16_window_set_mode,
    dos16_window_set_size,
    dos16_window_get_size,
    dos16_window_get_native_handle,
    dos16_poll_event,
    dos16_get_path,
    dos16_file_open,
    dos16_file_read,
    dos16_file_write,
    dos16_file_seek,
    dos16_file_tell,
    dos16_file_close,
    dos16_dir_open,
    dos16_dir_next,
    dos16_dir_close,
    dos16_process_spawn,
    dos16_process_wait,
    dos16_process_destroy
};

static dsys_result dos16_init(void)
{
    memset(&g_dos16, 0, sizeof(g_dos16));
    g_dos16.ev_head = 0;
    g_dos16.ev_tail = 0;
    g_dos16.initialized = 1;
    dos16_detect_mouse();
    return DSYS_OK;
}

static void dos16_shutdown(void)
{
    if (!g_dos16.initialized) {
        return;
    }
    if (g_dos16.main_window) {
        dos16_window_destroy(g_dos16.main_window);
    }
    dos16_restore_text_mode();
    memset(&g_dos16, 0, sizeof(g_dos16));
}

static dsys_caps dos16_get_caps(void)
{
    dsys_caps caps;
    caps = g_dos16_caps;
    caps.has_mouse = g_dos16.mouse_present ? true : false;
    return caps;
}

static uint64_t dos16_time_now_us(void)
{
    return dos16_time_now_us_internal();
}

static void dos16_sleep_ms(uint32_t ms)
{
    uint64_t start;
    uint64_t target;
    start = dos16_time_now_us_internal();
    target = start + ((uint64_t)ms * 1000ULL);
    while (dos16_time_now_us_internal() < target) {
        /* busy wait */
    }
}

static dsys_window* dos16_window_create(const dsys_window_desc* desc)
{
    dsys_window* win;

    (void)desc;
    if (g_dos16.main_window) {
        return g_dos16.main_window;
    }

    dos16_set_mode_13h();

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));

#if defined(MK_FP)
    win->fb.base = MK_FP(0xA000, 0x0000);
#else
    win->fb.base = (void _far*)0;
#endif
    win->fb.width = 320;
    win->fb.height = 200;
    win->fb.pitch = 320;
    win->fb.bpp = 8;
    win->fb.is_vesa = 0;
    win->fb.vesa_mode = 0x13;
    win->mode = DWIN_MODE_FULLSCREEN;

    g_dos16.main_window = win;
    return win;
}

static void dos16_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win == g_dos16.main_window) {
        g_dos16.main_window = NULL;
    }
    dos16_restore_text_mode();
    free(win);
}

static void dos16_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    (void)win;
    (void)mode;
}

static void dos16_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    (void)win;
    (void)w;
    (void)h;
}

static void dos16_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        return;
    }
    if (w) {
        *w = (int32_t)win->fb.width;
    }
    if (h) {
        *h = (int32_t)win->fb.height;
    }
}

static void* dos16_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)&win->fb;
}

static bool dos16_poll_event(dsys_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    dos16_poll_keyboard();
    dos16_poll_mouse();

    if (dos16_pop_event(ev)) {
        return true;
    }
    return false;
}

static bool dos16_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* p;

    if (!buf || buf_size == 0u) {
        return false;
    }

    p = ".";
    switch (kind) {
    case DSYS_PATH_APP_ROOT:    p = "."; break;
    case DSYS_PATH_USER_DATA:   p = "."; break;
    case DSYS_PATH_USER_CONFIG: p = "."; break;
    case DSYS_PATH_USER_CACHE:  p = "."; break;
    case DSYS_PATH_TEMP:        p = "."; break;
    default: break;
    }

    strncpy(buf, p, buf_size);
    buf[buf_size - 1u] = '\0';
    return true;
}

static void* dos16_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t dos16_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t dos16_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int dos16_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long dos16_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int dos16_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* dos16_dir_open(const char* path)
{
    dsys_dir_iter* it;

    if (!path) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        return NULL;
    }
    memset(it, 0, sizeof(*it));
    it->dir = opendir(path);
    if (!it->dir) {
        free(it);
        return NULL;
    }
    return it;
}

static bool dos16_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;

    if (!it || !out || !it->dir) {
        return false;
    }

    for (;;) {
        ent = readdir(it->dir);
        if (!ent) {
            return false;
        }
        if (ent->d_name[0] == '.' &&
            (ent->d_name[1] == '\0' ||
             (ent->d_name[1] == '.' && ent->d_name[2] == '\0'))) {
            continue;
        }
        strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = false;
        return true;
    }
}

static void dos16_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* dos16_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int dos16_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void dos16_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_dos16_get_vtable(void)
{
    return &g_dos16_vtable;
}

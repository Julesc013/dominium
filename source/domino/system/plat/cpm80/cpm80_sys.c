#include "cpm80_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Optional CP/M BDOS binding; stubbed when not on a CP/M toolchain. */
static unsigned char cpm80_bdos(unsigned char func, unsigned short de)
{
#if defined(__CPM__) || defined(DSYS_CPM80_NATIVE)
    extern int bdos(int func, int de);
    return (unsigned char)bdos((int)func, (int)de);
#else
    (void)func;
    (void)de;
    return 0;
#endif
}

cpm80_global_t g_cpm80;

static const dsys_caps g_cpm80_caps = { "cpm80", 1u, true, false, false, false };

/*----------------------------------------------------------------------
 * Helpers
 *----------------------------------------------------------------------*/
static void cpm80_push_event(const dsys_event* ev)
{
    int next;
    if (!ev) {
        return;
    }
    next = (g_cpm80.ev_tail + 1) % 16;
    if (next == g_cpm80.ev_head) {
        return;
    }
    g_cpm80.event_queue[g_cpm80.ev_tail] = *ev;
    g_cpm80.ev_tail = next;
}

static bool cpm80_pop_event(dsys_event* ev)
{
    if (g_cpm80.ev_head == g_cpm80.ev_tail) {
        return false;
    }
    if (ev) {
        *ev = g_cpm80.event_queue[g_cpm80.ev_head];
    }
    g_cpm80.ev_head = (g_cpm80.ev_head + 1) % 16;
    return true;
}

static int cpm80_read_char(void)
{
    unsigned char ch;
    ch = cpm80_bdos(6u, 0xFF00u);
    return (ch == 0u) ? -1 : (int)ch;
}

/*----------------------------------------------------------------------
 * Backend vtable
 *----------------------------------------------------------------------*/
static dsys_result cpm80_init(void);
static void        cpm80_shutdown(void);
static dsys_caps   cpm80_get_caps(void);

static uint64_t cpm80_time_now_us(void);
static void     cpm80_sleep_ms(uint32_t ms);

static dsys_window* cpm80_window_create(const dsys_window_desc* desc);
static void         cpm80_window_destroy(dsys_window* win);
static void         cpm80_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         cpm80_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         cpm80_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        cpm80_window_get_native_handle(dsys_window* win);

static bool cpm80_poll_event(dsys_event* ev);

static bool   cpm80_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  cpm80_file_open(const char* path, const char* mode);
static size_t cpm80_file_read(void* fh, void* buf, size_t size);
static size_t cpm80_file_write(void* fh, const void* buf, size_t size);
static int    cpm80_file_seek(void* fh, long offset, int origin);
static long   cpm80_file_tell(void* fh);
static int    cpm80_file_close(void* fh);

static dsys_dir_iter* cpm80_dir_open(const char* path);
static bool           cpm80_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           cpm80_dir_close(dsys_dir_iter* it);

static dsys_process* cpm80_process_spawn(const dsys_process_desc* desc);
static int           cpm80_process_wait(dsys_process* p);
static void          cpm80_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_cpm80_vtable = {
    cpm80_init,
    cpm80_shutdown,
    cpm80_get_caps,
    cpm80_time_now_us,
    cpm80_sleep_ms,
    cpm80_window_create,
    cpm80_window_destroy,
    cpm80_window_set_mode,
    cpm80_window_set_size,
    cpm80_window_get_size,
    cpm80_window_get_native_handle,
    cpm80_poll_event,
    cpm80_get_path,
    cpm80_file_open,
    cpm80_file_read,
    cpm80_file_write,
    cpm80_file_seek,
    cpm80_file_tell,
    cpm80_file_close,
    cpm80_dir_open,
    cpm80_dir_next,
    cpm80_dir_close,
    cpm80_process_spawn,
    cpm80_process_wait,
    cpm80_process_destroy
};

static dsys_result cpm80_init(void)
{
    memset(&g_cpm80, 0, sizeof(g_cpm80));
    g_cpm80.initialized = 1;
    g_cpm80.time_us = 0u;
    return DSYS_OK;
}

static void cpm80_shutdown(void)
{
    if (!g_cpm80.initialized) {
        return;
    }
    if (g_cpm80.main_window) {
        if (g_cpm80.main_window->fb.pixels) {
            free(g_cpm80.main_window->fb.pixels);
        }
        free(g_cpm80.main_window);
    }
    memset(&g_cpm80, 0, sizeof(g_cpm80));
}

static dsys_caps cpm80_get_caps(void)
{
    return g_cpm80_caps;
}

static uint64_t cpm80_time_now_us(void)
{
    return g_cpm80.time_us;
}

static void cpm80_sleep_ms(uint32_t ms)
{
    g_cpm80.time_us += ((uint64_t)ms * 1000ULL);
}

static dsys_window* cpm80_window_create(const dsys_window_desc* desc)
{
    dsys_window* win;
    uint16_t     w;
    uint16_t     h;
    uint32_t     size;

    if (g_cpm80.main_window) {
        return g_cpm80.main_window;
    }

    (void)desc;
    w = 320;
    h = 200;
    size = (uint32_t)w * (uint32_t)h;

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));

    win->fb.width = w;
    win->fb.height = h;
    win->fb.pitch = w;
    win->fb.bpp = 8;
    win->fb.pixels = (uint8_t*)malloc(size);
    if (win->fb.pixels) {
        memset(win->fb.pixels, 0, size);
    }
    win->mode = DWIN_MODE_FULLSCREEN;

    g_cpm80.main_window = win;
    return win;
}

static void cpm80_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win->fb.pixels) {
        free(win->fb.pixels);
    }
    if (g_cpm80.main_window == win) {
        g_cpm80.main_window = NULL;
    }
    free(win);
}

static void cpm80_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    (void)win;
    (void)mode;
}

static void cpm80_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    (void)win;
    (void)w;
    (void)h;
}

static void cpm80_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

static void* cpm80_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)&win->fb;
}

static bool cpm80_poll_event(dsys_event* ev)
{
    int ch;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    ch = cpm80_read_char();
    if (ch >= 0) {
        dsys_event e;
        memset(&e, 0, sizeof(e));
        if (ch == 27) {
            e.type = DSYS_EVENT_QUIT;
        } else {
            e.type = DSYS_EVENT_KEY_DOWN;
            e.payload.key.key = (int32_t)ch;
            e.payload.key.repeat = false;
        }
        cpm80_push_event(&e);
    }

    if (cpm80_pop_event(ev)) {
        return true;
    }
    return false;
}

static bool cpm80_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* p;

    (void)kind;
    if (!buf || buf_size == 0u) {
        return false;
    }
    p = "";
    strncpy(buf, p, buf_size);
    buf[buf_size - 1u] = '\0';
    return true;
}

static void* cpm80_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t cpm80_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t cpm80_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int cpm80_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long cpm80_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int cpm80_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* cpm80_dir_open(const char* path)
{
    (void)path;
    return NULL;
}

static bool cpm80_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    (void)it;
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static void cpm80_dir_close(dsys_dir_iter* it)
{
    (void)it;
}

static dsys_process* cpm80_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int cpm80_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void cpm80_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_cpm80_get_vtable(void)
{
    return &g_cpm80_vtable;
}

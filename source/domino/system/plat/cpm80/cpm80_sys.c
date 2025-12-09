#include "cpm80_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* Optional CP/M BDOS binding. When not building for CP/M, this stub returns 0
 * so the backend can still compile as a hosted stub. */
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

static const dsys_caps g_cpm80_caps = { "cpm80", 1u, true, false, false, false };
static uint64_t        g_cpm80_time_us = 0u;
static dsys_window*    g_cpm80_window = NULL;

cpm80_global_t g_cpm80;

static void cpm80_reset_state(void)
{
    memset(&g_cpm80, 0, sizeof(g_cpm80));
    g_cpm80_window = NULL;
    g_cpm80.fullscreen = 1;
    g_cpm80_time_us = 0u;
}

static bool cpm80_copy_string(const char* src, char* buf, size_t buf_size)
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
    if (g_cpm80.initialized) {
        return DSYS_OK;
    }

    cpm80_reset_state();
    g_cpm80.initialized = 1;
    return DSYS_OK;
}

static void cpm80_shutdown(void)
{
    if (!g_cpm80.initialized) {
        return;
    }
    if (g_cpm80_window) {
        free(g_cpm80_window);
        g_cpm80_window = NULL;
    }
    cpm80_reset_state();
}

static dsys_caps cpm80_get_caps(void)
{
    return g_cpm80_caps;
}

static uint64_t cpm80_time_now_us(void)
{
    uint64_t now;

    now = g_cpm80_time_us;
#if defined(CLOCKS_PER_SEC)
    {
        clock_t c;
        c = clock();
        if (c >= 0 && CLOCKS_PER_SEC > 0) {
            now = ((uint64_t)c * 1000000u) / (uint64_t)CLOCKS_PER_SEC;
            if (now < g_cpm80_time_us) {
                now = g_cpm80_time_us + 1000u;
            }
        } else {
            now = g_cpm80_time_us + 1000u;
        }
    }
#else
    now = g_cpm80_time_us + 1000u;
#endif
    g_cpm80_time_us = now;
    return g_cpm80_time_us;
}

static void cpm80_sleep_ms(uint32_t ms)
{
    uint64_t start;
    uint64_t target;

    start = cpm80_time_now_us();
    target = start + ((uint64_t)ms * 1000u);
    while (cpm80_time_now_us() < target) {
        /* busy wait; CP/M has no scheduler */
    }
}

static dsys_window* cpm80_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local_desc;
    dsys_window*     win;

    if (g_cpm80_window) {
        return NULL;
    }

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 0;
        local_desc.height = 0;
        local_desc.mode = DWIN_MODE_FULLSCREEN;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));

    win->width = local_desc.width;
    win->height = local_desc.height;
    win->mode = DWIN_MODE_FULLSCREEN;
    win->fb_ptr = NULL;

    g_cpm80.width = local_desc.width;
    g_cpm80.height = local_desc.height;
    g_cpm80.fullscreen = 1;
    g_cpm80_window = win;
    return win;
}

static void cpm80_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win == g_cpm80_window) {
        g_cpm80_window = NULL;
    }
    free(win);
}

static void cpm80_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
    g_cpm80.fullscreen = 1;
}

static void cpm80_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
    g_cpm80.width = w;
    g_cpm80.height = h;
}

static void cpm80_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

static void* cpm80_window_get_native_handle(dsys_window* win)
{
    /* CP/M-80 has no native window handle; return the logical window pointer. */
    return (void*)win;
}

static bool cpm80_poll_event(dsys_event* ev)
{
    unsigned char ch;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    ch = cpm80_bdos(6u, 0xFF00u);
    if (ch == 0u) {
        return false;
    }

    if (!ev) {
        return true;
    }

    if (ch == 0x1B || ch == 0x03) {
        ev->type = DSYS_EVENT_QUIT;
    } else {
        ev->type = DSYS_EVENT_KEY_DOWN;
        ev->payload.key.key = (int32_t)ch;
        ev->payload.key.repeat = false;
    }
    return true;
}

static bool cpm80_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* str;

    str = "A:";
    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        str = "A:";
        break;
    case DSYS_PATH_USER_DATA:
        str = "A:DOMDATA";
        break;
    case DSYS_PATH_USER_CONFIG:
        str = "A:DOMCFG";
        break;
    case DSYS_PATH_USER_CACHE:
        str = "A:CACHE";
        break;
    case DSYS_PATH_TEMP:
        str = "A:TEMP";
        break;
    default:
        str = "A:";
        break;
    }

    return cpm80_copy_string(str, buf, buf_size);
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
    dsys_dir_iter* it;
    size_t         len;

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        return NULL;
    }
    memset(it, 0, sizeof(*it));
    if (path) {
        len = strlen(path);
        if (len >= sizeof(it->pattern)) {
            len = sizeof(it->pattern) - 1u;
        }
        memcpy(it->pattern, path, len);
        it->pattern[len] = '\0';
    }
    it->done = 1;
    return it;
}

static bool cpm80_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    if (!it || it->done) {
        return false;
    }
    it->done = 1;
    return false;
}

static void cpm80_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    free(it);
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

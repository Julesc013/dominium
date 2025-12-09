#include "cocoa_sys.h"

#include <mach/mach_time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef NULL
#define NULL ((void*)0)
#endif

static dsys_result cocoa_init(void);
static void        cocoa_shutdown(void);
static dsys_caps   cocoa_get_caps(void);

static uint64_t cocoa_time_now_us(void);
static void     cocoa_sleep_ms(uint32_t ms);

static dsys_window* cocoa_window_create(const dsys_window_desc* desc);
static void         cocoa_window_destroy(dsys_window* win);
static void         cocoa_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         cocoa_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         cocoa_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        cocoa_window_get_native_handle(dsys_window* win);

static bool cocoa_poll_event(dsys_event* ev);

static bool   cocoa_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  cocoa_file_open(const char* path, const char* mode);
static size_t cocoa_file_read(void* fh, void* buf, size_t size);
static size_t cocoa_file_write(void* fh, const void* buf, size_t size);
static int    cocoa_file_seek(void* fh, long offset, int origin);
static long   cocoa_file_tell(void* fh);
static int    cocoa_file_close(void* fh);

static dsys_dir_iter* cocoa_dir_open(const char* path);
static bool           cocoa_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           cocoa_dir_close(dsys_dir_iter* it);

static dsys_process* cocoa_process_spawn(const dsys_process_desc* desc);
static int           cocoa_process_wait(dsys_process* p);
static void          cocoa_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_cocoa_vtable = {
    cocoa_init,
    cocoa_shutdown,
    cocoa_get_caps,
    cocoa_time_now_us,
    cocoa_sleep_ms,
    cocoa_window_create,
    cocoa_window_destroy,
    cocoa_window_set_mode,
    cocoa_window_set_size,
    cocoa_window_get_size,
    cocoa_window_get_native_handle,
    cocoa_poll_event,
    cocoa_get_path,
    cocoa_file_open,
    cocoa_file_read,
    cocoa_file_write,
    cocoa_file_seek,
    cocoa_file_tell,
    cocoa_file_close,
    cocoa_dir_open,
    cocoa_dir_next,
    cocoa_dir_close,
    cocoa_process_spawn,
    cocoa_process_wait,
    cocoa_process_destroy
};

static dsys_caps g_cocoa_caps = { "cocoa", 1u, true, true, false, true };

cocoa_global_t g_cocoa = { 0 };

static dsys_result cocoa_init(void)
{
    g_cocoa.initialized = 1;
    g_cocoa.main_window = NULL;
    g_cocoa.head = 0;
    g_cocoa.tail = 0;
    memset(g_cocoa.queue, 0, sizeof(g_cocoa.queue));
    cocoa_objc_init_app();
    return DSYS_OK;
}

static void cocoa_shutdown(void)
{
    if (g_cocoa.main_window) {
        cocoa_window_destroy(g_cocoa.main_window);
        g_cocoa.main_window = NULL;
    }
    cocoa_objc_shutdown();
    g_cocoa.initialized = 0;
    g_cocoa.head = 0;
    g_cocoa.tail = 0;
}

static dsys_caps cocoa_get_caps(void)
{
    return g_cocoa_caps;
}

static uint64_t cocoa_time_now_us(void)
{
    static mach_timebase_info_data_t tb = { 0, 0 };
    uint64_t t;
    uint64_t ns;

    if (tb.denom == 0) {
        mach_timebase_info(&tb);
        if (tb.denom == 0) {
            tb.numer = 1;
            tb.denom = 1;
        }
    }

    t = mach_absolute_time();
    ns = t * tb.numer / tb.denom;
    return ns / 1000ULL;
}

static void cocoa_sleep_ms(uint32_t ms)
{
    uint64_t target;
    target = cocoa_time_now_us() + ((uint64_t)ms * 1000ULL);
    while (cocoa_time_now_us() < target) {
        /* busy wait */
    }
}

static dsys_window* cocoa_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local;
    dsys_window*     win;
    void*            ns_window;

    if (desc) {
        local = *desc;
    } else {
        local.x = 0;
        local.y = 0;
        local.width = 800;
        local.height = 600;
        local.mode = DWIN_MODE_WINDOWED;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->width = (local.width > 0) ? local.width : 800;
    win->height = (local.height > 0) ? local.height : 600;
    win->mode = local.mode;
    g_cocoa.main_window = win;

    ns_window = cocoa_objc_create_window(win->width, win->height, "Domino");
    if (!ns_window) {
        free(win);
        g_cocoa.main_window = NULL;
        return NULL;
    }

    win->ns_window = ns_window;
    if (win->mode == DWIN_MODE_FULLSCREEN) {
        cocoa_objc_toggle_fullscreen(win->ns_window);
    }
    cocoa_window_get_size(win, &win->width, &win->height);
    return win;
}

static void cocoa_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win->ns_window) {
        cocoa_objc_destroy_window(win->ns_window);
    }
    if (g_cocoa.main_window == win) {
        g_cocoa.main_window = NULL;
    }
    free(win);
}

static void cocoa_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    dsys_window_mode prev;
    if (!win) {
        return;
    }
    prev = win->mode;
    win->mode = mode;
    if (!win->ns_window) {
        return;
    }
    if ((mode == DWIN_MODE_FULLSCREEN && prev != DWIN_MODE_FULLSCREEN) ||
        (mode != DWIN_MODE_FULLSCREEN && prev == DWIN_MODE_FULLSCREEN)) {
        cocoa_objc_toggle_fullscreen(win->ns_window);
    }
    cocoa_window_get_size(win, &win->width, &win->height);
}

static void cocoa_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    if (win->ns_window) {
        cocoa_objc_resize_window(win->ns_window, w, h);
        cocoa_objc_get_window_size(win->ns_window, &w, &h);
    }
    win->width = w;
    win->height = h;
}

static void cocoa_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        return;
    }
    if (win->ns_window) {
        cocoa_objc_get_window_size(win->ns_window, &win->width, &win->height);
    }
    if (w) {
        *w = win->width;
    }
    if (h) {
        *h = win->height;
    }
}

static void* cocoa_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return win->ns_window;
}

static bool cocoa_poll_event(dsys_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    cocoa_objc_pump_events();

    if (g_cocoa.head != g_cocoa.tail) {
        if (ev) {
            *ev = g_cocoa.queue[g_cocoa.head];
        }
        g_cocoa.head = (g_cocoa.head + 1) % COCOA_EVENT_QUEUE_SIZE;
        return true;
    }
    return false;
}

static bool cocoa_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    switch (kind) {
    case DSYS_PATH_APP_ROOT:    return cocoa_objc_get_path_exec(buf, buf_size);
    case DSYS_PATH_USER_DATA:   return cocoa_objc_get_path_data(buf, buf_size);
    case DSYS_PATH_USER_CONFIG: return cocoa_objc_get_path_config(buf, buf_size);
    case DSYS_PATH_USER_CACHE:  return cocoa_objc_get_path_cache(buf, buf_size);
    case DSYS_PATH_TEMP:        return cocoa_objc_get_path_temp(buf, buf_size);
    default:                    return false;
    }
}

static void* cocoa_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t cocoa_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t cocoa_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int cocoa_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long cocoa_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int cocoa_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* cocoa_dir_open(const char* path)
{
    DIR* dir;
    dsys_dir_iter* it;

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
    return it;
}

static bool cocoa_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;
    bool is_dir;

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

        is_dir = false;
#ifdef DT_DIR
        if (ent->d_type == DT_DIR) {
            is_dir = true;
#ifdef DT_UNKNOWN
        } else if (ent->d_type == DT_UNKNOWN) {
            struct stat st;
            if (fstatat(dirfd(it->dir), ent->d_name, &st, 0) == 0 && S_ISDIR(st.st_mode)) {
                is_dir = true;
            }
        } else {
            /* keep false */
#endif
        }
#else
        {
            struct stat st;
            if (fstatat(dirfd(it->dir), ent->d_name, &st, 0) == 0 && S_ISDIR(st.st_mode)) {
                is_dir = true;
            }
        }
#endif
        out->is_dir = is_dir;
        return true;
    }
}

static void cocoa_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* cocoa_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int cocoa_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void cocoa_process_destroy(dsys_process* p)
{
    (void)p;
}

void cocoa_push_event(const dsys_event* ev)
{
    int next;
    if (!ev) {
        return;
    }
    next = (g_cocoa.tail + 1) % COCOA_EVENT_QUEUE_SIZE;
    if (next == g_cocoa.head) {
        return;
    }
    g_cocoa.queue[g_cocoa.tail] = *ev;
    g_cocoa.tail = next;
}

const dsys_backend_vtable* dsys_cocoa_get_vtable(void)
{
    return &g_cocoa_vtable;
}

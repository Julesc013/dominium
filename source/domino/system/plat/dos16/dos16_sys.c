#include "dos16_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <conio.h>
#if defined(_WIN32)
#include <direct.h>
#else
#include <dir.h>
#endif
#include <sys/stat.h>

#define DOS16_EVENT_QUEUE_CAP 8

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

typedef struct dos16_event_queue_t {
    dsys_event buffer[DOS16_EVENT_QUEUE_CAP];
    int        head;
    int        tail;
    int        count;
} dos16_event_queue_t;

static const dsys_caps g_dos16_caps = { "dos16", 1u, true, false, false, false };
dos16_global_t         g_dos16;
static dsys_window*    g_dos16_window = NULL;
static dos16_event_queue_t g_dos16_events;

static void dos16_reset_state(void)
{
    memset(&g_dos16, 0, sizeof(g_dos16));
    memset(&g_dos16_events, 0, sizeof(g_dos16_events));
    g_dos16_window = NULL;
}

static void dos16_queue_event(const dsys_event* ev)
{
    if (!ev) {
        return;
    }
    if (g_dos16_events.count >= DOS16_EVENT_QUEUE_CAP) {
        return;
    }
    g_dos16_events.buffer[g_dos16_events.tail] = *ev;
    g_dos16_events.tail = (g_dos16_events.tail + 1) % DOS16_EVENT_QUEUE_CAP;
    g_dos16_events.count += 1;
}

static bool dos16_pop_event(dsys_event* ev)
{
    if (g_dos16_events.count == 0) {
        return false;
    }
    if (ev) {
        *ev = g_dos16_events.buffer[g_dos16_events.head];
    }
    g_dos16_events.head = (g_dos16_events.head + 1) % DOS16_EVENT_QUEUE_CAP;
    g_dos16_events.count -= 1;
    return true;
}

static bool dos16_copy_string(const char* src, char* buf, size_t buf_size)
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

static bool dos16_get_cwd(char* buf, size_t buf_size)
{
    char cwd[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

#if defined(_WIN32)
    if (_getcwd(cwd, sizeof(cwd)) != NULL) {
        return dos16_copy_string(cwd, buf, buf_size);
    }
#else
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        return dos16_copy_string(cwd, buf, buf_size);
    }
#endif

    buf[0] = '\0';
    return false;
}

static void dos16_join_path(char* dst, size_t cap, const char* base, const char* leaf)
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

static int dos16_read_key(void)
{
    int ch;

    if (!kbhit()) {
        return -1;
    }

    ch = getch();
    if (ch == 0 || ch == 0xE0) {
        int ext;
        ext = getch();
        ch = ((ch & 0xFF) << 8) | (ext & 0xFF);
    }
    return ch;
}

static void dos16_push_key_event(int keycode)
{
    dsys_event ev;

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_KEY_DOWN;
    ev.payload.key.key = keycode;
    ev.payload.key.repeat = false;
    dos16_queue_event(&ev);

    memset(&ev, 0, sizeof(ev));
    if (keycode == 27) {
        ev.type = DSYS_EVENT_QUIT;
    } else {
        ev.type = DSYS_EVENT_KEY_UP;
        ev.payload.key.key = keycode;
        ev.payload.key.repeat = false;
    }
    dos16_queue_event(&ev);
}

static void dos16_pump_input(void)
{
    int keycode;

    while (g_dos16_events.count < DOS16_EVENT_QUEUE_CAP) {
        keycode = dos16_read_key();
        if (keycode < 0) {
            break;
        }
        dos16_push_key_event(keycode);
    }
}

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
    if (g_dos16.initialized) {
        return DSYS_OK;
    }

    dos16_reset_state();
    g_dos16.fullscreen = 1;
    g_dos16.initialized = 1;
    return DSYS_OK;
}

static void dos16_shutdown(void)
{
    if (!g_dos16.initialized) {
        return;
    }
    if (g_dos16_window) {
        free(g_dos16_window);
        g_dos16_window = NULL;
    }
    dos16_reset_state();
}

static dsys_caps dos16_get_caps(void)
{
    return g_dos16_caps;
}

static uint64_t dos16_time_now_us(void)
{
    clock_t c;

    c = clock();
    if (c < 0) {
        return 0u;
    }
    if (CLOCKS_PER_SEC == 0) {
        return 0u;
    }
    return ((uint64_t)c * 1000000u) / (uint64_t)CLOCKS_PER_SEC;
}

static void dos16_sleep_ms(uint32_t ms)
{
    uint64_t start;
    uint64_t target;

    if (ms == 0u) {
        return;
    }

    start = dos16_time_now_us();
    target = start + ((uint64_t)ms * 1000u);
    while (dos16_time_now_us() < target) {
    }
}

static dsys_window* dos16_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local_desc;
    dsys_window*     win;

    if (g_dos16_window) {
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

    g_dos16.width = local_desc.width;
    g_dos16.height = local_desc.height;
    g_dos16.fullscreen = 1;
    g_dos16_window = win;
    return win;
}

static void dos16_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win == g_dos16_window) {
        g_dos16_window = NULL;
    }
    free(win);
}

static void dos16_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
    g_dos16.fullscreen = 1;
}

static void dos16_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
    g_dos16.width = w;
    g_dos16.height = h;
}

static void dos16_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

static void* dos16_window_get_native_handle(dsys_window* win)
{
    /* DOS has no OS window handle; return the logical window pointer for renderer use. */
    return (void*)win;
}

static bool dos16_poll_event(dsys_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    if (dos16_pop_event(ev)) {
        return true;
    }

    dos16_pump_input();
    return dos16_pop_event(ev);
}

static bool dos16_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    char base[260];
    char joined[260];

    if (!buf || buf_size == 0u) {
        return false;
    }

    base[0] = '\0';
    joined[0] = '\0';

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        if (dos16_get_cwd(buf, buf_size)) {
            return true;
        }
        break;

    case DSYS_PATH_USER_DATA:
        if (dos16_get_cwd(base, sizeof(base))) {
            dos16_join_path(joined, sizeof(joined), base, "DATA");
            return dos16_copy_string(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_USER_CONFIG:
        if (dos16_get_cwd(base, sizeof(base))) {
            dos16_join_path(joined, sizeof(joined), base, "CONFIG");
            return dos16_copy_string(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_USER_CACHE:
        if (dos16_get_cwd(base, sizeof(base))) {
            dos16_join_path(joined, sizeof(joined), base, "CACHE");
            return dos16_copy_string(joined, buf, buf_size);
        }
        break;

    case DSYS_PATH_TEMP:
        if (dos16_get_cwd(base, sizeof(base))) {
            dos16_join_path(joined, sizeof(joined), base, "TEMP");
            return dos16_copy_string(joined, buf, buf_size);
        }
        break;

    default:
        break;
    }

    buf[0] = '\0';
    return false;
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

static bool dos16_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;
    struct stat    st;
    char           full_path[260];
    size_t         base_len;
    size_t         name_len;

    if (!it || !out) {
        return false;
    }

    while (1) {
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
        base_len = strlen(it->base);
        name_len = strlen(out->name);
        if (base_len + name_len + 2u < sizeof(full_path)) {
            memcpy(full_path, it->base, base_len);
            if (base_len > 0u && full_path[base_len - 1u] != '\\' && full_path[base_len - 1u] != '/') {
                full_path[base_len] = '/';
                base_len += 1u;
            }
            memcpy(full_path + base_len, out->name, name_len);
            full_path[base_len + name_len] = '\0';
            if (stat(full_path, &st) == 0 && S_ISDIR(st.st_mode)) {
                out->is_dir = true;
            }
        }
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

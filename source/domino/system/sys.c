#include "domino/sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
#elif defined(_POSIX_VERSION)
#include <time.h>
#endif

struct dsys_window_t {
    int32_t          x;
    int32_t          y;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

struct dsys_process_t {
    int placeholder;
};

struct dsys_dir_iter_t {
    int placeholder;
};

static const dsys_caps g_dsys_caps = {
    "stub",
    0u,
    false,
    false,
    false,
    false
};

dsys_result dsys_init(void)
{
    return DSYS_OK;
}

void dsys_shutdown(void)
{
}

dsys_caps dsys_get_caps(void)
{
    return g_dsys_caps;
}

uint64_t dsys_time_now_us(void)
{
    uint64_t ticks;
    ticks = (uint64_t)clock();
    if (CLOCKS_PER_SEC != 0) {
        ticks = (ticks * 1000000u) / (uint64_t)CLOCKS_PER_SEC;
    }
    return ticks;
}

void dsys_sleep_ms(uint32_t ms)
{
#if defined(_WIN32)
    Sleep(ms);
#elif defined(_POSIX_VERSION)
    {
        struct timespec ts;
        ts.tv_sec = (time_t)(ms / 1000u);
        ts.tv_nsec = (long)((ms % 1000u) * 1000000u);
        nanosleep(&ts, (struct timespec*)0);
    }
#else
    {
        clock_t start;
        clock_t target;
        start = clock();
        target = start + (clock_t)((ms * CLOCKS_PER_SEC) / 1000u);
        while (clock() < target) {
            /* busy wait */
        }
    }
#endif
}

dsys_window* dsys_window_create(const dsys_window_desc* desc)
{
    dsys_window* win;
    dsys_window_desc local_desc;

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 0;
        local_desc.height = 0;
        local_desc.mode = DWIN_MODE_WINDOWED;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    win->x = local_desc.x;
    win->y = local_desc.y;
    win->width = local_desc.width;
    win->height = local_desc.height;
    win->mode = local_desc.mode;
    return win;
}

void dsys_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    free(win);
}

void dsys_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
}

void dsys_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win) {
        return;
    }
    win->width = w;
    win->height = h;
}

void dsys_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
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

void* dsys_window_get_native_handle(dsys_window* win)
{
    (void)win;
    return NULL;
}

bool dsys_poll_event(dsys_event* out)
{
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

bool dsys_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    (void)kind;
    if (!buf || buf_size == 0u) {
        return false;
    }
    if (buf_size < 2u) {
        buf[0] = '\0';
        return false;
    }
    buf[0] = '.';
    buf[1] = '\0';
    return true;
}

void* dsys_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

size_t dsys_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

size_t dsys_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

int dsys_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

long dsys_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

int dsys_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

dsys_dir_iter* dsys_dir_open(const char* path)
{
    (void)path;
    return NULL;
}

bool dsys_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    (void)it;
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

void dsys_dir_close(dsys_dir_iter* it)
{
    (void)it;
}

dsys_process* dsys_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

int dsys_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

void dsys_process_destroy(dsys_process* p)
{
    (void)p;
}

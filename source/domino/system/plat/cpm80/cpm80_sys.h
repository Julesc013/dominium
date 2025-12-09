#ifndef DOMINO_CPM80_SYS_H
#define DOMINO_CPM80_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

struct dsys_window_t {
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
    void*            fb_ptr; /* logical framebuffer pointer; renderer-owned */
};

typedef struct cpm80_global_t {
    int     initialized;
    int32_t width;
    int32_t height;
    int     fullscreen;
} cpm80_global_t;

struct dsys_dir_iter_t {
    char pattern[16];
    int  done;
};

struct dsys_process_t {
    int dummy;
};

extern cpm80_global_t g_cpm80;

const dsys_backend_vtable* dsys_cpm80_get_vtable(void);

#endif /* DOMINO_CPM80_SYS_H */

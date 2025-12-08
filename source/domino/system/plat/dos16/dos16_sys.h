#ifndef DOMINO_DOS16_SYS_H
#define DOMINO_DOS16_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>

struct dsys_window_t {
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
    void*            fb_ptr;
};

typedef struct dos16_global_t {
    int     initialized;
    int32_t width;
    int32_t height;
    int     fullscreen;
} dos16_global_t;

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    int dummy;
};

extern dos16_global_t g_dos16;

const dsys_backend_vtable* dsys_dos16_get_vtable(void);

#endif /* DOMINO_DOS16_SYS_H */

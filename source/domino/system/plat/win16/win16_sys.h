#ifndef DOMINO_WIN16_SYS_H
#define DOMINO_WIN16_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <windows.h>

struct dsys_window_t {
    HWND             hwnd;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

typedef struct win16_global_t {
    HINSTANCE hInstance;
    HWND      hwnd;
    int       class_registered;
    int       running;
} win16_global_t;

extern win16_global_t g_win16;

struct dsys_dir_iter_t {
    HANDLE          handle;
    WIN32_FIND_DATA data;
    int             first_pending;
    char            pattern[260];
};

struct dsys_process_t {
    int unused;
};

const dsys_backend_vtable* dsys_win16_get_vtable(void);

#endif /* DOMINO_WIN16_SYS_H */

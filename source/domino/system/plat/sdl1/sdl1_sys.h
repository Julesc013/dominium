#ifndef DOMINO_SDL1_SYS_H
#define DOMINO_SDL1_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <SDL.h>

#if defined(_WIN32)
#include <io.h>
#include <direct.h>
#else
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

struct dsys_window_t {
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
    SDL_Surface*     surface;
};

typedef struct sdl1_global_t {
    SDL_Surface* screen;
    int32_t      width;
    int32_t      height;
    int          fullscreen;
    int          initialized;
} sdl1_global_t;

struct dsys_dir_iter_t {
#if defined(_WIN32)
    intptr_t           handle;
    struct _finddata_t data;
    int                first_pending;
    char               pattern[260];
#else
    DIR*  dir;
    char  base[260];
#endif
};

struct dsys_process_t {
    int dummy;
};

const dsys_backend_vtable* dsys_sdl1_get_vtable(void);

#endif /* DOMINO_SDL1_SYS_H */

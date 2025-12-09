#ifndef DOMINO_SDL1_SYS_H
#define DOMINO_SDL1_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#if defined(_WIN32)
#include <direct.h>
#include <windows.h>
#else
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/wait.h>
#endif

typedef struct SDL_Surface SDL_Surface;

struct dsys_window_t {
    SDL_Surface*     surface;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

typedef struct sdl1_global_t {
    int          initialized;
    dsys_window* main_window;
    SDL_Surface* screen;
    int32_t      width;
    int32_t      height;
    int          fullscreen;
} sdl1_global_t;

extern sdl1_global_t g_sdl1;

struct dsys_dir_iter_t {
#if defined(_WIN32)
    HANDLE           handle;
    WIN32_FIND_DATAA data;
    int              first_pending;
#else
    DIR* dir;
#endif
};

struct dsys_process_t {
#if defined(_WIN32)
    HANDLE process;
    HANDLE thread;
#else
    pid_t pid;
#endif
};

const dsys_backend_vtable* dsys_sdl1_get_vtable(void);

#endif /* DOMINO_SDL1_SYS_H */

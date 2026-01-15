/*
FILE: source/domino/system/plat/sdl1/sdl1_sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/sdl1/sdl1_sys
RESPONSIBILITY: Defines internal contract for `sdl1_sys`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

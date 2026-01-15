/*
FILE: source/domino/system/dsys_internal.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_internal
RESPONSIBILITY: Defines internal contract for `dsys_internal`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DSYS_INTERNAL_H
#define DOMINO_DSYS_INTERNAL_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <stddef.h>
#include <stdint.h>

#if defined(DSYS_BACKEND_X11)
#include "plat/x11/x11_sys.h"
#elif defined(DSYS_BACKEND_WAYLAND)
#include "plat/wayland/wayland_sys.h"
#elif defined(DSYS_BACKEND_CARBON)
#include "plat/carbon/carbon_sys.h"
#elif defined(DSYS_BACKEND_COCOA)
#include "plat/cocoa/cocoa_sys.h"
#elif defined(DSYS_BACKEND_POSIX)
#include "plat/posix/posix_sys.h"
#elif defined(DSYS_BACKEND_DOS16)
#include "plat/dos16/dos16_sys.h"
#elif defined(DSYS_BACKEND_DOS32)
#include "plat/dos32/dos32_sys.h"
#elif defined(DSYS_BACKEND_WIN16)
#include "plat/win16/win16_sys.h"
#elif defined(DSYS_BACKEND_SDL1)
#include "plat/sdl1/sdl1_sys.h"
#elif defined(DSYS_BACKEND_CPM86)
#include "plat/cpm86/cpm86_sys.h"
#elif defined(DSYS_BACKEND_CPM80)
#include "plat/cpm80/cpm80_sys.h"
#else

#if defined(_WIN32)
#include <io.h>
#include <direct.h>
#elif defined(_POSIX_VERSION)
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

struct dsys_window_t {
    void*            native_handle;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
    uint32_t         window_id;
    struct dsys_window_t* next;
};

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
    void* handle;
};

#endif /* DSYS_BACKEND_X11 */

#endif /* DOMINO_DSYS_INTERNAL_H */

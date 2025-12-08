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

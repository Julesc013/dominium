#ifndef DOMINO_POSIX_SYS_H
#define DOMINO_POSIX_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

#include <dirent.h>
#include <sys/types.h>

struct dsys_window_t {
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
};

struct dsys_dir_iter_t {
    DIR*  dir;
    char  base[260];
};

struct dsys_process_t {
    pid_t pid;
};

const dsys_backend_vtable* dsys_posix_get_vtable(void);

#endif /* DOMINO_POSIX_SYS_H */

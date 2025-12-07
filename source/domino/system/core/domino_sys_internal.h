#ifndef DOMINO_SYS_INTERNAL_H
#define DOMINO_SYS_INTERNAL_H

#include <stddef.h>
#include "domino/sys.h"

struct domino_sys_file {
    void* handle;
};

struct domino_sys_dir_iter {
    void* handle;
    void* data;
    char  base_path[260];
    int   first_yielded;
};

struct domino_sys_process {
    void* handle;
    int   exit_code;
};

typedef struct domino_sys_ops {
    domino_sys_file* (*fopen_fn)(domino_sys_context*, const char*, const char*);
    size_t (*fread_fn)(domino_sys_context*, void*, size_t, size_t, domino_sys_file*);
    size_t (*fwrite_fn)(domino_sys_context*, const void*, size_t, size_t, domino_sys_file*);
    int    (*fclose_fn)(domino_sys_context*, domino_sys_file*);
    int    (*file_exists_fn)(domino_sys_context*, const char*);
    int    (*mkdirs_fn)(domino_sys_context*, const char*);

    domino_sys_dir_iter* (*dir_open_fn)(domino_sys_context*, const char*);
    int (*dir_next_fn)(domino_sys_context*, domino_sys_dir_iter*, char*, size_t, int*);
    void (*dir_close_fn)(domino_sys_context*, domino_sys_dir_iter*);

    double        (*time_seconds_fn)(domino_sys_context*);
    unsigned long (*time_millis_fn)(domino_sys_context*);
    void          (*sleep_millis_fn)(domino_sys_context*, unsigned long);

    int  (*process_spawn_fn)(domino_sys_context*, const domino_sys_process_desc*, domino_sys_process**);
    int  (*process_wait_fn)(domino_sys_context*, domino_sys_process*, int*);
    void (*process_destroy_fn)(domino_sys_context*, domino_sys_process*);

    void (*log_fn)(domino_sys_context*, domino_log_level, const char*, const char*);
} domino_sys_ops;

struct domino_sys_context {
    domino_sys_platform_info platform;
    domino_sys_paths         paths;
    domino_sys_ops           ops;
    void*                    backend_state;
    int                      backend_kind;
};

/* Backend entry points */
int  domino_sys_backend_init_win32(domino_sys_context* ctx);
void domino_sys_backend_shutdown_win32(domino_sys_context* ctx);

int  domino_sys_backend_init_posix(domino_sys_context* ctx);
void domino_sys_backend_shutdown_posix(domino_sys_context* ctx);

int  domino_sys_backend_init_stub(domino_sys_context* ctx);
void domino_sys_backend_shutdown_stub(domino_sys_context* ctx);

#endif /* DOMINO_SYS_INTERNAL_H */

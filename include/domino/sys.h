#ifndef DOMINO_SYS_H
#define DOMINO_SYS_H

/* Domino System Layer - stable C89 surface */

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dm_sys_context dm_sys_context;

enum dm_sys_log_level {
    DM_SYS_LOG_DEBUG = 0,
    DM_SYS_LOG_INFO  = 1,
    DM_SYS_LOG_WARN  = 2,
    DM_SYS_LOG_ERROR = 3
};

struct dm_sys_paths {
    const char* program_root;
    const char* data_root;
    const char* state_root;
};

struct dm_sys_vtable {
    /* LEGACY: all methods are stubbed out for now. */
    void (*shutdown)(dm_sys_context*);
    void (*log)(enum dm_sys_log_level lvl, const char* category, const char* msg);
};

struct dm_sys_context {
    struct dm_sys_paths paths;
    struct dm_sys_vtable vtable;
    void* user;
};

dm_sys_context* dm_sys_init(void);
void            dm_sys_shutdown(dm_sys_context* ctx);
void            dm_sys_set_paths(dm_sys_context* ctx, struct dm_sys_paths paths);
void            dm_sys_log(enum dm_sys_log_level lvl, const char* category, const char* msg);
uint64_t        dm_sys_monotonic_usec(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SYS_H */

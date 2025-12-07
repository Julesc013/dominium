#include "domino/sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

dm_sys_context* dm_sys_init(void)
{
    dm_sys_context* ctx = (dm_sys_context*)malloc(sizeof(dm_sys_context));
    if (!ctx) return NULL;
    ctx->paths.program_root = ".";
    ctx->paths.data_root    = "data";
    ctx->paths.state_root   = "state";
    ctx->vtable.shutdown    = NULL;
    ctx->vtable.log         = NULL;
    ctx->user               = NULL;
    return ctx;
}

void dm_sys_shutdown(dm_sys_context* ctx)
{
    if (ctx) {
        if (ctx->vtable.shutdown) {
            ctx->vtable.shutdown(ctx);
        }
        free(ctx);
    }
}

void dm_sys_set_paths(dm_sys_context* ctx, struct dm_sys_paths paths)
{
    if (ctx) {
        ctx->paths = paths;
    }
}

void dm_sys_log(enum dm_sys_log_level lvl, const char* category, const char* msg)
{
    const char* lvl_str = "INFO";
    switch (lvl) {
    case DM_SYS_LOG_DEBUG: lvl_str = "DEBUG"; break;
    case DM_SYS_LOG_INFO:  lvl_str = "INFO"; break;
    case DM_SYS_LOG_WARN:  lvl_str = "WARN"; break;
    case DM_SYS_LOG_ERROR: lvl_str = "ERROR"; break;
    default: break;
    }
    if (!category) category = "core";
    if (!msg) msg = "";
    printf("[domino:%s] %s: %s\n", lvl_str, category, msg);
}

uint64_t dm_sys_monotonic_usec(void)
{
    const clock_t now = clock();
    if (now == (clock_t)-1) return 0;
    return (uint64_t)now * (uint64_t)(1000000 / CLOCKS_PER_SEC);
}

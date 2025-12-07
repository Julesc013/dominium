#include "domino_sys_internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static domino_sys_file* null_fopen(domino_sys_context* ctx,
                                   const char* path,
                                   const char* mode)
{
    FILE* fp;
    domino_sys_file* f;
    (void)ctx;
    fp = fopen(path, mode);
    if (!fp) return NULL;
    f = (domino_sys_file*)malloc(sizeof(domino_sys_file));
    if (!f) {
        fclose(fp);
        return NULL;
    }
    f->handle = fp;
    return f;
}

static size_t null_fread(domino_sys_context* ctx,
                         void* buf, size_t size, size_t nmemb,
                         domino_sys_file* f)
{
    (void)ctx;
    if (!f || !f->handle) return 0;
    return fread(buf, size, nmemb, (FILE*)f->handle);
}

static size_t null_fwrite(domino_sys_context* ctx,
                          const void* buf, size_t size, size_t nmemb,
                          domino_sys_file* f)
{
    (void)ctx;
    if (!f || !f->handle) return 0;
    return fwrite(buf, size, nmemb, (FILE*)f->handle);
}

static int null_fclose(domino_sys_context* ctx, domino_sys_file* f)
{
    int r;
    (void)ctx;
    if (!f) return -1;
    r = 0;
    if (f->handle) {
        r = fclose((FILE*)f->handle);
    }
    free(f);
    return r;
}

static int null_exists(domino_sys_context* ctx, const char* path)
{
    FILE* fp;
    (void)ctx;
    fp = fopen(path, "rb");
    if (!fp) return 0;
    fclose(fp);
    return 1;
}

static int null_mkdirs(domino_sys_context* ctx, const char* path)
{
    (void)ctx;
    (void)path;
    /* Not implemented in stub. */
    return -1;
}

static domino_sys_dir_iter* null_dir_open(domino_sys_context* ctx, const char* path)
{
    (void)ctx;
    (void)path;
    return NULL;
}

static int null_dir_next(domino_sys_context* ctx,
                         domino_sys_dir_iter* it,
                         char* name_out, size_t cap,
                         int* is_dir_out)
{
    (void)ctx; (void)it; (void)name_out; (void)cap; (void)is_dir_out;
    return 0;
}

static void null_dir_close(domino_sys_context* ctx, domino_sys_dir_iter* it)
{
    (void)ctx;
    (void)it;
}

static double null_time_seconds(domino_sys_context* ctx)
{
    (void)ctx;
    return (double)clock() / (double)CLOCKS_PER_SEC;
}

static unsigned long null_time_millis(domino_sys_context* ctx)
{
    return (unsigned long)(null_time_seconds(ctx) * 1000.0);
}

static void null_sleep_millis(domino_sys_context* ctx, unsigned long ms)
{
    clock_t start;
    clock_t target;
    (void)ctx;
    start = clock();
    target = start + (clock_t)((ms * CLOCKS_PER_SEC) / 1000);
    while (clock() < target) {
        /* spin */
    }
}

static int null_process_spawn(domino_sys_context* ctx,
                              const domino_sys_process_desc* desc,
                              domino_sys_process** out_proc)
{
    (void)ctx; (void)desc; (void)out_proc;
    return -1;
}

static int null_process_wait(domino_sys_context* ctx,
                             domino_sys_process* proc,
                             int* exit_code_out)
{
    (void)ctx; (void)proc; (void)exit_code_out;
    return -1;
}

static void null_process_destroy(domino_sys_context* ctx,
                                 domino_sys_process* proc)
{
    (void)ctx;
    (void)proc;
}

int domino_sys_backend_init_stub(domino_sys_context* ctx)
{
    if (!ctx) return -1;
    memset(&ctx->ops, 0, sizeof(ctx->ops));
    ctx->ops.fopen_fn = null_fopen;
    ctx->ops.fread_fn = null_fread;
    ctx->ops.fwrite_fn = null_fwrite;
    ctx->ops.fclose_fn = null_fclose;
    ctx->ops.file_exists_fn = null_exists;
    ctx->ops.mkdirs_fn = null_mkdirs;
    ctx->ops.dir_open_fn = null_dir_open;
    ctx->ops.dir_next_fn = null_dir_next;
    ctx->ops.dir_close_fn = null_dir_close;
    ctx->ops.time_seconds_fn = null_time_seconds;
    ctx->ops.time_millis_fn = null_time_millis;
    ctx->ops.sleep_millis_fn = null_sleep_millis;
    ctx->ops.process_spawn_fn = null_process_spawn;
    ctx->ops.process_wait_fn = null_process_wait;
    ctx->ops.process_destroy_fn = null_process_destroy;
    ctx->ops.log_fn = 0; /* use default */
    ctx->backend_state = NULL;
    return 0;
}

void domino_sys_backend_shutdown_stub(domino_sys_context* ctx)
{
    (void)ctx;
}

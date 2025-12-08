#include "domino/sys.h"

#include <stdlib.h>
#include <string.h>

struct dsys_context {
    dsys_desc          desc;
    dsys_platform_info platform;
    dsys_paths         paths;
    dsys_log_fn        log_fn;
    void*              log_user;
};

struct dsys_file {
    int placeholder;
};

struct dsys_dir_iter {
    int placeholder;
};

struct dsys_process {
    int placeholder;
};

int dsys_create(const dsys_desc* desc, dsys_context** out_sys)
{
    dsys_context* ctx;
    dsys_desc local_desc;

    if (!out_sys) {
        return -1;
    }
    *out_sys = NULL;

    ctx = (dsys_context*)malloc(sizeof(dsys_context));
    if (!ctx) {
        return -1;
    }
    memset(ctx, 0, sizeof(*ctx));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
        local_desc.profile = DSYS_PROFILE_STANDARD;
    }
    ctx->desc = local_desc;
    ctx->log_fn = local_desc.log_fn;
    ctx->log_user = local_desc.log_user;

    ctx->platform.struct_size = sizeof(dsys_platform_info);
    ctx->platform.struct_version = 1u;
    ctx->platform.pointer_size = (uint32_t)sizeof(void*);
    ctx->platform.page_size = 4096u;
    ctx->platform.flags = 0u;

    ctx->paths.struct_size = sizeof(dsys_paths);
    ctx->paths.struct_version = 1u;
    ctx->paths.install_root[0] = '\0';
    ctx->paths.program_root[0] = '\0';
    ctx->paths.data_root[0] = '\0';
    ctx->paths.user_root[0] = '\0';
    ctx->paths.state_root[0] = '\0';
    ctx->paths.temp_root[0] = '\0';

    *out_sys = ctx;
    return 0;
}

void dsys_destroy(dsys_context* sys)
{
    if (!sys) {
        return;
    }
    free(sys);
}

int dsys_get_platform_info(dsys_context* sys, dsys_platform_info* out_info)
{
    if (!sys || !out_info) {
        return -1;
    }
    *out_info = sys->platform;
    return 0;
}

int dsys_get_paths(dsys_context* sys, dsys_paths* out_paths)
{
    if (!sys || !out_paths) {
        return -1;
    }
    *out_paths = sys->paths;
    return 0;
}

int dsys_set_log_hook(dsys_context* sys, dsys_log_fn log_fn, void* user_data)
{
    if (!sys) {
        return -1;
    }
    sys->log_fn = log_fn;
    sys->log_user = user_data;
    return 0;
}

uint64_t dsys_time_ticks(dsys_context* sys)
{
    (void)sys;
    return 0u;
}

double dsys_time_seconds(dsys_context* sys)
{
    (void)sys;
    return 0.0;
}

void dsys_sleep_millis(dsys_context* sys, uint32_t millis)
{
    (void)sys;
    (void)millis;
}

int dsys_file_exists(dsys_context* sys, const char* path)
{
    (void)sys;
    (void)path;
    return 0;
}

int dsys_mkdirs(dsys_context* sys, const char* path)
{
    (void)sys;
    (void)path;
    return 0;
}

dsys_file* dsys_file_open(dsys_context* sys, const char* path, const char* mode)
{
    (void)sys;
    (void)path;
    (void)mode;
    return NULL;
}

size_t dsys_file_read(dsys_file* file, void* buffer, size_t bytes)
{
    (void)file;
    (void)buffer;
    (void)bytes;
    return 0u;
}

size_t dsys_file_write(dsys_file* file, const void* buffer, size_t bytes)
{
    (void)file;
    (void)buffer;
    (void)bytes;
    return 0u;
}

void dsys_file_close(dsys_file* file)
{
    if (!file) {
        return;
    }
    free(file);
}

dsys_dir_iter* dsys_dir_open(dsys_context* sys, const char* path)
{
    (void)sys;
    (void)path;
    return NULL;
}

int dsys_dir_next(dsys_dir_iter* it, char* name_out, size_t cap, int* is_dir_out)
{
    (void)it;
    (void)name_out;
    (void)cap;
    (void)is_dir_out;
    return 0;
}

void dsys_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    free(it);
}

int dsys_process_spawn(dsys_context* sys, const dsys_process_desc* desc, dsys_process** out_proc)
{
    (void)sys;
    (void)desc;
    if (out_proc) {
        *out_proc = NULL;
    }
    return -1;
}

int dsys_process_wait(dsys_process* proc, int* exit_code_out)
{
    (void)proc;
    if (exit_code_out) {
        *exit_code_out = -1;
    }
    return -1;
}

void dsys_process_destroy(dsys_process* proc)
{
    if (!proc) {
        return;
    }
    free(proc);
}

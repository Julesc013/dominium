/*
FILE: source/domino/system/plat/unix/posix/sys_posix.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/unix/posix/sys_posix
RESPONSIBILITY: Implements `sys_posix`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino_sys_internal.h"

#if defined(__unix__) || defined(__unix) || defined(__APPLE__)

#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <spawn.h>
#include <sys/wait.h>

extern char **environ;

static void posix_join(char* dst, size_t cap, const char* a, const char* b)
{
    size_t i = 0;
    size_t j = 0;
    if (!dst || cap == 0) return;
    if (!a) a = "";
    if (!b) b = "";
    while (a[i] != '\0' && i + 1 < cap) {
        dst[i] = a[i];
        ++i;
    }
    if (i > 0 && i + 1 < cap) {
        char c = dst[i - 1];
        if (c != '/') {
            dst[i++] = '/';
        }
    }
    while (b[j] != '\0' && i + 1 < cap) {
        dst[i++] = b[j++];
    }
    dst[i] = '\0';
}

static domino_sys_file* posix_fopen(domino_sys_context* ctx,
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

static size_t posix_fread(domino_sys_context* ctx,
                          void* buf, size_t size, size_t nmemb,
                          domino_sys_file* f)
{
    (void)ctx;
    if (!f || !f->handle) return 0;
    return fread(buf, size, nmemb, (FILE*)f->handle);
}

static size_t posix_fwrite(domino_sys_context* ctx,
                           const void* buf, size_t size, size_t nmemb,
                           domino_sys_file* f)
{
    (void)ctx;
    if (!f || !f->handle) return 0;
    return fwrite(buf, size, nmemb, (FILE*)f->handle);
}

static int posix_fclose(domino_sys_context* ctx, domino_sys_file* f)
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

static int posix_exists(domino_sys_context* ctx, const char* path)
{
    struct stat st;
    (void)ctx;
    return (stat(path, &st) == 0);
}

static int posix_mkdirs(domino_sys_context* ctx, const char* path)
{
    char tmp[260];
    size_t i;
    (void)ctx;
    if (!path || !path[0]) return -1;
    strncpy(tmp, path, sizeof(tmp) - 1);
    tmp[sizeof(tmp) - 1] = '\0';
    for (i = 1; tmp[i] != '\0'; ++i) {
        if (tmp[i] == '/') {
            char hold = tmp[i];
            tmp[i] = '\0';
            mkdir(tmp, 0755);
            tmp[i] = hold;
        }
    }
    mkdir(tmp, 0755);
    return 0;
}

static domino_sys_dir_iter* posix_dir_open(domino_sys_context* ctx, const char* path)
{
    DIR* d;
    domino_sys_dir_iter* it;
    (void)ctx;
    d = opendir(path);
    if (!d) return NULL;
    it = (domino_sys_dir_iter*)malloc(sizeof(domino_sys_dir_iter));
    if (!it) {
        closedir(d);
        return NULL;
    }
    memset(it, 0, sizeof(*it));
    it->handle = d;
    strncpy(it->base_path, path, sizeof(it->base_path) - 1);
    it->base_path[sizeof(it->base_path) - 1] = '\0';
    return it;
}

static int posix_dir_next(domino_sys_context* ctx,
                          domino_sys_dir_iter* it,
                          char* name_out, size_t cap,
                          int* is_dir_out)
{
    struct dirent* ent;
    (void)ctx;
    if (!it || !it->handle || !name_out || cap == 0) return 0;
    for (;;) {
        ent = readdir((DIR*)it->handle);
        if (!ent) {
            return 0;
        }
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) {
            continue;
        }
        strncpy(name_out, ent->d_name, cap - 1);
        name_out[cap - 1] = '\0';
        if (is_dir_out) {
#ifdef DT_DIR
            if (ent->d_type == DT_DIR) {
                *is_dir_out = 1;
            } else if (ent->d_type == DT_UNKNOWN) {
                struct stat st;
                char full[260];
                posix_join(full, sizeof(full), it->base_path, ent->d_name);
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    *is_dir_out = 1;
                } else {
                    *is_dir_out = 0;
                }
            } else {
                *is_dir_out = 0;
            }
#else
            struct stat st;
            char full[260];
            posix_join(full, sizeof(full), it->base_path, ent->d_name);
            if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                *is_dir_out = 1;
            } else {
                *is_dir_out = 0;
            }
#endif
        }
        return 1;
    }
}

static void posix_dir_close(domino_sys_context* ctx, domino_sys_dir_iter* it)
{
    (void)ctx;
    if (!it) return;
    if (it->handle) {
        closedir((DIR*)it->handle);
    }
    free(it);
}

static double posix_time_seconds(domino_sys_context* ctx)
{
    struct timespec ts;
    (void)ctx;
#if defined(CLOCK_MONOTONIC)
    if (clock_gettime(CLOCK_MONOTONIC, &ts) == 0) {
        return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
    }
#endif
    {
        struct timeval tv;
        gettimeofday(&tv, NULL);
        return (double)tv.tv_sec + (double)tv.tv_usec / 1e6;
    }
}

static unsigned long posix_time_millis(domino_sys_context* ctx)
{
    return (unsigned long)(posix_time_seconds(ctx) * 1000.0);
}

static void posix_sleep_millis(domino_sys_context* ctx, unsigned long ms)
{
    (void)ctx;
    usleep(ms * 1000);
}

static int posix_process_spawn(domino_sys_context* ctx,
                               const domino_sys_process_desc* desc,
                               domino_sys_process** out_proc)
{
    pid_t pid;
    (void)ctx;
    if (!desc || !out_proc || !desc->path) return -1;
    if (posix_spawn(&pid, desc->path, NULL, NULL, (char* const*)desc->argv, environ) != 0) {
        return -1;
    }
    *out_proc = (domino_sys_process*)malloc(sizeof(domino_sys_process));
    if (!*out_proc) {
        return -1;
    }
    (*out_proc)->handle = (void*)(long)pid;
    (*out_proc)->exit_code = -1;
    return 0;
}

static int posix_process_wait(domino_sys_context* ctx,
                              domino_sys_process* proc,
                              int* exit_code_out)
{
    int status;
    pid_t pid;
    (void)ctx;
    if (!proc) return -1;
    pid = (pid_t)(long)proc->handle;
    if (waitpid(pid, &status, 0) < 0) {
        return -1;
    }
    if (WIFEXITED(status)) {
        proc->exit_code = WEXITSTATUS(status);
    } else {
        proc->exit_code = -1;
    }
    if (exit_code_out) {
        *exit_code_out = proc->exit_code;
    }
    return 0;
}

static void posix_process_destroy(domino_sys_context* ctx,
                                  domino_sys_process* proc)
{
    (void)ctx;
    if (!proc) return;
    free(proc);
}

int domino_sys_backend_init_posix(domino_sys_context* ctx)
{
    if (!ctx) return -1;
    memset(&ctx->ops, 0, sizeof(ctx->ops));
    ctx->ops.fopen_fn = posix_fopen;
    ctx->ops.fread_fn = posix_fread;
    ctx->ops.fwrite_fn = posix_fwrite;
    ctx->ops.fclose_fn = posix_fclose;
    ctx->ops.file_exists_fn = posix_exists;
    ctx->ops.mkdirs_fn = posix_mkdirs;
    ctx->ops.dir_open_fn = posix_dir_open;
    ctx->ops.dir_next_fn = posix_dir_next;
    ctx->ops.dir_close_fn = posix_dir_close;
    ctx->ops.time_seconds_fn = posix_time_seconds;
    ctx->ops.time_millis_fn = posix_time_millis;
    ctx->ops.sleep_millis_fn = posix_sleep_millis;
    ctx->ops.process_spawn_fn = posix_process_spawn;
    ctx->ops.process_wait_fn = posix_process_wait;
    ctx->ops.process_destroy_fn = posix_process_destroy;
    ctx->backend_state = NULL;
    ctx->platform.has_fork = 1;
    ctx->platform.has_unicode = 1;
    return 0;
}

void domino_sys_backend_shutdown_posix(domino_sys_context* ctx)
{
    (void)ctx;
}

#else /* non-posix build */

int domino_sys_backend_init_posix(domino_sys_context* ctx)
{
    (void)ctx;
    return -1;
}

void domino_sys_backend_shutdown_posix(domino_sys_context* ctx)
{
    (void)ctx;
}

#endif

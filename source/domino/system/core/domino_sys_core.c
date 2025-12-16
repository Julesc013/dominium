/*
FILE: source/domino/system/core/domino_sys_core.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/domino_sys_core
RESPONSIBILITY: Implements `domino_sys_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/sys.h"
#include "domino_sys_internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include <direct.h>
#define dom_getcwd _getcwd
#else
#include <unistd.h>
#define dom_getcwd getcwd
#endif

static void domino_sys_join_path(char* dst, size_t cap, const char* a, const char* b)
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
        if (c != '/' && c != '\\') {
            dst[i++] = '/';
        }
    }
    while (b[j] != '\0' && i + 1 < cap) {
        dst[i++] = b[j++];
    }
    dst[i] = '\0';
}

/*------------------------------------------------------------
 * Helpers
 *------------------------------------------------------------*/
static void domino_sys_default_log(domino_sys_context* ctx,
                                   domino_log_level level,
                                   const char* subsystem,
                                   const char* message)
{
    const char* lvl = "INFO";
    (void)ctx;
    switch (level) {
    case DOMINO_LOG_DEBUG: lvl = "DEBUG"; break;
    case DOMINO_LOG_INFO:  lvl = "INFO";  break;
    case DOMINO_LOG_WARN:  lvl = "WARN";  break;
    case DOMINO_LOG_ERROR: lvl = "ERROR"; break;
    default: break;
    }
    if (!subsystem) subsystem = "domino.sys";
    if (!message) message = "";
    printf("[%s] %s: %s\n", lvl, subsystem, message);
}

static void domino_sys_detect_platform(domino_sys_platform_info* out_info)
{
    if (!out_info) return;
    memset(out_info, 0, sizeof(*out_info));
#if defined(_WIN32)
    out_info->os = DOMINO_OS_WINDOWS;
#elif defined(__APPLE__)
    out_info->os = DOMINO_OS_MAC;
#elif defined(__unix__) || defined(__unix) || defined(__linux__)
    out_info->os = DOMINO_OS_UNIX;
#elif defined(__ANDROID__)
    out_info->os = DOMINO_OS_ANDROID;
#elif defined(__MSDOS__) || defined(__DOS__)
    out_info->os = DOMINO_OS_DOS;
#else
    out_info->os = DOMINO_OS_UNKNOWN;
#endif

#if defined(_M_IX86) || defined(__i386__)
    out_info->cpu = DOMINO_CPU_X86_32;
#elif defined(_M_X64) || defined(__x86_64__)
    out_info->cpu = DOMINO_CPU_X86_64;
#elif defined(__arm__) || defined(_M_ARM)
    out_info->cpu = DOMINO_CPU_ARM_32;
#elif defined(__aarch64__) || defined(_M_ARM64)
    out_info->cpu = DOMINO_CPU_ARM_64;
#elif defined(__m68k__)
    out_info->cpu = DOMINO_CPU_M68K;
#elif defined(__powerpc__) || defined(__ppc__)
    out_info->cpu = DOMINO_CPU_PPC;
#else
    out_info->cpu = DOMINO_CPU_OTHER;
#endif

    /* Simple defaults; refined by backend if needed. */
    out_info->profile = DOMINO_SYS_PROFILE_FULL;
    out_info->has_threads = 1;
    out_info->has_fork = 0;
    out_info->has_unicode = 1;
    out_info->is_legacy = 0;
}

static void domino_sys_set_default_paths(domino_sys_context* ctx)
{
    char cwd[260];
    if (!ctx) return;

    if (!ctx->paths.install_root[0]) {
        if (dom_getcwd(cwd, sizeof(cwd))) {
            strncpy(ctx->paths.install_root, cwd, sizeof(ctx->paths.install_root) - 1);
            ctx->paths.install_root[sizeof(ctx->paths.install_root) - 1] = '\0';
        } else {
            strncpy(ctx->paths.install_root, ".", sizeof(ctx->paths.install_root) - 1);
            ctx->paths.install_root[sizeof(ctx->paths.install_root) - 1] = '\0';
        }
    }

    if (!ctx->paths.program_root[0]) {
        domino_sys_join_path(ctx->paths.program_root, sizeof(ctx->paths.program_root), ctx->paths.install_root, "program");
    }
    if (!ctx->paths.data_root[0]) {
        domino_sys_join_path(ctx->paths.data_root, sizeof(ctx->paths.data_root), ctx->paths.install_root, "data");
    }
    if (!ctx->paths.user_root[0]) {
        domino_sys_join_path(ctx->paths.user_root, sizeof(ctx->paths.user_root), ctx->paths.install_root, "user");
    }
    if (!ctx->paths.state_root[0]) {
        domino_sys_join_path(ctx->paths.state_root, sizeof(ctx->paths.state_root), ctx->paths.install_root, "state");
    }
    if (!ctx->paths.temp_root[0]) {
        domino_sys_join_path(ctx->paths.temp_root, sizeof(ctx->paths.temp_root), ctx->paths.install_root, "temp");
    }
}

static int domino_sys_choose_backend(domino_sys_context* ctx)
{
    if (!ctx) return -1;
#if defined(_WIN32)
    if (domino_sys_backend_init_win32(ctx) == 0) {
        ctx->backend_kind = 1;
        return 0;
    }
#endif
#if defined(__unix__) || defined(__APPLE__)
    if (domino_sys_backend_init_posix(ctx) == 0) {
        ctx->backend_kind = 2;
        return 0;
    }
#endif
    if (domino_sys_backend_init_stub(ctx) == 0) {
        ctx->backend_kind = 0;
        return 0;
    }
    return -1;
}

/*------------------------------------------------------------
 * Public API
 *------------------------------------------------------------*/
int domino_sys_init(const domino_sys_desc* desc, domino_sys_context** out_ctx)
{
    domino_sys_context* ctx;
    domino_sys_desc local_desc;

    if (!out_ctx) {
        return -1;
    }
    *out_ctx = NULL;

    ctx = (domino_sys_context*)malloc(sizeof(domino_sys_context));
    if (!ctx) {
        return -1;
    }
    memset(ctx, 0, sizeof(*ctx));

    domino_sys_detect_platform(&ctx->platform);

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
        local_desc.profile_hint = DOMINO_SYS_PROFILE_AUTO;
    }

    if (local_desc.profile_hint != DOMINO_SYS_PROFILE_AUTO) {
        ctx->platform.profile = local_desc.profile_hint;
    }

    if (domino_sys_choose_backend(ctx) != 0) {
        free(ctx);
        return -1;
    }

    if (!ctx->ops.log_fn) {
        ctx->ops.log_fn = domino_sys_default_log;
    }

    domino_sys_set_default_paths(ctx);
    *out_ctx = ctx;
    return 0;
}

void domino_sys_shutdown(domino_sys_context* ctx)
{
    if (!ctx) return;

    switch (ctx->backend_kind) {
    case 1: domino_sys_backend_shutdown_win32(ctx); break;
    case 2: domino_sys_backend_shutdown_posix(ctx); break;
    case 0:
    default: domino_sys_backend_shutdown_stub(ctx); break;
    }
    free(ctx);
}

void domino_sys_get_platform_info(domino_sys_context* ctx,
                                  domino_sys_platform_info* out_info)
{
    if (!ctx || !out_info) return;
    *out_info = ctx->platform;
}

int domino_sys_get_paths(domino_sys_context* ctx, domino_sys_paths* out_paths)
{
    if (!ctx || !out_paths) return -1;
    *out_paths = ctx->paths;
    return 0;
}

domino_sys_file* domino_sys_fopen(domino_sys_context* ctx,
                                  const char* path,
                                  const char* mode)
{
    if (!ctx || !ctx->ops.fopen_fn) return NULL;
    return ctx->ops.fopen_fn(ctx, path, mode);
}

size_t domino_sys_fread(domino_sys_context* ctx,
                        void* buf, size_t size, size_t nmemb,
                        domino_sys_file* f)
{
    if (!ctx || !ctx->ops.fread_fn) return 0;
    return ctx->ops.fread_fn(ctx, buf, size, nmemb, f);
}

size_t domino_sys_fwrite(domino_sys_context* ctx,
                         const void* buf, size_t size, size_t nmemb,
                         domino_sys_file* f)
{
    if (!ctx || !ctx->ops.fwrite_fn) return 0;
    return ctx->ops.fwrite_fn(ctx, buf, size, nmemb, f);
}

int domino_sys_fclose(domino_sys_context* ctx,
                      domino_sys_file* f)
{
    if (!ctx || !ctx->ops.fclose_fn) return -1;
    return ctx->ops.fclose_fn(ctx, f);
}

int domino_sys_file_exists(domino_sys_context* ctx,
                           const char* path)
{
    if (!ctx || !ctx->ops.file_exists_fn) return 0;
    return ctx->ops.file_exists_fn(ctx, path);
}

int domino_sys_mkdirs(domino_sys_context* ctx,
                      const char* path)
{
    if (!ctx || !ctx->ops.mkdirs_fn) return -1;
    return ctx->ops.mkdirs_fn(ctx, path);
}

domino_sys_dir_iter* domino_sys_dir_open(domino_sys_context* ctx,
                                         const char* path)
{
    if (!ctx || !ctx->ops.dir_open_fn) return NULL;
    return ctx->ops.dir_open_fn(ctx, path);
}

int domino_sys_dir_next(domino_sys_context* ctx,
                        domino_sys_dir_iter* it,
                        char* name_out, size_t cap,
                        int* is_dir_out)
{
    if (!ctx || !ctx->ops.dir_next_fn) return 0;
    return ctx->ops.dir_next_fn(ctx, it, name_out, cap, is_dir_out);
}

void domino_sys_dir_close(domino_sys_context* ctx,
                          domino_sys_dir_iter* it)
{
    if (!ctx || !ctx->ops.dir_close_fn) return;
    ctx->ops.dir_close_fn(ctx, it);
}

double domino_sys_time_seconds(domino_sys_context* ctx)
{
    if (!ctx || !ctx->ops.time_seconds_fn) return 0.0;
    return ctx->ops.time_seconds_fn(ctx);
}

unsigned long domino_sys_time_millis(domino_sys_context* ctx)
{
    if (!ctx || !ctx->ops.time_millis_fn) return 0;
    return ctx->ops.time_millis_fn(ctx);
}

void domino_sys_sleep_millis(domino_sys_context* ctx,
                             unsigned long ms)
{
    if (!ctx || !ctx->ops.sleep_millis_fn) return;
    ctx->ops.sleep_millis_fn(ctx, ms);
}

int domino_sys_process_spawn(domino_sys_context* ctx,
                             const domino_sys_process_desc* desc,
                             domino_sys_process** out_proc)
{
    if (!ctx || !ctx->ops.process_spawn_fn) return -1;
    return ctx->ops.process_spawn_fn(ctx, desc, out_proc);
}

int domino_sys_process_wait(domino_sys_context* ctx,
                            domino_sys_process* proc,
                            int* exit_code_out)
{
    if (!ctx || !ctx->ops.process_wait_fn) return -1;
    return ctx->ops.process_wait_fn(ctx, proc, exit_code_out);
}

void domino_sys_process_destroy(domino_sys_context* ctx,
                                domino_sys_process* proc)
{
    if (!ctx || !ctx->ops.process_destroy_fn) return;
    ctx->ops.process_destroy_fn(ctx, proc);
}

void domino_sys_log(domino_sys_context* ctx,
                    domino_log_level level,
                    const char* subsystem,
                    const char* message)
{
    if (!ctx || !ctx->ops.log_fn) {
        domino_sys_default_log(ctx, level, subsystem, message);
        return;
    }
    ctx->ops.log_fn(ctx, level, subsystem, message);
}

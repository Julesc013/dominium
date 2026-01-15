/*
FILE: source/domino/system/plat/windows/win32/sys_win32.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/windows/win32/sys_win32
RESPONSIBILITY: Implements `sys_win32`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino_sys_internal.h"

#include <windows.h>
#include <direct.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void win32_set_install_root(domino_sys_context* ctx)
{
    char path[MAX_PATH];
    DWORD len;
    if (!ctx) return;
    len = GetModuleFileNameA(NULL, path, (DWORD)sizeof(path));
    if (len == 0 || len >= sizeof(path)) {
        return;
    }
    while (len > 0) {
        char c = path[len - 1];
        if (c == '\\' || c == '/' ) {
            path[len - 1] = '\0';
            break;
        }
        --len;
    }
    if (path[0] != '\0') {
        strncpy(ctx->paths.install_root, path, sizeof(ctx->paths.install_root) - 1);
        ctx->paths.install_root[sizeof(ctx->paths.install_root) - 1] = '\0';
    }
}

static domino_sys_file* win32_fopen(domino_sys_context* ctx,
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

static size_t win32_fread(domino_sys_context* ctx,
                          void* buf, size_t size, size_t nmemb,
                          domino_sys_file* f)
{
    (void)ctx;
    if (!f || !f->handle) return 0;
    return fread(buf, size, nmemb, (FILE*)f->handle);
}

static size_t win32_fwrite(domino_sys_context* ctx,
                           const void* buf, size_t size, size_t nmemb,
                           domino_sys_file* f)
{
    (void)ctx;
    if (!f || !f->handle) return 0;
    return fwrite(buf, size, nmemb, (FILE*)f->handle);
}

static int win32_fclose(domino_sys_context* ctx, domino_sys_file* f)
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

static int win32_exists(domino_sys_context* ctx, const char* path)
{
    DWORD attr;
    (void)ctx;
    attr = GetFileAttributesA(path);
    return (attr != INVALID_FILE_ATTRIBUTES);
}

static int win32_mkdirs(domino_sys_context* ctx, const char* path)
{
    char tmp[260];
    size_t i;
    (void)ctx;
    if (!path || !path[0]) return -1;
    strncpy(tmp, path, sizeof(tmp) - 1);
    tmp[sizeof(tmp) - 1] = '\0';
    for (i = 1; tmp[i] != '\0'; ++i) {
        if (tmp[i] == '\\' || tmp[i] == '/') {
            char hold = tmp[i];
            tmp[i] = '\0';
            _mkdir(tmp);
            tmp[i] = hold;
        }
    }
    if (_mkdir(tmp) != 0) {
        /* _mkdir returns -1 on failure; ignore if already exists */
    }
    return 0;
}

static domino_sys_dir_iter* win32_dir_open(domino_sys_context* ctx, const char* path)
{
    WIN32_FIND_DATAA* data;
    HANDLE h;
    domino_sys_dir_iter* it;
    char pattern[260];
    size_t len;
    (void)ctx;
    if (!path) return NULL;
    len = strlen(path);
    if (len + 3 >= sizeof(pattern)) {
        return NULL;
    }
    strcpy(pattern, path);
    if (len > 0 && path[len - 1] != '\\' && path[len - 1] != '/') {
        pattern[len] = '\\';
        pattern[len + 1] = '*';
        pattern[len + 2] = '\0';
    } else {
        pattern[len] = '*';
        pattern[len + 1] = '\0';
    }

    data = (WIN32_FIND_DATAA*)malloc(sizeof(WIN32_FIND_DATAA));
    if (!data) return NULL;

    h = FindFirstFileA(pattern, data);
    if (h == INVALID_HANDLE_VALUE) {
        free(data);
        return NULL;
    }

    it = (domino_sys_dir_iter*)malloc(sizeof(domino_sys_dir_iter));
    if (!it) {
        FindClose(h);
        free(data);
        return NULL;
    }
    memset(it, 0, sizeof(*it));
    it->handle = h;
    it->data = data;
    strncpy(it->base_path, path, sizeof(it->base_path) - 1);
    it->base_path[sizeof(it->base_path) - 1] = '\0';
    it->first_yielded = 0;
    return it;
}

static int win32_dir_next(domino_sys_context* ctx,
                          domino_sys_dir_iter* it,
                          char* name_out, size_t cap,
                          int* is_dir_out)
{
    WIN32_FIND_DATAA* data;
    int found = 0;
    (void)ctx;
    if (!it || !it->data || !name_out || cap == 0) return 0;
    data = (WIN32_FIND_DATAA*)it->data;

    for (;;) {
        if (!it->first_yielded) {
            it->first_yielded = 1;
        } else {
            if (!FindNextFileA((HANDLE)it->handle, data)) {
                return 0;
            }
        }
        if (strcmp(data->cFileName, ".") == 0 || strcmp(data->cFileName, "..") == 0) {
            continue;
        }
        found = 1;
        break;
    }

    if (found) {
        strncpy(name_out, data->cFileName, cap - 1);
        name_out[cap - 1] = '\0';
        if (is_dir_out) {
            *is_dir_out = (data->dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) ? 1 : 0;
        }
        return 1;
    }
    return 0;
}

static void win32_dir_close(domino_sys_context* ctx, domino_sys_dir_iter* it)
{
    (void)ctx;
    if (!it) return;
    if (it->handle) {
        FindClose((HANDLE)it->handle);
    }
    if (it->data) {
        free(it->data);
    }
    free(it);
}

static double win32_time_seconds(domino_sys_context* ctx)
{
    LARGE_INTEGER freq;
    LARGE_INTEGER now;
    (void)ctx;
    if (QueryPerformanceFrequency(&freq) && QueryPerformanceCounter(&now)) {
        return (double)now.QuadPart / (double)freq.QuadPart;
    }
    return (double)GetTickCount64() / 1000.0;
}

static unsigned long win32_time_millis(domino_sys_context* ctx)
{
    return (unsigned long)(win32_time_seconds(ctx) * 1000.0);
}

static void win32_sleep_millis(domino_sys_context* ctx, unsigned long ms)
{
    (void)ctx;
    Sleep(ms);
}

static int win32_process_spawn(domino_sys_context* ctx,
                               const domino_sys_process_desc* desc,
                               domino_sys_process** out_proc)
{
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    domino_sys_process* proc;
    char cmdline[1024];
    size_t offset = 0;
    size_t i;
    (void)ctx;
    if (!desc || !out_proc || !desc->path) return -1;

    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);
    memset(&pi, 0, sizeof(pi));
    memset(cmdline, 0, sizeof(cmdline));

    strncpy(cmdline, desc->path, sizeof(cmdline) - 1);
    offset = strlen(cmdline);

    if (desc->argv) {
        for (i = 0; desc->argv[i]; ++i) {
            size_t len = strlen(desc->argv[i]);
            if (offset + len + 2 >= sizeof(cmdline)) break;
            cmdline[offset++] = ' ';
            strncpy(cmdline + offset, desc->argv[i], sizeof(cmdline) - offset - 1);
            offset += len;
        }
    }

    if (!CreateProcessA(NULL,
                        cmdline,
                        NULL,
                        NULL,
                        FALSE,
                        0,
                        NULL,
                        desc->working_dir,
                        &si,
                        &pi)) {
        return -1;
    }

    CloseHandle(pi.hThread);

    proc = (domino_sys_process*)malloc(sizeof(domino_sys_process));
    if (!proc) {
        TerminateProcess(pi.hProcess, 1);
        CloseHandle(pi.hProcess);
        return -1;
    }
    proc->handle = pi.hProcess;
    proc->exit_code = -1;
    *out_proc = proc;
    return 0;
}

static int win32_process_wait(domino_sys_context* ctx,
                              domino_sys_process* proc,
                              int* exit_code_out)
{
    DWORD code;
    (void)ctx;
    if (!proc || !proc->handle) return -1;
    WaitForSingleObject((HANDLE)proc->handle, INFINITE);
    if (GetExitCodeProcess((HANDLE)proc->handle, &code)) {
        proc->exit_code = (int)code;
        if (exit_code_out) *exit_code_out = proc->exit_code;
        return 0;
    }
    return -1;
}

static void win32_process_destroy(domino_sys_context* ctx,
                                  domino_sys_process* proc)
{
    (void)ctx;
    if (!proc) return;
    if (proc->handle) {
        CloseHandle((HANDLE)proc->handle);
    }
    free(proc);
}

int domino_sys_backend_init_win32(domino_sys_context* ctx)
{
    if (!ctx) return -1;
    memset(&ctx->ops, 0, sizeof(ctx->ops));
    ctx->ops.fopen_fn = win32_fopen;
    ctx->ops.fread_fn = win32_fread;
    ctx->ops.fwrite_fn = win32_fwrite;
    ctx->ops.fclose_fn = win32_fclose;
    ctx->ops.file_exists_fn = win32_exists;
    ctx->ops.mkdirs_fn = win32_mkdirs;
    ctx->ops.dir_open_fn = win32_dir_open;
    ctx->ops.dir_next_fn = win32_dir_next;
    ctx->ops.dir_close_fn = win32_dir_close;
    ctx->ops.time_seconds_fn = win32_time_seconds;
    ctx->ops.time_millis_fn = win32_time_millis;
    ctx->ops.sleep_millis_fn = win32_sleep_millis;
    ctx->ops.process_spawn_fn = win32_process_spawn;
    ctx->ops.process_wait_fn = win32_process_wait;
    ctx->ops.process_destroy_fn = win32_process_destroy;
    ctx->backend_state = NULL;
    ctx->platform.has_threads = 1;
    ctx->platform.has_unicode = 1;
    win32_set_install_root(ctx);
    return 0;
}

void domino_sys_backend_shutdown_win32(domino_sys_context* ctx)
{
    (void)ctx;
}

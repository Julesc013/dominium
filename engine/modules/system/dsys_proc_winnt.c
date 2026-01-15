/*
FILE: source/domino/system/dsys_proc_winnt.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_proc_winnt
RESPONSIBILITY: Implements `dsys_proc_winnt`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys.h"

#include <windows.h>
#include <stdlib.h>
#include <string.h>

typedef struct dsys_process_impl {
    HANDLE process_handle;
} dsys_process_impl;

static char* d_concat_command_line(const char* path, const char* const* argv) {
    size_t total = 0;
    size_t i;
    char* buf;
    if (!path || !argv) return 0;
    for (i = 0; argv[i]; ++i) {
        total += strlen(argv[i]) + 3; /* quotes + space */
    }
    total += strlen(path) + 3;
    buf = (char*)malloc(total + 1);
    if (!buf) return 0;
    buf[0] = '\0';
    strcat(buf, "\"");
    strcat(buf, path);
    strcat(buf, "\"");
    for (i = 1; argv[i]; ++i) {
        strcat(buf, " \"");
        strcat(buf, argv[i]);
        strcat(buf, "\"");
    }
    return buf;
}

dsys_proc_result dsys_proc_spawn(const char* path,
                                 const char* const* argv,
                                 int inherit_stdio,
                                 dsys_process_handle* out_handle) {
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    char* cmdline;
    BOOL ok;

    (void)inherit_stdio; /* stdin/out/err inheritance is default when handles are inheritable */

    if (!path || !argv || !argv[0]) {
        return DSYS_PROC_ERROR_GENERIC;
    }

    cmdline = d_concat_command_line(path, argv);
    if (!cmdline) {
        return DSYS_PROC_ERROR_GENERIC;
    }

    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);
    memset(&pi, 0, sizeof(pi));

    ok = CreateProcessA(
        NULL,
        cmdline,
        NULL,
        NULL,
        inherit_stdio ? TRUE : FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi);

    free(cmdline);

    if (!ok) {
        return DSYS_PROC_ERROR_GENERIC;
    }

    if (out_handle) {
        dsys_process_impl* impl = (dsys_process_impl*)malloc(sizeof(dsys_process_impl));
        if (!impl) {
            CloseHandle(pi.hThread);
            CloseHandle(pi.hProcess);
            return DSYS_PROC_ERROR_GENERIC;
        }
        impl->process_handle = pi.hProcess;
        out_handle->impl = impl;
    } else {
        CloseHandle(pi.hProcess);
    }
    CloseHandle(pi.hThread);

    return DSYS_PROC_OK;
}

dsys_proc_result dsys_proc_wait(dsys_process_handle* handle,
                                int* out_exit_code) {
    dsys_process_impl* impl;
    DWORD wait_res;
    DWORD code = 0;
    if (!handle || !handle->impl) return DSYS_PROC_ERROR_GENERIC;
    impl = (dsys_process_impl*)handle->impl;

    wait_res = WaitForSingleObject(impl->process_handle, INFINITE);
    if (wait_res != WAIT_OBJECT_0) {
        CloseHandle(impl->process_handle);
        free(impl);
        handle->impl = 0;
        return DSYS_PROC_ERROR_GENERIC;
    }

    if (!GetExitCodeProcess(impl->process_handle, &code)) {
        CloseHandle(impl->process_handle);
        free(impl);
        handle->impl = 0;
        return DSYS_PROC_ERROR_GENERIC;
    }

    if (out_exit_code) {
        *out_exit_code = (int)code;
    }

    CloseHandle(impl->process_handle);
    free(impl);
    handle->impl = 0;
    return DSYS_PROC_OK;
}

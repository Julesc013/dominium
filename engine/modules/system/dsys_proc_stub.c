/*
FILE: source/domino/system/dsys_proc_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_proc_stub
RESPONSIBILITY: Implements `dsys_proc_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys.h"

dsys_proc_result dsys_proc_spawn(const char* path,
                                 const char* const* argv,
                                 int inherit_stdio,
                                 dsys_process_handle* out_handle) {
    (void)path;
    (void)argv;
    (void)inherit_stdio;
    (void)out_handle;
    return DSYS_PROC_ERROR_UNSUPPORTED;
}

dsys_proc_result dsys_proc_wait(dsys_process_handle* handle,
                                int* out_exit_code) {
    (void)handle;
    (void)out_exit_code;
    return DSYS_PROC_ERROR_UNSUPPORTED;
}

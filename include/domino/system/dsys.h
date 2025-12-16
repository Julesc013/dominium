/*
FILE: include/domino/system/dsys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / system/dsys
RESPONSIBILITY: Defines the public contract for `dsys` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Domino system abstraction stub (C89). */
#ifndef DOMINO_SYSTEM_DSYS_H
#define DOMINO_SYSTEM_DSYS_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsys_proc_result {
    DSYS_PROC_OK = 0,
    DSYS_PROC_ERROR_GENERIC = -1,
    DSYS_PROC_ERROR_UNSUPPORTED = -2
} dsys_proc_result;

typedef struct dsys_process_handle {
    void* impl;
} dsys_process_handle;

void dsys_set_log_callback(dsys_log_fn fn);

dsys_proc_result dsys_proc_spawn(const char* path,
                                 const char* const* argv,
                                 int inherit_stdio,
                                 dsys_process_handle* out_handle);

dsys_proc_result dsys_proc_wait(dsys_process_handle* handle,
                                int* out_exit_code);

/* Returns non-zero if process appears to be running under a terminal/console.
   Used only to distinguish CLI-style shell invocation from double-click/desktop launch. */
int dsys_running_in_terminal(void);

/*------------------------------------------------------------
 * Terminal (text UI) abstraction
 *------------------------------------------------------------*/
int  dsys_terminal_init(void);
void dsys_terminal_shutdown(void);
void dsys_terminal_clear(void);
void dsys_terminal_draw_text(int row, int col, const char* text);
void dsys_terminal_get_size(int* rows, int* cols);
int  dsys_terminal_poll_key(void); /* returns keycode or 0 if none */

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SYSTEM_DSYS_H */

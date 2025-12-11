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

typedef void (*dsys_log_fn)(const char* message);

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

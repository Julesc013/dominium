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

#ifndef DSS_PROC_H
#define DSS_PROC_H

#include "dss_error.h"

#ifdef __cplusplus
#include <string>
#include <vector>

struct dss_proc_spawn_t {
    std::vector<std::string> argv;
    std::vector<std::string> env;
    std::string cwd;
    dss_bool capture_stdout;
    dss_bool capture_stderr;
};

struct dss_proc_result_t {
    dss_i32 exit_code;
    std::vector<dss_u8> stdout_bytes;
    std::vector<dss_u8> stderr_bytes;
};

struct dss_proc_api_t {
    void *ctx;
    dss_error_t (*spawn)(void *ctx,
                         const dss_proc_spawn_t *req,
                         dss_proc_result_t *out_result);
};

#endif /* __cplusplus */

#endif /* DSS_PROC_H */

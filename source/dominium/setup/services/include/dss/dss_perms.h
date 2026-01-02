#ifndef DSS_PERMS_H
#define DSS_PERMS_H

#include "dss_error.h"

#ifdef __cplusplus
#include <string>

struct dss_scope_paths_t {
    std::string install_root;
    std::string data_root;
};

struct dss_perms_api_t {
    void *ctx;
    dss_error_t (*is_elevated)(void *ctx, dss_bool *out_is_elevated);
    dss_error_t (*request_elevation_supported)(void *ctx, dss_bool *out_supported);
    dss_error_t (*get_user_scope_paths)(void *ctx, dss_scope_paths_t *out_paths);
    dss_error_t (*get_system_scope_paths)(void *ctx, dss_scope_paths_t *out_paths);
};

#endif /* __cplusplus */

#endif /* DSS_PERMS_H */

#ifndef DSS_SERVICES_H
#define DSS_SERVICES_H

#include "dss_archive.h"
#include "dss_error.h"
#include "dss_fs.h"
#include "dss_hash.h"
#include "dss_perms.h"
#include "dss_platform.h"
#include "dss_proc.h"

#ifdef __cplusplus
#include <string>

struct dss_registry_win_api_t {
    void *ctx;
    dss_error_t (*read_string)(void *ctx,
                               const char *key,
                               const char *value,
                               std::string *out_value);
};

struct dss_pkgmgr_linux_api_t {
    void *ctx;
    dss_error_t (*query_installed)(void *ctx,
                                   const char *package_name,
                                   dss_bool *out_installed);
};

struct dss_codesign_macos_api_t {
    void *ctx;
    dss_error_t (*sign_path)(void *ctx, const char *path);
};

struct dss_services_t {
    dss_fs_api_t fs;
    dss_proc_api_t proc;
    dss_hash_api_t hash;
    dss_archive_api_t archive;
    dss_perms_api_t perms;
    dss_platform_api_t platform;
    dss_registry_win_api_t registry_win;
    dss_pkgmgr_linux_api_t pkgmgr_linux;
    dss_codesign_macos_api_t codesign_macos;
};

struct dss_services_config_t {
    const char *sandbox_root;
    const char *platform_triple;
};

DSS_API void dss_services_config_init(dss_services_config_t *config);
DSS_API dss_error_t dss_services_init_real(dss_services_t *out_services);
DSS_API dss_error_t dss_services_init_fake(const dss_services_config_t *config,
                                           dss_services_t *out_services);
DSS_API void dss_services_shutdown(dss_services_t *services);

#endif /* __cplusplus */

#endif /* DSS_SERVICES_H */

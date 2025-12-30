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
#include "dominium/provider_content_source.h"
#include "dominium/provider_keychain.h"
#include "dominium/provider_net.h"
#include "dominium/provider_os_integration.h"
#include "dominium/provider_trust.h"

struct dss_services_t {
    dss_fs_api_t fs;
    dss_proc_api_t proc;
    dss_hash_api_t hash;
    dss_archive_api_t archive;
    dss_perms_api_t perms;
    dss_platform_api_t platform;
    const provider_content_source_v1* provider_content;
    const provider_trust_v1* provider_trust;
    const provider_keychain_v1* provider_keychain;
    const provider_net_v1* provider_net;
    const provider_os_integration_v1* provider_os_integration;
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

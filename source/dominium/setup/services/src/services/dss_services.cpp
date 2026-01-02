#include "dss/dss_services.h"

#include <cstring>

void dss_services_config_init(dss_services_config_t *config) {
    if (!config) {
        return;
    }
    config->sandbox_root = 0;
    config->platform_triple = 0;
}

/* Module init/shutdown hooks (internal). */
void dss_fs_init_real(dss_fs_api_t *api);
void dss_fs_init_fake(dss_fs_api_t *api, const char *sandbox_root);
void dss_fs_shutdown(dss_fs_api_t *api);

void dss_proc_init_real(dss_proc_api_t *api);
void dss_proc_init_fake(dss_proc_api_t *api);
void dss_proc_shutdown(dss_proc_api_t *api);

void dss_hash_init_real(dss_hash_api_t *api);
void dss_hash_init_fake(dss_hash_api_t *api);
void dss_hash_shutdown(dss_hash_api_t *api);

void dss_archive_init_real(dss_archive_api_t *api);
void dss_archive_init_fake(dss_archive_api_t *api);
void dss_archive_shutdown(dss_archive_api_t *api);

void dss_perms_init_real(dss_perms_api_t *api);
void dss_perms_init_fake(dss_perms_api_t *api, const char *sandbox_root);
void dss_perms_shutdown(dss_perms_api_t *api);

void dss_platform_init_real(dss_platform_api_t *api);
void dss_platform_init_fake(dss_platform_api_t *api, const char *triple);
void dss_platform_shutdown(dss_platform_api_t *api);

dss_error_t dss_services_init_real(dss_services_t *out_services) {
    if (!out_services) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    std::memset(out_services, 0, sizeof(*out_services));
    dss_fs_init_real(&out_services->fs);
    dss_proc_init_real(&out_services->proc);
    dss_hash_init_real(&out_services->hash);
    dss_archive_init_real(&out_services->archive);
    dss_perms_init_real(&out_services->perms);
    dss_platform_init_real(&out_services->platform);
    out_services->provider_content = 0;
    out_services->provider_trust = 0;
    out_services->provider_keychain = 0;
    out_services->provider_net = 0;
    out_services->provider_os_integration = 0;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_services_init_fake(const dss_services_config_t *config,
                                   dss_services_t *out_services) {
    const char *sandbox_root = 0;
    const char *platform_triple = 0;
    if (!out_services) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    if (config) {
        sandbox_root = config->sandbox_root;
        platform_triple = config->platform_triple;
    }
    std::memset(out_services, 0, sizeof(*out_services));
    dss_fs_init_fake(&out_services->fs, sandbox_root);
    dss_proc_init_fake(&out_services->proc);
    dss_hash_init_fake(&out_services->hash);
    dss_archive_init_fake(&out_services->archive);
    dss_perms_init_fake(&out_services->perms, sandbox_root);
    dss_platform_init_fake(&out_services->platform, platform_triple);
    out_services->provider_content = 0;
    out_services->provider_trust = 0;
    out_services->provider_keychain = 0;
    out_services->provider_net = 0;
    out_services->provider_os_integration = 0;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

void dss_services_shutdown(dss_services_t *services) {
    if (!services) {
        return;
    }
    dss_fs_shutdown(&services->fs);
    dss_proc_shutdown(&services->proc);
    dss_hash_shutdown(&services->hash);
    dss_archive_shutdown(&services->archive);
    dss_perms_shutdown(&services->perms);
    dss_platform_shutdown(&services->platform);
    services->provider_content = 0;
    services->provider_trust = 0;
    services->provider_keychain = 0;
    services->provider_net = 0;
    services->provider_os_integration = 0;
}

#ifndef DSK_FRONTEND_REQUEST_BUILDER_H
#define DSK_FRONTEND_REQUEST_BUILDER_H

#include "dsk/dsk_contracts.h"
#include "dss/dss_services.h"

#include <string>
#include <vector>

struct dsk_request_build_opts_t {
    dsk_u16 operation;
    dsk_u16 install_scope;
    dsk_u16 ui_mode;
    dsk_u32 policy_flags;
    dsk_u32 required_caps;
    dsk_u32 prohibited_caps;
    dsk_u16 ownership_preference;
    std::string preferred_install_root;
    std::string payload_root;
    std::string requested_splat_id;
    std::string frontend_id;
    std::string target_platform_triple;
    std::string manifest_path;
    std::vector<std::string> requested_components;
    std::vector<std::string> excluded_components;
};

void dsk_request_build_opts_init(dsk_request_build_opts_t *opts);

dsk_status_t dsk_request_build_request(const dsk_request_build_opts_t *opts,
                                       const dss_services_t *services,
                                       dsk_request_t *out_request);

dsk_status_t dsk_request_build_bytes(const dsk_request_build_opts_t *opts,
                                     const dss_services_t *services,
                                     std::vector<dsk_u8> *out_bytes,
                                     dsk_request_t *out_request);

dsk_u16 dsk_request_parse_operation(const char *value);
dsk_u16 dsk_request_parse_scope(const char *value);
dsk_u16 dsk_request_parse_ui_mode(const char *value);
dsk_u16 dsk_request_parse_ownership(const char *value);

#endif

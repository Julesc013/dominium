/*
FILE: source/dominium/providers/provider_net_null.c
MODULE: Dominium
PURPOSE: Null network provider (not supported).
*/
#include "dominium/provider_net.h"

#include <string.h>

static const char* provider_net_null_id(void) {
    return "null";
}

static dom_abi_result provider_net_null_query_interface(dom_iid iid, void** out_iface);

static dom_abi_result provider_net_null_fetch(const provider_net_request_v1* req,
                                              const char* staging_path,
                                              provider_net_response_v1* out_resp,
                                              err_t* out_err) {
    (void)req;
    (void)staging_path;
    if (out_resp) {
        memset(out_resp, 0, sizeof(*out_resp));
    }
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static const provider_net_v1 g_provider_net_null = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_net_v1),
    provider_net_null_query_interface,
    provider_net_null_id,
    provider_net_null_fetch
};

static dom_abi_result provider_net_null_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1 || iid == PROVIDER_IID_NET_V1) {
        *out_iface = (void*)&g_provider_net_null;
        return 0;
    }
    return (dom_abi_result)-1;
}

const provider_net_v1* provider_net_null_v1(void) {
    return &g_provider_net_null;
}

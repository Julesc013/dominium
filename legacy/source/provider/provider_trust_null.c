/*
FILE: source/dominium/providers/provider_trust_null.c
MODULE: Dominium
PURPOSE: Null trust provider (always unverified).
*/
#include "dominium/provider_trust.h"

static const char* provider_trust_null_id(void) {
    return "null";
}

static dom_abi_result provider_trust_null_query_interface(dom_iid iid, void** out_iface);

static dom_abi_result provider_trust_null_verify_manifest(const provider_trust_manifest_v1* req,
                                                          u32* out_result,
                                                          err_t* out_err) {
    (void)req;
    if (out_result) {
        *out_result = (u32)PROVIDER_TRUST_RESULT_UNVERIFIED;
    }
    if (out_err) {
        *out_err = err_ok();
    }
    return 0;
}

static dom_abi_result provider_trust_null_verify_artifact(const provider_trust_artifact_v1* req,
                                                          u32* out_result,
                                                          err_t* out_err) {
    (void)req;
    if (out_result) {
        *out_result = (u32)PROVIDER_TRUST_RESULT_UNVERIFIED;
    }
    if (out_err) {
        *out_err = err_ok();
    }
    return 0;
}

static const provider_trust_v1 g_provider_trust_null = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_trust_v1),
    provider_trust_null_query_interface,
    provider_trust_null_id,
    provider_trust_null_verify_manifest,
    provider_trust_null_verify_artifact
};

static dom_abi_result provider_trust_null_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1 || iid == PROVIDER_IID_TRUST_V1) {
        *out_iface = (void*)&g_provider_trust_null;
        return 0;
    }
    return (dom_abi_result)-1;
}

const provider_trust_v1* provider_trust_null_v1(void) {
    return &g_provider_trust_null;
}

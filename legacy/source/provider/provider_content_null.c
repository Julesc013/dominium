/*
FILE: source/dominium/providers/provider_content_null.c
MODULE: Dominium
PURPOSE: Null content source provider (always unsupported).
*/
#include "dominium/provider_content_source.h"

#include <string.h>

static const char* provider_content_null_id(void) {
    return "null";
}

static dom_abi_result provider_content_null_query_interface(dom_iid iid, void** out_iface);

static dom_abi_result provider_content_null_enumerate(provider_content_source_list_v1* out_sources,
                                                      err_t* out_err) {
    if (out_sources) {
        out_sources->count = 0u;
        memset(out_sources->entries, 0, sizeof(out_sources->entries));
    }
    if (out_err) {
        *out_err = err_ok();
    }
    return 0;
}

static dom_abi_result provider_content_null_resolve(const provider_content_request_v1* req,
                                                    provider_content_artifact_ref_v1* out_ref,
                                                    err_t* out_err) {
    (void)req;
    if (out_ref) {
        memset(out_ref, 0, sizeof(*out_ref));
    }
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_content_null_acquire(const provider_content_request_v1* req,
                                                    const char* staging_path,
                                                    err_t* out_err) {
    (void)req;
    (void)staging_path;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static const provider_content_source_v1 g_provider_content_null = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_content_source_v1),
    provider_content_null_query_interface,
    provider_content_null_id,
    provider_content_null_enumerate,
    provider_content_null_resolve,
    provider_content_null_acquire
};

static dom_abi_result provider_content_null_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1 || iid == PROVIDER_IID_CONTENT_SOURCE_V1) {
        *out_iface = (void*)&g_provider_content_null;
        return 0;
    }
    return (dom_abi_result)-1;
}

const provider_content_source_v1* provider_content_null_v1(void) {
    return &g_provider_content_null;
}

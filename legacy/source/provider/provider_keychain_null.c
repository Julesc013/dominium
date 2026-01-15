/*
FILE: source/dominium/providers/provider_keychain_null.c
MODULE: Dominium
PURPOSE: Null keychain provider (not supported).
*/
#include "dominium/provider_keychain.h"

static const char* provider_keychain_null_id(void) {
    return "null";
}

static dom_abi_result provider_keychain_null_query_interface(dom_iid iid, void** out_iface);

static dom_abi_result provider_keychain_null_store(const char* key_id,
                                                   const unsigned char* data,
                                                   u32 data_len,
                                                   err_t* out_err) {
    (void)key_id;
    (void)data;
    (void)data_len;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_keychain_null_load(const char* key_id,
                                                  unsigned char* out_data,
                                                  u32* inout_len,
                                                  err_t* out_err) {
    (void)key_id;
    (void)out_data;
    if (inout_len) {
        *inout_len = 0u;
    }
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_keychain_null_delete(const char* key_id,
                                                    err_t* out_err) {
    (void)key_id;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static const provider_keychain_v1 g_provider_keychain_null = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_keychain_v1),
    provider_keychain_null_query_interface,
    provider_keychain_null_id,
    provider_keychain_null_store,
    provider_keychain_null_load,
    provider_keychain_null_delete
};

static dom_abi_result provider_keychain_null_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1 || iid == PROVIDER_IID_KEYCHAIN_V1) {
        *out_iface = (void*)&g_provider_keychain_null;
        return 0;
    }
    return (dom_abi_result)-1;
}

const provider_keychain_v1* provider_keychain_null_v1(void) {
    return &g_provider_keychain_null;
}

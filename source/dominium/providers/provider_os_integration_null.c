/*
FILE: source/dominium/providers/provider_os_integration_null.c
MODULE: Dominium
PURPOSE: Null OS integration provider (not supported).
*/
#include "dominium/provider_os_integration.h"

static const char* provider_os_null_id(void) {
    return "null";
}

static dom_abi_result provider_os_null_query_interface(dom_iid iid, void** out_iface);

static dom_abi_result provider_os_null_create_shortcut(const provider_os_shortcut_desc_v1* desc,
                                                       err_t* out_err) {
    (void)desc;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_os_null_remove_shortcut(const char* app_id,
                                                       err_t* out_err) {
    (void)app_id;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_os_null_register_assoc(const provider_os_file_assoc_desc_v1* desc,
                                                      err_t* out_err) {
    (void)desc;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_os_null_unregister_assoc(const char* extension,
                                                        const char* app_id,
                                                        err_t* out_err) {
    (void)extension;
    (void)app_id;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static dom_abi_result provider_os_null_open_folder(const char* path_rel,
                                                   u32 is_instance_relative,
                                                   err_t* out_err) {
    (void)path_rel;
    (void)is_instance_relative;
    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON,
                            (u16)ERRC_COMMON_UNSUPPORTED,
                            (u32)(ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL),
                            (u32)ERRMSG_COMMON_UNSUPPORTED);
    }
    return (dom_abi_result)-1;
}

static const provider_os_integration_v1 g_provider_os_null = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_os_integration_v1),
    provider_os_null_query_interface,
    provider_os_null_id,
    provider_os_null_create_shortcut,
    provider_os_null_remove_shortcut,
    provider_os_null_register_assoc,
    provider_os_null_unregister_assoc,
    provider_os_null_open_folder
};

static dom_abi_result provider_os_null_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1 || iid == PROVIDER_IID_OS_INTEGRATION_V1) {
        *out_iface = (void*)&g_provider_os_null;
        return 0;
    }
    return (dom_abi_result)-1;
}

const provider_os_integration_v1* provider_os_integration_null_v1(void) {
    return &g_provider_os_null;
}

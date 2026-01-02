/*
FILE: source/dominium/providers/provider_null.c
MODULE: Dominium
PURPOSE: Null provider stub (R-1 placeholder).
*/
#include "dominium/provider_api.h"

static const char *provider_null_id(void) {
    return "null";
}

static dom_abi_result provider_null_query_interface(dom_iid iid, void **out_iface);

static const provider_api_v1 g_provider_null = {
    DOM_ABI_HEADER_INIT(PROVIDER_API_VERSION, provider_api_v1),
    provider_null_query_interface,
    provider_null_id
};

static dom_abi_result provider_null_query_interface(dom_iid iid, void **out_iface) {
    if (!out_iface) {
        return -1;
    }
    *out_iface = 0;
    if (iid == PROVIDER_IID_CORE_V1) {
        *out_iface = (void *)&g_provider_null;
        return 0;
    }
    return -1;
}

const provider_api_v1* provider_null_v1(void) {
    return &g_provider_null;
}

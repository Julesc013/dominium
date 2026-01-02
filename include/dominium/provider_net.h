/*
FILE: include/dominium/provider_net.h
MODULE: Dominium
PURPOSE: Network transport provider ABI (optional).
*/
#ifndef DOMINIUM_PROVIDER_NET_H
#define DOMINIUM_PROVIDER_NET_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dominium/core_err.h"
#include "dominium/provider_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_IID_NET_V1 ((dom_iid)0x504E5431u) /* 'PNT1' */

typedef struct provider_net_request_v1 {
    u32 struct_size;
    u32 struct_version;
    const char* url;
    const unsigned char* request_tlv;
    u32 request_tlv_len;
} provider_net_request_v1;

typedef struct provider_net_response_v1 {
    u32 struct_size;
    u32 struct_version;
    u32 status_code;
    u64 size_bytes;
} provider_net_response_v1;

typedef struct provider_net_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char* (*provider_id)(void);

    dom_abi_result (*fetch)(const provider_net_request_v1* req,
                            const char* staging_path,
                            provider_net_response_v1* out_resp,
                            err_t* out_err);
} provider_net_v1;

const provider_net_v1* provider_net_null_v1(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_NET_H */

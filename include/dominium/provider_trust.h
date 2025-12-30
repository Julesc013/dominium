/*
FILE: include/dominium/provider_trust.h
MODULE: Dominium
PURPOSE: Trust/signature verification provider ABI.
*/
#ifndef DOMINIUM_PROVIDER_TRUST_H
#define DOMINIUM_PROVIDER_TRUST_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dominium/core_err.h"
#include "dominium/provider_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_IID_TRUST_V1 ((dom_iid)0x50545231u) /* 'PTR1' */

typedef enum provider_trust_result_e {
    PROVIDER_TRUST_RESULT_UNKNOWN = 0u,
    PROVIDER_TRUST_RESULT_VERIFIED = 1u,
    PROVIDER_TRUST_RESULT_UNVERIFIED = 2u,
    PROVIDER_TRUST_RESULT_REFUSED = 3u
} provider_trust_result;

typedef struct provider_trust_manifest_v1 {
    u32 struct_size;
    u32 struct_version;
    const unsigned char* manifest_bytes;
    u32 manifest_size;
    const unsigned char* signature_bytes;
    u32 signature_size;
    const char* key_id;
} provider_trust_manifest_v1;

typedef struct provider_trust_artifact_v1 {
    u32 struct_size;
    u32 struct_version;
    const unsigned char* hash_bytes;
    u32 hash_len;
    const unsigned char* signature_bytes;
    u32 signature_size;
    const char* key_id;
} provider_trust_artifact_v1;

typedef struct provider_trust_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char* (*provider_id)(void);

    dom_abi_result (*verify_manifest)(const provider_trust_manifest_v1* req,
                                      u32* out_result,
                                      err_t* out_err);
    dom_abi_result (*verify_artifact)(const provider_trust_artifact_v1* req,
                                      u32* out_result,
                                      err_t* out_err);
} provider_trust_v1;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_TRUST_H */

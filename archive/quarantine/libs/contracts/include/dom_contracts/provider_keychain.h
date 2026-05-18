/*
FILE: include/dominium/provider_keychain.h
MODULE: Dominium
PURPOSE: Keychain/secure storage provider ABI.
*/
#ifndef DOMINIUM_PROVIDER_KEYCHAIN_H
#define DOMINIUM_PROVIDER_KEYCHAIN_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dom_contracts/core_err.h"
#include "dom_contracts/provider_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_IID_KEYCHAIN_V1 ((dom_iid)0x504B4331u) /* 'PKC1' */

typedef struct provider_keychain_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char* (*provider_id)(void);

    dom_abi_result (*store_secret)(const char* key_id,
                                   const unsigned char* data,
                                   u32 data_len,
                                   err_t* out_err);
    dom_abi_result (*load_secret)(const char* key_id,
                                  unsigned char* out_buf,
                                  u32* inout_len,
                                  err_t* out_err);
    dom_abi_result (*delete_secret)(const char* key_id,
                                    err_t* out_err);
} provider_keychain_v1;

const provider_keychain_v1* provider_keychain_null_v1(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_KEYCHAIN_H */

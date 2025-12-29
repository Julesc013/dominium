/*
FILE: include/dominium/provider_api.h
MODULE: Dominium
PURPOSE: Provider API facade (R-1 placeholder; query_interface pattern).
*/
#ifndef DOMINIUM_PROVIDER_API_H
#define DOMINIUM_PROVIDER_API_H

#include "domino/abi.h"
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_API_VERSION 1u
#define PROVIDER_IID_CORE_V1 ((dom_iid)0x50525631u) /* 'PRV1' */

typedef struct provider_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char *(*name)(void);
} provider_api_v1;

const provider_api_v1* provider_null_v1(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PROVIDER_API_H */

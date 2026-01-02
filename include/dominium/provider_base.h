/*
FILE: include/dominium/provider_base.h
MODULE: Dominium
PURPOSE: Provider base ABI (query_interface + stable provider_id).
NOTES: Provider IDs are stable string tokens; all provider vtables share the base fields.
*/
#ifndef DOMINIUM_PROVIDER_BASE_H
#define DOMINIUM_PROVIDER_BASE_H

#include "domino/abi.h"
#include "dominium/core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_API_VERSION 1u
#define PROVIDER_IID_CORE_V1 ((dom_iid)0x50525631u) /* 'PRV1' */

typedef struct provider_base_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char* (*provider_id)(void);
} provider_base_v1;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_BASE_H */

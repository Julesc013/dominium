/*
FILE: include/dominium/provider_api.h
MODULE: Dominium
PURPOSE: Provider API facade (base interface).
*/
#ifndef DOMINIUM_PROVIDER_API_H
#define DOMINIUM_PROVIDER_API_H

#include "dom_contracts/provider_base.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef provider_base_v1 provider_api_v1;

const provider_api_v1* provider_null_v1(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PROVIDER_API_H */

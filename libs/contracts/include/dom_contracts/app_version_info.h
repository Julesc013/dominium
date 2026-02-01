/*
FILE: include/dom_contracts/app_version_info.h
MODULE: Dominium
PURPOSE: Application-layer version identity (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_VERSION_INFO_H
#define DOMINIUM_APP_VERSION_INFO_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_app_version_info: build/version identity surface. */
typedef struct dom_app_version_info_t {
    u32 struct_size;
    u32 struct_version;
    const char* product_id;
    const char* product_version;
    const char* build_id;
    const char* git_hash;
    const char* toolchain_id;
} dom_app_version_info;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_VERSION_INFO_H */

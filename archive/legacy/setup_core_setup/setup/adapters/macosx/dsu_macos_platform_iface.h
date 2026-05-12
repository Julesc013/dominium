/*
FILE: source/dominium/setup/adapters/macos/dsu_macos_platform_iface.h
MODULE: Dominium Setup
PURPOSE: macOS platform interface implementation (Plan S-6).
*/
#ifndef DSU_MACOS_PLATFORM_IFACE_H_INCLUDED
#define DSU_MACOS_PLATFORM_IFACE_H_INCLUDED

#include "dsu/dsu_platform_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_macos_platform_user_t {
    dsu_u32 reserved;
} dsu_macos_platform_user_t;

dsu_status_t dsu_macos_platform_iface_init(dsu_platform_iface_t *out_iface);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_MACOS_PLATFORM_IFACE_H_INCLUDED */

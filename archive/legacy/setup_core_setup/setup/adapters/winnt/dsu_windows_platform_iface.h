/*
FILE: source/dominium/setup/adapters/windows/dsu_windows_platform_iface.h
MODULE: Dominium Setup
PURPOSE: Windows platform interface implementation (Plan S-6).
*/
#ifndef DSU_WINDOWS_PLATFORM_IFACE_H_INCLUDED
#define DSU_WINDOWS_PLATFORM_IFACE_H_INCLUDED

#include "dsu/dsu_platform_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_windows_platform_user_t {
    dsu_u32 reserved;
} dsu_windows_platform_user_t;

dsu_status_t dsu_windows_platform_iface_init(dsu_platform_iface_t *out_iface);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_WINDOWS_PLATFORM_IFACE_H_INCLUDED */


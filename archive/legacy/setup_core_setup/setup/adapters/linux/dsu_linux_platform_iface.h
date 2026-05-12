/*
FILE: source/dominium/setup/adapters/linux/dsu_linux_platform_iface.h
MODULE: Dominium Setup
PURPOSE: Linux platform interface implementation (Plan S-6).
*/
#ifndef DSU_LINUX_PLATFORM_IFACE_H_INCLUDED
#define DSU_LINUX_PLATFORM_IFACE_H_INCLUDED

#include "dsu/dsu_platform_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_linux_platform_user_t {
    dsu_u32 reserved;
} dsu_linux_platform_user_t;

dsu_status_t dsu_linux_platform_iface_init(dsu_platform_iface_t *out_iface);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LINUX_PLATFORM_IFACE_H_INCLUDED */

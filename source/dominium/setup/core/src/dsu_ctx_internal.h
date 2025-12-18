/*
FILE: source/dominium/setup/core/src/dsu_ctx_internal.h
MODULE: Dominium Setup
PURPOSE: Internal definition of dsu_ctx_t for core modules.
*/
#ifndef DSU_CTX_INTERNAL_H_INCLUDED
#define DSU_CTX_INTERNAL_H_INCLUDED

#include "../include/dsu/dsu_ctx.h"

#include "dsu/dsu_platform_iface.h"

struct dsu_ctx {
    dsu_config_t config;
    dsu_callbacks_t callbacks;
    void *callbacks_user;
    dsu_log_t *audit_log;

    dsu_platform_iface_t platform_iface;
    void *platform_user;
};

#endif /* DSU_CTX_INTERNAL_H_INCLUDED */

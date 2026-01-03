/*
FILE: source/dominium/setup/core/include/dsu/dsu_ctx.h
MODULE: Dominium Setup
LAYER / SUBSYSTEM: Setup Core context API
RESPONSIBILITY:
  - Owns the public context handle type and lifecycle entry points.
  - Does not define manifest/plan formats or any UI behavior.
ALLOWED DEPENDENCIES: dsu_callbacks.h, dsu_config.h, dsu_types.h.
FORBIDDEN DEPENDENCIES: Platform headers; setup core implementation headers.
THREADING MODEL: Single-threaded API; no internal threading guarantees.
ERROR MODEL: dsu_status_t return codes for creation/reset; NULL on invalid accessors.
DETERMINISM GUARANTEES: Determinism is configured via dsu_config_t and enforced by core implementation.
VERSIONING / ABI / DATA FORMAT NOTES: Opaque handle type; ABI stability depends on struct_size/versioned config and callbacks.
EXTENSION POINTS: None (opaque handle; extension occurs inside core implementation).
*/
/*
FILE: source/dominium/setup/core/include/dsu/dsu_ctx.h
MODULE: Dominium Setup
PURPOSE: Setup Core context lifecycle.
*/
#ifndef DSU_CTX_H_INCLUDED
#define DSU_CTX_H_INCLUDED

#include "dsu_callbacks.h"
#include "dsu_config.h"
#include "dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_ctx dsu_ctx_t;
typedef struct dsu_log dsu_log_t;

DSU_API dsu_status_t dsu_ctx_create(const dsu_config_t *config,
                                   const dsu_callbacks_t *callbacks,
                                   void *callbacks_user,
                                   dsu_ctx_t **out_ctx);

DSU_API void dsu_ctx_destroy(dsu_ctx_t *ctx);

/* Returns a pointer owned by the context. */
DSU_API dsu_log_t *dsu_ctx_get_audit_log(dsu_ctx_t *ctx);

DSU_API dsu_status_t dsu_ctx_reset_audit_log(dsu_ctx_t *ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_CTX_H_INCLUDED */


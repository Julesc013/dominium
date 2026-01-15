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

/**
 * Purpose: Opaque handle for Setup Core context state.
 * ABI / layout constraints: Opaque type; size and layout are internal to Setup Core.
 */
typedef struct dsu_ctx dsu_ctx_t;
/**
 * Purpose: Opaque handle for the context audit log.
 * ABI / layout constraints: Opaque type; size and layout are internal to Setup Core.
 */
typedef struct dsu_log dsu_log_t;

/**
 * Purpose: Create a Setup Core context with optional configuration and callbacks.
 * Parameters:
 *   config:
 *     - meaning: Optional configuration overrides (NULL uses defaults).
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; read-only for duration of the call.
 *     - nullability: May be NULL.
 *     - aliasing rules: May alias other caller state; not retained.
 *   callbacks:
 *     - meaning: Optional callback set (NULL disables callbacks).
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; read-only for duration of the call.
 *     - nullability: May be NULL.
 *     - aliasing rules: May alias other caller state; not retained.
 *   callbacks_user:
 *     - meaning: User pointer forwarded to callbacks.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid while callbacks are in use.
 *     - nullability: May be NULL.
 *     - aliasing rules: May alias other caller state.
 *   out_ctx:
 *     - meaning: Receives the created context handle.
 *     - units: Not applicable.
 *     - ownership / lifetime: Output; caller owns the handle and must destroy it.
 *     - nullability: Must be non-NULL.
 *     - aliasing rules: Must not alias input pointers.
 * Return values / error codes:
 *   - DSU_STATUS_SUCCESS: Context created.
 *   - DSU_STATUS_INVALID_ARGS: Invalid arguments or struct version/size mismatch.
 *   - DSU_STATUS_IO_ERROR: Allocation failure.
 *   - Any status propagated from dsu_log_create.
 * Preconditions: out_ctx is non-NULL; if provided, config/callbacks versions and sizes match.
 * Postconditions: On success, *out_ctx is non-NULL; on failure, *out_ctx is set to NULL.
 * Side effects: Allocates memory, initializes platform interface, creates audit log.
 * Thread-safety / reentrancy guarantees: Not thread-safe; call from a single thread.
 * Determinism guarantees: Determinism policy is configured via dsu_config_t.
 */
DSU_API dsu_status_t dsu_ctx_create(const dsu_config_t *config,
                                   const dsu_callbacks_t *callbacks,
                                   void *callbacks_user,
                                   dsu_ctx_t **out_ctx);

/**
 * Purpose: Destroy a Setup Core context and release its resources.
 * Parameters:
 *   ctx:
 *     - meaning: Context handle to destroy.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; invalid after return.
 *     - nullability: May be NULL (no-op).
 *     - aliasing rules: Must not alias other live contexts.
 * Preconditions: No other thread is using ctx.
 * Postconditions: ctx is invalidated; associated audit log is destroyed.
 * Side effects: Frees memory and audit log storage.
 * Thread-safety / reentrancy guarantees: Not thread-safe; call from a single thread.
 */
DSU_API void dsu_ctx_destroy(dsu_ctx_t *ctx);

/**
 * Purpose: Fetch the audit log handle owned by a context.
 * Parameters:
 *   ctx:
 *     - meaning: Context handle to query.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid for the call.
 *     - nullability: May be NULL.
 *     - aliasing rules: Read-only access.
 * Return values / error codes:
 *   - Non-NULL pointer to an audit log owned by the context.
 *   - NULL if ctx is NULL.
 * Preconditions: None.
 * Postconditions: Returned pointer remains owned by ctx.
 * Side effects: None.
 * Thread-safety / reentrancy guarantees: Not thread-safe; call from a single thread.
 */
/* Returns a pointer owned by the context. */
DSU_API dsu_log_t *dsu_ctx_get_audit_log(dsu_ctx_t *ctx);

/**
 * Purpose: Reset the audit log associated with a context.
 * Parameters:
 *   ctx:
 *     - meaning: Context handle whose audit log is reset.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid for the call.
 *     - nullability: May be NULL.
 *     - aliasing rules: Read-only access to ctx handle.
 * Return values / error codes:
 *   - DSU_STATUS_SUCCESS: Log reset succeeded.
 *   - DSU_STATUS_INVALID_ARGS: ctx is NULL.
 *   - DSU_STATUS_INTERNAL_ERROR: Context has no audit log.
 *   - Any status propagated from dsu_log_reset.
 * Preconditions: ctx is non-NULL and has an audit log.
 * Postconditions: Audit log is reset to empty state.
 * Side effects: Mutates audit log state.
 * Thread-safety / reentrancy guarantees: Not thread-safe; call from a single thread.
 * Determinism guarantees: Reset does not introduce nondeterministic state.
 */
DSU_API dsu_status_t dsu_ctx_reset_audit_log(dsu_ctx_t *ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_CTX_H_INCLUDED */


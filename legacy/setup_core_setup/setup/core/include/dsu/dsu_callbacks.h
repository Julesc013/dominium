/*
FILE: source/dominium/setup/core/include/dsu/dsu_callbacks.h
MODULE: Dominium Setup
LAYER / SUBSYSTEM: Setup Core callbacks
RESPONSIBILITY:
  - Owns callback type definitions and the versioned callbacks struct.
  - Does not implement logging, progress aggregation, or threading.
ALLOWED DEPENDENCIES: dsu_types.h.
FORBIDDEN DEPENDENCIES: Platform headers; UI/renderer subsystems.
THREADING MODEL: Not applicable (callback signatures only).
ERROR MODEL: Not applicable (callbacks do not return status codes).
DETERMINISM GUARANTEES: Determinism is unaffected by callback presence; callbacks are observational.
VERSIONING / ABI / DATA FORMAT NOTES: struct_size/struct_version gate ABI compatibility; DSU_CALLBACKS_VERSION is the current schema.
EXTENSION POINTS: Reserved fields and version/size gating support forward-compatible extensions.
*/
/*
FILE: source/dominium/setup/core/include/dsu/dsu_callbacks.h
MODULE: Dominium Setup
PURPOSE: Host callbacks for logging and progress reporting.
*/
#ifndef DSU_CALLBACKS_H_INCLUDED
#define DSU_CALLBACKS_H_INCLUDED

#include "dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Purpose: Current schema/version for dsu_callbacks_t.
 * ABI / layout constraints: Written to dsu_callbacks_t.struct_version.
 */
#define DSU_CALLBACKS_VERSION 1u

/**
 * Purpose: Log severity levels reported by Setup Core.
 * Return values / error codes:
 *   - DSU_LOG_SEVERITY_DEBUG: Diagnostic detail.
 *   - DSU_LOG_SEVERITY_INFO: Informational status.
 *   - DSU_LOG_SEVERITY_WARN: Recoverable warning.
 *   - DSU_LOG_SEVERITY_ERROR: Error condition.
 */
typedef enum dsu_log_severity_t {
    DSU_LOG_SEVERITY_DEBUG = 0,
    DSU_LOG_SEVERITY_INFO = 1,
    DSU_LOG_SEVERITY_WARN = 2,
    DSU_LOG_SEVERITY_ERROR = 3
} dsu_log_severity_t;

/**
 * Purpose: Log categories for routing and filtering.
 * Return values / error codes:
 *   - DSU_LOG_CATEGORY_GENERAL: General/core messages.
 *   - DSU_LOG_CATEGORY_MANIFEST: Manifest loading/validation.
 *   - DSU_LOG_CATEGORY_RESOLVE: Resolution and dependency checks.
 *   - DSU_LOG_CATEGORY_PLAN: Plan creation/validation.
 *   - DSU_LOG_CATEGORY_EXECUTE: Apply/execute stages.
 *   - DSU_LOG_CATEGORY_IO: File and IO operations.
 */
typedef enum dsu_log_category_t {
    DSU_LOG_CATEGORY_GENERAL = 0,
    DSU_LOG_CATEGORY_MANIFEST = 1,
    DSU_LOG_CATEGORY_RESOLVE = 2,
    DSU_LOG_CATEGORY_PLAN = 3,
    DSU_LOG_CATEGORY_EXECUTE = 4,
    DSU_LOG_CATEGORY_IO = 5
} dsu_log_category_t;

/**
 * Purpose: Receives structured log events from Setup Core.
 * Parameters:
 *   user:
 *     - meaning: Caller-supplied callback user pointer.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid while callbacks are in use.
 *     - nullability: May be NULL.
 *     - aliasing rules: May alias other caller state.
 *   event_id:
 *     - meaning: Core-defined event identifier.
 *     - units: Numeric identifier.
 *     - ownership / lifetime: Value.
 *     - nullability: Not applicable.
 *     - aliasing rules: Not applicable.
 *   severity:
 *     - meaning: Severity level (dsu_log_severity_t).
 *     - units: Enum value.
 *     - ownership / lifetime: Value.
 *     - nullability: Not applicable.
 *     - aliasing rules: Not applicable.
 *   category:
 *     - meaning: Category level (dsu_log_category_t).
 *     - units: Enum value.
 *     - ownership / lifetime: Value.
 *     - nullability: Not applicable.
 *     - aliasing rules: Not applicable.
 *   timestamp:
 *     - meaning: Core-provided timestamp (0 in deterministic mode).
 *     - units: Implementation-defined.
 *     - ownership / lifetime: Value.
 *     - nullability: Not applicable.
 *     - aliasing rules: Not applicable.
 *   message:
 *     - meaning: Human-readable message string.
 *     - units: NUL-terminated string.
 *     - ownership / lifetime: Owned by core; valid for the duration of the call.
 *     - nullability: May be NULL.
 *     - aliasing rules: Read-only.
 * Side effects: Callback-defined; core ignores return (void).
 * Thread-safety / reentrancy guarantees: No additional synchronization is provided by the core.
 * Determinism guarantees: Callback side effects must not affect core determinism.
 */
typedef void (*dsu_log_callback_t)(void *user,
                                  dsu_u32 event_id,
                                  dsu_u8 severity,
                                  dsu_u8 category,
                                  dsu_u32 timestamp,
                                  const char *message);

/**
 * Purpose: Receives progress updates for long-running operations.
 * Parameters:
 *   user:
 *     - meaning: Caller-supplied callback user pointer.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid while callbacks are in use.
 *     - nullability: May be NULL.
 *     - aliasing rules: May alias other caller state.
 *   current:
 *     - meaning: Current progress count.
 *     - units: Implementation-defined units.
 *     - ownership / lifetime: Value.
 *     - nullability: Not applicable.
 *     - aliasing rules: Not applicable.
 *   total:
 *     - meaning: Total progress count.
 *     - units: Implementation-defined units.
 *     - ownership / lifetime: Value.
 *     - nullability: Not applicable.
 *     - aliasing rules: Not applicable.
 *   phase:
 *     - meaning: Optional phase label for the current operation.
 *     - units: NUL-terminated string.
 *     - ownership / lifetime: Owned by core; valid for the duration of the call.
 *     - nullability: May be NULL.
 *     - aliasing rules: Read-only.
 * Side effects: Callback-defined; core ignores return (void).
 * Thread-safety / reentrancy guarantees: No additional synchronization is provided by the core.
 * Determinism guarantees: Callback side effects must not affect core determinism.
 */
typedef void (*dsu_progress_callback_t)(void *user,
                                       dsu_u32 current,
                                       dsu_u32 total,
                                       const char *phase);

/**
 * Purpose: Callback set for logging and progress reporting.
 * ABI / layout constraints:
 *   - struct_size: Size of this struct in bytes.
 *   - struct_version: Must match DSU_CALLBACKS_VERSION.
 *   - log: Log callback (optional).
 *   - progress: Progress callback (optional).
 *   - reserved: Zero-initialize for forward compatibility.
 * Preconditions: Callers should initialize via dsu_callbacks_init before overriding fields.
 */
typedef struct dsu_callbacks_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;
    dsu_log_callback_t log;
    dsu_progress_callback_t progress;
    dsu_u32 reserved[4];
} dsu_callbacks_t;

/**
 * Purpose: Initialize a dsu_callbacks_t to ABI/version defaults.
 * Parameters:
 *   cbs:
 *     - meaning: Destination callbacks struct to initialize.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid for initialization.
 *     - nullability: May be NULL; function is a no-op.
 *     - aliasing rules: May alias other caller state.
 * Preconditions: None.
 * Postconditions: On non-NULL input, struct_size/version are set and callbacks are NULL.
 * Side effects: Writes to *cbs.
 * Thread-safety / reentrancy guarantees: Reentrant; no global state.
 * Determinism guarantees: Default callbacks are NULL and do not affect determinism.
 */
DSU_API void dsu_callbacks_init(dsu_callbacks_t *cbs);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_CALLBACKS_H_INCLUDED */


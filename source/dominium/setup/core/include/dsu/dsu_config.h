/*
FILE: source/dominium/setup/core/include/dsu/dsu_config.h
MODULE: Dominium Setup
LAYER / SUBSYSTEM: Setup Core configuration policy
RESPONSIBILITY:
  - Owns the versioned configuration struct and determinism/IO policy flags.
  - Does not create contexts or perform IO.
ALLOWED DEPENDENCIES: dsu_types.h.
FORBIDDEN DEPENDENCIES: Platform headers; setup core implementation headers.
THREADING MODEL: Not applicable (data definitions only).
ERROR MODEL: Not applicable (no error handling logic).
DETERMINISM GUARANTEES: DSU_CONFIG_FLAG_DETERMINISTIC defines deterministic execution policy.
VERSIONING / ABI / DATA FORMAT NOTES: struct_size/struct_version gate ABI compatibility; DSU_CONFIG_VERSION is the current schema.
EXTENSION POINTS: Reserved fields and version/size gating support forward-compatible extensions.
*/
/*
FILE: source/dominium/setup/core/include/dsu/dsu_config.h
MODULE: Dominium Setup
PURPOSE: Configuration and determinism policy for Setup Core.
*/
#ifndef DSU_CONFIG_H_INCLUDED
#define DSU_CONFIG_H_INCLUDED

#include "dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Purpose: Current schema/version for dsu_config_t.
 * ABI / layout constraints: Written to dsu_config_t.struct_version.
 */
#define DSU_CONFIG_VERSION 1u

/**
 * Purpose: Enables deterministic execution policy for Setup Core.
 * Side effects: Timestamps are forced to 0 and output ordering is stabilized by core routines.
 * Determinism guarantees: When set, core operations avoid nondeterministic timestamps.
 */
/* Determinism: when set, timestamps are forced to 0 and outputs are stable. */
#define DSU_CONFIG_FLAG_DETERMINISTIC 0x00000001u

/**
 * Purpose: Configuration payload for Setup Core context initialization.
 * ABI / layout constraints:
 *   - struct_size: Size of this struct in bytes.
 *   - struct_version: Must match DSU_CONFIG_VERSION.
 *   - flags: Bitmask of DSU_CONFIG_FLAG_* values.
 *   - max_file_bytes: Maximum bytes permitted for whole-file loads (0 => default policy).
 *   - reserved: Zero-initialize for forward compatibility.
 * Preconditions: Callers should initialize via dsu_config_init before overriding fields.
 */
/* IO policy: maximum bytes permitted for whole-file loads (0 => default). */
typedef struct dsu_config_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;
    dsu_u32 flags;
    dsu_u32 max_file_bytes;
    dsu_u32 reserved[4];
} dsu_config_t;

/**
 * Purpose: Initialize a dsu_config_t to ABI/version defaults.
 * Parameters:
 *   cfg:
 *     - meaning: Destination configuration struct to initialize.
 *     - units: Not applicable.
 *     - ownership / lifetime: Caller-owned; must remain valid for initialization.
 *     - nullability: May be NULL; function is a no-op.
 *     - aliasing rules: May alias other caller state.
 * Preconditions: None.
 * Postconditions: On non-NULL input, struct_size/version and default flags are set.
 * Side effects: Writes to *cfg.
 * Thread-safety / reentrancy guarantees: Reentrant; no global state.
 * Determinism guarantees: Initializes deterministic flag by default.
 */
DSU_API void dsu_config_init(dsu_config_t *cfg);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_CONFIG_H_INCLUDED */


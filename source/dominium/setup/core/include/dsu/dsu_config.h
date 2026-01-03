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

#define DSU_CONFIG_VERSION 1u

/* Determinism: when set, timestamps are forced to 0 and outputs are stable. */
#define DSU_CONFIG_FLAG_DETERMINISTIC 0x00000001u

/* IO policy: maximum bytes permitted for whole-file loads (0 => default). */
typedef struct dsu_config_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;
    dsu_u32 flags;
    dsu_u32 max_file_bytes;
    dsu_u32 reserved[4];
} dsu_config_t;

DSU_API void dsu_config_init(dsu_config_t *cfg);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_CONFIG_H_INCLUDED */


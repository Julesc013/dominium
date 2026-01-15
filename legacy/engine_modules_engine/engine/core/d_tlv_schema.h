/*
FILE: source/domino/core/d_tlv_schema.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_tlv_schema
RESPONSIBILITY: Defines internal contract for `d_tlv_schema`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TLV schema registry (C89). */
#ifndef D_TLV_SCHEMA_H
#define D_TLV_SCHEMA_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u16 d_tlv_schema_id;

/* Callback that validates and optionally upgrades a TLV blob. */
typedef int (*d_tlv_schema_validate_fn)(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded /* may be NULL if no upgrade is required */
);

/* Schema descriptor */
typedef struct d_tlv_schema_desc {
    d_tlv_schema_id          schema_id;
    u16                      version;    /* schema version */
    d_tlv_schema_validate_fn validate_fn;
} d_tlv_schema_desc;

/* Register a TLV schema. Returns 0 on success, non-zero on error. */
int d_tlv_schema_register(const d_tlv_schema_desc *desc);

/* Validate TLV blob against schema+version. Returns 0 on success, non-zero on error. */
int d_tlv_schema_validate(
    d_tlv_schema_id         schema_id,
    u16                     version,
    const struct d_tlv_blob *in,
    struct d_tlv_blob       *out_upgraded /* optional; can be NULL */
);

#ifdef __cplusplus
}
#endif

#endif /* D_TLV_SCHEMA_H */

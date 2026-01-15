/*
FILE: source/domino/res/dg_tlv_schema.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/dg_tlv_schema
RESPONSIBILITY: Defines internal contract for `dg_tlv_schema`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TLV schema descriptors (deterministic plumbing; C89).
 *
 * This module describes TLV payload shapes; it does not impose any gameplay
 * semantics. Validation and canonicalization are separate concerns.
 */
#ifndef DG_TLV_SCHEMA_H
#define DG_TLV_SCHEMA_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dg_tlv_tag;

/* Field descriptor flags */
#define DG_TLV_FIELD_REQUIRED   0x00000001u
#define DG_TLV_FIELD_REPEATABLE 0x00000002u

typedef struct dg_tlv_field_desc {
    dg_tlv_tag tag;
    u32        flags; /* DG_TLV_FIELD_* */
    const char *name; /* optional; not used for determinism */
} dg_tlv_field_desc;

typedef struct dg_tlv_schema_desc {
    dg_schema_id             schema_id;
    u16                      schema_ver;
    const dg_tlv_field_desc *fields;
    u32                      field_count;
    const char              *name; /* optional; not used for determinism */
} dg_tlv_schema_desc;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TLV_SCHEMA_H */


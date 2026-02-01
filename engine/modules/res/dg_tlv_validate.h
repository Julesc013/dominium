/*
FILE: source/domino/res/dg_tlv_validate.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/dg_tlv_validate
RESPONSIBILITY: Defines internal contract for `dg_tlv_validate`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* TLV validation helpers (deterministic plumbing; C89).
 *
 * Validation checks payload well-formedness and (optionally) schema conformance.
 * No platform APIs. No implicit endianness; TLV headers are little-endian.
 */
#ifndef DG_TLV_VALIDATE_H
#define DG_TLV_VALIDATE_H

#include "res/dg_tlv_schema.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Returns 0 if TLV container is well-formed, non-zero otherwise. */
int dg_tlv_validate_well_formed(const unsigned char *tlv, u32 tlv_len);

/* Returns 0 if TLV is well-formed and conforms to schema, non-zero otherwise.
 * If schema is NULL, this is equivalent to dg_tlv_validate_well_formed.
 */
int dg_tlv_validate_against_schema(
    const dg_tlv_schema_desc *schema,
    const unsigned char      *tlv,
    u32                       tlv_len
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TLV_VALIDATE_H */


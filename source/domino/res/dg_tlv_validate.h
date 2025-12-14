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


/* Field packet ABI (deterministic; C89).
 *
 * Field packets are generic frames around TLV payloads. Field addressing and
 * semantics are schema-defined and must remain fixed-point only.
 */
#ifndef DG_PKT_FIELD_H
#define DG_PKT_FIELD_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_pkt_field_sample {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_field_sample;

typedef struct dg_pkt_field_update {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_field_update;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_FIELD_H */


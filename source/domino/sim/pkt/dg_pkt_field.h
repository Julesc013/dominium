/*
FILE: source/domino/sim/pkt/dg_pkt_field.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/dg_pkt_field
RESPONSIBILITY: Defines internal contract for `dg_pkt_field`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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


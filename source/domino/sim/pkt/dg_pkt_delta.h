/* Delta packet ABI (deterministic; C89). */
#ifndef DG_PKT_DELTA_H
#define DG_PKT_DELTA_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_pkt_delta {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_delta;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_DELTA_H */


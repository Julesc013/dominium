/* Intent packet ABI (deterministic; C89). */
#ifndef DG_PKT_INTENT_H
#define DG_PKT_INTENT_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_pkt_intent {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_intent;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_INTENT_H */


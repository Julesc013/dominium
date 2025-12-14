/* Message packet ABI (deterministic; C89). */
#ifndef DG_PKT_MESSAGE_H
#define DG_PKT_MESSAGE_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_pkt_message {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_message;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_MESSAGE_H */


/* Probe packet ABI (deterministic framing; C89).
 * Probes MUST NOT mutate simulation state.
 */
#ifndef DG_PKT_PROBE_H
#define DG_PKT_PROBE_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_pkt_probe {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_probe;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_PROBE_H */


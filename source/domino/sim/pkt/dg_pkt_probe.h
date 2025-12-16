/*
FILE: source/domino/sim/pkt/dg_pkt_probe.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/dg_pkt_probe
RESPONSIBILITY: Implements `dg_pkt_probe`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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


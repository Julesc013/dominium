/* Deterministic packet interfaces (scaffold; C89).
 * See docs/SPEC_PACKETS.md
 */
#ifndef D_SIM_PKT_H
#define D_SIM_PKT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque packet view/handle (representation is TLV-backed). */
typedef struct d_sim_pkt d_sim_pkt;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_SIM_PKT_H */


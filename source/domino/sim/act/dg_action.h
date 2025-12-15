/* Generic action interface (deterministic; C89).
 *
 * Actions are semantic-free typed transformations:
 *   (agent_id, intent, world_state view) -> delta packets
 *
 * Actions MUST NOT mutate authoritative state directly; they only emit deltas.
 */
#ifndef DG_ACTION_H
#define DG_ACTION_H

#include "agent/dg_agent_ids.h"
#include "sim/pkt/dg_pkt_delta.h"
#include "sim/pkt/dg_pkt_intent.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef int (*dg_action_emit_delta_fn)(const dg_pkt_delta *delta, void *emit_ctx);

typedef struct dg_action_vtbl {
    /* Optional deterministic work estimate (units). */
    u32 (*estimate_cost)(dg_agent_id agent_id, const dg_pkt_intent *intent, const void *world_state);

    /* Validate intent against current authoritative state view.
     * Returns D_TRUE if ok, D_FALSE if rejected (reason is optional).
     */
    d_bool (*validate)(dg_agent_id agent_id, const dg_pkt_intent *intent, const void *world_state, u32 *out_reason);

    /* Emit delta packets for a validated intent. Returns 0 on success. */
    int (*apply)(
        dg_agent_id              agent_id,
        const dg_pkt_intent     *intent,
        const void              *world_state,
        dg_action_emit_delta_fn  emit_delta,
        void                    *emit_ctx
    );
} dg_action_vtbl;

/* Helper: estimate cost or return a default. */
u32 dg_action_estimate_cost(
    const dg_action_vtbl *vtbl,
    dg_agent_id           agent_id,
    const dg_pkt_intent  *intent,
    const void           *world_state,
    u32                   default_cost
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_ACTION_H */


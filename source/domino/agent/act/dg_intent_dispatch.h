/* Intent dispatch (deterministic; C89).
 *
 * Intent dispatch produces action requests in canonical order.
 * Action application (intent->delta) is handled by the action system.
 */
#ifndef DG_INTENT_DISPATCH_H
#define DG_INTENT_DISPATCH_H

#include "agent/act/dg_intent_buffer.h"
#include "sim/act/dg_action_registry.h"
#include "sim/act/dg_delta_buffer.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_action_request {
    dg_tick     tick;
    dg_agent_id agent_id;
    dg_type_id  intent_type_id;
    u32         intent_seq;

    /* Default routing: action type id equals intent type id. */
    dg_type_id  action_type_id;

    /* Index into the canonicalized dg_intent_buffer. */
    u32         intent_index;
} dg_action_request;

typedef struct dg_action_request_buffer {
    dg_tick tick;

    dg_action_request *reqs;
    u32                count;
    u32                capacity;

    d_bool owns_storage;
    u32    probe_refused;
} dg_action_request_buffer;

void dg_action_request_buffer_init(dg_action_request_buffer *b);
void dg_action_request_buffer_free(dg_action_request_buffer *b);
int  dg_action_request_buffer_reserve(dg_action_request_buffer *b, u32 max_reqs);
void dg_action_request_buffer_begin_tick(dg_action_request_buffer *b, dg_tick tick);

u32 dg_action_request_buffer_count(const dg_action_request_buffer *b);
const dg_action_request *dg_action_request_buffer_at(const dg_action_request_buffer *b, u32 index);
u32 dg_action_request_buffer_probe_refused(const dg_action_request_buffer *b);

/* Build action requests from an already-canonicalized intent buffer.
 * Returns 0 on success, non-zero if refused/invalid.
 */
int dg_intent_dispatch_build_requests(
    const dg_intent_buffer        *intents,
    dg_action_request_buffer      *out_reqs
);

/* Apply actions for intents and emit delta packets into out_deltas.
 * - intents MUST be canonicalized before dispatch.
 * - out_deltas MUST have begin_tick() called for intents->tick.
 * - phase is used for the delta commit ordering key (dg_order_key).
 */
int dg_intent_dispatch_to_deltas(
    const dg_intent_buffer  *intents,
    const dg_action_registry *actions,
    const void              *world_state,
    dg_delta_buffer         *out_deltas,
    u16                      phase
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_INTENT_DISPATCH_H */

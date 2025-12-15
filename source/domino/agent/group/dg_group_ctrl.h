/* Group controller interface (deterministic; C89).
 *
 * Group controllers are semantic-free decision layers operating on a stable
 * member list and aggregated observations, emitting group intents.
 */
#ifndef DG_GROUP_CTRL_H
#define DG_GROUP_CTRL_H

#include "agent/group/dg_group.h"
#include "agent/mind/dg_mind.h" /* dg_intent_emit_fn + prng/budget helpers */

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_group_ctrl_desc dg_group_ctrl_desc;

typedef struct dg_group_ctrl_vtbl {
    int (*step)(
        dg_group_id               group_id,
        const dg_group           *group,
        const dg_observation_buffer *observations,
        void                     *internal_state,
        dg_tick                   tick,
        u32                       budget_units,
        u32                      *io_seq,
        dg_intent_emit_fn         emit,
        void                     *emit_ctx
    );

    u32 (*estimate_cost)(
        dg_group_id                group_id,
        const dg_group            *group,
        const dg_observation_buffer *observations,
        const void                *internal_state
    );

    int (*serialize_state)(const void *state, unsigned char *out, u32 out_cap, u32 *out_len);
} dg_group_ctrl_vtbl;

struct dg_group_ctrl_desc {
    dg_type_id         ctrl_id;
    dg_group_ctrl_vtbl vtbl;
    u32                stride;               /* cadence decimation */
    u32                internal_state_bytes; /* optional */
    const char        *name;                /* optional */
};

d_bool dg_group_ctrl_should_run(const dg_group_ctrl_desc *c, dg_tick tick, dg_group_id group_id);
u32 dg_group_ctrl_estimate_cost(
    const dg_group_ctrl_desc       *c,
    dg_group_id                     group_id,
    const dg_group                 *group,
    const dg_observation_buffer    *observations,
    const void                     *internal_state,
    u32                             default_cost
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GROUP_CTRL_H */


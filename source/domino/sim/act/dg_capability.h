/* Generic capability sets (deterministic; C89).
 *
 * Capabilities declare what actions an agent is allowed to request/perform.
 * This module is semantic-free; it only stores/queries stable action type IDs.
 */
#ifndef DG_CAPABILITY_H
#define DG_CAPABILITY_H

#include "agent/dg_agent_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_capability_set {
    dg_type_id *action_type_ids; /* sorted ascending */
    u32         count;
    u32         capacity;
} dg_capability_set;

void dg_capability_set_init(dg_capability_set *s);
void dg_capability_set_free(dg_capability_set *s);

/* Allocate bounded storage for action ids. */
int dg_capability_set_reserve(dg_capability_set *s, u32 capacity);

/* Add an allowed action id (keeps sorted unique order). */
int dg_capability_set_add(dg_capability_set *s, dg_type_id action_type_id);

d_bool dg_capability_set_contains(const dg_capability_set *s, dg_type_id action_type_id);
u32 dg_capability_set_count(const dg_capability_set *s);
dg_type_id dg_capability_set_at(const dg_capability_set *s, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_CAPABILITY_H */


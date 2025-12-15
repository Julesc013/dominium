/* Group membership container (deterministic; C89).
 *
 * Groups are semantic-free sets of agent_ids with stable ordering.
 * Used for herds/flocks/squads/swarms and non-physical controllers.
 */
#ifndef DG_GROUP_H
#define DG_GROUP_H

#include "agent/dg_agent_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_group {
    dg_group_id group_id;

    dg_agent_id *members;  /* sorted ascending */
    u32          count;
    u32          capacity;
    d_bool       owns_storage;

    u32 probe_refused_members;
} dg_group;

void dg_group_init(dg_group *g);
void dg_group_free(dg_group *g);
int dg_group_reserve(dg_group *g, u32 capacity);

void dg_group_set_id(dg_group *g, dg_group_id group_id);

/* Member operations (deterministic stable ordering by agent_id). */
int dg_group_add_member(dg_group *g, dg_agent_id agent_id);
int dg_group_remove_member(dg_group *g, dg_agent_id agent_id);

d_bool dg_group_contains(const dg_group *g, dg_agent_id agent_id);
u32 dg_group_member_count(const dg_group *g);
dg_agent_id dg_group_member_at(const dg_group *g, u32 index);

u32 dg_group_probe_refused_members(const dg_group *g);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GROUP_H */


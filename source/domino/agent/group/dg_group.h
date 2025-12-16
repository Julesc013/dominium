/*
FILE: source/domino/agent/group/dg_group.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/group/dg_group
RESPONSIBILITY: Implements `dg_group`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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


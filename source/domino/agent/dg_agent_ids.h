/* Agent/actor stable identifier types (deterministic; C89).
 *
 * Agents are semantic-free actors whose behavior is expressed as:
 *   sensors -> observations -> minds/controllers -> intents -> actions -> deltas
 *
 * IDs here are stable numeric identifiers suitable for canonical ordering.
 */
#ifndef DG_AGENT_IDS_H
#define DG_AGENT_IDS_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dg_entity_id dg_agent_id;

typedef u64 dg_archetype_id; /* content-defined */
typedef u64 dg_faction_id;   /* optional; 0 means none */
typedef u64 dg_group_id;     /* optional; 0 means none */

/* Stable component instance id within a kind's SoA store. 0 means none. */
typedef u32 dg_comp_id;

#define DG_AGENT_ID_NONE ((dg_agent_id)0u)
#define DG_ARCHETYPE_ID_NONE ((dg_archetype_id)0u)
#define DG_FACTION_ID_NONE ((dg_faction_id)0u)
#define DG_GROUP_ID_NONE ((dg_group_id)0u)
#define DG_COMP_ID_NONE ((dg_comp_id)0u)

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_AGENT_IDS_H */


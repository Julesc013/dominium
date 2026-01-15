/*
FILE: source/domino/agent/dg_agent.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/dg_agent
RESPONSIBILITY: Defines internal contract for `dg_agent`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Agent core model (deterministic; C89).
 *
 * Agents are composition-only data records with stable IDs and component
 * attachments (component data is stored in SoA via dg_agent_comp_registry).
 *
 * There is no semantic gameplay logic here.
 */
#ifndef DG_AGENT_H
#define DG_AGENT_H

#include "agent/dg_agent_comp.h"
#include "sim/lod/dg_rep.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DG_AGENT_MAX_COMPONENTS 32u

typedef struct dg_agent_comp_ref {
    dg_type_id kind_id;
    dg_comp_id comp_id;
} dg_agent_comp_ref;

typedef struct dg_agent_record {
    dg_agent_id     agent_id;     /* stable */
    dg_archetype_id archetype_id; /* content-defined */
    dg_faction_id   faction_id;   /* optional; 0 means none */

    dg_domain_id    domain_id;
    dg_chunk_id     chunk_id;

    dg_rep_state    lod;          /* deterministic representation state */

    dg_agent_comp_ref comps[DG_AGENT_MAX_COMPONENTS];
    u32               comp_count;
} dg_agent_record;

typedef struct dg_agent_db {
    dg_agent_record *agents;   /* sorted by agent_id */
    u32              count;
    u32              capacity;

    dg_agent_id      next_agent_id; /* for minting ids when init.agent_id==0 */

    dg_agent_comp_registry comp_reg;

    u32 probe_refused_agents;
    u32 probe_refused_components;
} dg_agent_db;

void dg_agent_db_init(dg_agent_db *db);
void dg_agent_db_free(dg_agent_db *db);

int dg_agent_db_reserve(dg_agent_db *db, u32 agent_capacity, u32 comp_kind_capacity);

/* Register component kinds (allocates bounded SoA storage per kind). */
int dg_agent_db_register_component_kind(dg_agent_db *db, const dg_agent_comp_kind_desc *desc);

/* Add/remove agents. Returns 0 on success. */
int dg_agent_db_add(dg_agent_db *db, const dg_agent_record *init, dg_agent_id *out_agent_id);
int dg_agent_db_remove(dg_agent_db *db, dg_agent_id agent_id);

u32 dg_agent_db_count(const dg_agent_db *db);
const dg_agent_record *dg_agent_db_at(const dg_agent_db *db, u32 index);
dg_agent_record *dg_agent_db_find_mut(dg_agent_db *db, dg_agent_id agent_id);
const dg_agent_record *dg_agent_db_find(const dg_agent_db *db, dg_agent_id agent_id);

/* Component attachment helpers (1 component per kind per agent). */
int dg_agent_db_attach_component(dg_agent_db *db, dg_agent_id agent_id, dg_type_id kind_id, dg_comp_id *out_comp_id);
int dg_agent_db_detach_component(dg_agent_db *db, dg_agent_id agent_id, dg_type_id kind_id);
dg_comp_id dg_agent_db_component_of(const dg_agent_db *db, dg_agent_id agent_id, dg_type_id kind_id);

u32 dg_agent_db_probe_refused_agents(const dg_agent_db *db);
u32 dg_agent_db_probe_refused_components(const dg_agent_db *db);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_AGENT_H */


/* Agent component registry and storage (deterministic; C89).
 *
 * Components are pure data; there is no behavior in this module.
 *
 * Requirements:
 * - Composition only (no inheritance).
 * - Storage is SoA per component kind.
 * - Deterministic iteration order (chunk-aligned ordering).
 * - Bounded storage: all arrays must be reserved.
 */
#ifndef DG_AGENT_COMP_H
#define DG_AGENT_COMP_H

#include "agent/dg_agent_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_agent_comp_kind_desc {
    dg_type_id   kind_id;   /* stable taxonomy id for the component kind */
    u32          elem_size; /* bytes per component instance (0 allowed for tag components) */
    u32          capacity;  /* max instances for this kind (bounded) */
    const char  *name;      /* optional; not used for determinism */
} dg_agent_comp_kind_desc;

typedef struct dg_agent_comp_kind {
    dg_agent_comp_kind_desc desc;

    unsigned char *data; /* elem_size * capacity; may be NULL if elem_size==0 or capacity==0 */

    dg_agent_id  *owner_agent; /* capacity; 0 means free slot */
    dg_domain_id *domain_id;   /* capacity; cached for deterministic ordering */
    dg_chunk_id  *chunk_id;    /* capacity; cached for deterministic ordering */

    dg_comp_id   *active_ids;  /* capacity; sorted by (domain_id, chunk_id, owner_agent, comp_id) */
    u32           active_count;

    dg_comp_id   *free_ids;    /* capacity; stack of free ids (deterministic) */
    u32           free_count;

    u32           probe_refused_alloc;
} dg_agent_comp_kind;

typedef struct dg_agent_comp_registry {
    dg_agent_comp_kind *kinds;    /* sorted by kind_id */
    u32                 count;
    u32                 capacity;
} dg_agent_comp_registry;

void dg_agent_comp_registry_init(dg_agent_comp_registry *reg);
void dg_agent_comp_registry_free(dg_agent_comp_registry *reg);

/* Reserve number of component kinds (entries). Storage per kind is reserved by register_kind(). */
int dg_agent_comp_registry_reserve(dg_agent_comp_registry *reg, u32 kind_capacity);

/* Register a component kind and allocate bounded storage for it. Returns 0 on success. */
int dg_agent_comp_registry_register_kind(dg_agent_comp_registry *reg, const dg_agent_comp_kind_desc *desc);

u32 dg_agent_comp_registry_count(const dg_agent_comp_registry *reg);
const dg_agent_comp_kind *dg_agent_comp_registry_at(const dg_agent_comp_registry *reg, u32 index);
dg_agent_comp_kind *dg_agent_comp_registry_find_mut(dg_agent_comp_registry *reg, dg_type_id kind_id);
const dg_agent_comp_kind *dg_agent_comp_registry_find(const dg_agent_comp_registry *reg, dg_type_id kind_id);

/* Allocate/free component instances. Returns 0 on failure. */
dg_comp_id dg_agent_comp_alloc(
    dg_agent_comp_registry *reg,
    dg_type_id              kind_id,
    dg_agent_id             owner_agent,
    dg_domain_id            domain_id,
    dg_chunk_id             chunk_id
);

int dg_agent_comp_free(dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id);

/* Data accessors (returns NULL for invalid ids or tag components). */
void *dg_agent_comp_data(dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id);
const void *dg_agent_comp_data_const(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id);

/* Owner + location metadata. Returns 0 values if invalid. */
dg_agent_id dg_agent_comp_owner(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id);
dg_domain_id dg_agent_comp_domain(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id);
dg_chunk_id dg_agent_comp_chunk(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id);

/* Deterministic iteration over active components of a kind. */
u32 dg_agent_comp_active_count(const dg_agent_comp_registry *reg, dg_type_id kind_id);
dg_comp_id dg_agent_comp_active_at(const dg_agent_comp_registry *reg, dg_type_id kind_id, u32 index);

u32 dg_agent_comp_probe_refused_alloc(const dg_agent_comp_registry *reg, dg_type_id kind_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_AGENT_COMP_H */


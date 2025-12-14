/* Delta handler registry (deterministic; C89).
 *
 * Delta handlers are registered by delta type id and iterated in canonical
 * ascending type-id order.
 */
#ifndef DG_DELTA_REGISTRY_H
#define DG_DELTA_REGISTRY_H

#include "sim/pkt/dg_pkt_delta.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_delta_handler_vtbl {
    /* Apply MUST be deterministic and MUST NOT perform IO. */
    void (*apply)(void *world, const dg_pkt_delta *delta);

    /* Optional cost estimate for budgeting (work units). */
    u32 (*estimate_cost)(const dg_pkt_delta *delta);
} dg_delta_handler_vtbl;

typedef struct dg_delta_registry_entry {
    dg_type_id             type_id;
    dg_delta_handler_vtbl  vtbl;
    const char            *name;        /* optional; not used for determinism */
    u32                    insert_index; /* stable tie-break/debug */
} dg_delta_registry_entry;

typedef struct dg_delta_registry {
    dg_delta_registry_entry *entries;
    u32                      count;
    u32                      capacity;
    u32                      next_insert_index;
} dg_delta_registry;

void dg_delta_registry_init(dg_delta_registry *reg);
void dg_delta_registry_free(dg_delta_registry *reg);
int dg_delta_registry_reserve(dg_delta_registry *reg, u32 capacity);

/* Register a handler. Returns 0 on success. */
int dg_delta_registry_add(
    dg_delta_registry          *reg,
    dg_type_id                  type_id,
    const dg_delta_handler_vtbl *vtbl,
    const char                 *name
);

u32 dg_delta_registry_count(const dg_delta_registry *reg);
const dg_delta_registry_entry *dg_delta_registry_at(const dg_delta_registry *reg, u32 index);
const dg_delta_registry_entry *dg_delta_registry_find(const dg_delta_registry *reg, dg_type_id type_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DELTA_REGISTRY_H */


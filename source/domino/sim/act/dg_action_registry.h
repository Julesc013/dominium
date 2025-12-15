/* Action registry (deterministic; C89).
 *
 * Actions are registered by action type id and iterated/queried in canonical
 * ascending type-id order (no hash-map iteration).
 */
#ifndef DG_ACTION_REGISTRY_H
#define DG_ACTION_REGISTRY_H

#include "sim/act/dg_action.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_action_registry_entry {
    dg_type_id      type_id; /* action type id (usually equals intent type id) */
    dg_action_vtbl  vtbl;
    const char     *name;        /* optional; not used for determinism */
    u32             insert_index; /* stable tie-break/debug */
} dg_action_registry_entry;

typedef struct dg_action_registry {
    dg_action_registry_entry *entries; /* sorted by type_id */
    u32                       count;
    u32                       capacity;
    u32                       next_insert_index;
} dg_action_registry;

void dg_action_registry_init(dg_action_registry *reg);
void dg_action_registry_free(dg_action_registry *reg);
int dg_action_registry_reserve(dg_action_registry *reg, u32 capacity);

/* Register an action handler. Returns 0 on success. */
int dg_action_registry_add(
    dg_action_registry     *reg,
    dg_type_id              type_id,
    const dg_action_vtbl   *vtbl,
    const char             *name
);

u32 dg_action_registry_count(const dg_action_registry *reg);
const dg_action_registry_entry *dg_action_registry_at(const dg_action_registry *reg, u32 index);
const dg_action_registry_entry *dg_action_registry_find(const dg_action_registry *reg, dg_type_id type_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_ACTION_REGISTRY_H */


/* Generic dynamic registry (C89). */
#ifndef D_REGISTRY_H
#define D_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_registry_entry {
    u32   id;    /* numeric ID assigned by registry */
    void *ptr;   /* pointer to stored object; registry does not own the object */
} d_registry_entry;

typedef struct d_registry {
    d_registry_entry *entries;
    u32               capacity;
    u32               count;
    u32               next_id;   /* next ID to assign; must never be 0 */
} d_registry;

/* Initialize an empty registry with external storage. */
void d_registry_init(
    d_registry        *reg,
    d_registry_entry  *storage,
    u32                capacity,
    u32                first_id
);

/* Add an entry; returns assigned ID or 0 on failure. */
u32 d_registry_add(d_registry *reg, void *ptr);

/* Get pointer by ID, or NULL if not found. */
void *d_registry_get(const d_registry *reg, u32 id);

/* Optional: unwrap entries by index; returns NULL if out-of-range. */
d_registry_entry *d_registry_get_by_index(d_registry *reg, u32 index);

#ifdef __cplusplus
}
#endif

#endif /* D_REGISTRY_H */

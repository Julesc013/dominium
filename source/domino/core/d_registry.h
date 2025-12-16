/*
FILE: source/domino/core/d_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_registry
RESPONSIBILITY: Implements `d_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

/* Add an entry with an explicit id; returns assigned id or 0 on failure. */
u32 d_registry_add_with_id(d_registry *reg, u32 id, void *ptr);

/* Get pointer by ID, or NULL if not found. */
void *d_registry_get(const d_registry *reg, u32 id);

/* Optional: unwrap entries by index; returns NULL if out-of-range. */
d_registry_entry *d_registry_get_by_index(d_registry *reg, u32 index);

#ifdef __cplusplus
}
#endif

#endif /* D_REGISTRY_H */

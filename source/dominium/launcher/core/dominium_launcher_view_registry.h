/*
FILE: source/dominium/launcher/core/dominium_launcher_view_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/dominium_launcher_view_registry
RESPONSIBILITY: Implements `dominium_launcher_view_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_VIEW_REGISTRY_H
#define DOMINIUM_LAUNCHER_VIEW_REGISTRY_H

#include "dominium_launcher_view.h"

typedef struct dominium_launcher_view_registry dominium_launcher_view_registry;

/* Creation/destruction */
dominium_launcher_view_registry* dominium_launcher_view_registry_create(void);
void dominium_launcher_view_registry_destroy(dominium_launcher_view_registry* reg);

/* Register a view: copy desc inside registry; returns 0 if OK, non-zero on error */
int dominium_launcher_view_register(dominium_launcher_view_registry* reg,
                                    const dominium_launcher_view_desc* desc);

/* Get an array of all views sorted by (priority, id). The array pointer is owned by the registry. */
int dominium_launcher_view_list(const dominium_launcher_view_registry* reg,
                                const dominium_launcher_view_desc** out_array,
                                unsigned int* out_count);

/* Find by id; returns NULL if not found */
const dominium_launcher_view_desc* dominium_launcher_view_find(
    const dominium_launcher_view_registry* reg,
    const char* id);

#endif /* DOMINIUM_LAUNCHER_VIEW_REGISTRY_H */

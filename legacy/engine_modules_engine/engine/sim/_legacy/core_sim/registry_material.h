/*
FILE: source/domino/sim/_legacy/core_sim/registry_material.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/registry_material
RESPONSIBILITY: Defines internal contract for `registry_material`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_REGISTRY_MATERIAL_H
#define DOM_REGISTRY_MATERIAL_H

#include "core_types.h"
#include "core_fixed.h"
#include "core_ids.h"

typedef u16 MatId;

typedef struct MaterialDesc {
    MatId        id;
    const char  *name;
    fix32        density;
    fix32        hardness;
    fix32        melting_point;
    fix32        boiling_point;
} MaterialDesc;

typedef struct MaterialRegistry {
    MaterialDesc *materials;
    u16           count;
    u16           capacity;
} MaterialRegistry;

void material_registry_init(MaterialRegistry *reg, u16 capacity);
void material_registry_free(MaterialRegistry *reg);
MatId material_register(MaterialRegistry *reg, const MaterialDesc *desc);
const MaterialDesc *material_get(const MaterialRegistry *reg, MatId id);

#endif /* DOM_REGISTRY_MATERIAL_H */

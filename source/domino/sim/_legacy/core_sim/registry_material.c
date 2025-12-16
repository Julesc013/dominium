/*
FILE: source/domino/sim/_legacy/core_sim/registry_material.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/registry_material
RESPONSIBILITY: Implements `registry_material`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "registry_material.h"

#include <stdlib.h>
#include <string.h>

void material_registry_init(MaterialRegistry *reg, u16 capacity)
{
    if (!reg) return;
    memset(reg, 0, sizeof(*reg));
    if (capacity > 0) {
        reg->materials = (MaterialDesc *)malloc(sizeof(MaterialDesc) * capacity);
        if (reg->materials) {
            reg->capacity = capacity;
        }
    }
}

void material_registry_free(MaterialRegistry *reg)
{
    if (!reg) return;
    if (reg->materials) {
        free(reg->materials);
        reg->materials = NULL;
    }
    reg->capacity = 0;
    reg->count = 0;
}

MatId material_register(MaterialRegistry *reg, const MaterialDesc *desc)
{
    MaterialDesc *slot;
    if (!reg || !desc) return 0;
    if (reg->count >= reg->capacity) {
        u16 new_cap = (reg->capacity == 0) ? 4U : (u16)(reg->capacity * 2U);
        MaterialDesc *new_arr = (MaterialDesc *)realloc(reg->materials, sizeof(MaterialDesc) * new_cap);
        if (!new_arr) {
            return 0;
        }
        reg->materials = new_arr;
        reg->capacity = new_cap;
    }
    slot = &reg->materials[reg->count];
    *slot = *desc;
    slot->id = reg->count;
    reg->count++;
    return slot->id;
}

const MaterialDesc *material_get(const MaterialRegistry *reg, MatId id)
{
    if (!reg) return NULL;
    if (id >= reg->count) return NULL;
    return &reg->materials[id];
}

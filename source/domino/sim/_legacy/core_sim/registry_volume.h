/*
FILE: source/domino/sim/_legacy/core_sim/registry_volume.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/registry_volume
RESPONSIBILITY: Implements `registry_volume`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_REGISTRY_VOLUME_H
#define DOM_REGISTRY_VOLUME_H

#include "core_types.h"
#include "core_ids.h"

typedef struct VolumeDesc {
    VolumeId    id;
    const char *name;
} VolumeDesc;

typedef struct VolumeRegistry {
    VolumeDesc *volumes;
    u16         count;
    u16         capacity;
} VolumeRegistry;

void volume_registry_init(VolumeRegistry *reg, u16 capacity);
void volume_registry_free(VolumeRegistry *reg);
VolumeId volume_register(VolumeRegistry *reg, const VolumeDesc *desc);
const VolumeDesc *volume_get(const VolumeRegistry *reg, VolumeId id);

#endif /* DOM_REGISTRY_VOLUME_H */

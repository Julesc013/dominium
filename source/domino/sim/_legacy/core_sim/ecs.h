/*
FILE: source/domino/sim/_legacy/core_sim/ecs.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/ecs
RESPONSIBILITY: Defines internal contract for `ecs`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_ECS_H
#define DOM_ECS_H

#include "core_types.h"
#include "core_ids.h"
#include "world_addr.h"

typedef struct Entity {
    EntityId id;
    SimPos   pos;
} Entity;

typedef struct ECS {
    Entity   *entities;
    u32       count;
    u32       capacity;
    EntityId  next_id;
} ECS;

void ecs_init(ECS *ecs, u32 initial_capacity);
void ecs_free(ECS *ecs);

EntityId ecs_create(ECS *ecs, const SimPos *pos);
b32      ecs_destroy(ECS *ecs, EntityId id);
Entity   *ecs_get(ECS *ecs, EntityId id);

void ecs_tick(ECS *ecs, fix32 dt);

#endif /* DOM_ECS_H */

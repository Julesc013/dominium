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

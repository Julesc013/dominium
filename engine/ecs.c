#include "ecs.h"

#include <stdlib.h>
#include <string.h>

static b32 ensure_capacity(ECS *ecs, u32 needed)
{
    u32 new_cap;
    Entity *new_entities;
    if (ecs->capacity >= needed) {
        return TRUE;
    }
    new_cap = (ecs->capacity == 0) ? 8U : (ecs->capacity * 2U);
    if (new_cap < needed) {
        new_cap = needed;
    }
    new_entities = (Entity *)realloc(ecs->entities, sizeof(Entity) * new_cap);
    if (!new_entities) {
        return FALSE;
    }
    ecs->entities = new_entities;
    ecs->capacity = new_cap;
    return TRUE;
}

void ecs_init(ECS *ecs, u32 initial_capacity)
{
    if (!ecs) return;
    memset(ecs, 0, sizeof(*ecs));
    ecs->next_id = 1;
    if (initial_capacity > 0) {
        ecs->entities = (Entity *)malloc(sizeof(Entity) * initial_capacity);
        if (ecs->entities) {
            ecs->capacity = initial_capacity;
        }
    }
}

void ecs_free(ECS *ecs)
{
    if (!ecs) return;
    if (ecs->entities) {
        free(ecs->entities);
        ecs->entities = NULL;
    }
    ecs->capacity = 0;
    ecs->count = 0;
    ecs->next_id = 1;
}

EntityId ecs_create(ECS *ecs, const SimPos *pos)
{
    Entity *ent;
    if (!ecs) return 0;
    if (!ensure_capacity(ecs, ecs->count + 1U)) {
        return 0;
    }
    ent = &ecs->entities[ecs->count++];
    ent->id = ecs->next_id++;
    if (pos) {
        ent->pos = *pos;
    } else {
        memset(&ent->pos, 0, sizeof(ent->pos));
    }
    return ent->id;
}

b32 ecs_destroy(ECS *ecs, EntityId id)
{
    u32 i;
    if (!ecs) return FALSE;
    for (i = 0; i < ecs->count; ++i) {
        if (ecs->entities[i].id == id) {
            u32 tail = ecs->count - 1U;
            if (i != tail) {
                memmove(&ecs->entities[i], &ecs->entities[i + 1], sizeof(Entity) * (tail - i));
            }
            ecs->count--;
            return TRUE;
        }
    }
    return FALSE;
}

Entity *ecs_get(ECS *ecs, EntityId id)
{
    u32 i;
    if (!ecs) return NULL;
    for (i = 0; i < ecs->count; ++i) {
        if (ecs->entities[i].id == id) {
            return &ecs->entities[i];
        }
    }
    return NULL;
}

void ecs_tick(ECS *ecs, fix32 dt)
{
    u32 i;
    (void)dt;
    if (!ecs) return;
    for (i = 0; i < ecs->count; ++i) {
        simpos_normalise(&ecs->entities[i].pos);
    }
}

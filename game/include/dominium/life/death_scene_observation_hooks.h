/*
FILE: include/dominium/life/death_scene_observation_hooks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines death scene observation hooks for epistemic systems.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Hook ordering is deterministic.
*/
#ifndef DOMINIUM_LIFE_DEATH_SCENE_OBSERVATION_H
#define DOMINIUM_LIFE_DEATH_SCENE_OBSERVATION_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_death_scene_observation {
    u64 death_event_id;
    u64 remains_id;
    u64 body_id;
    u64 person_id;
    u32 cause_code;
    dom_act_time_t act_time;
    u64 location_ref;
} life_death_scene_observation;

typedef struct life_death_scene_observation_log {
    life_death_scene_observation* entries;
    u32 count;
    u32 capacity;
} life_death_scene_observation_log;

typedef void (*life_death_scene_observation_cb)(void* user,
                                                const life_death_scene_observation* observation);

typedef struct life_death_scene_observation_hooks {
    life_death_scene_observation_log* log;
    life_death_scene_observation_cb cb;
    void* user;
} life_death_scene_observation_hooks;

void life_death_scene_observation_log_init(life_death_scene_observation_log* log,
                                           life_death_scene_observation* storage,
                                           u32 capacity);
int life_death_scene_observation_append(life_death_scene_observation_log* log,
                                        const life_death_scene_observation* observation);

void life_death_scene_observation_hooks_init(life_death_scene_observation_hooks* hooks,
                                             life_death_scene_observation_log* log,
                                             life_death_scene_observation_cb cb,
                                             void* user);
void life_death_scene_observation_emit(life_death_scene_observation_hooks* hooks,
                                       const life_death_scene_observation* observation);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_DEATH_SCENE_OBSERVATION_H */

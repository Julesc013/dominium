/*
FILE: game/core/life/death_scene_observation_hooks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements death scene observation hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Hook ordering is deterministic.
*/
#include "dominium/life/death_scene_observation_hooks.h"

#include <string.h>

void life_death_scene_observation_log_init(life_death_scene_observation_log* log,
                                           life_death_scene_observation* storage,
                                           u32 capacity)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_death_scene_observation) * (size_t)capacity);
    }
}

int life_death_scene_observation_append(life_death_scene_observation_log* log,
                                        const life_death_scene_observation* observation)
{
    if (!log || !observation || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    log->entries[log->count++] = *observation;
    return 0;
}

void life_death_scene_observation_hooks_init(life_death_scene_observation_hooks* hooks,
                                             life_death_scene_observation_log* log,
                                             life_death_scene_observation_cb cb,
                                             void* user)
{
    if (!hooks) {
        return;
    }
    hooks->log = log;
    hooks->cb = cb;
    hooks->user = user;
}

void life_death_scene_observation_emit(life_death_scene_observation_hooks* hooks,
                                       const life_death_scene_observation* observation)
{
    if (!hooks || !observation) {
        return;
    }
    if (hooks->log) {
        (void)life_death_scene_observation_append(hooks->log, observation);
    }
    if (hooks->cb) {
        hooks->cb(hooks->user, observation);
    }
}

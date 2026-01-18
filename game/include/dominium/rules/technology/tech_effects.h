/*
FILE: include/dominium/rules/technology/tech_effects.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / technology
RESPONSIBILITY: Defines technology effects and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Effect ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_TECH_EFFECTS_H
#define DOMINIUM_RULES_TECH_EFFECTS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum tech_effect_type {
    TECH_EFFECT_UNLOCK_RECIPE = 1,
    TECH_EFFECT_UNLOCK_POLICY = 2,
    TECH_EFFECT_UNLOCK_RESEARCH = 3
} tech_effect_type;

typedef struct tech_effect {
    u64 tech_id;
    tech_effect_type type;
    u64 target_id;
    u32 flags;
} tech_effect;

typedef struct tech_effect_registry {
    tech_effect* effects;
    u32 count;
    u32 capacity;
} tech_effect_registry;

void tech_effect_registry_init(tech_effect_registry* reg,
                               tech_effect* storage,
                               u32 capacity);
int tech_effect_register(tech_effect_registry* reg,
                         u64 tech_id,
                         tech_effect_type type,
                         u64 target_id,
                         u32 flags);
tech_effect* tech_effect_find(tech_effect_registry* reg,
                              u64 tech_id,
                              u64 target_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_TECH_EFFECTS_H */

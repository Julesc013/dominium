/*
Ability package registry (LIFE1).
*/
#ifndef DOMINIUM_LIFE_ABILITY_PACKAGES_H
#define DOMINIUM_LIFE_ABILITY_PACKAGES_H

#include "dominium/life/life_types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    LIFE_BOOL_FALSE = 0,
    LIFE_BOOL_TRUE = 1,
    LIFE_BOOL_INHERIT = 2
};

enum {
    LIFE_UI_CAP_EPISTEMIC_PRIV = 1u << 0,
    LIFE_UI_CAP_DEBUG_PRIV = 1u << 1
};

enum {
    LIFE_GAME_CAP_CREATIVE_TOOLS = 1u << 0,
    LIFE_GAME_CAP_SPECTATOR = 1u << 1
};

#define LIFE_POLICY_ID_INHERIT 0xFFFFFFFFu

typedef struct life_ability_package {
    u32 package_id;
    u32 parent_id;
    u64 ui_caps;
    u64 game_caps;
    u32 allowed_policy_mask;
    u8 death_end_control;
    u8 transfer_allowed;
    u8 spectator_on_refusal;
    u32 default_policy_id;
} life_ability_package;

typedef struct life_ability_registry {
    life_ability_package* packages;
    u32 count;
    u32 capacity;
} life_ability_registry;

void life_ability_registry_init(life_ability_registry* reg,
                                life_ability_package* storage,
                                u32 capacity);
int life_ability_registry_register(life_ability_registry* reg,
                                   const life_ability_package* pkg);
const life_ability_package* life_ability_registry_find(const life_ability_registry* reg,
                                                       u32 package_id);
int life_ability_registry_resolve(const life_ability_registry* reg,
                                  u32 package_id,
                                  life_ability_package* out_pkg);
int life_ability_register_presets(life_ability_registry* reg);
int life_ability_package_allows_policy(const life_ability_package* pkg,
                                       life_policy_type type);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_ABILITY_PACKAGES_H */

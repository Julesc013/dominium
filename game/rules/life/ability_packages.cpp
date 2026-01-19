/*
FILE: game/core/life/ability_packages.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements ability package registry and inheritance resolution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resolution order and inheritance must be deterministic.
*/
#include "dominium/life/ability_packages.h"

#include <string.h>

static int life_ability_merge(const life_ability_package* parent,
                              life_ability_package* child)
{
    if (!parent || !child) {
        return -1;
    }
    child->ui_caps |= parent->ui_caps;
    child->game_caps |= parent->game_caps;
    child->allowed_policy_mask |= parent->allowed_policy_mask;

    if (child->death_end_control == LIFE_BOOL_INHERIT) {
        child->death_end_control = parent->death_end_control;
    }
    if (child->transfer_allowed == LIFE_BOOL_INHERIT) {
        child->transfer_allowed = parent->transfer_allowed;
    }
    if (child->spectator_on_refusal == LIFE_BOOL_INHERIT) {
        child->spectator_on_refusal = parent->spectator_on_refusal;
    }
    if (child->default_policy_id == LIFE_POLICY_ID_INHERIT) {
        child->default_policy_id = parent->default_policy_id;
    }
    return 0;
}

void life_ability_registry_init(life_ability_registry* reg,
                                life_ability_package* storage,
                                u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->packages = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_ability_package) * (size_t)capacity);
    }
}

int life_ability_registry_register(life_ability_registry* reg,
                                   const life_ability_package* pkg)
{
    u32 i;
    if (!reg || !pkg) {
        return -1;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->packages[i].package_id == pkg->package_id) {
            return -2;
        }
    }
    if (reg->count >= reg->capacity || !reg->packages) {
        return -3;
    }
    reg->packages[reg->count++] = *pkg;
    return 0;
}

const life_ability_package* life_ability_registry_find(const life_ability_registry* reg,
                                                       u32 package_id)
{
    u32 i;
    if (!reg || !reg->packages) {
        return NULL;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->packages[i].package_id == package_id) {
            return &reg->packages[i];
        }
    }
    return NULL;
}

static int life_ability_resolve_inner(const life_ability_registry* reg,
                                      u32 package_id,
                                      life_ability_package* out_pkg,
                                      u32 depth)
{
    const life_ability_package* pkg;
    life_ability_package parent_pkg;

    if (!reg || !out_pkg) {
        return -1;
    }
    if (depth > reg->count + 1u) {
        return -2;
    }
    pkg = life_ability_registry_find(reg, package_id);
    if (!pkg) {
        return -3;
    }
    *out_pkg = *pkg;
    if (pkg->parent_id != 0u) {
        if (life_ability_resolve_inner(reg, pkg->parent_id, &parent_pkg, depth + 1u) != 0) {
            return -4;
        }
        if (life_ability_merge(&parent_pkg, out_pkg) != 0) {
            return -5;
        }
    }
    return 0;
}

int life_ability_registry_resolve(const life_ability_registry* reg,
                                  u32 package_id,
                                  life_ability_package* out_pkg)
{
    return life_ability_resolve_inner(reg, package_id, out_pkg, 0u);
}

int life_ability_register_presets(life_ability_registry* reg)
{
    life_ability_package pkg;

    if (!reg) {
        return -1;
    }

    memset(&pkg, 0, sizeof(pkg));
    pkg.package_id = LIFE_ABILITY_HARDCORE_ID;
    pkg.parent_id = 0u;
    pkg.ui_caps = 0u;
    pkg.game_caps = 0u;
    pkg.allowed_policy_mask = LIFE_POLICY_MASK(LIFE_POLICY_S1);
    pkg.death_end_control = LIFE_BOOL_TRUE;
    pkg.transfer_allowed = LIFE_BOOL_TRUE;
    pkg.spectator_on_refusal = LIFE_BOOL_TRUE;
    pkg.default_policy_id = LIFE_POLICY_S1;
    if (life_ability_registry_register(reg, &pkg) != 0) {
        return -2;
    }

    memset(&pkg, 0, sizeof(pkg));
    pkg.package_id = LIFE_ABILITY_SOFTCORE_ID;
    pkg.parent_id = LIFE_ABILITY_HARDCORE_ID;
    pkg.ui_caps = 0u;
    pkg.game_caps = 0u;
    pkg.allowed_policy_mask = LIFE_POLICY_MASK(LIFE_POLICY_S2) |
                              LIFE_POLICY_MASK(LIFE_POLICY_S3) |
                              LIFE_POLICY_MASK(LIFE_POLICY_S4);
    pkg.death_end_control = LIFE_BOOL_INHERIT;
    pkg.transfer_allowed = LIFE_BOOL_INHERIT;
    pkg.spectator_on_refusal = LIFE_BOOL_INHERIT;
    pkg.default_policy_id = LIFE_POLICY_ID_INHERIT;
    if (life_ability_registry_register(reg, &pkg) != 0) {
        return -3;
    }

    memset(&pkg, 0, sizeof(pkg));
    pkg.package_id = LIFE_ABILITY_CREATIVE_ID;
    pkg.parent_id = LIFE_ABILITY_SOFTCORE_ID;
    pkg.ui_caps = LIFE_UI_CAP_DEBUG_PRIV;
    pkg.game_caps = LIFE_GAME_CAP_CREATIVE_TOOLS;
    pkg.allowed_policy_mask = 0u;
    pkg.death_end_control = LIFE_BOOL_INHERIT;
    pkg.transfer_allowed = LIFE_BOOL_INHERIT;
    pkg.spectator_on_refusal = LIFE_BOOL_INHERIT;
    pkg.default_policy_id = LIFE_POLICY_ID_INHERIT;
    if (life_ability_registry_register(reg, &pkg) != 0) {
        return -4;
    }

    memset(&pkg, 0, sizeof(pkg));
    pkg.package_id = LIFE_ABILITY_SPECTATOR_ID;
    pkg.parent_id = LIFE_ABILITY_CREATIVE_ID;
    pkg.ui_caps = LIFE_UI_CAP_EPISTEMIC_PRIV;
    pkg.game_caps = LIFE_GAME_CAP_SPECTATOR;
    pkg.allowed_policy_mask = 0u;
    pkg.death_end_control = LIFE_BOOL_INHERIT;
    pkg.transfer_allowed = LIFE_BOOL_FALSE;
    pkg.spectator_on_refusal = LIFE_BOOL_TRUE;
    pkg.default_policy_id = 0u;
    if (life_ability_registry_register(reg, &pkg) != 0) {
        return -5;
    }

    return 0;
}

int life_ability_package_allows_policy(const life_ability_package* pkg,
                                       life_policy_type type)
{
    if (!pkg) {
        return 0;
    }
    return ((pkg->allowed_policy_mask & LIFE_POLICY_MASK(type)) != 0u);
}

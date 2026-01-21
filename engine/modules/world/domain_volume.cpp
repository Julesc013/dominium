/*
FILE: source/domino/world/domain_volume.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain_volume
RESPONSIBILITY: Implements domain volume runtime state and policy defaults.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed defaults; policy-driven resolution selection.
*/
#include "domino/world/domain_volume.h"

#include <string.h>

void dom_domain_policy_init(dom_domain_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->tile_size = d_q16_16_from_int(64);
    policy->max_resolution = DOM_DOMAIN_RES_FULL;
    policy->sample_dim_full = 8u;
    policy->sample_dim_medium = 4u;
    policy->sample_dim_coarse = 2u;
    policy->cost_full = 100u;
    policy->cost_medium = 40u;
    policy->cost_coarse = 10u;
    policy->cost_analytic = 5u;
    policy->tile_build_cost_full = 80u;
    policy->tile_build_cost_medium = 30u;
    policy->tile_build_cost_coarse = 10u;
    policy->ray_step = d_q16_16_from_int(1);
    policy->max_ray_steps = 64u;
}

void dom_domain_volume_init(dom_domain_volume* volume)
{
    u32 i;
    if (!volume) {
        return;
    }
    memset(volume, 0, sizeof(*volume));
    volume->existence_state = DOM_DOMAIN_EXISTENCE_NONEXISTENT;
    volume->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    dom_domain_policy_init(&volume->policy);
    for (i = 0u; i < DOM_DOMAIN_LOCAL_TILE_SLOTS; ++i) {
        dom_domain_tile_init(&volume->local_tiles[i]);
        volume->local_tile_ids[i] = 0u;
        volume->local_tile_versions[i] = 0u;
        volume->local_tile_valid[i] = D_FALSE;
    }
}

void dom_domain_volume_free(dom_domain_volume* volume)
{
    u32 i;
    if (!volume) {
        return;
    }
    for (i = 0u; i < DOM_DOMAIN_LOCAL_TILE_SLOTS; ++i) {
        dom_domain_tile_free(&volume->local_tiles[i]);
        volume->local_tile_ids[i] = 0u;
        volume->local_tile_versions[i] = 0u;
        volume->local_tile_valid[i] = D_FALSE;
    }
}

static void dom_domain_volume_clear_local_tiles(dom_domain_volume* volume)
{
    u32 i;
    if (!volume) {
        return;
    }
    for (i = 0u; i < DOM_DOMAIN_LOCAL_TILE_SLOTS; ++i) {
        dom_domain_tile_free(&volume->local_tiles[i]);
        dom_domain_tile_init(&volume->local_tiles[i]);
        volume->local_tile_ids[i] = 0u;
        volume->local_tile_versions[i] = 0u;
        volume->local_tile_valid[i] = D_FALSE;
    }
}

void dom_domain_volume_set_source(dom_domain_volume* volume, const dom_domain_sdf_source* source)
{
    if (!volume) {
        return;
    }
    volume->source = source;
    dom_domain_volume_clear_local_tiles(volume);
}

void dom_domain_volume_set_cache(dom_domain_volume* volume, struct dom_domain_cache* cache)
{
    if (!volume) {
        return;
    }
    volume->cache = cache;
}

void dom_domain_volume_set_policy(dom_domain_volume* volume, const dom_domain_policy* policy)
{
    if (!volume || !policy) {
        return;
    }
    volume->policy = *policy;
    dom_domain_volume_clear_local_tiles(volume);
}

void dom_domain_volume_set_state(dom_domain_volume* volume, u32 existence_state, u32 archival_state)
{
    if (!volume) {
        return;
    }
    if (volume->existence_state != existence_state || volume->archival_state != archival_state) {
        volume->existence_state = existence_state;
        volume->archival_state = archival_state;
        dom_domain_volume_clear_local_tiles(volume);
    }
}

void dom_domain_volume_set_authoring_version(dom_domain_volume* volume, u32 version)
{
    if (!volume) {
        return;
    }
    if (volume->authoring_version != version) {
        volume->authoring_version = version;
        dom_domain_volume_clear_local_tiles(volume);
    }
}

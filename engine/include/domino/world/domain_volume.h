/*


FILE: include/domino/world/domain_volume.h


MODULE: Domino


LAYER / SUBSYSTEM: Domino API / world/domain_volume


RESPONSIBILITY: Defines domain volume runtime inputs, policy, and state.


ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.


FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.


THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.


ERROR MODEL: Return codes/NULL pointers; no exceptions.


DETERMINISM: Policy-driven resolution selection; no wall-clock inputs.


VERSIONING / ABI / DATA FORMAT NOTES: Versioned by DOMAIN0/DOMAIN1 specs.


EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.


*/


#ifndef DOMINO_WORLD_DOMAIN_VOLUME_H


#define DOMINO_WORLD_DOMAIN_VOLUME_H





#include "domino/world/domain_tile.h"





#ifdef __cplusplus


extern "C" {


#endif





struct dom_domain_cache;





typedef enum dom_domain_existence_state {


    DOM_DOMAIN_EXISTENCE_NONEXISTENT = 0,


    DOM_DOMAIN_EXISTENCE_DECLARED = 1,


    DOM_DOMAIN_EXISTENCE_LATENT = 2,


    DOM_DOMAIN_EXISTENCE_REFINABLE = 3,


    DOM_DOMAIN_EXISTENCE_REALIZED = 4,


    DOM_DOMAIN_EXISTENCE_ARCHIVED = 5


} dom_domain_existence_state;





typedef enum dom_domain_archival_state {


    DOM_DOMAIN_ARCHIVAL_LIVE = 0,


    DOM_DOMAIN_ARCHIVAL_FROZEN = 1,


    DOM_DOMAIN_ARCHIVAL_ARCHIVED = 2,


    DOM_DOMAIN_ARCHIVAL_FORKED = 3


} dom_domain_archival_state;





typedef struct dom_domain_policy {


    q16_16 tile_size;


    u32    max_resolution; /* dom_domain_resolution */


    u32    sample_dim_full;


    u32    sample_dim_medium;


    u32    sample_dim_coarse;


    u32    cost_full;


    u32    cost_medium;


    u32    cost_coarse;


    u32    cost_analytic;


    u32    tile_build_cost_full;


    u32    tile_build_cost_medium;


    u32    tile_build_cost_coarse;


    q16_16 ray_step;


    u32    max_ray_steps;


} dom_domain_policy;





#define DOM_DOMAIN_LOCAL_TILE_SLOTS 3u





typedef struct dom_domain_volume {


    dom_domain_id          domain_id;


    u32                    authoring_version;


    u32                    existence_state; /* dom_domain_existence_state */


    u32                    archival_state;  /* dom_domain_archival_state */


    const dom_domain_sdf_source *source;


    dom_domain_policy      policy;


    struct dom_domain_cache *cache;





    dom_domain_tile        local_tiles[DOM_DOMAIN_LOCAL_TILE_SLOTS];


    u64                    local_tile_ids[DOM_DOMAIN_LOCAL_TILE_SLOTS];


    u32                    local_tile_versions[DOM_DOMAIN_LOCAL_TILE_SLOTS];


    d_bool                 local_tile_valid[DOM_DOMAIN_LOCAL_TILE_SLOTS];


} dom_domain_volume;





void dom_domain_policy_init(dom_domain_policy* policy);


void dom_domain_volume_init(dom_domain_volume* volume);


void dom_domain_volume_free(dom_domain_volume* volume);


void dom_domain_volume_set_source(dom_domain_volume* volume, const dom_domain_sdf_source* source);


void dom_domain_volume_set_cache(dom_domain_volume* volume, struct dom_domain_cache* cache);


void dom_domain_volume_set_policy(dom_domain_volume* volume, const dom_domain_policy* policy);


void dom_domain_volume_set_state(dom_domain_volume* volume, u32 existence_state, u32 archival_state);


void dom_domain_volume_set_authoring_version(dom_domain_volume* volume, u32 version);





#ifdef __cplusplus


} /* extern "C" */


#endif





#endif /* DOMINO_WORLD_DOMAIN_VOLUME_H */



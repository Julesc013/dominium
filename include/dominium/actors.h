#ifndef DOMINIUM_ACTORS_H
#define DOMINIUM_ACTORS_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "domino/dworld.h"
#include "dominium/world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_actor_id;

typedef enum dom_actor_kind {
    DOM_ACTOR_KIND_UNKNOWN = 0,
    DOM_ACTOR_KIND_PLAYER,
    DOM_ACTOR_KIND_NPC,
    DOM_ACTOR_KIND_ROBOT
} dom_actor_kind;

typedef struct dom_actor_spawn_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_actor_kind kind;
    dom_surface_id surface;
    WPosExact      position;
    uint32_t       controller_id;
    uint32_t       flags;
} dom_actor_spawn_desc;

typedef struct dom_actor_state {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_actor_id   id;
    dom_actor_kind kind;
    dom_surface_id surface;
    WPosExact      position;
    uint32_t       life_support_mbar;
    uint32_t       health_permille;
    uint32_t       flags;
} dom_actor_state;

dom_status dom_actor_spawn(const dom_actor_spawn_desc* desc,
                           dom_actor_id* out_id);
dom_status dom_actor_despawn(dom_actor_id id);
dom_status dom_actor_get_state(dom_actor_id id,
                               dom_actor_state* out_state,
                               size_t out_state_size);
dom_status dom_actor_tick(dom_actor_id id, uint32_t dt_millis);
dom_status dom_actors_step(uint32_t dt_millis);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_ACTORS_H */

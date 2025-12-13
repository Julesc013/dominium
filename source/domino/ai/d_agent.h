/* Generic agent controller state (C89). */
#ifndef D_AGENT_H
#define D_AGENT_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "content/d_content.h"
#include "job/d_job_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_agent_caps_s {
    d_content_tag tags;   /* capabilities: WALK, DRIVE, OPERATE_PROCESS, HAUL, BUILD, etc. */
    q16_16        max_speed;
    q16_16        max_carry_mass;
} d_agent_caps;

typedef struct d_agent_state_s {
    d_agent_id   id;
    u32          owner_eid;        /* entity in world: struct/vehicle/actor */
    d_agent_caps caps;

    d_job_id     current_job;
    q32_32       pos_x;
    q32_32       pos_y;
    q32_32       pos_z;

    /* Simple movement + state flags */
    u16          flags;            /* MOVING, IDLE, EXECUTING, etc. */
} d_agent_state;

enum {
    D_AGENT_FLAG_IDLE      = 1u << 0,
    D_AGENT_FLAG_MOVING    = 1u << 1,
    D_AGENT_FLAG_EXECUTING = 1u << 2
};

int d_agent_system_init(d_world *w);
void d_agent_system_shutdown(d_world *w);

d_agent_id d_agent_register(d_world *w, const d_agent_state *init);
int        d_agent_unregister(d_world *w, d_agent_id id);

int d_agent_get(const d_world *w, d_agent_id id, d_agent_state *out);
int d_agent_update(d_world *w, const d_agent_state *st);

u32 d_agent_count(const d_world *w);
int d_agent_get_by_index(const d_world *w, u32 index, d_agent_state *out);

void d_agent_tick(d_world *w, u32 ticks);

int d_agent_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_AGENT_H */


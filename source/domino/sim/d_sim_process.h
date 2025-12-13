/* Generic production/process runner (C89). */
#ifndef D_SIM_PROCESS_H
#define D_SIM_PROCESS_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_sim_process_stats_s {
    d_process_id process_id;
    u32          cycles_completed;
    u32          output_units;     /* sum of OUTPUT_ITEM units produced */
    u32          ticks_observed;   /* world ticks observed (for rate calculations) */
} d_sim_process_stats;

void d_sim_process_tick(d_world *w, u32 ticks);

u32 d_sim_process_stats_count(const d_world *w);
int d_sim_process_stats_get_by_index(const d_world *w, u32 index, d_sim_process_stats *out);

#ifdef __cplusplus
}
#endif

#endif /* D_SIM_PROCESS_H */


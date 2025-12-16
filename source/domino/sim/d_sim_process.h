/*
FILE: source/domino/sim/d_sim_process.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/d_sim_process
RESPONSIBILITY: Implements `d_sim_process`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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


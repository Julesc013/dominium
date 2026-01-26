/*
FILE: include/domino/sim.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / sim
RESPONSIBILITY: Defines the public contract for `sim` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SIM_H_INCLUDED
#define DOMINO_SIM_H_INCLUDED

#include "domino/baseline.h"
#include "domino/sys.h"
#include "domino/inst.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dom_core_t;
/* dom_core: Public type used by `sim`. */
typedef struct dom_core_t dom_core;

/* dom_sim: Public type used by `sim`. */
typedef struct dom_sim dom_sim;

/* dom_sim_state: Public type used by `sim`. */
typedef struct dom_sim_state {
    uint32_t struct_size;
    uint32_t struct_version;
    uint64_t ticks;
    uint64_t sim_time_usec;
    uint32_t dt_usec;
    uint32_t ups;          /* target updates per second */
    bool     paused;
} dom_sim_state;

/* Purpose: Tick sim.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_sim_tick(dom_core* core,
                  dom_instance_id inst,
                  uint32_t ticks);

/* Purpose: Get state.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_sim_get_state(dom_core* core,
                       dom_instance_id inst,
                       dom_sim_state* out);

/*------------------------------------------------------------
 * Legacy deterministic sim stubs (kept for compatibility)
 *------------------------------------------------------------*/
struct dm_sim_config {
    uint64_t seed;
};

/* dm_sim_context: Public type used by `sim`. */
typedef struct dm_sim_context dm_sim_context;

/* Purpose: Create sim.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dm_sim_context* dm_sim_create(const struct dm_sim_config* cfg);
/* Purpose: Destroy sim.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            dm_sim_destroy(dm_sim_context* sim);
/* Purpose: Tick sim.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            dm_sim_tick(dm_sim_context* sim, uint32_t dt_usec);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SIM_H_INCLUDED */

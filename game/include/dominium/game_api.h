/*
FILE: include/dominium/game_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / game_api
RESPONSIBILITY: Defines the public contract for `game_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_GAME_API_H
#define DOMINIUM_GAME_API_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "domino/mod.h"
#include "domino/sim.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_game_runtime: Public type used by `game_api`. */
typedef struct dom_game_runtime dom_game_runtime;

/* dom_game_runtime_desc: Public type used by `game_api`. */
typedef struct dom_game_runtime_desc {
    uint32_t struct_size;
    uint32_t struct_version;
    dom_core* core;
    dom_sim* sim;
    dom_canvas* canvas;
    void*     user_data;
} dom_game_runtime_desc;

/* dom_game_command: Public type used by `game_api`. */
typedef struct dom_game_command {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* name;
    const void* payload;
    size_t      payload_size;
} dom_game_command;

/* dom_game_query: Public type used by `game_api`. */
typedef struct dom_game_query {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* name;
    const void* payload;
    size_t      payload_size;
} dom_game_query;

/* dom_game_sim_step_args: Public type used by `game_api`. */
typedef struct dom_game_sim_step_args {
    uint32_t        struct_size;
    uint32_t        struct_version;
    dom_instance_id inst;
    double          dt_s;
} dom_game_sim_step_args;

/* Purpose: Create game runtime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_game_runtime_create(const dom_game_runtime_desc* desc,
                                   dom_game_runtime** out_runtime);
/* Purpose: Destroy game runtime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void       dom_game_runtime_destroy(dom_game_runtime* runtime);
/* Purpose: Tick game runtime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_game_runtime_tick(dom_game_runtime* runtime, uint32_t dt_millis);
/* Purpose: Execute game runtime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_game_runtime_execute(dom_game_runtime* runtime,
                                    const dom_game_command* cmd);
/* Purpose: Query game runtime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_game_runtime_query(dom_game_runtime* runtime,
                                  const dom_game_query* query,
                                  void* response_buffer,
                                  size_t response_buffer_size);

/* Called by Domino sim for each instance tick */
void dom_game_sim_step(dom_core* core, const dom_game_sim_step_args* args);
/* Purpose: Steps dom game debug sim.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
uint64_t dom_game_debug_sim_steps(dom_instance_id inst);

/* Convenience entry point used by current product layer */
int dominium_game_run(const domino_instance_desc* inst);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_GAME_API_H */

/*
FILE: include/domino/sim/sim.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / sim/sim
RESPONSIBILITY: Defines the public contract for `sim` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SIM_SIM_H
#define DOMINO_SIM_SIM_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_world_config: Public type used by `sim`. */
typedef struct d_world_config {
    u32 seed;
    u32 width;
    u32 height;
} d_world_config;

/* Purpose: Config d world create from.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_world* d_world_create_from_config(const d_world_config* cfg);
/* Purpose: Tick world.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void     d_world_tick(d_world* world);
/* Purpose: Checksum d world.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
u32      d_world_checksum(const d_world* world);
/* Purpose: Tlv d world save.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
d_bool   d_world_save_tlv(const d_world* world, const char* path);
/* Purpose: Tlv d world load.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
d_world* d_world_load_tlv(const char* path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SIM_SIM_H */

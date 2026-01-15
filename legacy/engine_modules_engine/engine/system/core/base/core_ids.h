/*
FILE: source/domino/system/core/base/core_ids.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/core_ids
RESPONSIBILITY: Defines internal contract for `core_ids`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CORE_IDS_H
#define DOM_CORE_IDS_H

#include "core_types.h"

typedef u64 EntityId;
typedef u64 VolumeId;
typedef u64 FluidSpaceId;
typedef u64 ThermalSpaceId;
typedef u64 NetNodeId;
typedef u64 NetEdgeId;
typedef u64 RNGId;
typedef u32 RecipeId;

#endif /* DOM_CORE_IDS_H */

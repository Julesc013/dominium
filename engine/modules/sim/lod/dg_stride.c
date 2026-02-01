/*
FILE: source/domino/sim/lod/dg_stride.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_stride
RESPONSIBILITY: Implements `dg_stride`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "sim/lod/dg_stride.h"

#include "core/dg_det_hash.h"

d_bool dg_stride_should_run(dg_tick tick, u64 stable_id, u32 stride) {
    u64 h;
    u64 s;
    if (stride <= 1u) {
        return D_TRUE;
    }
    h = dg_det_hash_u64(stable_id);
    s = (u64)stride;
    return (((tick + h) % s) == 0u) ? D_TRUE : D_FALSE;
}


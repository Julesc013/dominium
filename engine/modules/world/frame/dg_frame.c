/*
FILE: source/domino/world/frame/dg_frame.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_frame
RESPONSIBILITY: Implements `dg_frame`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "world/frame/dg_frame.h"

d_bool dg_frame_id_is_world(dg_frame_id id) {
    return (id == DG_FRAME_ID_WORLD) ? D_TRUE : D_FALSE;
}


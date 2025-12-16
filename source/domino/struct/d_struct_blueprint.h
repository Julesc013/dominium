/*
FILE: source/domino/struct/d_struct_blueprint.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/d_struct_blueprint
RESPONSIBILITY: Defines internal contract for `d_struct_blueprint`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_STRUCT_BLUEPRINT_H
#define D_STRUCT_BLUEPRINT_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Instantiate blueprint at world position (x,y,z), no rotation for now. */
int d_struct_spawn_blueprint(
    d_world                  *w,
    const d_proto_blueprint  *bp,
    q16_16                    x,
    q16_16                    y,
    q16_16                    z
);

#ifdef __cplusplus
}
#endif

#endif /* D_STRUCT_BLUEPRINT_H */

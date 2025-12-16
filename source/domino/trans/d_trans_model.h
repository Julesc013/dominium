/*
FILE: source/domino/trans/d_trans_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/d_trans_model
RESPONSIBILITY: Defines internal contract for `d_trans_model`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Transport model vtable (C89). */
#ifndef D_TRANS_MODEL_H
#define D_TRANS_MODEL_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "trans/d_trans.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dtrans_model_vtable {
    u16 model_id; /* within D_MODEL_FAMILY_TRANS */

    /* Called to tick a spline instance. */
    void (*tick_spline)(
        d_world           *w,
        d_spline_instance *spline,
        u32                ticks
    );
} dtrans_model_vtable;

int dtrans_register_model(const dtrans_model_vtable *vt);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_MODEL_H */

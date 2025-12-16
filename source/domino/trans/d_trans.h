/*
FILE: source/domino/trans/d_trans.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/d_trans
RESPONSIBILITY: Implements `d_trans`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Transport subsystem public interface (C89). */
#ifndef D_TRANS_H
#define D_TRANS_H

#include "trans/d_trans_spline.h"
#include "trans/d_trans_mover.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Subsystem registration hook (called once at startup). */
void d_trans_register_subsystem(void);

/* Debug validator hook. */
int d_trans_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_H */

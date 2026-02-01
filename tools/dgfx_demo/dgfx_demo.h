/*
FILE: source/tools/dgfx_demo/dgfx_demo.h
MODULE: Repository
LAYER / SUBSYSTEM: source/tools/dgfx_demo
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DGFX_DEMO_H
#define DOMINIUM_DGFX_DEMO_H

#include "domino/gfx.h"

/* Run a simple, blocking demo loop for a given backend.
   Returns 0 on success, non-zero on failure. */
int dgfx_run_demo(dgfx_backend_t backend);

/* Optional single-frame helper. */
int dgfx_run_demo_single_frame(dgfx_backend_t backend);

#endif /* DOMINIUM_DGFX_DEMO_H */

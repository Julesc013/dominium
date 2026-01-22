/*
FILE: include/domino/app/runtime.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / app/runtime
RESPONSIBILITY: Defines shared runtime loop constants for product entrypoints; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_APP_RUNTIME_H
#define DOMINO_APP_RUNTIME_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Timing modes shared across products. */
typedef enum d_app_timing_mode {
    D_APP_TIMING_DETERMINISTIC = 0,
    D_APP_TIMING_INTERACTIVE = 1
} d_app_timing_mode;

/* Canonical exit codes shared across products. */
enum {
    D_APP_EXIT_OK = 0,
    D_APP_EXIT_FAILURE = 1,
    D_APP_EXIT_USAGE = 2,
    D_APP_EXIT_UNAVAILABLE = 3,
    D_APP_EXIT_SIGNAL = 130
};

/* Fixed timestep for deterministic app loops (microseconds). */
enum { D_APP_FIXED_TIMESTEP_US = 16666 };

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_APP_RUNTIME_H */

/*
FILE: source/dominium/game/runtime/dom_fidelity.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_fidelity
RESPONSIBILITY: Defines fidelity ladder for derived rendering/data readiness.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Derived-only; fidelity changes must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_FIDELITY_H
#define DOM_FIDELITY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_FIDELITY_STATE_VERSION = 1u
};

typedef enum dom_fidelity_level {
    DOM_FIDELITY_MIN = 0,
    DOM_FIDELITY_LOW = 1,
    DOM_FIDELITY_MED = 2,
    DOM_FIDELITY_HIGH = 3
} dom_fidelity_level;

enum {
    DOM_FIDELITY_MISSING_NONE = 0u,
    DOM_FIDELITY_MISSING_DERIVED = 1u << 0
};

typedef struct dom_fidelity_state {
    u32 struct_size;
    u32 struct_version;
    u32 level;
    u32 min_level;
    u32 max_level;
    u32 missing_mask;
} dom_fidelity_state;

void dom_fidelity_init(dom_fidelity_state *st, u32 initial_level);
void dom_fidelity_mark_missing(dom_fidelity_state *st, u32 mask);
void dom_fidelity_mark_ready(dom_fidelity_state *st, u32 mask);
void dom_fidelity_step(dom_fidelity_state *st);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_FIDELITY_H */

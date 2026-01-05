/*
FILE: source/dominium/game/runtime/dom_fidelity.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_fidelity
RESPONSIBILITY: Implements fidelity ladder transitions.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Derived-only; fidelity changes must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_fidelity.h"

void dom_fidelity_init(dom_fidelity_state *st, u32 initial_level) {
    if (!st) {
        return;
    }
    st->struct_size = sizeof(*st);
    st->struct_version = DOM_FIDELITY_STATE_VERSION;
    st->min_level = DOM_FIDELITY_MIN;
    st->max_level = DOM_FIDELITY_HIGH;
    st->level = initial_level;
    if (st->level < st->min_level) {
        st->level = st->min_level;
    }
    if (st->level > st->max_level) {
        st->level = st->max_level;
    }
    st->missing_mask = DOM_FIDELITY_MISSING_NONE;
}

void dom_fidelity_mark_missing(dom_fidelity_state *st, u32 mask) {
    if (!st) {
        return;
    }
    st->missing_mask |= mask;
}

void dom_fidelity_mark_ready(dom_fidelity_state *st, u32 mask) {
    if (!st) {
        return;
    }
    st->missing_mask &= ~mask;
}

void dom_fidelity_step(dom_fidelity_state *st) {
    if (!st) {
        return;
    }
    if (st->missing_mask != 0u) {
        if (st->level > st->min_level) {
            st->level -= 1u;
        }
        return;
    }
    if (st->level < st->max_level) {
        st->level += 1u;
    }
}

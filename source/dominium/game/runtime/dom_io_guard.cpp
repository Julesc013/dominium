/*
FILE: source/dominium/game/runtime/dom_io_guard.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_io_guard
RESPONSIBILITY: Implements UI-thread IO guard and stall counters.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; counters must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal API only.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_io_guard.h"

#include <cstdio>

namespace {

static u32 g_ui_scope_depth = 0u;
static u32 g_derived_scope_depth = 0u;
static u32 g_io_violation_count = 0u;
static u32 g_stall_count = 0u;
static u32 g_last_frame_ms = 0u;

static void log_violation(const char *op, const char *path) {
    const char *op_s = op ? op : "io_op";
    const char *path_s = path ? path : "(null)";
    std::fprintf(stderr,
                 "IO_BAN violation op=%s path=%s ui_depth=%u derived_depth=%u\n",
                 op_s,
                 path_s,
                 (unsigned)g_ui_scope_depth,
                 (unsigned)g_derived_scope_depth);
}

static void log_stall(u32 frame_ms, u32 threshold_ms) {
    std::fprintf(stderr,
                 "STALL frame_ms=%u threshold_ms=%u\n",
                 (unsigned)frame_ms,
                 (unsigned)threshold_ms);
}

} // namespace

extern "C" {

void dom_io_guard_reset(void) {
    g_ui_scope_depth = 0u;
    g_derived_scope_depth = 0u;
    g_io_violation_count = 0u;
    g_stall_count = 0u;
    g_last_frame_ms = 0u;
}

void dom_io_guard_enter_ui(void) {
    g_ui_scope_depth += 1u;
}

void dom_io_guard_exit_ui(void) {
    if (g_ui_scope_depth > 0u) {
        g_ui_scope_depth -= 1u;
    }
}

void dom_io_guard_enter_derived(void) {
    g_derived_scope_depth += 1u;
}

void dom_io_guard_exit_derived(void) {
    if (g_derived_scope_depth > 0u) {
        g_derived_scope_depth -= 1u;
    }
}

int dom_io_guard_io_allowed(void) {
    if (g_ui_scope_depth == 0u) {
        return 1;
    }
    if (g_derived_scope_depth > 0u) {
        return 1;
    }
    return 0;
}

void dom_io_guard_note_violation(const char *op, const char *path) {
    g_io_violation_count += 1u;
    log_violation(op, path);
}

void dom_io_guard_note_stall(u32 frame_ms, u32 threshold_ms) {
    g_last_frame_ms = frame_ms;
    g_stall_count += 1u;
    log_stall(frame_ms, threshold_ms);
}

u32 dom_io_guard_violation_count(void) {
    return g_io_violation_count;
}

u32 dom_io_guard_stall_count(void) {
    return g_stall_count;
}

u32 dom_io_guard_last_frame_ms(void) {
    return g_last_frame_ms;
}

} /* extern "C" */

/*
FILE: source/dominium/game/runtime/dom_io_guard.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_io_guard
RESPONSIBILITY: Provides UI-thread IO guard and stall counters.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; counters must not affect authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal API only.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_IO_GUARD_H
#define DOM_IO_GUARD_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

void dom_io_guard_reset(void);
void dom_io_guard_enter_ui(void);
void dom_io_guard_exit_ui(void);
void dom_io_guard_enter_derived(void);
void dom_io_guard_exit_derived(void);

int dom_io_guard_io_allowed(void);
void dom_io_guard_note_violation(const char *op, const char *path);
void dom_io_guard_note_stall(u32 frame_ms, u32 threshold_ms);

u32 dom_io_guard_violation_count(void);
u32 dom_io_guard_stall_count(void);
u32 dom_io_guard_last_frame_ms(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_IO_GUARD_H */

/*
FILE: source/domino/struct/d_struct_instance.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/d_struct_instance
RESPONSIBILITY: Implements `d_struct_instance`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "struct/d_struct_instance.h"

void d_struct_instance_reset(d_struct_instance *inst) {
    if (!inst) {
        return;
    }
    memset(inst, 0, sizeof(*inst));
}


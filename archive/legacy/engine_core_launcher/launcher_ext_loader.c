/*
FILE: source/domino/core/launcher_ext_loader.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/launcher_ext_loader
RESPONSIBILITY: Implements `launcher_ext_loader`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/launcher_ext.h"
#include "core_internal.h"

bool launcher_ext_load_all(dom_core* core)
{
    (void)core;
    return true;
}

void launcher_ext_unload_all(dom_core* core)
{
    (void)core;
}

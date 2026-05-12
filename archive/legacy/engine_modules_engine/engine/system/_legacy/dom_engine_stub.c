/*
FILE: source/domino/system/_legacy/dom_engine_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/_legacy/dom_engine_stub
RESPONSIBILITY: Implements `dom_engine_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
// LEGACY: candidate for removal/refactor
/* Minimal dom_engine stub to satisfy build graph. */
int dom_engine_stub(void) { return 0; }

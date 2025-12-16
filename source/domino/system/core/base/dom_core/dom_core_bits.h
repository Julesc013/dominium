/*
FILE: source/domino/system/core/base/dom_core/dom_core_bits.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_bits
RESPONSIBILITY: Defines internal contract for `dom_core_bits`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CORE_BITS_H
#define DOM_CORE_BITS_H

int dom_core_bits_stub(void);

#endif /* DOM_CORE_BITS_H */

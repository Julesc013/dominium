/*
FILE: source/domino/render/api/ui/dom_ui_core.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/ui/dom_ui_core
RESPONSIBILITY: Implements `dom_ui_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_UI_CORE_H
#define DOM_UI_CORE_H

int dom_ui_init(void);

#endif /* DOM_UI_CORE_H */

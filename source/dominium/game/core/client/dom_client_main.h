/*
FILE: source/dominium/game/core/client/dom_client_main.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/core/client/dom_client_main
RESPONSIBILITY: Implements `dom_client_main`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CLIENT_MAIN_H
#define DOM_CLIENT_MAIN_H

/*
 * Minimal Dominium client MVP entry (Windows).
 * Creates platform + renderer + sim world, then runs a basic loop.
 */

int dom_client_run(void);

#endif /* DOM_CLIENT_MAIN_H */

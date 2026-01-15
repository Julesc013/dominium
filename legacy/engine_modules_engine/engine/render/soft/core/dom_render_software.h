/*
FILE: source/domino/render/soft/core/dom_render_software.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/core/dom_render_software
RESPONSIBILITY: Defines internal contract for `dom_render_software`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_RENDER_SOFTWARE_H
#define DOM_RENDER_SOFTWARE_H

#include "dom_render_api.h"

#ifdef __cplusplus
extern "C" {
#endif

const DomRenderBackendAPI *dom_render_backend_software(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_RENDER_SOFTWARE_H */

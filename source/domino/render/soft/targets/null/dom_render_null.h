/*
FILE: source/domino/render/soft/targets/null/dom_render_null.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/targets/null/dom_render_null
RESPONSIBILITY: Implements `dom_render_null`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_RENDER_NULL_H
#define DOM_RENDER_NULL_H

#include "dom_render_api.h"

#ifdef __cplusplus
extern "C" {
#endif

const DomRenderBackendAPI *dom_render_backend_null(void);
const DomRenderBackendAPI *dom_render_backend_vector2d(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_RENDER_NULL_H */

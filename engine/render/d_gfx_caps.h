/*
FILE: source/domino/render/d_gfx_caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/d_gfx_caps
RESPONSIBILITY: Compatibility wrapper for `render/d_gfx_caps.h`.
ALLOWED DEPENDENCIES: `include/domino/**`, `include/render/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Capability masks are deterministic and fixed per backend build.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (wrapper only).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_RENDER_D_GFX_CAPS_WRAPPER_H
#define DOMINO_RENDER_D_GFX_CAPS_WRAPPER_H

#include "render/d_gfx_caps.h"

#endif /* DOMINO_RENDER_D_GFX_CAPS_WRAPPER_H */

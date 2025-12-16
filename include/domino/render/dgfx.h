/*
FILE: include/domino/render/dgfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/dgfx
RESPONSIBILITY: Defines the public contract for `dgfx` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_RENDER_DGFX_H_INCLUDED
#define DOMINO_RENDER_DGFX_H_INCLUDED

/* Compatibility shim to keep the dgfx IR reachable from render/ paths. */
#include "domino/gfx.h"

#endif /* DOMINO_RENDER_DGFX_H_INCLUDED */

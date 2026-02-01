/*
FILE: source/domino/res/d_res_proto.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/d_res_proto
RESPONSIBILITY: Defines internal contract for `d_res_proto`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Legacy resource proto wrapper; use content/d_content.h. */
#ifndef D_RES_PROTO_H
#define D_RES_PROTO_H

#include "content/d_content.h"

#endif /* D_RES_PROTO_H */

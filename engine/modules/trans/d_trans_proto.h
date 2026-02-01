/*
FILE: source/domino/trans/d_trans_proto.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/d_trans_proto
RESPONSIBILITY: Defines internal contract for `d_trans_proto`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Legacy spline profile wrapper; use content/d_content.h. */
#ifndef D_TRANS_PROTO_H
#define D_TRANS_PROTO_H

#include "content/d_content.h"

#endif /* D_TRANS_PROTO_H */

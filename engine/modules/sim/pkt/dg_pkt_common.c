/*
FILE: source/domino/sim/pkt/dg_pkt_common.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/dg_pkt_common
RESPONSIBILITY: Implements `dg_pkt_common`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "sim/pkt/dg_pkt_common.h"

void dg_pkt_hdr_clear(dg_pkt_hdr *hdr) {
    if (!hdr) {
        return;
    }
    memset(hdr, 0, sizeof(*hdr));
}


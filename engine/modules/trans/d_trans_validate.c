/*
FILE: source/domino/trans/d_trans_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/d_trans_validate
RESPONSIBILITY: Implements `d_trans_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "content/d_content.h"
#include "trans/d_trans.h"

int d_trans_validate(const d_world *w) {
    u32 i;
    u32 spline_count;
    u32 mover_count;

    if (!w) {
        return -1;
    }

    spline_count = d_trans_spline_count(w);
    for (i = 0u; i < spline_count; ++i) {
        d_spline_instance s;
        d_spline_node node0;
        u16 got = 0u;
        const d_proto_spline_profile *p;

        memset(&s, 0, sizeof(s));
        if (d_trans_spline_get_by_index(w, i, &s) != 0) {
            return -1;
        }
        if (s.id == 0u || s.profile_id == 0u || s.node_count < 2u) {
            return -1;
        }
        p = d_content_get_spline_profile(s.profile_id);
        if (!p) {
            return -1;
        }
        memset(&node0, 0, sizeof(node0));
        if (d_trans_spline_copy_nodes(w, s.node_start_index, s.node_count, &node0, 1u, &got) != 0) {
            return -1;
        }
        if (got == 0u) {
            return -1;
        }
    }

    mover_count = d_trans_mover_count(w);
    for (i = 0u; i < mover_count; ++i) {
        d_mover m;
        d_spline_instance s;

        memset(&m, 0, sizeof(m));
        if (d_trans_mover_get_by_index(w, i, &m) != 0) {
            return -1;
        }
        if (m.id == 0u || m.kind == D_MOVER_KIND_NONE || m.spline_id == 0u) {
            return -1;
        }
        memset(&s, 0, sizeof(s));
        if (d_trans_spline_get(w, m.spline_id, &s) != 0) {
            return -1;
        }
    }

    return 0;
}

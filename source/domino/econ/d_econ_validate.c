/*
FILE: source/domino/econ/d_econ_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / econ/d_econ_validate
RESPONSIBILITY: Implements `d_econ_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "econ/d_econ_metrics.h"

#include "core/d_org.h"

int d_econ_validate(const d_world *w) {
    u32 i;
    u32 count;
    (void)w;

    count = d_econ_org_metrics_count();
    for (i = 0u; i < count; ++i) {
        d_econ_org_metrics m;
        d_org org;
        if (d_econ_org_metrics_get_by_index(i, &m) != 0) {
            fprintf(stderr, "econ validate: failed get_by_index %u\n", (unsigned)i);
            return -1;
        }
        if (m.org_id == 0u) {
            fprintf(stderr, "econ validate: invalid org_id at index %u\n", (unsigned)i);
            return -1;
        }
        if (d_org_get(m.org_id, &org) != 0) {
            fprintf(stderr, "econ validate: missing org %u for metrics\n", (unsigned)m.org_id);
            return -1;
        }
    }
    return 0;
}


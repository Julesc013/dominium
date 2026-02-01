/*
FILE: source/domino/research/d_research_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / research/d_research_validate
RESPONSIBILITY: Implements `d_research_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "research/d_research_state.h"

#include "core/d_org.h"
#include "content/d_content.h"

int d_research_validate(const struct d_world *w) {
    u32 oi;
    u32 org_count;
    u32 expected_research = d_content_research_count();
    (void)w;

    org_count = d_org_count();
    for (oi = 0u; oi < org_count; ++oi) {
        d_org org;
        d_research_org_state st;
        u32 ri;

        if (d_org_get_by_index(oi, &org) != 0) {
            fprintf(stderr, "research validate: failed get org index %u\n", (unsigned)oi);
            return -1;
        }
        if (org.id == 0u) {
            fprintf(stderr, "research validate: invalid org id at index %u\n", (unsigned)oi);
            return -1;
        }
        if (d_research_get_org_state(org.id, &st) != 0) {
            fprintf(stderr, "research validate: missing research state for org %u\n", (unsigned)org.id);
            return -1;
        }
        if (st.org_id != org.id) {
            fprintf(stderr, "research validate: org_id mismatch for org %u\n", (unsigned)org.id);
            return -1;
        }
        if ((u32)st.research_count != expected_research) {
            fprintf(stderr, "research validate: research_count mismatch for org %u\n", (unsigned)org.id);
            return -1;
        }
        if (st.research_count > 0u && !st.researches) {
            fprintf(stderr, "research validate: null research array for org %u\n", (unsigned)org.id);
            return -1;
        }

        for (ri = 0u; ri < (u32)st.research_count; ++ri) {
            const d_research_progress *p = &st.researches[ri];
            if (p->id == 0u || !d_content_get_research(p->id)) {
                fprintf(stderr, "research validate: invalid research id in org %u\n", (unsigned)org.id);
                return -1;
            }
            if (p->progress < 0) {
                fprintf(stderr, "research validate: negative progress for org %u research %u\n",
                        (unsigned)org.id, (unsigned)p->id);
                return -1;
            }
            if (p->state > (u8)D_RESEARCH_STATE_LOCKED) {
                fprintf(stderr, "research validate: invalid state for org %u research %u\n",
                        (unsigned)org.id, (unsigned)p->id);
                return -1;
            }
        }
    }

    return 0;
}


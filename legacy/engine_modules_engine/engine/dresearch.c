/*
FILE: source/domino/dresearch.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dresearch
RESPONSIBILITY: Implements `dresearch`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dresearch.h"

#include <string.h>
#include <stdlib.h>

#define DRESEARCH_MAX_TECH 512

static Tech g_techs[DRESEARCH_MAX_TECH];
static TechId g_tech_count = 0;

static TechProgress *g_progress = 0;
static U32 g_progress_cap = 0;

TechId dresearch_register_tech(const Tech *def)
{
    Tech copy;
    if (!def || !def->name) return 0;
    if (g_tech_count >= (TechId)DRESEARCH_MAX_TECH) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = (TechId)(g_tech_count + 1);
    }
    g_techs[g_tech_count] = copy;
    g_tech_count++;
    return copy.id;
}

const Tech *dresearch_get_tech(TechId id)
{
    if (id == 0 || id > g_tech_count) return 0;
    return &g_techs[id - 1];
}

void dresearch_init_progress(U32 max_techs)
{
    if (g_progress) return;
    if (max_techs == 0) max_techs = DRESEARCH_MAX_TECH;
    g_progress = (TechProgress*)malloc(sizeof(TechProgress) * max_techs);
    if (!g_progress) {
        g_progress_cap = 0;
        return;
    }
    memset(g_progress, 0, sizeof(TechProgress) * max_techs);
    g_progress_cap = max_techs;
}

TechProgress *dresearch_get_progress(TechId id)
{
    if (id == 0 || id > g_progress_cap) return 0;
    return &g_progress[id - 1];
}

void dresearch_apply_work(TechId tech, U32 science_units)
{
    TechProgress *p;
    const Tech *t;
    Q16_16 delta = 0;
    if (!g_progress || tech == 0 || science_units == 0) return;
    p = dresearch_get_progress(tech);
    t = dresearch_get_tech(tech);
    if (!p || !t) return;
    if (p->completed) return;
    if (t->science_count == 0) {
        p->progress_0_1 = (Q16_16)(1 << 16);
        p->completed = true;
        return;
    }
    delta = (Q16_16)(((I64)science_units << 16) / (I64)t->science_count);
    p->progress_0_1 = (Q16_16)(p->progress_0_1 + delta);
    if (p->progress_0_1 >= (Q16_16)(1 << 16)) {
        p->progress_0_1 = (Q16_16)(1 << 16);
        p->completed = true;
    }
}

void dresearch_tick(SimTick t)
{
    (void)t;
    /* Work is applied explicitly via dresearch_apply_work */
}

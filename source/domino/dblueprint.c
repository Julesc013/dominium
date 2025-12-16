/*
FILE: source/domino/dblueprint.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dblueprint
RESPONSIBILITY: Implements `dblueprint`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dblueprint.h"

#include <string.h>
#include <stdlib.h>

#define DBLUEPRINT_MAX 256

static Blueprint g_blueprints[DBLUEPRINT_MAX];
static BlueprintId g_blueprint_count = 0;

static Blueprint *dblueprint_lookup(BlueprintId id)
{
    if (id == 0 || id > g_blueprint_count) return 0;
    return &g_blueprints[id - 1];
}

BlueprintId dblueprint_create(const char *name, U32 elem_capacity)
{
    Blueprint *bp;
    if (g_blueprint_count >= (BlueprintId)DBLUEPRINT_MAX) return 0;
    g_blueprint_count++;
    bp = &g_blueprints[g_blueprint_count - 1];
    memset(bp, 0, sizeof(*bp));
    bp->id = g_blueprint_count;
    bp->name = name;
    bp->elem_capacity = elem_capacity;
    if (elem_capacity > 0) {
        bp->elems = (BlueprintElement*)malloc(sizeof(BlueprintElement) * elem_capacity);
        if (!bp->elems) {
            bp->elem_capacity = 0;
            g_blueprint_count--;
            return 0;
        }
        memset(bp->elems, 0, sizeof(BlueprintElement) * elem_capacity);
    }
    return bp->id;
}

Blueprint *dblueprint_get(BlueprintId id)
{
    return dblueprint_lookup(id);
}

void dblueprint_destroy(BlueprintId id)
{
    Blueprint *bp = dblueprint_lookup(id);
    if (!bp) return;
    if (bp->elems) {
        free(bp->elems);
        bp->elems = 0;
    }
    memset(bp, 0, sizeof(*bp));
}

BlueprintElementId dblueprint_add_element(BlueprintId id, const BlueprintElement *elem)
{
    Blueprint *bp = dblueprint_lookup(id);
    BlueprintElement *dst;
    if (!bp || !elem) return 0;
    if (!bp->elems || bp->elem_count >= bp->elem_capacity) return 0;
    dst = &bp->elems[bp->elem_count];
    *dst = *elem;
    dst->id = bp->elem_count + 1;
    bp->elem_count++;
    return dst->id;
}

static JobKind dblueprint_job_kind(BlueprintOpKind op)
{
    switch (op) {
        case BPOP_PLACE_ELEMENT:
        case BPOP_PLACE_MACHINE:
        case BPOP_MODIFY_TERRAIN:
            return JOB_BUILD;
        case BPOP_REMOVE_ELEMENT:
            return JOB_DECONSTRUCT;
        default:
            return JOB_CUSTOM;
    }
}

void dblueprint_generate_jobs(BlueprintId id)
{
    Blueprint *bp = dblueprint_lookup(id);
    JobId *job_map;
    U32 i, j;
    if (!bp || bp->elem_count == 0) return;
    job_map = (JobId*)malloc(sizeof(JobId) * bp->elem_count);
    if (!job_map) return;
    memset(job_map, 0, sizeof(JobId) * bp->elem_count);

    /* First pass: create jobs */
    for (i = 0; i < bp->elem_count; ++i) {
        BlueprintElement *be = &bp->elems[i];
        Job def;
        memset(&def, 0, sizeof(def));
        def.kind = dblueprint_job_kind(be->kind);
        def.state = JOB_PENDING;
        def.target_tile = be->tile;
        def.required_item = be->required_item;
        def.required_count = be->required_count;
        def.work_time_s = (Q16_16)(1 << 16); /* placeholder 1s */
        job_map[i] = djob_create(&def);
    }

    /* Second pass: apply dependencies */
    for (i = 0; i < bp->elem_count; ++i) {
        BlueprintElement *be = &bp->elems[i];
        JobId jid = job_map[i];
        Job *jptr = djob_get(jid);
        if (!jptr) continue;
        jptr->dep_count = 0;
        for (j = 0; j < be->dep_count && j < 4; ++j) {
            BlueprintElementId dep_elem = be->deps[j];
            U32 k;
            for (k = 0; k < bp->elem_count; ++k) {
                if (bp->elems[k].id == dep_elem) {
                    if (jptr->dep_count < 4) {
                        jptr->deps[jptr->dep_count++] = job_map[k];
                    }
                    break;
                }
            }
        }
    }

    free(job_map);
}

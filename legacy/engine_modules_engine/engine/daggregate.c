/*
FILE: source/domino/daggregate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / daggregate
RESPONSIBILITY: Implements `daggregate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/daggregate.h"

#include <string.h>

#define DAGG_MAX_AGGREGATES        512
#define DAGG_MAX_ELEMENTS          8192
#define DAGG_MAX_ELEMENTS_PER_AGG  512

static Aggregate g_aggregates[DAGG_MAX_AGGREGATES];
static bool      g_agg_used[DAGG_MAX_AGGREGATES];
static ElementId g_agg_elements[DAGG_MAX_AGGREGATES][DAGG_MAX_ELEMENTS_PER_AGG];

static Element   g_elements[DAGG_MAX_ELEMENTS];
static U32       g_element_count = 0;

static Aggregate *dagg_get_slot(AggregateId id)
{
    U32 idx;
    if (id == 0) return 0;
    idx = (U32)(id - 1);
    if (idx >= DAGG_MAX_AGGREGATES) return 0;
    if (!g_agg_used[idx]) return 0;
    return &g_aggregates[idx];
}

Aggregate *dagg_get(AggregateId id)
{
    return dagg_get_slot(id);
}

static Element *dagg_element_lookup(ElementId id)
{
    U32 i;
    for (i = 0; i < g_element_count; ++i) {
        if (g_elements[i].id == id) {
            return &g_elements[i];
        }
    }
    return 0;
}

static Element *dagg_element_ensure(ElementId id)
{
    Element *elem = dagg_element_lookup(id);
    if (elem) return elem;
    if (g_element_count >= DAGG_MAX_ELEMENTS) return 0;
    elem = &g_elements[g_element_count++];
    memset(elem, 0, sizeof(*elem));
    elem->id = id;
    return elem;
}

AggregateId dagg_create(AggregateMobilityKind mobility, EnvironmentKind env)
{
    U32 idx;
    Aggregate *agg = 0;
    for (idx = 0; idx < DAGG_MAX_AGGREGATES; ++idx) {
        if (!g_agg_used[idx]) {
            g_agg_used[idx] = true;
            agg = &g_aggregates[idx];
            break;
        }
    }
    if (!agg) return 0;

    memset(agg, 0, sizeof(*agg));
    agg->id = (AggregateId)(idx + 1);
    agg->mobility = mobility;
    agg->env = env;
    agg->element_ids = g_agg_elements[idx];
    agg->drag_coeff = 0;
    agg->lift_coeff = 0;
    agg->buoyancy_factor = 0;

    memset(g_agg_elements[idx], 0, sizeof(g_agg_elements[idx]));

    dagg_recompute_mass_volume(agg->id);
    return agg->id;
}

void dagg_destroy(AggregateId id)
{
    Aggregate *agg;
    U32 idx;
    U32 i;
    agg = dagg_get_slot(id);
    if (!agg) return;

    idx = (U32)(id - 1);
    for (i = 0; i < agg->element_count; ++i) {
        Element *elem = dagg_element_lookup(agg->element_ids[i]);
        if (elem) {
            elem->agg = 0;
        }
    }
    agg->element_count = 0;
    memset(g_agg_elements[idx], 0, sizeof(g_agg_elements[idx]));
    agg->element_ids = g_agg_elements[idx];
    agg->id = 0;
    agg->mobility = AGG_STATIC;
    agg->env = ENV_SURFACE_GRID;
    agg->mass = (MassKg)0;
    agg->volume = (VolM3)0;
    agg->drag_coeff = 0;
    agg->lift_coeff = 0;
    agg->buoyancy_factor = 0;
    g_agg_used[idx] = false;
}

bool dagg_attach_element(AggregateId agg_id, ElementId elem_id)
{
    Aggregate *agg;
    Element *elem;
    U32 i;
    agg = dagg_get_slot(agg_id);
    if (!agg) return false;
    if (agg->element_count >= DAGG_MAX_ELEMENTS_PER_AGG) return false;

    elem = dagg_element_ensure(elem_id);
    if (!elem) return false;
    if (elem->agg != 0 && elem->agg != agg_id) {
        /* Element already belongs elsewhere; require explicit detach */
        return false;
    }

    for (i = 0; i < agg->element_count; ++i) {
        if (agg->element_ids[i] == elem_id) {
            elem->agg = agg_id;
            return true;
        }
    }

    agg->element_ids[agg->element_count] = elem_id;
    agg->element_count++;
    elem->agg = agg_id;

    dagg_recompute_mass_volume(agg_id);
    return true;
}

bool dagg_detach_element(AggregateId agg_id, ElementId elem_id)
{
    Aggregate *agg;
    U32 i;
    agg = dagg_get_slot(agg_id);
    if (!agg) return false;

    for (i = 0; i < agg->element_count; ++i) {
        if (agg->element_ids[i] == elem_id) {
            Element *elem = dagg_element_lookup(elem_id);
            if (elem) {
                elem->agg = 0;
            }
            if (agg->element_count > 0) {
                agg->element_count--;
                agg->element_ids[i] = agg->element_ids[agg->element_count];
                agg->element_ids[agg->element_count] = 0;
            }
            dagg_recompute_mass_volume(agg_id);
            return true;
        }
    }
    return false;
}

void dagg_recompute_mass_volume(AggregateId agg_id)
{
    Aggregate *agg = dagg_get_slot(agg_id);
    if (!agg) return;

    agg->mass = (MassKg)((I64)agg->element_count);
    agg->volume = (VolM3)(((I64)agg->element_count) << 16);
    /* TODO: derive from materials, geometry, and fluid volume */
}

/*
FILE: game/rules/population/population_projections.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements epistemic population projections.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Projections update deterministically.
*/
#include "dominium/rules/population/population_projections.h"

#include <string.h>

void population_projection_registry_init(population_projection_registry* reg,
                                         population_projection* storage,
                                         u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->projections = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(population_projection) * (size_t)capacity);
    }
}

static u32 population_projection_find_index(const population_projection_registry* reg,
                                            u64 cohort_id,
                                            int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->projections) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->projections[i].cohort_id == cohort_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->projections[i].cohort_id > cohort_id) {
            break;
        }
    }
    return i;
}

int population_projection_report(population_projection_registry* reg,
                                 u64 cohort_id,
                                 u32 known_min,
                                 u32 known_max,
                                 dom_act_time_t report_tick)
{
    int found = 0;
    u32 idx;
    u32 i;
    population_projection* entry;

    if (!reg || !reg->projections) {
        return -1;
    }
    idx = population_projection_find_index(reg, cohort_id, &found);
    if (!found) {
        if (reg->count >= reg->capacity) {
            return -2;
        }
        for (i = reg->count; i > idx; --i) {
            reg->projections[i] = reg->projections[i - 1u];
        }
        reg->count += 1u;
    }
    entry = &reg->projections[idx];
    memset(entry, 0, sizeof(*entry));
    entry->cohort_id = cohort_id;
    entry->known_min = known_min;
    entry->known_max = (known_max < known_min) ? known_min : known_max;
    entry->report_tick = report_tick;
    entry->is_known = 1;
    return 0;
}

int population_projection_get(const population_projection_registry* reg,
                              u64 cohort_id,
                              population_projection* out_view)
{
    int found = 0;
    u32 idx;
    if (!out_view) {
        return -1;
    }
    memset(out_view, 0, sizeof(*out_view));
    out_view->cohort_id = cohort_id;
    out_view->is_known = 0;
    out_view->report_tick = DOM_TIME_ACT_MAX;
    if (!reg || !reg->projections) {
        return 0;
    }
    idx = population_projection_find_index(reg, cohort_id, &found);
    if (!found) {
        return 0;
    }
    *out_view = reg->projections[idx];
    return 0;
}

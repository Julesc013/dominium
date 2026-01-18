/*
FILE: game/rules/population/demographics.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements deterministic cohort bucket updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Bucket updates are deterministic and ordered.
*/
#include "dominium/rules/population/demographics.h"

#include <string.h>

static u32 population_bucket_sum(const u32* buckets, u32 count)
{
    u32 i;
    u32 sum = 0u;
    if (!buckets) {
        return 0u;
    }
    for (i = 0u; i < count; ++i) {
        sum += buckets[i];
    }
    return sum;
}

static void population_bucket_add(u32* buckets, u32 count, u32 add)
{
    if (!buckets || count == 0u) {
        return;
    }
    buckets[0] += add;
}

static void population_bucket_remove_from_tail(u32* buckets, u32 count, u32 remove)
{
    u32 i;
    if (!buckets || count == 0u) {
        return;
    }
    for (i = count; i > 0u && remove > 0u; --i) {
        u32 idx = i - 1u;
        u32 take = buckets[idx];
        if (take > remove) {
            buckets[idx] -= remove;
            return;
        }
        buckets[idx] = 0u;
        remove -= take;
    }
}

int population_demographics_init(population_cohort_state* cohort)
{
    if (!cohort) {
        return -1;
    }
    memset(cohort->age_buckets, 0, sizeof(cohort->age_buckets));
    memset(cohort->sex_buckets, 0, sizeof(cohort->sex_buckets));
    memset(cohort->health_buckets, 0, sizeof(cohort->health_buckets));
    if (cohort->count > 0u) {
        cohort->age_buckets[0] = cohort->count;
        cohort->sex_buckets[POPULATION_SEX_UNKNOWN_INDEX] = cohort->count;
        cohort->health_buckets[POPULATION_HEALTH_DEFAULT_INDEX] = cohort->count;
    }
    return 0;
}

int population_demographics_validate(const population_cohort_state* cohort,
                                     population_refusal_code* out_refusal)
{
    u32 age_sum;
    u32 sex_sum;
    u32 health_sum;
    if (out_refusal) {
        *out_refusal = POP_REFUSAL_NONE;
    }
    if (!cohort) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_INVALID_BUCKET_DISTRIBUTION;
        }
        return -1;
    }
    age_sum = population_bucket_sum(cohort->age_buckets, POPULATION_AGE_BUCKETS);
    sex_sum = population_bucket_sum(cohort->sex_buckets, POPULATION_SEX_BUCKETS);
    health_sum = population_bucket_sum(cohort->health_buckets, POPULATION_HEALTH_BUCKETS);
    if (age_sum != cohort->count ||
        sex_sum != cohort->count ||
        health_sum != cohort->count) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_INVALID_BUCKET_DISTRIBUTION;
        }
        return -2;
    }
    return 0;
}

int population_demographics_apply_delta(population_cohort_state* cohort,
                                        i32 delta,
                                        u64 provenance_mix,
                                        population_refusal_code* out_refusal)
{
    u32 add;
    u32 remove;
    u32 next;
    if (out_refusal) {
        *out_refusal = POP_REFUSAL_NONE;
    }
    if (!cohort) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_COHORT_NOT_FOUND;
        }
        return -1;
    }
    if (delta == 0) {
        return 0;
    }
    if (delta > 0) {
        add = (u32)delta;
        cohort->count += add;
        population_bucket_add(cohort->age_buckets, POPULATION_AGE_BUCKETS, add);
        cohort->sex_buckets[POPULATION_SEX_UNKNOWN_INDEX] += add;
        cohort->health_buckets[POPULATION_HEALTH_DEFAULT_INDEX] += add;
    } else {
        remove = (u32)(-delta);
        if (remove > cohort->count) {
            remove = cohort->count;
        }
        next = cohort->count - remove;
        population_bucket_remove_from_tail(cohort->age_buckets, POPULATION_AGE_BUCKETS, remove);
        population_bucket_remove_from_tail(cohort->sex_buckets, POPULATION_SEX_BUCKETS, remove);
        population_bucket_remove_from_tail(cohort->health_buckets, POPULATION_HEALTH_BUCKETS, remove);
        cohort->count = next;
    }
    cohort->provenance_summary_hash ^= provenance_mix;
    return 0;
}

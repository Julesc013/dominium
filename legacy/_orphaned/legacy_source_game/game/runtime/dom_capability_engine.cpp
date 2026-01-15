/*
FILE: source/dominium/game/runtime/dom_capability_engine.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/capability_engine
RESPONSIBILITY: Derives capability snapshots from belief/time knowledge inputs.
*/
#include "runtime/dom_capability_engine.h"

#include <algorithm>
#include <vector>

namespace {

static u64 u64_max(void) {
    return (u64)~(u64)0;
}

static i64 i64_max(void) {
    return (i64)0x7fffffffffffffffLL;
}

static i64 i64_min(void) {
    return (i64)(-0x7fffffffffffffffLL - 1LL);
}

static int compare_subject(const dom_capability_subject &a,
                           const dom_capability_subject &b) {
    if (a.kind != b.kind) {
        return (a.kind < b.kind) ? -1 : 1;
    }
    if (a.id != b.id) {
        return (a.id < b.id) ? -1 : 1;
    }
    return 0;
}

static int compare_capability(const dom_capability &a, const dom_capability &b) {
    if (a.capability_id != b.capability_id) {
        return (a.capability_id < b.capability_id) ? -1 : 1;
    }
    {
        const int cmp = compare_subject(a.subject, b.subject);
        if (cmp != 0) {
            return cmp;
        }
    }
    if (a.source_provenance != b.source_provenance) {
        return (a.source_provenance < b.source_provenance) ? -1 : 1;
    }
    if (a.observed_tick != b.observed_tick) {
        return (a.observed_tick < b.observed_tick) ? -1 : 1;
    }
    return 0;
}

static bool capability_less(const dom_capability &a, const dom_capability &b) {
    return compare_capability(a, b) < 0;
}

static u64 scale_u64(u64 value, i32 scale_q16) {
    const u64 max = u64_max();
    u64 scale;
    if (scale_q16 <= 0) {
        scale = 1u << 16;
    } else {
        scale = (u64)scale_q16;
    }
    if (value == 0u) {
        return 0u;
    }
    if (scale > 0u && value > (max / scale)) {
        return max;
    }
    return (value * scale) >> 16;
}

static i64 clamp_i64_add(i64 base, i64 delta) {
    if (delta > 0 && base > (i64_max() - delta)) {
        return i64_max();
    }
    if (delta < 0 && base < (i64_min() - delta)) {
        return i64_min();
    }
    return base + delta;
}

static void apply_filters(dom_capability &cap, const dom_capability_filters *filters) {
    if (!filters) {
        return;
    }
    if (filters->latency_scale_q16 != 0 && filters->latency_scale_q16 != (1 << 16)) {
        u64 scaled = scale_u64(cap.latency_ticks, filters->latency_scale_q16);
        if (scaled != cap.latency_ticks) {
            cap.flags |= DOM_CAPABILITY_FLAG_DEGRADED;
        }
        cap.latency_ticks = scaled;
    }
    if (filters->uncertainty_scale_q16 != 0 && filters->uncertainty_scale_q16 != (1 << 16)) {
        i64 min_val = cap.value_min;
        i64 max_val = cap.value_max;
        if (max_val < min_val) {
            i64 tmp = min_val;
            min_val = max_val;
            max_val = tmp;
        }
        {
            const i64 span = max_val - min_val;
            const i64 half = span / 2;
            const u64 new_half = scale_u64((u64)((half < 0) ? 0 : half),
                                           filters->uncertainty_scale_q16);
            const i64 mid = min_val + half;
            cap.value_min = clamp_i64_add(mid, (i64)-(i64)new_half);
            cap.value_max = clamp_i64_add(mid, (i64)new_half);
            if (new_half != (u64)half) {
                cap.flags |= DOM_CAPABILITY_FLAG_DEGRADED;
            }
        }
    }
    if (filters->staleness_grace_ticks > 0u &&
        cap.staleness_ticks <= (u64)filters->staleness_grace_ticks) {
        cap.staleness_ticks = 0u;
        cap.flags &= ~DOM_CAPABILITY_FLAG_STALE;
    }
}

static void append_time_knowledge(std::vector<dom_capability> &out,
                                  dom_time_actor_id actor_id,
                                  const dom_time_knowledge *knowledge,
                                  dom_tick tick,
                                  dom_ups ups,
                                  const dom_time_clock_env *env,
                                  const dom_capability_filters *filters) {
    u32 count = 0u;
    u32 cal_count = 0u;
    if (!knowledge) {
        return;
    }

    (void)dom_time_knowledge_sample_all(knowledge, tick, ups, env, 0, 0u, &count);
    if (count > 0u) {
        std::vector<dom_time_clock_reading> readings(count);
        (void)dom_time_knowledge_sample_all(knowledge,
                                            tick,
                                            ups,
                                            env,
                                            &readings[0],
                                            count,
                                            &count);
        for (u32 i = 0u; i < count; ++i) {
            const dom_time_clock_reading &reading = readings[i];
            dom_capability cap;
            cap.capability_id = DOM_CAP_TIME_READOUT;
            cap.subject.kind = DOM_CAP_SUBJECT_CLOCK;
            cap.subject.id = reading.clock_id;
            cap.observed_tick = tick;
            cap.delivery_tick = tick;
            cap.expiry_tick = 0;
            cap.latency_ticks = 0u;
            cap.staleness_ticks = 0u;
            cap.source_provenance = reading.clock_id;
            cap.flags = 0u;

            if (reading.flags & DOM_TIME_CLOCK_READING_DEGRADED) {
                cap.flags |= DOM_CAPABILITY_FLAG_DEGRADED;
            }
            if (reading.flags & DOM_TIME_CLOCK_READING_UNKNOWN ||
                reading.flags & DOM_TIME_CLOCK_READING_UNAVAILABLE) {
                cap.flags |= DOM_CAPABILITY_FLAG_UNKNOWN;
                cap.resolution_tier = DOM_RESOLUTION_UNKNOWN;
                cap.value_min = 0;
                cap.value_max = 0;
                apply_filters(cap, filters);
                out.push_back(cap);
                continue;
            }

            cap.resolution_tier = (reading.uncertainty_seconds == 0u)
                ? DOM_RESOLUTION_EXACT
                : DOM_RESOLUTION_BOUNDED;
            cap.value_min = (i64)reading.observed_act - (i64)reading.uncertainty_seconds;
            cap.value_max = (i64)reading.observed_act + (i64)reading.uncertainty_seconds;
            apply_filters(cap, filters);
            out.push_back(cap);
        }
    }

    (void)dom_time_knowledge_list_calendars(knowledge, 0, 0u, &cal_count);
    if (cal_count > 0u) {
        std::vector<dom_calendar_id> calendars(cal_count);
        (void)dom_time_knowledge_list_calendars(knowledge,
                                                &calendars[0],
                                                cal_count,
                                                &cal_count);
        for (u32 i = 0u; i < cal_count; ++i) {
            dom_capability cap;
            cap.capability_id = DOM_CAP_CALENDAR_VIEW;
            cap.subject.kind = DOM_CAP_SUBJECT_CALENDAR;
            cap.subject.id = calendars[i];
            cap.resolution_tier = DOM_RESOLUTION_BINARY;
            cap.value_min = 0;
            cap.value_max = 0;
            cap.observed_tick = tick;
            cap.delivery_tick = tick;
            cap.expiry_tick = 0;
            cap.latency_ticks = 0u;
            cap.staleness_ticks = 0u;
            cap.source_provenance = calendars[i];
            cap.flags = 0u;
            (void)actor_id;
            apply_filters(cap, filters);
            out.push_back(cap);
        }
    }
}

} // namespace

struct dom_capability_engine {
    std::vector<dom_capability> cache;
    dom_capability_snapshot snapshot;
    u64 last_belief_revision;
    u64 last_time_revision;
    dom_tick last_tick;
    d_bool has_cache;
};

dom_capability_engine *dom_capability_engine_create(void) {
    dom_capability_engine *engine = new dom_capability_engine();
    if (!engine) {
        return 0;
    }
    if (dom_capability_engine_init(engine) != DOM_CAPABILITY_ENGINE_OK) {
        delete engine;
        return 0;
    }
    return engine;
}

void dom_capability_engine_destroy(dom_capability_engine *engine) {
    if (!engine) {
        return;
    }
    delete engine;
}

int dom_capability_engine_init(dom_capability_engine *engine) {
    if (!engine) {
        return DOM_CAPABILITY_ENGINE_INVALID_ARGUMENT;
    }
    engine->cache.clear();
    engine->snapshot.tick = 0;
    engine->snapshot.capability_count = 0u;
    engine->snapshot.capabilities = 0;
    engine->last_belief_revision = 0u;
    engine->last_time_revision = 0u;
    engine->last_tick = 0;
    engine->has_cache = D_FALSE;
    return DOM_CAPABILITY_ENGINE_OK;
}

const dom_capability_snapshot *dom_capability_engine_build_snapshot(
    dom_capability_engine *engine,
    dom_time_actor_id actor_id,
    const dom_belief_store *belief_store,
    const dom_time_knowledge *time_knowledge,
    dom_tick tick,
    dom_ups ups,
    const dom_time_clock_env *clock_env,
    const dom_capability_filters *filters) {
    u64 belief_revision = 0u;
    u64 time_revision = 0u;
    u32 record_count = 0u;
    std::vector<dom_belief_record> records;

    if (!engine) {
        return 0;
    }
    if (belief_store) {
        if (dom_belief_store_get_revision(belief_store, &belief_revision) != DOM_BELIEF_OK) {
            return 0;
        }
    }
    if (time_knowledge) {
        if (dom_time_knowledge_get_revision(time_knowledge, &time_revision) != DOM_TIME_KNOWLEDGE_OK) {
            return 0;
        }
    }

    if (engine->has_cache == D_TRUE &&
        engine->last_tick == tick &&
        engine->last_belief_revision == belief_revision &&
        engine->last_time_revision == time_revision) {
        return &engine->snapshot;
    }

    engine->cache.clear();

    if (belief_store) {
        (void)dom_belief_store_list_records(belief_store, 0, 0u, &record_count);
        if (record_count > 0u) {
            records.resize(record_count);
            (void)dom_belief_store_list_records(belief_store,
                                                &records[0],
                                                record_count,
                                                &record_count);
        }
    }

    if (record_count > 0u) {
        size_t i = 0u;
        while (i < record_count) {
            const dom_belief_record &first = records[i];
            size_t j = i + 1u;
            i64 range_min = first.value_min;
            i64 range_max = first.value_max;
            u32 min_resolution = first.resolution_tier;
            dom_belief_record best = first;
            u32 flags = 0u;
            u32 conflict = 0u;

            while (j < record_count) {
                const dom_belief_record &rec = records[j];
                if (rec.capability_id != first.capability_id ||
                    compare_subject(rec.subject, first.subject) != 0) {
                    break;
                }
                if (rec.value_min < range_min) range_min = rec.value_min;
                if (rec.value_max > range_max) range_max = rec.value_max;
                if (rec.resolution_tier < min_resolution) {
                    min_resolution = rec.resolution_tier;
                }
                if (rec.delivery_tick > best.delivery_tick ||
                    (rec.delivery_tick == best.delivery_tick && rec.record_id > best.record_id)) {
                    best = rec;
                }
                if (rec.source_provenance != first.source_provenance ||
                    rec.value_min != first.value_min ||
                    rec.value_max != first.value_max) {
                    conflict = 1u;
                }
                ++j;
            }

            {
                dom_capability cap;
                cap.capability_id = first.capability_id;
                cap.subject = first.subject;
                cap.value_min = range_min;
                cap.value_max = range_max;
                cap.observed_tick = best.observed_tick;
                cap.delivery_tick = best.delivery_tick;
                cap.expiry_tick = best.expiry_tick;
                cap.source_provenance = best.source_provenance;
                cap.latency_ticks = (best.delivery_tick > best.observed_tick)
                    ? (u64)(best.delivery_tick - best.observed_tick)
                    : 0u;
                cap.staleness_ticks = (tick > best.delivery_tick)
                    ? (u64)(tick - best.delivery_tick)
                    : 0u;
                flags = 0u;
                if (best.flags & DOM_BELIEF_FLAG_UNKNOWN) {
                    flags |= DOM_CAPABILITY_FLAG_UNKNOWN;
                    cap.resolution_tier = DOM_RESOLUTION_UNKNOWN;
                } else {
                    cap.resolution_tier = min_resolution;
                }
                if (best.flags & DOM_BELIEF_FLAG_STALE) {
                    flags |= DOM_CAPABILITY_FLAG_STALE;
                }
                if (best.expiry_tick != 0 && tick > best.expiry_tick) {
                    flags |= DOM_CAPABILITY_FLAG_STALE;
                }
                if (conflict) {
                    flags |= DOM_CAPABILITY_FLAG_CONFLICT;
                }
                cap.flags = flags;
                apply_filters(cap, filters);
                engine->cache.push_back(cap);
            }
            i = j;
        }
    }

    append_time_knowledge(engine->cache,
                          actor_id,
                          time_knowledge,
                          tick,
                          ups,
                          clock_env,
                          filters);

    if (!engine->cache.empty()) {
        std::sort(engine->cache.begin(), engine->cache.end(), capability_less);
    }

    engine->snapshot.tick = tick;
    engine->snapshot.capability_count = (u32)engine->cache.size();
    engine->snapshot.capabilities = engine->cache.empty() ? 0 : &engine->cache[0];
    engine->last_belief_revision = belief_revision;
    engine->last_time_revision = time_revision;
    engine->last_tick = tick;
    engine->has_cache = D_TRUE;
    return &engine->snapshot;
}

int dom_capability_snapshot_list(const dom_capability_snapshot *snapshot,
                                 dom_capability *out_caps,
                                 u32 max_caps,
                                 u32 *out_count) {
    if (!snapshot || !out_count) {
        return DOM_CAPABILITY_ENGINE_INVALID_ARGUMENT;
    }
    *out_count = snapshot->capability_count;
    if (!out_caps || max_caps == 0u) {
        return DOM_CAPABILITY_ENGINE_OK;
    }
    {
        const u32 limit = (max_caps < snapshot->capability_count)
            ? max_caps
            : snapshot->capability_count;
        for (u32 i = 0u; i < limit; ++i) {
            out_caps[i] = snapshot->capabilities[i];
        }
    }
    return DOM_CAPABILITY_ENGINE_OK;
}

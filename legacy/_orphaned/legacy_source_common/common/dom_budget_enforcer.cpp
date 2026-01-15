/*
FILE: source/dominium/common/dom_budget_enforcer.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_budget_enforcer
RESPONSIBILITY: Budget limits and enforcement state for non-authoritative work.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C89/C++98 headers.
FORBIDDEN DEPENDENCIES: OS headers; authoritative sim logic.
*/
#include "dom_budget_enforcer.h"

#include <cstring>

#include "dominium/caps_split.h"

namespace {

static u32 sanitize_tier(u32 tier) {
    if (tier == dom::DOM_PERF_TIER_MODERN || tier == dom::DOM_PERF_TIER_SERVER) {
        return tier;
    }
    return dom::DOM_PERF_TIER_BASELINE;
}

static void set_baseline(dom_budget_limits *limits) {
    limits->sim_tick_cost_ms_max = 12u;
    limits->derived_jobs_ms_per_frame_max = 2u;
    limits->derived_io_bytes_per_frame_max = 256u * 1024u;
    limits->derived_jobs_per_frame_max = 4u;
    limits->render_submit_ms_max = 8u;
    limits->max_active_bubbles = 1u;
    limits->max_surface_chunks_active = 256u;
    limits->max_entities_per_bubble = 2048u;
    limits->max_ai_ops_per_tick = 8u;
    limits->max_ai_factions_per_tick = 4u;
    limits->max_cosmo_entities_iterated_per_tick = 4096u;
}

static void set_modern(dom_budget_limits *limits) {
    limits->sim_tick_cost_ms_max = 12u;
    limits->derived_jobs_ms_per_frame_max = 4u;
    limits->derived_io_bytes_per_frame_max = 512u * 1024u;
    limits->derived_jobs_per_frame_max = 8u;
    limits->render_submit_ms_max = 10u;
    limits->max_active_bubbles = 1u;
    limits->max_surface_chunks_active = 512u;
    limits->max_entities_per_bubble = 4096u;
    limits->max_ai_ops_per_tick = 16u;
    limits->max_ai_factions_per_tick = 8u;
    limits->max_cosmo_entities_iterated_per_tick = 8192u;
}

static void set_server(dom_budget_limits *limits) {
    limits->sim_tick_cost_ms_max = 16u;
    limits->derived_jobs_ms_per_frame_max = 8u;
    limits->derived_io_bytes_per_frame_max = 2u * 1024u * 1024u;
    limits->derived_jobs_per_frame_max = 16u;
    limits->render_submit_ms_max = 0u;
    limits->max_active_bubbles = 1u;
    limits->max_surface_chunks_active = 1024u;
    limits->max_entities_per_bubble = 8192u;
    limits->max_ai_ops_per_tick = 32u;
    limits->max_ai_factions_per_tick = 16u;
    limits->max_cosmo_entities_iterated_per_tick = 16384u;
}

static u32 min_u32(u32 a, u32 b) {
    return (a < b) ? a : b;
}

static u32 clamp_to_limit(u32 value, u32 limit) {
    if (value == 0u) {
        return 0u;
    }
    if (limit == 0u) {
        return value;
    }
    return min_u32(value, limit);
}

static u32 scale_budget(u32 value, u32 numerator, u32 denominator) {
    if (value == 0u || denominator == 0u) {
        return value;
    }
    {
        const u64 scaled = (u64)value * (u64)numerator / (u64)denominator;
        if (scaled == 0u) {
            return 1u;
        }
        return (u32)scaled;
    }
}

static u32 scaled_by_pressure(u32 base, u32 pressure) {
    if (pressure == 0u) {
        return base;
    }
    if (pressure == 1u) {
        return scale_budget(base, 3u, 4u);
    }
    if (pressure == 2u) {
        return scale_budget(base, 1u, 2u);
    }
    return scale_budget(base, 1u, 4u);
}

static u32 fidelity_for_pressure(u32 pressure) {
    switch (pressure) {
    case 0u:
        return DOM_BUDGET_FIDELITY_HIGH;
    case 1u:
        return DOM_BUDGET_FIDELITY_MED;
    case 2u:
        return DOM_BUDGET_FIDELITY_LOW;
    default:
        break;
    }
    return DOM_BUDGET_FIDELITY_MIN;
}

} // namespace

int dom_budget_limits_for_tier(u32 perf_tier, dom_budget_limits *out_limits) {
    if (!out_limits) {
        return -1;
    }
    std::memset(out_limits, 0, sizeof(*out_limits));
    out_limits->struct_size = (u32)sizeof(*out_limits);
    out_limits->struct_version = DOM_BUDGET_LIMITS_VERSION;

    perf_tier = sanitize_tier(perf_tier);
    out_limits->perf_tier = perf_tier;
    switch (perf_tier) {
    case dom::DOM_PERF_TIER_MODERN:
        set_modern(out_limits);
        break;
    case dom::DOM_PERF_TIER_SERVER:
        set_server(out_limits);
        break;
    case dom::DOM_PERF_TIER_BASELINE:
    default:
        set_baseline(out_limits);
        break;
    }
    return 0;
}

int dom_budget_enforcer_init(dom_budget_enforcer *enforcer,
                             const dom_budget_limits *limits) {
    if (!enforcer || !limits) {
        return -1;
    }
    std::memset(enforcer, 0, sizeof(*enforcer));
    enforcer->limits = *limits;
    enforcer->base_derived_budget_ms = limits->derived_jobs_ms_per_frame_max;
    enforcer->base_derived_budget_io_bytes = limits->derived_io_bytes_per_frame_max;
    enforcer->base_derived_budget_jobs = limits->derived_jobs_per_frame_max;
    enforcer->pressure = 0u;

    std::memset(&enforcer->state, 0, sizeof(enforcer->state));
    enforcer->state.struct_size = (u32)sizeof(enforcer->state);
    enforcer->state.struct_version = DOM_BUDGET_STATE_VERSION;
    enforcer->state.over_mask = 0u;
    enforcer->state.pressure = 0u;
    enforcer->state.fidelity_max = DOM_BUDGET_FIDELITY_HIGH;
    enforcer->state.derived_budget_ms = enforcer->base_derived_budget_ms;
    enforcer->state.derived_budget_io_bytes = enforcer->base_derived_budget_io_bytes;
    enforcer->state.derived_budget_jobs = enforcer->base_derived_budget_jobs;
    enforcer->state.ai_max_ops_per_tick = limits->max_ai_ops_per_tick;
    enforcer->state.ai_max_factions_per_tick = limits->max_ai_factions_per_tick;
    enforcer->state.max_active_bubbles = limits->max_active_bubbles;
    enforcer->state.max_surface_chunks_active = limits->max_surface_chunks_active;
    enforcer->state.max_entities_per_bubble = limits->max_entities_per_bubble;
    enforcer->state.max_cosmo_entities_iterated_per_tick = limits->max_cosmo_entities_iterated_per_tick;
    return 0;
}

int dom_budget_enforcer_set_base_derived(dom_budget_enforcer *enforcer,
                                         u32 base_ms,
                                         u32 base_io_bytes,
                                         u32 base_jobs) {
    if (!enforcer) {
        return -1;
    }
    enforcer->base_derived_budget_ms = base_ms;
    enforcer->base_derived_budget_io_bytes = base_io_bytes;
    enforcer->base_derived_budget_jobs = base_jobs;
    return 0;
}

int dom_budget_enforcer_update(dom_budget_enforcer *enforcer,
                               const dom_profiler_frame *frame,
                               const dom_budget_derived_sample *derived,
                               u32 active_bubbles,
                               u32 active_surface_chunks) {
    u32 over_mask = 0u;
    u32 pressure;
    u32 base_ms;
    u32 base_io;
    u32 base_jobs;
    u32 scaled_ms;
    u32 scaled_io;
    u32 scaled_jobs;

    if (!enforcer) {
        return -1;
    }

    if (frame) {
        if (enforcer->limits.sim_tick_cost_ms_max > 0u) {
            const u64 limit_us = (u64)enforcer->limits.sim_tick_cost_ms_max * 1000ull;
            if (frame->zones[DOM_PROFILER_ZONE_SIM_TICK].last_us > limit_us) {
                over_mask |= DOM_BUDGET_OVER_SIM_TICK;
            }
        }
        if (enforcer->limits.render_submit_ms_max > 0u) {
            const u64 limit_us = (u64)enforcer->limits.render_submit_ms_max * 1000ull;
            if (frame->zones[DOM_PROFILER_ZONE_RENDER_SUBMIT].last_us > limit_us) {
                over_mask |= DOM_BUDGET_OVER_RENDER_SUBMIT;
            }
        }
    }

    if (derived) {
        if (enforcer->limits.derived_jobs_ms_per_frame_max > 0u &&
            derived->last_pump_ms > enforcer->limits.derived_jobs_ms_per_frame_max) {
            over_mask |= DOM_BUDGET_OVER_DERIVED_MS;
        }
        if (enforcer->limits.derived_io_bytes_per_frame_max > 0u &&
            derived->last_pump_io_bytes > enforcer->limits.derived_io_bytes_per_frame_max) {
            over_mask |= DOM_BUDGET_OVER_DERIVED_IO;
        }
        if (enforcer->limits.derived_jobs_per_frame_max > 0u &&
            derived->last_pump_jobs > enforcer->limits.derived_jobs_per_frame_max) {
            over_mask |= DOM_BUDGET_OVER_DERIVED_JOBS;
        }
    }

    if (enforcer->limits.max_surface_chunks_active > 0u &&
        active_surface_chunks > enforcer->limits.max_surface_chunks_active) {
        over_mask |= DOM_BUDGET_OVER_SURFACE_CHUNKS;
    }
    if (enforcer->limits.max_active_bubbles > 0u &&
        active_bubbles > enforcer->limits.max_active_bubbles) {
        over_mask |= DOM_BUDGET_OVER_ACTIVE_BUBBLES;
    }

    pressure = enforcer->pressure;
    if (over_mask != 0u) {
        if (pressure < 3u) {
            pressure += 1u;
        }
    } else if (pressure > 0u) {
        pressure -= 1u;
    }
    enforcer->pressure = pressure;

    base_ms = clamp_to_limit(enforcer->base_derived_budget_ms,
                             enforcer->limits.derived_jobs_ms_per_frame_max);
    base_io = clamp_to_limit(enforcer->base_derived_budget_io_bytes,
                             enforcer->limits.derived_io_bytes_per_frame_max);
    base_jobs = clamp_to_limit(enforcer->base_derived_budget_jobs,
                               enforcer->limits.derived_jobs_per_frame_max);

    scaled_ms = scaled_by_pressure(base_ms, pressure);
    scaled_io = scaled_by_pressure(base_io, pressure);
    scaled_jobs = scaled_by_pressure(base_jobs, pressure);

    enforcer->state.struct_size = (u32)sizeof(enforcer->state);
    enforcer->state.struct_version = DOM_BUDGET_STATE_VERSION;
    enforcer->state.over_mask = over_mask;
    enforcer->state.pressure = pressure;
    enforcer->state.fidelity_max = fidelity_for_pressure(pressure);
    enforcer->state.derived_budget_ms = scaled_ms;
    enforcer->state.derived_budget_io_bytes = scaled_io;
    enforcer->state.derived_budget_jobs = scaled_jobs;
    enforcer->state.ai_max_ops_per_tick = enforcer->limits.max_ai_ops_per_tick;
    enforcer->state.ai_max_factions_per_tick = enforcer->limits.max_ai_factions_per_tick;
    enforcer->state.max_active_bubbles = enforcer->limits.max_active_bubbles;
    enforcer->state.max_surface_chunks_active = enforcer->limits.max_surface_chunks_active;
    enforcer->state.max_entities_per_bubble = enforcer->limits.max_entities_per_bubble;
    enforcer->state.max_cosmo_entities_iterated_per_tick =
        enforcer->limits.max_cosmo_entities_iterated_per_tick;

    return 0;
}

int dom_budget_enforcer_get_state(const dom_budget_enforcer *enforcer,
                                  dom_budget_state *out_state) {
    if (!enforcer || !out_state) {
        return -1;
    }
    *out_state = enforcer->state;
    return 0;
}

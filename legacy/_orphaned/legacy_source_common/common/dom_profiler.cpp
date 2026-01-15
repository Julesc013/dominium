/*
FILE: source/dominium/common/dom_profiler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_profiler
RESPONSIBILITY: Implements lightweight profiling for runtime subsystems.
*/
#include "dom_profiler.h"

#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/sys.h"
}

namespace {

struct DomProfilerState {
    u64 frame_start_us;
    dom_profiler_zone_stats accum[DOM_PROFILER_ZONE_COUNT];
    dom_profiler_frame last_frame;
};

static DomProfilerState g_state;

static void reset_stats(dom_profiler_zone_stats *stats) {
    if (!stats) {
        return;
    }
    std::memset(stats, 0, sizeof(*stats) * DOM_PROFILER_ZONE_COUNT);
}

static void init_frame(dom_profiler_frame *frame) {
    if (!frame) {
        return;
    }
    frame->struct_size = sizeof(*frame);
    frame->struct_version = DOM_PROFILER_FRAME_VERSION;
    frame->frame_us = 0u;
    std::memset(frame->zones, 0, sizeof(frame->zones));
}

} // namespace

extern "C" {

void dom_profiler_reset(void) {
    g_state.frame_start_us = 0u;
    reset_stats(g_state.accum);
    init_frame(&g_state.last_frame);
}

void dom_profiler_begin_frame(void) {
    g_state.frame_start_us = dsys_time_now_us();
    reset_stats(g_state.accum);
}

void dom_profiler_end_frame(void) {
    const u64 end_us = dsys_time_now_us();
    g_state.last_frame.struct_size = sizeof(g_state.last_frame);
    g_state.last_frame.struct_version = DOM_PROFILER_FRAME_VERSION;
    g_state.last_frame.frame_us = (g_state.frame_start_us > 0u)
                                      ? (end_us - g_state.frame_start_us)
                                      : 0u;
    for (u32 i = 0u; i < DOM_PROFILER_ZONE_COUNT; ++i) {
        g_state.last_frame.zones[i] = g_state.accum[i];
    }
}

u64 dom_profiler_begin_zone(u32 zone) {
    if (zone >= DOM_PROFILER_ZONE_COUNT) {
        return 0u;
    }
    return dsys_time_now_us();
}

void dom_profiler_end_zone(u32 zone, u64 token) {
    if (zone >= DOM_PROFILER_ZONE_COUNT || token == 0u) {
        return;
    }
    const u64 end_us = dsys_time_now_us();
    const u64 delta = (end_us >= token) ? (end_us - token) : 0u;
    dom_profiler_zone_stats &stats = g_state.accum[zone];
    stats.total_us += delta;
    stats.last_us = delta;
    stats.hits += 1u;
}

int dom_profiler_get_last_frame(dom_profiler_frame *out_frame) {
    if (!out_frame) {
        return -1;
    }
    *out_frame = g_state.last_frame;
    return 0;
}

const char *dom_profiler_zone_name(u32 zone) {
    switch (zone) {
    case DOM_PROFILER_ZONE_SIM_TICK:
        return "sim_tick";
    case DOM_PROFILER_ZONE_LANE_UPDATE:
        return "lane_update";
    case DOM_PROFILER_ZONE_ORBIT_UPDATE:
        return "orbit_update";
    case DOM_PROFILER_ZONE_SURFACE_STREAM:
        return "surface_streaming";
    case DOM_PROFILER_ZONE_DERIVED_PUMP:
        return "derived_pump";
    case DOM_PROFILER_ZONE_AI:
        return "ai_scheduler";
    case DOM_PROFILER_ZONE_NET_PUMP:
        return "net_pump";
    case DOM_PROFILER_ZONE_RENDER_SUBMIT:
        return "render_submit";
    case DOM_PROFILER_ZONE_INPUT:
        return "input_pump";
    default:
        break;
    }
    return "unknown";
}

int dom_profiler_write_json(const dom_profiler_frame *frame, const char *path) {
    FILE *fh;
    if (!frame || !path || !path[0]) {
        return -1;
    }
    fh = std::fopen(path, "wb");
    if (!fh) {
        return -1;
    }
    std::fprintf(fh, "{\n");
    std::fprintf(fh, "  \"schema_version\": %u,\n",
                 (unsigned)frame->struct_version);
    std::fprintf(fh, "  \"frame_us\": %llu,\n",
                 (unsigned long long)frame->frame_us);
    std::fprintf(fh, "  \"zones\": [\n");
    for (u32 i = 0u; i < DOM_PROFILER_ZONE_COUNT; ++i) {
        const dom_profiler_zone_stats &z = frame->zones[i];
        const char *name = dom_profiler_zone_name(i);
        std::fprintf(fh,
                     "    {\"id\": %u, \"name\": \"%s\", \"total_us\": %llu, \"last_us\": %llu, \"hits\": %u}%s\n",
                     (unsigned)i,
                     name ? name : "unknown",
                     (unsigned long long)z.total_us,
                     (unsigned long long)z.last_us,
                     (unsigned)z.hits,
                     (i + 1u < DOM_PROFILER_ZONE_COUNT) ? "," : "");
    }
    std::fprintf(fh, "  ]\n");
    std::fprintf(fh, "}\n");
    std::fclose(fh);
    return 0;
}

} /* extern "C" */

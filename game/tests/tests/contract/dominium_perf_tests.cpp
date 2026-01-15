/*
FILE: tests/contract/dominium_perf_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for performance budgets and derived work limits.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Derived-only; does not alter authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md`.
*/
#include <cstdio>
#include <cstring>

#include "dom_budget_enforcer.h"
#include "dom_profiler.h"
#include "dominium/caps_split.h"
#include "runtime/dom_derived_jobs.h"
#include "runtime/dom_surface_chunks.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void init_frame(dom_profiler_frame &frame) {
    std::memset(&frame, 0, sizeof(frame));
    frame.struct_size = sizeof(frame);
    frame.struct_version = DOM_PROFILER_FRAME_VERSION;
}

static int test_baseline_perf_sim(void) {
    dom_budget_limits limits;
    dom_budget_enforcer enforcer;
    dom_budget_state state;
    dom_budget_derived_sample sample;
    dom_profiler_frame frame;

    if (dom_budget_limits_for_tier(dom::DOM_PERF_TIER_BASELINE, &limits) != 0) {
        return fail("failed to fetch baseline budget limits");
    }
    if (dom_budget_enforcer_init(&enforcer, &limits) != 0) {
        return fail("failed to init budget enforcer");
    }
    (void)dom_budget_enforcer_set_base_derived(&enforcer,
                                               limits.derived_jobs_ms_per_frame_max,
                                               limits.derived_io_bytes_per_frame_max,
                                               limits.derived_jobs_per_frame_max);

    std::memset(&sample, 0, sizeof(sample));
    init_frame(frame);

    if (dom_budget_enforcer_update(&enforcer, &frame, &sample, 0u, 0u) != 0) {
        return fail("budget update failed");
    }
    if (dom_budget_enforcer_get_state(&enforcer, &state) != 0) {
        return fail("budget state fetch failed");
    }
    if (state.over_mask != 0u) {
        return fail("expected no over-budget flags for baseline sample");
    }
    if (state.fidelity_max != DOM_BUDGET_FIDELITY_HIGH) {
        return fail("expected high fidelity under baseline budgets");
    }
    if (state.derived_budget_ms != limits.derived_jobs_ms_per_frame_max) {
        return fail("derived ms budget mismatch");
    }
    return 0;
}

static int test_warp_perf(void) {
    dom_budget_limits limits;
    dom_budget_enforcer enforcer;
    dom_budget_state state;
    dom_budget_derived_sample sample;
    dom_profiler_frame frame;

    if (dom_budget_limits_for_tier(dom::DOM_PERF_TIER_BASELINE, &limits) != 0) {
        return fail("failed to fetch baseline budget limits");
    }
    if (dom_budget_enforcer_init(&enforcer, &limits) != 0) {
        return fail("failed to init budget enforcer");
    }
    (void)dom_budget_enforcer_set_base_derived(&enforcer,
                                               limits.derived_jobs_ms_per_frame_max,
                                               limits.derived_io_bytes_per_frame_max,
                                               limits.derived_jobs_per_frame_max);

    std::memset(&sample, 0, sizeof(sample));
    init_frame(frame);
    frame.zones[DOM_PROFILER_ZONE_SIM_TICK].last_us =
        (u64)(limits.sim_tick_cost_ms_max + 1u) * 1000ull;

    if (dom_budget_enforcer_update(&enforcer, &frame, &sample, 0u, 0u) != 0) {
        return fail("budget update failed");
    }
    if (dom_budget_enforcer_get_state(&enforcer, &state) != 0) {
        return fail("budget state fetch failed");
    }
    if ((state.over_mask & DOM_BUDGET_OVER_SIM_TICK) == 0u) {
        return fail("expected sim tick over-budget flag");
    }
    if (state.fidelity_max != DOM_BUDGET_FIDELITY_MED) {
        return fail("expected fidelity drop on over-budget sim tick");
    }
    if (state.derived_budget_ms >= limits.derived_jobs_ms_per_frame_max) {
        return fail("expected derived budget to reduce under pressure");
    }
    return 0;
}

static int test_surface_streaming_stress(void) {
    dom_surface_chunks_desc desc;
    dom_surface_chunks *chunks;
    u32 count = 0u;
    const u32 limit = 8u;

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_SURFACE_CHUNKS_DESC_VERSION;
    desc.max_chunks = 16u;
    desc.chunk_size_m = 16u;

    chunks = dom_surface_chunks_create(&desc);
    if (!chunks) {
        return fail("surface chunks create failed");
    }

    for (u32 i = 0u; i < desc.max_chunks; ++i) {
        dom_surface_chunk_key key;
        dom_surface_chunk_status status;
        key.body_id = 1ull;
        key.step_turns_q16 = 1;
        key.lat_index = (i32)i;
        key.lon_index = 0;
        if (dom_surface_chunk_get_or_create(chunks, &key, &status) != DOM_SURFACE_CHUNKS_OK) {
            dom_surface_chunks_destroy(chunks);
            return fail("surface chunk create failed");
        }
        if (dom_surface_chunk_request_load(chunks, &key) != DOM_SURFACE_CHUNKS_OK) {
            dom_surface_chunks_destroy(chunks);
            return fail("surface chunk request failed");
        }
    }

    if (dom_surface_chunks_list_active(chunks, 0, 0u, &count) != DOM_SURFACE_CHUNKS_OK) {
        dom_surface_chunks_destroy(chunks);
        return fail("surface chunk list failed");
    }
    if (count < desc.max_chunks) {
        dom_surface_chunks_destroy(chunks);
        return fail("expected active chunks to reach max before eviction");
    }

    (void)dom_surface_chunk_evict(chunks, limit);
    if (dom_surface_chunks_list_active(chunks, 0, 0u, &count) != DOM_SURFACE_CHUNKS_OK) {
        dom_surface_chunks_destroy(chunks);
        return fail("surface chunk list failed after eviction");
    }
    if (count > limit) {
        dom_surface_chunks_destroy(chunks);
        return fail("expected active chunks to respect eviction limit");
    }

    dom_surface_chunks_destroy(chunks);
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_baseline_perf_sim()) != 0) return rc;
    if ((rc = test_warp_perf()) != 0) return rc;
    if ((rc = test_surface_streaming_stress()) != 0) return rc;
    std::printf("dominium perf tests passed\n");
    return 0;
}

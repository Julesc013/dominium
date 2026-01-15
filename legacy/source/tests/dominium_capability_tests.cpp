/*
FILE: source/tests/dominium_capability_tests.cpp
MODULE: Repository
RESPONSIBILITY: Contract tests for capability derivation and determinism.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS time, locales, or authoritative world state.
*/
#include <cstdio>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "runtime/dom_belief_store.h"
#include "runtime/dom_capability_engine.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static dom_belief_record make_record(u64 record_id,
                                     dom_capability_id cap,
                                     u32 subject_kind,
                                     u64 subject_id,
                                     i64 min_val,
                                     i64 max_val,
                                     dom_tick observed,
                                     dom_tick delivered,
                                     dom_tick expiry,
                                     u64 provenance,
                                     u32 flags,
                                     u32 resolution) {
    dom_belief_record r;
    r.record_id = record_id;
    r.capability_id = cap;
    r.subject.kind = subject_kind;
    r.subject.id = subject_id;
    r.resolution_tier = resolution;
    r.value_min = min_val;
    r.value_max = max_val;
    r.observed_tick = observed;
    r.delivery_tick = delivered;
    r.expiry_tick = expiry;
    r.source_provenance = provenance;
    r.flags = flags;
    return r;
}

static int snapshot_to_vec(const dom_capability_snapshot *snap,
                           std::vector<dom_capability> &out) {
    u32 count = 0u;
    if (!snap) {
        return DOM_CAPABILITY_ENGINE_INVALID_ARGUMENT;
    }
    (void)dom_capability_snapshot_list(snap, 0, 0u, &count);
    out.resize(count);
    if (count > 0u) {
        (void)dom_capability_snapshot_list(snap, &out[0], count, &count);
    }
    return DOM_CAPABILITY_ENGINE_OK;
}

static int test_deterministic_order(void) {
    dom_belief_store *a = dom_belief_store_create();
    dom_belief_store *b = dom_belief_store_create();
    dom_capability_engine *engine_a = dom_capability_engine_create();
    dom_capability_engine *engine_b = dom_capability_engine_create();
    dom_belief_record r1 = make_record(1u, DOM_CAP_MAP_VIEW, DOM_CAP_SUBJECT_LOCATION, 10u,
                                       5, 15, 10, 12, 0, 100u, 0u, DOM_RESOLUTION_BOUNDED);
    dom_belief_record r2 = make_record(2u, DOM_CAP_HEALTH_STATUS, DOM_CAP_SUBJECT_ENTITY, 42u,
                                       80, 100, 10, 12, 0, 200u, 0u, DOM_RESOLUTION_EXACT);
    std::vector<dom_capability> cap_a;
    std::vector<dom_capability> cap_b;

    if (!a || !b || !engine_a || !engine_b) {
        return fail("setup failed");
    }

    (void)dom_belief_store_add_record(a, &r1);
    (void)dom_belief_store_add_record(a, &r2);
    (void)dom_belief_store_add_record(b, &r2);
    (void)dom_belief_store_add_record(b, &r1);

    if (!dom_capability_engine_build_snapshot(engine_a, 1u, a, 0, 100, 60u, 0, 0) ||
        !dom_capability_engine_build_snapshot(engine_b, 1u, b, 0, 100, 60u, 0, 0)) {
        return fail("snapshot build failed");
    }
    if (snapshot_to_vec(dom_capability_engine_build_snapshot(engine_a, 1u, a, 0, 100, 60u, 0, 0), cap_a) != 0 ||
        snapshot_to_vec(dom_capability_engine_build_snapshot(engine_b, 1u, b, 0, 100, 60u, 0, 0), cap_b) != 0) {
        return fail("snapshot list failed");
    }
    if (cap_a.size() != cap_b.size()) {
        return fail("capability counts differ");
    }
    for (size_t i = 0u; i < cap_a.size(); ++i) {
        if (cap_a[i].capability_id != cap_b[i].capability_id ||
            cap_a[i].subject.kind != cap_b[i].subject.kind ||
            cap_a[i].subject.id != cap_b[i].subject.id) {
            return fail("capability ordering mismatch");
        }
    }

    dom_belief_store_destroy(a);
    dom_belief_store_destroy(b);
    dom_capability_engine_destroy(engine_a);
    dom_capability_engine_destroy(engine_b);
    return 0;
}

static int test_removal(void) {
    dom_belief_store *store = dom_belief_store_create();
    dom_capability_engine *engine = dom_capability_engine_create();
    dom_belief_record r1 = make_record(10u, DOM_CAP_COMMAND_STATUS, DOM_CAP_SUBJECT_COMMAND, 99u,
                                       1, 1, 5, 5, 0, 10u, 0u, DOM_RESOLUTION_BINARY);
    const dom_capability_snapshot *snap;
    u32 count = 0u;

    if (!store || !engine) {
        return fail("setup failed");
    }
    (void)dom_belief_store_add_record(store, &r1);
    snap = dom_capability_engine_build_snapshot(engine, 1u, store, 0, 6, 60u, 0, 0);
    (void)dom_capability_snapshot_list(snap, 0, 0u, &count);
    if (count != 1u) {
        return fail("expected one capability");
    }
    (void)dom_belief_store_remove_record(store, r1.record_id);
    snap = dom_capability_engine_build_snapshot(engine, 1u, store, 0, 6, 60u, 0, 0);
    (void)dom_capability_snapshot_list(snap, 0, 0u, &count);
    if (count != 0u) {
        return fail("expected empty snapshot after removal");
    }
    dom_belief_store_destroy(store);
    dom_capability_engine_destroy(engine);
    return 0;
}

static int test_conflict_merge(void) {
    dom_belief_store *store = dom_belief_store_create();
    dom_capability_engine *engine = dom_capability_engine_create();
    dom_belief_record r1 = make_record(1u, DOM_CAP_MARKET_QUOTES, DOM_CAP_SUBJECT_MARKET, 7u,
                                       10, 20, 10, 12, 0, 1u, 0u, DOM_RESOLUTION_BOUNDED);
    dom_belief_record r2 = make_record(2u, DOM_CAP_MARKET_QUOTES, DOM_CAP_SUBJECT_MARKET, 7u,
                                       30, 40, 8, 9, 0, 2u, 0u, DOM_RESOLUTION_BOUNDED);
    std::vector<dom_capability> caps;
    if (!store || !engine) {
        return fail("setup failed");
    }
    (void)dom_belief_store_add_record(store, &r1);
    (void)dom_belief_store_add_record(store, &r2);
    if (snapshot_to_vec(dom_capability_engine_build_snapshot(engine, 1u, store, 0, 20, 60u, 0, 0), caps) != 0) {
        return fail("snapshot list failed");
    }
    if (caps.size() != 1u) {
        return fail("expected merged capability");
    }
    if (!(caps[0].flags & DOM_CAPABILITY_FLAG_CONFLICT)) {
        return fail("expected conflict flag");
    }
    if (caps[0].value_min != 10 || caps[0].value_max != 40) {
        return fail("merged range incorrect");
    }
    dom_belief_store_destroy(store);
    dom_capability_engine_destroy(engine);
    return 0;
}

static int test_uncertainty_scaling(void) {
    dom_belief_store *store = dom_belief_store_create();
    dom_capability_engine *engine = dom_capability_engine_create();
    dom_belief_record r1 = make_record(1u, DOM_CAP_INVENTORY_SUMMARY, DOM_CAP_SUBJECT_RESOURCE, 2u,
                                       10, 20, 10, 11, 0, 3u, 0u, DOM_RESOLUTION_BOUNDED);
    dom_capability_filters filters;
    std::vector<dom_capability> caps;
    if (!store || !engine) {
        return fail("setup failed");
    }
    filters.latency_scale_q16 = 0;
    filters.uncertainty_scale_q16 = (2 << 16);
    filters.staleness_grace_ticks = 0u;
    (void)dom_belief_store_add_record(store, &r1);
    if (snapshot_to_vec(dom_capability_engine_build_snapshot(engine, 1u, store, 0, 20, 60u, 0, &filters), caps) != 0) {
        return fail("snapshot list failed");
    }
    if (caps.empty()) {
        return fail("missing capability");
    }
    if (caps[0].value_min != 5 || caps[0].value_max != 25) {
        return fail("uncertainty scale incorrect");
    }
    if (!(caps[0].flags & DOM_CAPABILITY_FLAG_DEGRADED)) {
        return fail("expected degraded flag");
    }
    dom_belief_store_destroy(store);
    dom_capability_engine_destroy(engine);
    return 0;
}

static int test_time_and_calendar_caps(void) {
    dom_time_knowledge *tk = dom_time_knowledge_create(1u);
    dom_capability_engine *engine = dom_capability_engine_create();
    dom_time_clock_def sundial;
    dom_time_clock_env env = { D_TRUE, D_TRUE, D_TRUE, 0u, 0u };
    std::vector<dom_capability> caps;
    d_bool found_clock = D_FALSE;
    d_bool found_calendar = D_FALSE;

    if (!tk || !engine) {
        return fail("setup failed");
    }
    (void)dom_time_clock_init_sundial(100u, DOM_TIME_FRAME_ACT, &sundial);
    (void)dom_time_knowledge_add_clock(tk, &sundial, 0);
    (void)dom_time_knowledge_add_calendar(tk, 42u);

    if (snapshot_to_vec(dom_capability_engine_build_snapshot(engine, 1u, 0, tk, 120, 60u, &env, 0), caps) != 0) {
        return fail("snapshot list failed");
    }
    for (size_t i = 0u; i < caps.size(); ++i) {
        if (caps[i].capability_id == DOM_CAP_TIME_READOUT &&
            caps[i].subject.kind == DOM_CAP_SUBJECT_CLOCK &&
            caps[i].subject.id == 100u) {
            found_clock = D_TRUE;
        }
        if (caps[i].capability_id == DOM_CAP_CALENDAR_VIEW &&
            caps[i].subject.kind == DOM_CAP_SUBJECT_CALENDAR &&
            caps[i].subject.id == 42u) {
            found_calendar = D_TRUE;
        }
    }
    if (found_clock == D_FALSE) {
        return fail("missing time readout capability");
    }
    if (found_calendar == D_FALSE) {
        return fail("missing calendar capability");
    }
    dom_time_knowledge_destroy(tk);
    dom_capability_engine_destroy(engine);
    return 0;
}

static int test_unknown_propagation(void) {
    dom_belief_store *store = dom_belief_store_create();
    dom_capability_engine *engine = dom_capability_engine_create();
    dom_belief_record r1 = make_record(77u, DOM_CAP_ENVIRONMENTAL_STATUS, DOM_CAP_SUBJECT_ENV, 11u,
                                       0, 0, 2, 2, 0, 9u, DOM_BELIEF_FLAG_UNKNOWN, DOM_RESOLUTION_UNKNOWN);
    std::vector<dom_capability> caps;
    if (!store || !engine) {
        return fail("setup failed");
    }
    (void)dom_belief_store_add_record(store, &r1);
    if (snapshot_to_vec(dom_capability_engine_build_snapshot(engine, 1u, store, 0, 5, 60u, 0, 0), caps) != 0) {
        return fail("snapshot list failed");
    }
    if (caps.empty()) {
        return fail("missing capability");
    }
    if (!(caps[0].flags & DOM_CAPABILITY_FLAG_UNKNOWN)) {
        return fail("expected unknown flag");
    }
    if (caps[0].resolution_tier != DOM_RESOLUTION_UNKNOWN) {
        return fail("expected unknown resolution");
    }
    dom_belief_store_destroy(store);
    dom_capability_engine_destroy(engine);
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_deterministic_order()) != 0) return rc;
    if ((rc = test_removal()) != 0) return rc;
    if ((rc = test_conflict_merge()) != 0) return rc;
    if ((rc = test_uncertainty_scaling()) != 0) return rc;
    if ((rc = test_time_and_calendar_caps()) != 0) return rc;
    if ((rc = test_unknown_propagation()) != 0) return rc;
    std::printf("dominium capability tests passed\n");
    return 0;
}

/*
FILE: source/tests/dom_derived_order_independence_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure derived job ordering does not affect sim hash.
*/
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "sim/d_sim_hash.h"
}

#include "runtime/dom_derived_jobs.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static d_world *make_world(void) {
    d_world_meta meta;
    std::memset(&meta, 0, sizeof(meta));
    meta.seed = 12345u;
    meta.world_size_m = 1024u;
    meta.vertical_min = d_q16_16_from_int(-64);
    meta.vertical_max = d_q16_16_from_int(64);
    meta.core_version = 1u;
    meta.suite_version = 1u;
    meta.compat_profile_id = 0u;
    meta.extra.ptr = (unsigned char *)0;
    meta.extra.len = 0u;
    return d_world_create(&meta);
}

static int pump_jobs(dom_derived_job_kind a, dom_derived_job_kind b) {
    dom_derived_queue_desc desc;
    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_DERIVED_QUEUE_DESC_VERSION;

    dom_derived_queue *queue = dom_derived_queue_create(&desc);
    if (!queue) {
        return 0;
    }

    if (dom_derived_submit(queue, a, (const dom_derived_job_payload *)0, 1) == 0u) {
        dom_derived_queue_destroy(queue);
        return 0;
    }
    if (dom_derived_submit(queue, b, (const dom_derived_job_payload *)0, 2) == 0u) {
        dom_derived_queue_destroy(queue);
        return 0;
    }

    (void)dom_derived_pump(queue, 10u, 0u, 8u);
    dom_derived_queue_destroy(queue);
    return 1;
}

int main() {
    d_world *world = make_world();
    if (!world) {
        return fail("world_create");
    }

    const d_world_hash h0 = d_sim_hash_world(world);

    if (!pump_jobs(DERIVED_BUILD_MESH, DERIVED_BUILD_MAP_TILE)) {
        d_world_destroy(world);
        return fail("pump_jobs_ab");
    }
    const d_world_hash h1 = d_sim_hash_world(world);

    if (!pump_jobs(DERIVED_BUILD_MAP_TILE, DERIVED_BUILD_MESH)) {
        d_world_destroy(world);
        return fail("pump_jobs_ba");
    }
    const d_world_hash h2 = d_sim_hash_world(world);

    if (h0 != h1 || h0 != h2) {
        d_world_destroy(world);
        return fail("hash_changed");
    }

    d_world_destroy(world);
    return 0;
}

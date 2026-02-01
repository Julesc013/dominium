/*
FILE: tests/contract/dominium_no_modal_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for no-modal-loading, derived ordering, and snapshot isolation.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstring>

#include "runtime/dom_derived_jobs.h"
#include "runtime/dom_game_handshake.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_io_guard.h"
#include "runtime/dom_snapshot.h"

#include "dom_game_net.h"
#include "dom_instance.h"
#include "dom_session.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void init_instance(dom::InstanceInfo &inst) {
    inst.id = "test_instance";
    inst.world_seed = 1u;
    inst.world_size_m = 1024u;
    inst.vertical_min_m = -64;
    inst.vertical_max_m = 256;
    inst.suite_version = 1u;
    inst.core_version = 1u;
    inst.last_product = "game";
    inst.last_product_version = "0.0.0";
    inst.packs.clear();
    inst.mods.clear();
}

static dom_game_runtime *make_runtime(dom::DomSession &session,
                                      dom::DomGameNet &net,
                                      dom::InstanceInfo &inst) {
    dom_game_runtime_init_desc desc;
    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
    desc.session = &session;
    desc.net = &net;
    desc.instance = &inst;
    desc.ups = 60u;
    desc.run_id = 1ull;
    return dom_game_runtime_create(&desc);
}

static int test_no_modal_loading(void) {
    dom_io_guard_reset();
    dom_io_guard_enter_ui();
    {
        dom::DomGameHandshake hs;
        if (dom::dom_game_handshake_from_file("missing_handshake.tlv", hs)) {
            dom_io_guard_exit_ui();
            return fail("handshake read unexpectedly succeeded under UI scope");
        }
        if (dom_io_guard_violation_count() != 1u) {
            dom_io_guard_exit_ui();
            return fail("expected IO violation count increment");
        }
    }
    dom_io_guard_exit_ui();

    {
        dom_derived_queue_desc desc;
        dom_derived_queue *queue;
        dom_derived_job_budget_hint hint;
        dom_derived_job_payload payload;
        dom_derived_job_id job_id;
        dom_derived_job_status status;

        std::memset(&desc, 0, sizeof(desc));
        desc.struct_size = sizeof(desc);
        desc.struct_version = DOM_DERIVED_QUEUE_DESC_VERSION;
        desc.max_jobs = 4u;
        desc.max_payload_bytes = 256u;
        desc.flags = 0u;

        queue = dom_derived_queue_create(&desc);
        if (!queue) {
            return fail("derived queue create failed");
        }

        hint.work_ms = 50u;
        hint.io_bytes = 1024u;
        payload.data = &hint;
        payload.size = sizeof(hint);

        job_id = dom_derived_submit(queue, DERIVED_IO_READ_FILE, &payload, 0);
        if (job_id == 0u) {
            dom_derived_queue_destroy(queue);
            return fail("derived IO job submission failed");
        }

        if (dom_derived_pump(queue, 1u, 16u, 1u) != 0) {
            dom_derived_queue_destroy(queue);
            return fail("IO job should not run under budget/IO-disabled queue");
        }

        std::memset(&status, 0, sizeof(status));
        if (dom_derived_poll(queue, job_id, &status) != 0) {
            dom_derived_queue_destroy(queue);
            return fail("derived job poll failed");
        }
        if (status.state != DOM_DERIVED_JOB_PENDING) {
            dom_derived_queue_destroy(queue);
            return fail("expected IO job to remain pending");
        }

        dom_derived_queue_destroy(queue);
    }

    return 0;
}

static int run_derived_jobs(const dom_derived_job_kind *kinds, size_t count) {
    size_t i;
    dom_derived_queue_desc desc;
    dom_derived_queue *queue;
    dom_derived_stats stats;

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_DERIVED_QUEUE_DESC_VERSION;
    desc.max_jobs = 8u;
    desc.max_payload_bytes = 256u;
    desc.flags = 0u;

    queue = dom_derived_queue_create(&desc);
    if (!queue) {
        return fail("derived queue create failed");
    }

    for (i = 0u; i < count; ++i) {
        if (dom_derived_submit(queue, kinds[i], 0, 0) == 0u) {
            dom_derived_queue_destroy(queue);
            return fail("derived job submission failed");
        }
    }

    (void)dom_derived_pump(queue, 5u, 0u, (u32)count);
    std::memset(&stats, 0, sizeof(stats));
    if (dom_derived_stats(queue, &stats) != 0) {
        dom_derived_queue_destroy(queue);
        return fail("derived stats failed");
    }
    if (stats.completed != (u32)count) {
        dom_derived_queue_destroy(queue);
        return fail("expected all derived jobs to complete");
    }

    dom_derived_queue_destroy(queue);
    return 0;
}

static int test_derived_order_independence(void) {
    dom::DomSession session;
    dom::DomGameNet net;
    dom::InstanceInfo inst;
    dom_game_runtime *rt;
    u64 h0;
    u64 h1;
    u64 h2;
    const dom_derived_job_kind order_a[] = {
        DERIVED_BUILD_MESH,
        DERIVED_DECOMPRESS,
        DERIVED_BUILD_MAP_TILE
    };
    const dom_derived_job_kind order_b[] = {
        DERIVED_BUILD_MAP_TILE,
        DERIVED_BUILD_MESH,
        DERIVED_DECOMPRESS
    };

    init_instance(inst);
    rt = make_runtime(session, net, inst);
    if (!rt) {
        return fail("runtime create failed");
    }
    h0 = dom_game_runtime_get_hash(rt);

    if (run_derived_jobs(order_a, sizeof(order_a) / sizeof(order_a[0])) != 0) {
        dom_game_runtime_destroy(rt);
        return 1;
    }
    h1 = dom_game_runtime_get_hash(rt);
    if (h1 != h0) {
        dom_game_runtime_destroy(rt);
        return fail("derived job completion altered runtime hash (order A)");
    }

    if (run_derived_jobs(order_b, sizeof(order_b) / sizeof(order_b[0])) != 0) {
        dom_game_runtime_destroy(rt);
        return 1;
    }
    h2 = dom_game_runtime_get_hash(rt);
    if (h2 != h0) {
        dom_game_runtime_destroy(rt);
        return fail("derived job completion altered runtime hash (order B)");
    }

    dom_game_runtime_destroy(rt);
    return 0;
}

static int test_snapshot_isolation(void) {
    dom::DomSession session;
    dom::DomGameNet net;
    dom::InstanceInfo inst;
    dom_game_runtime *rt;
    u64 h0;
    u64 h1;
    unsigned i;

    init_instance(inst);
    rt = make_runtime(session, net, inst);
    if (!rt) {
        return fail("runtime create failed");
    }

    h0 = dom_game_runtime_get_hash(rt);
    for (i = 0u; i < 8u; ++i) {
        dom_game_snapshot *snap = dom_game_runtime_build_snapshot(rt, DOM_GAME_SNAPSHOT_FLAG_RUNTIME);
        if (!snap) {
            dom_game_runtime_destroy(rt);
            return fail("snapshot build failed");
        }
        if (snap->runtime.struct_version != DOM_RUNTIME_SUMMARY_SNAPSHOT_VERSION) {
            dom_game_runtime_release_snapshot(snap);
            dom_game_runtime_destroy(rt);
            return fail("snapshot version mismatch");
        }
        dom_game_runtime_release_snapshot(snap);
    }
    h1 = dom_game_runtime_get_hash(rt);
    if (h1 != h0) {
        dom_game_runtime_destroy(rt);
        return fail("snapshot build altered runtime hash");
    }

    dom_game_runtime_destroy(rt);
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_no_modal_loading()) != 0) return rc;
    if ((rc = test_derived_order_independence()) != 0) return rc;
    if ((rc = test_snapshot_isolation()) != 0) return rc;
    std::printf("dominium no-modal-loading tests passed\n");
    return 0;
}
